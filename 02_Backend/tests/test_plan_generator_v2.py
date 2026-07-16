"""
训练计划管理模块白盒测试脚本
测试对象：PlanGeneratorV2核心方法 + TrainingPlan.get_cycle_days() + TrainingSchedule.can_postpone()
运行方式：cd D:/FitnessGraduationProject/02_Backend; python -m unittest tests/test_plan_generator_v2.py -v
"""

import unittest
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.plan_generator_v2 import PlanGeneratorV2
from app.models.plan import (
    TrainingPlan, PlanSession, SessionActionItem, TrainingSchedule,
    PlanTypeEnum, SchemeTypeEnum, SessionTypeEnum, ScheduleStatusEnum
)
from app.models.action import TrainingAction, ActionCategoryEnum, DifficultyLevelEnum


def _create_mock_user(fitness_goal="增肌", experience_level="中级", age=25):
    return SimpleNamespace(
        user_id="test_user_001",
        name="测试用户",
        phone="13800000001",
        fitness_goal=fitness_goal,
        experience_level=experience_level,
        age=age,
        preferred_muscles=None
    )


def _create_mock_action(
    action_id="act_001",
    name="测试动作",
    action_category=ActionCategoryEnum.MAIN_STRENGTH,
    difficulty_level=DifficultyLevelEnum.INTERMEDIATE,
    target_muscles=None,
    equipment_id="eq_001",
    estimated_seconds=3
):
    action = SimpleNamespace(
        action_id=action_id,
        name=name,
        action_category=action_category,
        difficulty_level=difficulty_level,
        target_muscles=json.dumps(target_muscles, ensure_ascii=False) if target_muscles else None,
        equipment_id=equipment_id,
        estimated_seconds=estimated_seconds,
        video_demo_url=None,
        image_url=None,
        safety_tips=None
    )
    action.get_target_muscles_list = lambda: (
        json.loads(action.target_muscles) if action.target_muscles else []
    )
    return action


def _create_generator(user=None, equipment_ids=None):
    if user is None:
        user = _create_mock_user()
    db = MagicMock()
    if equipment_ids is None:
        equipment_ids = {"eq_001", "eq_002", "eq_003", "eq_006", "eq_018"}
    rel_results = [SimpleNamespace(equipment_id=eid) for eid in equipment_ids]

    def _query_side_effect(model):
        mock_q = MagicMock()
        mock_q.filter.return_value.all.return_value = rel_results
        mock_q.filter.return_value.first.return_value = SimpleNamespace(
            inventory_id="inv_001", user_id="test_user_001", name="测试器材",
            equipment_id="eq_001"
        )
        return mock_q

    db.query.side_effect = _query_side_effect
    generator = object.__new__(PlanGeneratorV2)
    generator.db = db
    generator.user = user
    generator.inventory_id = "inv_001"
    generator.user_equipment_ids = equipment_ids
    return generator


def _setup_db_actions(generator, actions):
    def query_side_effect(model):
        mock_q = MagicMock()
        mock_q.filter.return_value.all.return_value = actions
        mock_q.filter.return_value.first.return_value = actions[0] if actions else None
        return mock_q

    generator.db.query.side_effect = query_side_effect


class TestFatLossPlanStructure(unittest.TestCase):

    def setUp(self):
        self.generator = _create_generator(
            user=_create_mock_user(fitness_goal="减脂", experience_level="中级")
        )
        warmup_actions = [
            _create_mock_action(action_id=f"w{i}", action_category=ActionCategoryEnum.WARMUP,
                                difficulty_level=DifficultyLevelEnum.BEGINNER, estimated_seconds=30)
            for i in range(3)
        ]
        strength_actions = [
            _create_mock_action(action_id=f"s{i}", action_category=ActionCategoryEnum.MAIN_STRENGTH,
                                difficulty_level=DifficultyLevelEnum.INTERMEDIATE, estimated_seconds=3)
            for i in range(4)
        ]
        cardio_action = _create_mock_action(
            action_id="c1", action_category=ActionCategoryEnum.MAIN_CARDIO,
            difficulty_level=DifficultyLevelEnum.INTERMEDIATE, estimated_seconds=45,
            equipment_id="eq_018"
        )
        cooldown_actions = [
            _create_mock_action(action_id=f"cd{i}", action_category=ActionCategoryEnum.COOLDOWN,
                                difficulty_level=DifficultyLevelEnum.BEGINNER, estimated_seconds=25)
            for i in range(3)
        ]
        all_actions = warmup_actions + strength_actions + [cardio_action] + cooldown_actions
        _setup_db_actions(self.generator, all_actions)

    def test_fat_loss_generates_three_training_days(self):
        sessions = self.generator._generate_fat_loss_plan()
        training_parts = set()
        for s in sessions:
            if hasattr(s, 'training_part') and s.training_part:
                training_parts.add(s.training_part)
        self.assertEqual(training_parts, {"推", "腿", "拉"})

    def test_fat_loss_each_day_has_three_sessions(self):
        sessions = self.generator._generate_fat_loss_plan()
        for part in ["推", "腿", "拉"]:
            part_sessions = [s for s in sessions if hasattr(s, 'training_part') and s.training_part == part]
            self.assertEqual(len(part_sessions), 3, f"{part}日应有3个阶段")

    def test_fat_loss_session_types_are_warmup_main_cooldown(self):
        sessions = self.generator._generate_fat_loss_plan()
        for part in ["推", "腿", "拉"]:
            part_sessions = [s for s in sessions if hasattr(s, 'training_part') and s.training_part == part]
            types = [s.session_type for s in part_sessions]
            self.assertIn(SessionTypeEnum.WARMUP, types)
            self.assertIn(SessionTypeEnum.MAIN, types)
            self.assertIn(SessionTypeEnum.COOLDOWN, types)

    def test_fat_loss_warmup_has_three_actions(self):
        sessions = self.generator._generate_fat_loss_plan()
        warmup_sessions = [s for s in sessions if s.session_type == SessionTypeEnum.WARMUP]
        for ws in warmup_sessions:
            self.assertEqual(len(ws.action_items), 3)

    def test_fat_loss_main_has_strength_plus_cardio(self):
        sessions = self.generator._generate_fat_loss_plan()
        main_sessions = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN]
        for ms in main_sessions:
            self.assertEqual(len(ms.action_items), 5)

    def test_fat_loss_cooldown_has_three_actions(self):
        sessions = self.generator._generate_fat_loss_plan()
        cooldown_sessions = [s for s in sessions if s.session_type == SessionTypeEnum.COOLDOWN]
        for cs in cooldown_sessions:
            self.assertEqual(len(cs.action_items), 3)

    def test_fat_loss_total_sessions(self):
        sessions = self.generator._generate_fat_loss_plan()
        self.assertEqual(len(sessions), 9)


class TestMuscleGainOneSplitActionCount(unittest.TestCase):

    def setUp(self):
        self.generator = _create_generator()
        actions = [
            _create_mock_action(action_id=f"w{i}", action_category=ActionCategoryEnum.WARMUP,
                                estimated_seconds=30, equipment_id="none")
            for i in range(3)
        ] + [
            _create_mock_action(action_id=f"s{i}", action_category=ActionCategoryEnum.MAIN_STRENGTH,
                                estimated_seconds=3, equipment_id="none")
            for i in range(6)
        ] + [
            _create_mock_action(action_id=f"cd{i}", action_category=ActionCategoryEnum.COOLDOWN,
                                estimated_seconds=25, equipment_id="none")
            for i in range(3)
        ]
        _setup_db_actions(self.generator, actions)

    def test_one_split_main_session_has_six_actions(self):
        sessions = self.generator._generate_muscle_gain_plan(SchemeTypeEnum.ONE_SPLIT, None)
        main_session = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN]
        self.assertEqual(len(main_session), 1)
        self.assertEqual(len(main_session[0].action_items), 6)


class TestMuscleGainMultiSplitActionCount(unittest.TestCase):

    def setUp(self):
        self.generator = _create_generator()
        actions = [
            _create_mock_action(action_id=f"w{i}", action_category=ActionCategoryEnum.WARMUP,
                                estimated_seconds=30, equipment_id="none")
            for i in range(3)
        ] + [
            _create_mock_action(action_id=f"s{i}", action_category=ActionCategoryEnum.MAIN_STRENGTH,
                                estimated_seconds=3, equipment_id="none")
            for i in range(4)
        ] + [
            _create_mock_action(action_id=f"cd{i}", action_category=ActionCategoryEnum.COOLDOWN,
                                estimated_seconds=25, equipment_id="none")
            for i in range(3)
        ]
        _setup_db_actions(self.generator, actions)

    def test_two_split_main_session_has_four_actions(self):
        sessions = self.generator._generate_muscle_gain_plan(SchemeTypeEnum.TWO_SPLIT, None)
        main_session = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN]
        self.assertEqual(len(main_session), 1)
        self.assertEqual(len(main_session[0].action_items), 4)

    def test_three_split_main_session_has_four_actions(self):
        sessions = self.generator._generate_muscle_gain_plan(SchemeTypeEnum.THREE_SPLIT, None)
        main_session = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN]
        self.assertEqual(len(main_session), 1)
        self.assertEqual(len(main_session[0].action_items), 4)

    def test_four_split_main_session_has_four_actions(self):
        sessions = self.generator._generate_muscle_gain_plan(SchemeTypeEnum.FOUR_SPLIT, None)
        main_session = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN]
        self.assertEqual(len(main_session), 1)
        self.assertEqual(len(main_session[0].action_items), 4)


class TestGetCycleDays(unittest.TestCase):

    def _create_plan_with_cycle(self, cycle_rule):
        plan = SimpleNamespace(cycle_rule=cycle_rule)
        plan.get_cycle_days = TrainingPlan.get_cycle_days.__get__(plan)
        return plan

    def test_cycle_3on_1off(self):
        plan = self._create_plan_with_cycle("练 3 休 1")
        self.assertEqual(plan.get_cycle_days(), 4)

    def test_cycle_2on_1off(self):
        plan = self._create_plan_with_cycle("练 2 休 1")
        self.assertEqual(plan.get_cycle_days(), 3)

    def test_cycle_2on_1off_2on_2off(self):
        plan = self._create_plan_with_cycle("练 2 休 1, 练 2 休 2")
        self.assertEqual(plan.get_cycle_days(), 7)

    def test_cycle_unknown_rule(self):
        plan = self._create_plan_with_cycle("练 1 休 1")
        self.assertEqual(plan.get_cycle_days(), 4)

    def test_cycle_none(self):
        plan = self._create_plan_with_cycle(None)
        self.assertEqual(plan.get_cycle_days(), 4)


class TestCanPostpone(unittest.TestCase):

    def _create_schedule(self, postpone_count=0):
        schedule = SimpleNamespace(postpone_count=postpone_count)
        schedule.can_postpone = TrainingSchedule.can_postpone.__get__(schedule)
        return schedule

    def test_can_postpone_allowed(self):
        schedule = self._create_schedule(postpone_count=1)
        self.assertTrue(schedule.can_postpone(1))

    def test_can_postpone_exactly_three(self):
        schedule = self._create_schedule(postpone_count=0)
        self.assertTrue(schedule.can_postpone(3))

    def test_can_postpone_exceeded(self):
        schedule = self._create_schedule(postpone_count=3)
        self.assertFalse(schedule.can_postpone(1))

    def test_can_postpone_would_exceed(self):
        schedule = self._create_schedule(postpone_count=2)
        self.assertFalse(schedule.can_postpone(2))

    def test_can_postpone_zero_count(self):
        schedule = self._create_schedule(postpone_count=0)
        self.assertTrue(schedule.can_postpone(1))

    def test_can_postpone_two_days(self):
        schedule = self._create_schedule(postpone_count=1)
        self.assertTrue(schedule.can_postpone(2))


class TestDefaultParameters(unittest.TestCase):

    def setUp(self):
        self.generator = _create_generator()
        actions = [
            _create_mock_action(action_id=f"s{i}", action_category=ActionCategoryEnum.MAIN_STRENGTH,
                                estimated_seconds=3, equipment_id="none")
            for i in range(4)
        ] + [
            _create_mock_action(action_id=f"w{i}", action_category=ActionCategoryEnum.WARMUP,
                                estimated_seconds=30, equipment_id="none")
            for i in range(3)
        ] + [
            _create_mock_action(action_id=f"cd{i}", action_category=ActionCategoryEnum.COOLDOWN,
                                estimated_seconds=25, equipment_id="none")
            for i in range(3)
        ]
        _setup_db_actions(self.generator, actions)

    def test_default_sets(self):
        sessions = self.generator._generate_muscle_gain_plan(SchemeTypeEnum.THREE_SPLIT, None)
        main_session = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN][0]
        for item in main_session.action_items:
            self.assertEqual(item.sets, 4)

    def test_default_reps(self):
        sessions = self.generator._generate_muscle_gain_plan(SchemeTypeEnum.THREE_SPLIT, None)
        main_session = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN][0]
        for item in main_session.action_items:
            self.assertEqual(item.reps_per_set, 12)

    def test_default_rest_seconds(self):
        sessions = self.generator._generate_muscle_gain_plan(SchemeTypeEnum.THREE_SPLIT, None)
        main_session = [s for s in sessions if s.session_type == SessionTypeEnum.MAIN][0]
        for item in main_session.action_items:
            self.assertEqual(item.rest_seconds_default, 60)


class TestEquipmentAvailabilityFilter(unittest.TestCase):

    def setUp(self):
        self.user_equipment_ids = {"eq_001", "eq_002"}
        self.generator = _create_generator(equipment_ids=self.user_equipment_ids)
        available_action = _create_mock_action(
            action_id="available", equipment_id="eq_001",
            action_category=ActionCategoryEnum.MAIN_STRENGTH, estimated_seconds=3
        )
        unavailable_action = _create_mock_action(
            action_id="unavailable", equipment_id="eq_999",
            action_category=ActionCategoryEnum.MAIN_STRENGTH, estimated_seconds=3
        )
        no_equip_action = _create_mock_action(
            action_id="no_equip", equipment_id="none",
            action_category=ActionCategoryEnum.MAIN_STRENGTH, estimated_seconds=3
        )
        _setup_db_actions(self.generator, [available_action, unavailable_action, no_equip_action])

    def test_available_equipment_action_included(self):
        filtered = self.generator._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH", target_muscles=["全身肌群"], count=10
        )
        filtered_ids = [a.action_id for a in filtered]
        self.assertIn("available", filtered_ids)

    def test_unavailable_equipment_action_excluded(self):
        filtered = self.generator._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH", target_muscles=["全身肌群"], count=10
        )
        filtered_ids = [a.action_id for a in filtered]
        self.assertNotIn("unavailable", filtered_ids)

    def test_no_equipment_action_included(self):
        filtered = self.generator._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH", target_muscles=["全身肌群"], count=10
        )
        filtered_ids = [a.action_id for a in filtered]
        self.assertIn("no_equip", filtered_ids)


class TestDifficultyAdaptationFilter(unittest.TestCase):

    def setUp(self):
        self.beginner_user = _create_mock_user(experience_level="BEGINNER")
        self.generator = _create_generator(user=self.beginner_user)
        beginner_action = _create_mock_action(
            action_id="beginner_act", difficulty_level="BEGINNER",
            action_category=ActionCategoryEnum.MAIN_STRENGTH, estimated_seconds=3,
            equipment_id="none"
        )
        intermediate_action = _create_mock_action(
            action_id="intermediate_act", difficulty_level="INTERMEDIATE",
            action_category=ActionCategoryEnum.MAIN_STRENGTH, estimated_seconds=3,
            equipment_id="none"
        )
        advanced_action = _create_mock_action(
            action_id="advanced_act", difficulty_level="ADVANCED",
            action_category=ActionCategoryEnum.MAIN_STRENGTH, estimated_seconds=3,
            equipment_id="none"
        )
        _setup_db_actions(self.generator, [beginner_action, intermediate_action, advanced_action])

    def test_beginner_plan_no_advanced_actions(self):
        filtered = self.generator._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH", target_muscles=["全身肌群"], count=10
        )
        filtered_ids = [a.action_id for a in filtered]
        self.assertNotIn("advanced_act", filtered_ids)

    def test_beginner_plan_has_beginner_actions(self):
        filtered = self.generator._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH", target_muscles=["全身肌群"], count=10
        )
        filtered_ids = [a.action_id for a in filtered]
        self.assertIn("beginner_act", filtered_ids)

    def test_beginner_plan_has_intermediate_actions(self):
        filtered = self.generator._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH", target_muscles=["全身肌群"], count=10
        )
        filtered_ids = [a.action_id for a in filtered]
        self.assertIn("intermediate_act", filtered_ids)


class TestMusclesMatch(unittest.TestCase):

    def setUp(self):
        self.generator = _create_generator()

    def test_exact_match(self):
        self.assertTrue(self.generator._muscles_match(["胸大肌"], ["胸大肌"]))

    def test_partial_match(self):
        self.assertTrue(self.generator._muscles_match(["胸大肌"], ["胸大肌", "三角肌"]))

    def test_no_match(self):
        self.assertFalse(self.generator._muscles_match(["背阔肌"], ["股四头肌"]))

    def test_empty_action_muscles(self):
        self.assertTrue(self.generator._muscles_match([], ["胸大肌"]))

    def test_empty_target_muscles(self):
        self.assertTrue(self.generator._muscles_match(["胸大肌"], []))

    def test_global_muscles_in_target(self):
        self.assertTrue(self.generator._muscles_match(["胸大肌"], ["全身肌群"]))

    def test_global_muscles_in_action(self):
        self.assertTrue(self.generator._muscles_match(["全身肌群"], ["胸大肌"]))

    def test_cardio_muscles_in_action(self):
        self.assertTrue(self.generator._muscles_match(["心肺功能"], ["胸大肌"]))

    def test_substring_match(self):
        self.assertTrue(self.generator._muscles_match(["三角肌前束"], ["三角肌"]))


class TestGetCycleRule(unittest.TestCase):

    def setUp(self):
        self.generator = _create_generator()

    def test_fat_loss_cycle_rule(self):
        rule = self.generator._get_cycle_rule(PlanTypeEnum.FAT_LOSS, None)
        self.assertEqual(rule, "练 3 休 1")

    def test_one_split_cycle_rule(self):
        rule = self.generator._get_cycle_rule(PlanTypeEnum.MUSCLE_GAIN, SchemeTypeEnum.ONE_SPLIT)
        self.assertEqual(rule, "练 1 休 1")

    def test_two_split_cycle_rule(self):
        rule = self.generator._get_cycle_rule(PlanTypeEnum.MUSCLE_GAIN, SchemeTypeEnum.TWO_SPLIT)
        self.assertEqual(rule, "练 2 休 1")

    def test_three_split_cycle_rule(self):
        rule = self.generator._get_cycle_rule(PlanTypeEnum.MUSCLE_GAIN, SchemeTypeEnum.THREE_SPLIT)
        self.assertEqual(rule, "练 3 休 1")

    def test_four_split_cycle_rule(self):
        rule = self.generator._get_cycle_rule(PlanTypeEnum.MUSCLE_GAIN, SchemeTypeEnum.FOUR_SPLIT)
        self.assertEqual(rule, "练 2 休 1, 练 2 休 2")


class TestValidateUserProfile(unittest.TestCase):

    def test_valid_profile(self):
        user = _create_mock_user(age=25, experience_level="中级", fitness_goal="增肌")
        generator = _create_generator(user=user)
        try:
            generator._validate_user_profile()
        except ValueError:
            self.fail("有效资料不应抛出异常")

    def test_missing_age(self):
        user = _create_mock_user(age=None, experience_level="中级", fitness_goal="增肌")
        generator = _create_generator(user=user)
        with self.assertRaises(ValueError) as ctx:
            generator._validate_user_profile()
        self.assertIn("完善身体数据", str(ctx.exception))

    def test_missing_experience_level(self):
        user = _create_mock_user(age=25, experience_level=None, fitness_goal="增肌")
        generator = _create_generator(user=user)
        with self.assertRaises(ValueError):
            generator._validate_user_profile()

    def test_missing_fitness_goal(self):
        user = _create_mock_user(age=25, experience_level="中级", fitness_goal=None)
        generator = _create_generator(user=user)
        with self.assertRaises(ValueError):
            generator._validate_user_profile()


class TestCreateActionItem(unittest.TestCase):

    def setUp(self):
        self.generator = _create_generator()
        self.action = _create_mock_action(
            action_id="act_test", estimated_seconds=3,
            action_category=ActionCategoryEnum.MAIN_STRENGTH,
            equipment_id="none"
        )

    def test_strength_action_total_duration(self):
        item = self.generator._create_action_item(
            self.action, "MAIN_STRENGTH",
            sets=4, reps=12, rest_seconds=60, sequence_order=1
        )
        expected = 4 * (3 * 12 + 60) - 60
        self.assertEqual(item.total_duration_seconds, expected)

    def test_warmup_action_total_duration(self):
        item = self.generator._create_action_item(
            self.action, "WARMUP", sequence_order=1
        )
        self.assertIsNotNone(item.total_duration_seconds)
        self.assertGreater(item.total_duration_seconds, 0)

    def test_cardio_action_total_duration(self):
        item = self.generator._create_action_item(
            self.action, "MAIN_CARDIO",
            duration_minutes=30, sequence_order=1
        )
        self.assertEqual(item.total_duration_seconds, 30 * 60)

    def test_cooldown_action_total_duration(self):
        item = self.generator._create_action_item(
            self.action, "COOLDOWN", sequence_order=1
        )
        self.assertIsNotNone(item.total_duration_seconds)
        self.assertGreater(item.total_duration_seconds, 0)

    def test_default_rest_seconds(self):
        item = self.generator._create_action_item(
            self.action, "MAIN_STRENGTH",
            sets=4, reps=12, rest_seconds=60, sequence_order=1
        )
        self.assertEqual(item.rest_seconds_default, 60)


class TestSchemeConfig(unittest.TestCase):

    def test_one_split_config(self):
        config = PlanGeneratorV2.SCHEME_CONFIG[SchemeTypeEnum.ONE_SPLIT]
        self.assertEqual(config["cycle_rule"], "练 1 休 1")
        self.assertEqual(config["training_parts"], ["全身"])
        self.assertEqual(config["actions_per_session"], 6)
        self.assertEqual(config["sets"], 4)
        self.assertEqual(config["reps"], 12)
        self.assertEqual(config["rest_seconds"], 60)

    def test_two_split_config(self):
        config = PlanGeneratorV2.SCHEME_CONFIG[SchemeTypeEnum.TWO_SPLIT]
        self.assertEqual(config["cycle_rule"], "练 2 休 1")
        self.assertEqual(config["training_parts"], ["上肢", "下肢"])
        self.assertEqual(config["actions_per_session"], 4)

    def test_three_split_config(self):
        config = PlanGeneratorV2.SCHEME_CONFIG[SchemeTypeEnum.THREE_SPLIT]
        self.assertEqual(config["cycle_rule"], "练 3 休 1")
        self.assertEqual(config["training_parts"], ["推", "腿", "拉"])
        self.assertEqual(config["actions_per_session"], 4)

    def test_four_split_config(self):
        config = PlanGeneratorV2.SCHEME_CONFIG[SchemeTypeEnum.FOUR_SPLIT]
        self.assertEqual(config["cycle_rule"], "练 2 休 1, 练 2 休 2")
        self.assertEqual(config["training_parts"], ["胸三头", "背二头", "肩", "腿"])
        self.assertEqual(config["actions_per_session"], 4)

    def test_fat_loss_config(self):
        config = PlanGeneratorV2.FAT_LOSS_CONFIG
        self.assertEqual(config["cycle_rule"], "练 3 休 1")
        self.assertEqual(config["training_parts"], ["推", "腿", "拉"])
        self.assertEqual(config["warmup_actions"], 3)
        self.assertEqual(config["strength_actions"], 4)
        self.assertEqual(config["cardio_duration_minutes"], 30)
        self.assertEqual(config["cooldown_actions"], 3)
        self.assertEqual(config["sets"], 4)
        self.assertEqual(config["reps"], 12)
        self.assertEqual(config["rest_seconds"], 60)


if __name__ == '__main__':
    unittest.main()
