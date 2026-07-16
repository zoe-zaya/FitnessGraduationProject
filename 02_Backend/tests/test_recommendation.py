"""
动作管理模块白盒测试脚本
测试对象：ActionRecommender推荐算法 + TrainingAction.is_suitable_for_user()
运行方式：cd D:/FitnessGraduationProject/02_Backend; python -m unittest tests/test_recommendation.py -v
"""

import unittest
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.recommendation import ActionRecommender
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
    action_category="main_strength",
    difficulty_level="中级",
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


def _create_suitable_action(difficulty_level=DifficultyLevelEnum.INTERMEDIATE):
    action = SimpleNamespace(
        difficulty_level=difficulty_level
    )
    action.is_suitable_for_user = TrainingAction.is_suitable_for_user.__get__(action)
    return action


class TestGoalWeightMuscleGain(unittest.TestCase):

    def setUp(self):
        self.user = _create_mock_user(fitness_goal="增肌", experience_level="中级")
        self.recommender = ActionRecommender(db=MagicMock(), user=self.user)

    def test_muscle_gain_strength_weight(self):
        weight = self.recommender._get_goal_weight("main_strength")
        self.assertEqual(weight, 1.5)

    def test_muscle_gain_cardio_weight(self):
        weight = self.recommender._get_goal_weight("main_cardio")
        self.assertEqual(weight, 0.8)

    def test_muscle_gain_warmup_weight(self):
        weight = self.recommender._get_goal_weight("warmup")
        self.assertEqual(weight, 1.0)

    def test_muscle_gain_cooldown_weight(self):
        weight = self.recommender._get_goal_weight("cooldown")
        self.assertEqual(weight, 1.0)

    def test_muscle_gain_strength_scores_higher_than_cardio(self):
        strength_action = _create_mock_action(
            action_id="s1", name="力量动作",
            action_category="main_strength", difficulty_level="中级",
            estimated_seconds=3
        )
        cardio_action = _create_mock_action(
            action_id="c1", name="有氧动作",
            action_category="main_cardio", difficulty_level="中级",
            estimated_seconds=45
        )
        strength_score = self.recommender._calculate_match_score(strength_action)
        cardio_score = self.recommender._calculate_match_score(cardio_action)
        self.assertGreater(strength_score, cardio_score)


class TestGoalWeightFatLoss(unittest.TestCase):

    def setUp(self):
        self.user = _create_mock_user(fitness_goal="减脂", experience_level="中级")
        self.recommender = ActionRecommender(db=MagicMock(), user=self.user)

    def test_fat_loss_cardio_weight(self):
        weight = self.recommender._get_goal_weight("main_cardio")
        self.assertEqual(weight, 1.5)

    def test_fat_loss_strength_weight(self):
        weight = self.recommender._get_goal_weight("main_strength")
        self.assertEqual(weight, 0.8)

    def test_fat_loss_cardio_scores_higher_than_strength(self):
        cardio_action = _create_mock_action(
            action_id="c1", name="有氧动作",
            action_category="main_cardio", difficulty_level="中级",
            estimated_seconds=45
        )
        strength_action = _create_mock_action(
            action_id="s1", name="力量动作",
            action_category="main_strength", difficulty_level="中级",
            estimated_seconds=3
        )
        cardio_score = self.recommender._calculate_match_score(cardio_action)
        strength_score = self.recommender._calculate_match_score(strength_action)
        self.assertGreater(cardio_score, strength_score)


class TestBeginnerFilterAdvanced(unittest.TestCase):

    def setUp(self):
        self.user = _create_mock_user(fitness_goal="增肌", experience_level="初学者")
        self.recommender = ActionRecommender(db=MagicMock(), user=self.user)

    def test_beginner_advanced_difficulty_weight_is_zero(self):
        weight = self.recommender._get_difficulty_weight("高级")
        self.assertEqual(weight, 0.0)

    def test_beginner_intermediate_difficulty_weight(self):
        weight = self.recommender._get_difficulty_weight("中级")
        self.assertEqual(weight, 0.9)

    def test_beginner_beginner_difficulty_weight(self):
        weight = self.recommender._get_difficulty_weight("初级")
        self.assertEqual(weight, 1.2)

    def test_beginner_advanced_action_base_score_is_zero(self):
        advanced_action = _create_mock_action(
            action_id="adv1", name="高级动作",
            action_category="main_strength", difficulty_level="高级",
            estimated_seconds=100
        )
        score = self.recommender._calculate_match_score(advanced_action)
        self.assertEqual(score, 0.0)

    def test_beginner_filter_removes_advanced_actions(self):
        beginner_action = _create_mock_action(
            action_id="b1", name="初级动作", difficulty_level="初级"
        )
        intermediate_action = _create_mock_action(
            action_id="i1", name="中级动作", difficulty_level="中级"
        )
        advanced_action = _create_mock_action(
            action_id="a1", name="高级动作", difficulty_level="高级"
        )
        actions = [beginner_action, intermediate_action, advanced_action]
        filtered = self.recommender._filter_by_user_profile(actions)
        filtered_ids = [a.action_id for a in filtered]
        self.assertIn("b1", filtered_ids)
        self.assertIn("i1", filtered_ids)
        self.assertNotIn("a1", filtered_ids)


class TestComprehensiveScoreCalculation(unittest.TestCase):

    def setUp(self):
        self.user = _create_mock_user(fitness_goal="增肌", experience_level="中级")
        self.recommender = ActionRecommender(db=MagicMock(), user=self.user)

    def test_score_calculation_goal_weight_applied(self):
        action = _create_mock_action(
            action_category="main_strength", difficulty_level="中级",
            estimated_seconds=100
        )
        goal_weight = self.recommender._get_goal_weight("main_strength")
        difficulty_weight = self.recommender._get_difficulty_weight("中级")
        expected_base = 100.0 * goal_weight * difficulty_weight
        score = self.recommender._calculate_match_score(action)
        self.assertAlmostEqual(score, expected_base, places=0)

    def test_score_calculation_cardio_lower_for_muscle_gain(self):
        action = _create_mock_action(
            action_category="main_cardio", difficulty_level="中级",
            estimated_seconds=100
        )
        score = self.recommender._calculate_match_score(action)
        self.assertLess(score, 100.0)

    def test_score_ordering_strength_over_cardio_for_muscle_gain(self):
        strength_action = _create_mock_action(
            action_id="s1", action_category="main_strength",
            difficulty_level="中级", estimated_seconds=3
        )
        cardio_action = _create_mock_action(
            action_id="c1", action_category="main_cardio",
            difficulty_level="中级", estimated_seconds=45
        )
        s_score = self.recommender._calculate_match_score(strength_action)
        c_score = self.recommender._calculate_match_score(cardio_action)
        self.assertGreater(s_score, c_score)

    def test_popularity_bonus_strength_optimal(self):
        action = _create_mock_action(
            action_category="main_strength", difficulty_level="中级",
            estimated_seconds=3
        )
        bonus = self.recommender._calculate_popularity_bonus(action)
        self.assertEqual(bonus, 5.0)

    def test_popularity_bonus_cardio_optimal(self):
        action = _create_mock_action(
            action_category="main_cardio", difficulty_level="中级",
            estimated_seconds=45
        )
        bonus = self.recommender._calculate_popularity_bonus(action)
        self.assertEqual(bonus, 5.0)

    def test_popularity_bonus_warmup_optimal(self):
        action = _create_mock_action(
            action_category="warmup", difficulty_level="初级",
            estimated_seconds=30
        )
        bonus = self.recommender._calculate_popularity_bonus(action)
        self.assertEqual(bonus, 5.0)

    def test_popularity_bonus_cooldown_optimal(self):
        action = _create_mock_action(
            action_category="cooldown", difficulty_level="初级",
            estimated_seconds=25
        )
        bonus = self.recommender._calculate_popularity_bonus(action)
        self.assertEqual(bonus, 5.0)

    def test_popularity_bonus_strength_suboptimal(self):
        action = _create_mock_action(
            action_category="main_strength", difficulty_level="中级",
            estimated_seconds=1
        )
        bonus = self.recommender._calculate_popularity_bonus(action)
        self.assertEqual(bonus, 2.0)

    def test_popularity_bonus_no_match(self):
        action = _create_mock_action(
            action_category="main_strength", difficulty_level="中级",
            estimated_seconds=100
        )
        bonus = self.recommender._calculate_popularity_bonus(action)
        self.assertEqual(bonus, 0.0)

    def test_muscle_bonus_with_preferred_muscles(self):
        self.user.preferred_muscles = ["胸大肌", "三角肌"]
        action = _create_mock_action(
            action_category="main_strength", difficulty_level="中级",
            target_muscles=["胸大肌", "肱三头肌"], estimated_seconds=3
        )
        bonus = self.recommender._calculate_muscle_bonus(action)
        self.assertEqual(bonus, 10.0)

    def test_muscle_bonus_no_overlap(self):
        self.user.preferred_muscles = ["股四头肌"]
        action = _create_mock_action(
            action_category="main_strength", difficulty_level="中级",
            target_muscles=["胸大肌", "三角肌"], estimated_seconds=3
        )
        bonus = self.recommender._calculate_muscle_bonus(action)
        self.assertEqual(bonus, 0.0)

    def test_muscle_bonus_multiple_overlap(self):
        self.user.preferred_muscles = ["胸大肌", "三角肌"]
        action = _create_mock_action(
            action_category="main_strength", difficulty_level="中级",
            target_muscles=["胸大肌", "三角肌"], estimated_seconds=3
        )
        bonus = self.recommender._calculate_muscle_bonus(action)
        self.assertEqual(bonus, 20.0)


class TestIsSuitableForUser(unittest.TestCase):

    def test_beginner_suitable_for_beginner_action(self):
        action = _create_suitable_action(difficulty_level=DifficultyLevelEnum.BEGINNER)
        self.assertTrue(action.is_suitable_for_user("初学者"))

    def test_beginner_suitable_for_intermediate_action(self):
        action = _create_suitable_action(difficulty_level=DifficultyLevelEnum.INTERMEDIATE)
        self.assertTrue(action.is_suitable_for_user("初学者"))

    def test_beginner_not_suitable_for_advanced_action(self):
        action = _create_suitable_action(difficulty_level=DifficultyLevelEnum.ADVANCED)
        self.assertFalse(action.is_suitable_for_user("初学者"))

    def test_intermediate_suitable_for_beginner_action(self):
        action = _create_suitable_action(difficulty_level=DifficultyLevelEnum.BEGINNER)
        self.assertTrue(action.is_suitable_for_user("中级"))

    def test_intermediate_suitable_for_intermediate_action(self):
        action = _create_suitable_action(difficulty_level=DifficultyLevelEnum.INTERMEDIATE)
        self.assertTrue(action.is_suitable_for_user("中级"))

    def test_intermediate_not_suitable_for_advanced_action(self):
        action = _create_suitable_action(difficulty_level=DifficultyLevelEnum.ADVANCED)
        self.assertFalse(action.is_suitable_for_user("中级"))

    def test_advanced_suitable_for_all_actions(self):
        for level in [DifficultyLevelEnum.BEGINNER, DifficultyLevelEnum.INTERMEDIATE, DifficultyLevelEnum.ADVANCED]:
            action = _create_suitable_action(difficulty_level=level)
            self.assertTrue(action.is_suitable_for_user("高级"), f"高级用户应适合{level.value}动作")


class TestReplaceRecommendSorting(unittest.TestCase):

    def test_sorting_by_muscle_similarity(self):
        original_muscles = {"胸大肌", "三角肌"}

        high_sim_muscles = {"胸大肌", "三角肌"}
        mid_sim_muscles = {"胸大肌"}
        low_sim_muscles = {"背阔肌"}

        high_sim = len(original_muscles & high_sim_muscles) / len(original_muscles)
        mid_sim = len(original_muscles & mid_sim_muscles) / len(original_muscles)
        low_sim = len(original_muscles & low_sim_muscles) / len(original_muscles)

        self.assertGreater(high_sim, mid_sim)
        self.assertGreater(mid_sim, low_sim)
        self.assertEqual(high_sim, 1.0)
        self.assertEqual(mid_sim, 0.5)
        self.assertEqual(low_sim, 0.0)

    def test_sorting_order_descending(self):
        similarities = [
            (MagicMock(), 1.0),
            (MagicMock(), 0.5),
            (MagicMock(), 0.0),
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        self.assertEqual(similarities[0][1], 1.0)
        self.assertEqual(similarities[1][1], 0.5)
        self.assertEqual(similarities[2][1], 0.0)


class TestAgeFilter(unittest.TestCase):

    def setUp(self):
        self.user = _create_mock_user(fitness_goal="增肌", experience_level="中级", age=65)
        self.recommender = ActionRecommender(db=MagicMock(), user=self.user)

    def test_elderly_high_impact_action_filtered(self):
        high_impact_action = _create_mock_action(
            action_id="hi1", name="波比跳",
            difficulty_level="中级", estimated_seconds=3
        )
        actions = [high_impact_action]
        filtered = self.recommender._filter_by_user_profile(actions)
        self.assertEqual(len(filtered), 0)

    def test_elderly_normal_action_kept(self):
        normal_action = _create_mock_action(
            action_id="n1", name="哑铃弯举",
            difficulty_level="中级", estimated_seconds=3
        )
        actions = [normal_action]
        filtered = self.recommender._filter_by_user_profile(actions)
        self.assertEqual(len(filtered), 1)

    def test_young_user_high_impact_action_kept(self):
        young_user = _create_mock_user(fitness_goal="增肌", experience_level="中级", age=25)
        young_recommender = ActionRecommender(db=MagicMock(), user=young_user)
        high_impact_action = _create_mock_action(
            action_id="hi1", name="波比跳",
            difficulty_level="中级", estimated_seconds=3
        )
        actions = [high_impact_action]
        filtered = young_recommender._filter_by_user_profile(actions)
        self.assertEqual(len(filtered), 1)


class TestDifficultyWeightMatrix(unittest.TestCase):

    def test_all_difficulty_weights_for_beginner(self):
        user = _create_mock_user(experience_level="初学者")
        recommender = ActionRecommender(db=MagicMock(), user=user)
        self.assertEqual(recommender._get_difficulty_weight("初级"), 1.2)
        self.assertEqual(recommender._get_difficulty_weight("中级"), 0.9)
        self.assertEqual(recommender._get_difficulty_weight("高级"), 0.0)

    def test_all_difficulty_weights_for_intermediate(self):
        user = _create_mock_user(experience_level="中级")
        recommender = ActionRecommender(db=MagicMock(), user=user)
        self.assertEqual(recommender._get_difficulty_weight("初级"), 1.1)
        self.assertEqual(recommender._get_difficulty_weight("中级"), 1.2)
        self.assertEqual(recommender._get_difficulty_weight("高级"), 0.9)

    def test_all_difficulty_weights_for_advanced(self):
        user = _create_mock_user(experience_level="高级")
        recommender = ActionRecommender(db=MagicMock(), user=user)
        self.assertEqual(recommender._get_difficulty_weight("初级"), 1.0)
        self.assertEqual(recommender._get_difficulty_weight("中级"), 1.1)
        self.assertEqual(recommender._get_difficulty_weight("高级"), 1.2)


if __name__ == '__main__':
    unittest.main()
