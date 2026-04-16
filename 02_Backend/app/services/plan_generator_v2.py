"""
训练计划生成服务（V2.1 版）
根据需求规格说明书 2.1 版实现
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import logging
import json

from app.models.user import User
from app.models.equipment import EquipmentInventory, GymEquipment, inventory_equipment_rel
from app.models.action import TrainingAction, ActionCategoryEnum, DifficultyLevelEnum
from app.models.plan import (
    TrainingPlan, PlanSession, SessionActionItem, TrainingSchedule,
    PlanTypeEnum, SchemeTypeEnum, SessionTypeEnum, ScheduleStatusEnum
)

logger = logging.getLogger(__name__)


class PlanGeneratorV2:
    """
    训练计划生成引擎（V2.1 版）
    支持减脂计划和增肌计划（四种分化方案）
    """
    
    # ==================== 训练部位与肌群映射 ====================
    TRAINING_PART_MUSCLES = {
        "胸部": ["胸大肌", "三角肌前束", "肱三头肌"],
        "背部": ["背阔肌", "斜方肌", "肱二头肌"],
        "肩部": ["三角肌", "斜方肌", "肩袖肌群"],
        "手臂": ["肱二头肌", "肱三头肌", "前臂肌群"],
        "腿部": ["股四头肌", "腘绳肌", "臀大肌", "小腿三头肌"],
        "臀部": ["臀大肌", "臀中肌", "臀小肌", "腘绳肌"],
        "核心": ["腹直肌", "腹外斜肌", "核心肌群"],
        "全身": ["全身肌群", "心肺功能", "核心肌群"],
        "上肢": ["胸大肌", "背阔肌", "三角肌", "肱二头肌", "肱三头肌"],
        "下肢": ["股四头肌", "腘绳肌", "臀大肌", "小腿三头肌"],
        "推": ["胸大肌", "三角肌", "肱三头肌"],
        "拉": ["背阔肌", "斜方肌", "肱二头肌"],
        "胸三头": ["胸大肌", "肱三头肌", "三角肌前束"],
        "背二头": ["背阔肌", "肱二头肌", "斜方肌"]
    }
    
    # ==================== 分化方案配置 ====================
    SCHEME_CONFIG = {
        SchemeTypeEnum.ONE_SPLIT: {
            "cycle_rule": "练 1 休 1",
            "training_parts": ["全身"],
            "actions_per_session": 6,
            "sets": 4,
            "reps": 12,
            "rest_seconds": 60
        },
        SchemeTypeEnum.TWO_SPLIT: {
            "cycle_rule": "练 2 休 1",
            "training_parts": ["上肢", "下肢"],
            "actions_per_session": 4,
            "sets": 4,
            "reps": 12,
            "rest_seconds": 60
        },
        SchemeTypeEnum.THREE_SPLIT: {
            "cycle_rule": "练 3 休 1",
            "training_parts": ["推", "腿", "拉"],  # 推日、腿日、拉日
            "actions_per_session": 4,
            "sets": 4,
            "reps": 12,
            "rest_seconds": 60
        },
        SchemeTypeEnum.FOUR_SPLIT: {
            "cycle_rule": "练 2 休 1, 练 2 休 2",
            "training_parts": ["胸三头", "背二头", "肩", "腿"],
            "actions_per_session": 4,
            "sets": 4,
            "reps": 12,
            "rest_seconds": 60
        }
    }
    
    # ==================== 减脂计划配置 ====================
    FAT_LOSS_CONFIG = {
        "cycle_rule": "练 3 休 1",
        "warmup_actions": 3,
        "strength_actions": 4,
        "cardio_duration_minutes": 30,
        "cooldown_actions": 3,
        "sets": 4,
        "reps": 12,
        "rest_seconds": 60
    }
    
    def __init__(self, db: Session, user: User, inventory_id: str):
        """
        初始化计划生成器
        
        参数：
            db: 数据库会话
            user: 当前用户对象
            inventory_id: 目标器材清单 ID
        """
        self.db = db
        self.user = user
        self.inventory_id = inventory_id
        self.user_equipment_ids = self._get_user_equipment_ids()
    
    def generate_plan(
        self,
        plan_type: PlanTypeEnum,
        scheme_type: Optional[SchemeTypeEnum] = None,
        training_part: Optional[str] = None,
        plan_name: Optional[str] = None
    ) -> TrainingPlan:
        """
        生成个性化训练计划（V2.1 核心方法）
        
        参数：
            plan_type: 计划类型（减脂/增肌）
            scheme_type: 分化方案（仅增肌计划需要）
            training_part: 训练部位
            plan_name: 计划名称
        
        返回：
            生成的训练计划对象
        """
        # ========== 步骤 1: 验证前置条件 ==========
        self._validate_user_profile()
        self._validate_inventory()
        
        # ========== 步骤 2: 验证计划类型与方案 ==========
        if plan_type == PlanTypeEnum.MUSCLE_GAIN and not scheme_type:
            raise ValueError("增肌计划必须指定分化方案")
        
        if plan_type == PlanTypeEnum.FAT_LOSS and scheme_type:
            raise ValueError("减脂计划不需要分化方案")
        
        # ========== 步骤 3: 创建计划基础信息 ==========
        target_plan_name = plan_name or self._generate_plan_name(plan_type, scheme_type, training_part)
        cycle_rule = self._get_cycle_rule(plan_type, scheme_type)
        
        plan = TrainingPlan(
            plan_id=str(uuid.uuid4()),
            user_id=self.user.user_id,
            inventory_id=self.inventory_id,
            plan_name=target_plan_name,
            plan_type=plan_type,
            scheme_type=scheme_type,
            cycle_rule=cycle_rule,
            fitness_goal=plan_type,
            training_part=training_part,
            status="active"
        )
        
        # ========== 步骤 4: 生成训练日程（7 天） ==========
        schedules = self._generate_weekly_schedule(plan, plan_type, scheme_type)
        plan.schedules = schedules
        
        # ========== 步骤 5: 根据日程生成各次训练的计划 ==========
        # 注意：V2.1 版中，每次训练生成独立的 PlanSession
        # 这里简化处理，生成一个包含三阶段的计划模板
        
        if plan_type == PlanTypeEnum.FAT_LOSS:
            sessions = self._generate_fat_loss_plan()
        else:
            sessions = self._generate_muscle_gain_plan(scheme_type, training_part)
        
        plan.sessions = sessions
        
        # ========== 步骤 6: 保存计划 ==========
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        logger.info(f"计划生成成功：plan_id={plan.plan_id}, plan_type={plan_type}, "
                   f"scheme_type={scheme_type}, cycle_rule={cycle_rule}")
        
        return plan
    
    def _get_user_equipment_ids(self) -> set:
        """获取用户器材清单中的器材 ID 集合"""
        rels = self.db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == self.inventory_id
        ).all()
        return {rel.equipment_id for rel in rels}
    
    def _validate_user_profile(self):
        """验证用户资料完整性"""
        required_fields = [
            self.user.age,
            self.user.experience_level,
            self.user.fitness_goal
        ]
        if not all(required_fields):
            raise ValueError("请先完善身体数据后再生成训练计划")
    
    def _validate_inventory(self):
        """验证器材清单有效性"""
        inventory = self.db.query(EquipmentInventory).filter(
            EquipmentInventory.inventory_id == self.inventory_id,
            EquipmentInventory.user_id == self.user.user_id
        ).first()
        
        if not inventory:
            raise ValueError("器材清单不存在或无权访问")
        
        if not self.user_equipment_ids:
            raise ValueError("器材清单为空，请先添加器材")
    
    def _generate_plan_name(self, plan_type: PlanTypeEnum, scheme_type: Optional[SchemeTypeEnum], training_part: Optional[str]) -> str:
        """自动生成计划名称"""
        date_str = datetime.now().strftime("%m%d")
        
        if plan_type == PlanTypeEnum.FAT_LOSS:
            return f"减脂训练计划-{date_str}"
        else:
            scheme_name_map = {
                SchemeTypeEnum.ONE_SPLIT: "一分化",
                SchemeTypeEnum.TWO_SPLIT: "二分化",
                SchemeTypeEnum.THREE_SPLIT: "三分化",
                SchemeTypeEnum.FOUR_SPLIT: "四分化"
            }
            scheme_name = scheme_name_map.get(scheme_type, "")
            return f"{scheme_name}增肌计划-{date_str}"
    
    def _get_cycle_rule(self, plan_type: PlanTypeEnum, scheme_type: Optional[SchemeTypeEnum]) -> str:
        """获取循环规则"""
        if plan_type == PlanTypeEnum.FAT_LOSS:
            return self.FAT_LOSS_CONFIG["cycle_rule"]
        else:
            config = self.SCHEME_CONFIG.get(scheme_type)
            return config["cycle_rule"] if config else "练 3 休 1"
    
    def _generate_weekly_schedule(
        self,
        plan: TrainingPlan,
        plan_type: PlanTypeEnum,
        scheme_type: Optional[SchemeTypeEnum]
    ) -> List[TrainingSchedule]:
        """生成 7 天训练日程"""
        schedules = []
        today = datetime.now().date()
        
        if plan_type == PlanTypeEnum.FAT_LOSS:
            # 减脂：练 3 休 1
            for i in range(7):
                schedule_date = today + timedelta(days=i)
                is_rest_day = (i % 4) == 3  # 第 4 天休息
                
                schedule = TrainingSchedule(
                    schedule_id=str(uuid.uuid4()),
                    plan_id=plan.plan_id,
                    scheduled_date=schedule_date,
                    status=ScheduleStatusEnum.REST if is_rest_day else ScheduleStatusEnum.PLANNED,
                    session_id=None if is_rest_day else None  # 后续关联具体阶段
                )
                schedules.append(schedule)
        
        else:
            # 增肌：根据分化方案
            config = self.SCHEME_CONFIG.get(scheme_type)
            if not config:
                return schedules
            
            training_parts = config["training_parts"]
            cycle_rule = config["cycle_rule"]
            
            for i in range(7):
                schedule_date = today + timedelta(days=i)
                
                # 根据方案确定当天训练内容
                if scheme_type == SchemeTypeEnum.ONE_SPLIT:
                    is_rest_day = (i % 2) == 1
                    part = training_parts[0] if not is_rest_day else None
                elif scheme_type == SchemeTypeEnum.TWO_SPLIT:
                    cycle_pos = i % 3
                    is_rest_day = cycle_pos == 2
                    part = training_parts[cycle_pos] if not is_rest_day else None
                elif scheme_type == SchemeTypeEnum.THREE_SPLIT:
                    cycle_pos = i % 4
                    is_rest_day = cycle_pos == 3
                    part = training_parts[cycle_pos] if not is_rest_day else None
                else:  # FOUR_SPLIT
                    cycle_pos = i % 7
                    rest_days = [2, 5, 6]  # 第 3、6、7 天休息
                    is_rest_day = cycle_pos in rest_days
                    part = training_parts[cycle_pos] if not is_rest_day else None
                
                schedule = TrainingSchedule(
                    schedule_id=str(uuid.uuid4()),
                    plan_id=plan.plan_id,
                    scheduled_date=schedule_date,
                    status=ScheduleStatusEnum.REST if is_rest_day else ScheduleStatusEnum.PLANNED,
                    session_id=None
                )
                schedules.append(schedule)
        
        return schedules
    
    def _generate_fat_loss_plan(self) -> List[PlanSession]:
        """生成减脂计划（热身 + 无氧 + 有氧 + 拉伸）"""
        sessions = []
        config = self.FAT_LOSS_CONFIG
        
        # ========== 阶段 1: 热身激活 ==========
        warmup_actions = self._filter_actions_by_category_and_muscles(
            category="WARMUP",
            target_muscles=["全身肌群", "心肺功能"],
            count=config["warmup_actions"]
        )
        
        warmup_items = [
            self._create_action_item(action, "WARMUP")
            for action in warmup_actions
        ]
        
        warmup_session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.WARMUP,
            sequence_order=1,
            estimated_duration_minutes=sum(item.total_duration_seconds for item in warmup_items) // 60,
            target_muscles=json.dumps(["全身肌群", "心肺功能"], ensure_ascii=False),
            description="全身激活热身",
            action_items=warmup_items
        )
        sessions.append(warmup_session)
        
        # ========== 阶段 2: 正式训练（无氧 + 有氧） ==========
        # 无氧部分：4 个力量动作
        strength_actions = self._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH",
            target_muscles=["全身肌群"],
            count=config["strength_actions"]
        )
        
        strength_items = [
            self._create_action_item(
                action,
                "MAIN_STRENGTH",
                sets=config["sets"],
                reps=config["reps"],
                rest_seconds=config["rest_seconds"]
            )
            for action in strength_actions
        ]
        
        # 有氧部分：30 分钟跑步机爬坡（或其他有氧）
        cardio_action = self._get_cardio_action()
        cardio_item = self._create_action_item(
            cardio_action,
            "MAIN_CARDIO",
            duration_minutes=config["cardio_duration_minutes"]
        )
        
        main_items = strength_items + [cardio_item]
        
        main_session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.MAIN,
            sequence_order=2,
            estimated_duration_minutes=sum(item.total_duration_seconds for item in main_items) // 60,
            target_muscles=json.dumps(["全身肌群"], ensure_ascii=False),
            description="无氧 + 有氧减脂训练",
            action_items=main_items
        )
        sessions.append(main_session)
        
        # ========== 阶段 3: 拉伸放松 ==========
        cooldown_actions = self._filter_actions_by_category_and_muscles(
            category="COOLDOWN",
            target_muscles=["全身肌群"],
            count=config["cooldown_actions"]
        )
        
        cooldown_items = [
            self._create_action_item(action, "COOLDOWN")
            for action in cooldown_actions
        ]
        
        cooldown_session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.COOLDOWN,
            sequence_order=3,
            estimated_duration_minutes=sum(item.total_duration_seconds for item in cooldown_items) // 60,
            target_muscles=json.dumps(["全身肌群"], ensure_ascii=False),
            description="全身拉伸放松",
            action_items=cooldown_items
        )
        sessions.append(cooldown_session)
        
        return sessions
    
    def _generate_muscle_gain_plan(
        self,
        scheme_type: SchemeTypeEnum,
        training_part: Optional[str]
    ) -> List[PlanSession]:
        """生成增肌计划（根据分化方案）"""
        sessions = []
        config = self.SCHEME_CONFIG.get(scheme_type)
        
        if not config:
            return sessions
        
        # 获取当前训练部位的肌群
        if training_part:
            target_muscles = self.TRAINING_PART_MUSCLES.get(training_part, ["全身肌群"])
        else:
            # 根据分化方案确定肌群
            parts = config["training_parts"]
            target_muscles = []
            for part in parts:
                target_muscles.extend(self.TRAINING_PART_MUSCLES.get(part, []))
            target_muscles = list(set(target_muscles))
        
        # ========== 阶段 1: 热身激活 ==========
        warmup_actions = self._filter_actions_by_category_and_muscles(
            category="WARMUP",
            target_muscles=target_muscles,
            count=3
        )
        
        warmup_items = [
            self._create_action_item(action, "WARMUP")
            for action in warmup_actions
        ]
        
        warmup_session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.WARMUP,
            sequence_order=1,
            estimated_duration_minutes=sum(item.total_duration_seconds for item in warmup_items) // 60,
            target_muscles=json.dumps(target_muscles, ensure_ascii=False),
            description=f"{training_part or '增肌'}热身激活",
            action_items=warmup_items
        )
        sessions.append(warmup_session)
        
        # ========== 阶段 2: 正式训练（力量） ==========
        strength_actions = self._filter_actions_by_category_and_muscles(
            category="MAIN_STRENGTH",
            target_muscles=target_muscles,
            count=config["actions_per_session"]
        )
        
        strength_items = [
            self._create_action_item(
                action,
                "MAIN_STRENGTH",
                sets=config["sets"],
                reps=config["reps"],
                rest_seconds=config["rest_seconds"]
            )
            for action in strength_actions
        ]
        
        main_session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.MAIN,
            sequence_order=2,
            estimated_duration_minutes=sum(item.total_duration_seconds for item in strength_items) // 60,
            target_muscles=json.dumps(target_muscles, ensure_ascii=False),
            description=f"{training_part or '增肌'}力量训练",
            action_items=strength_items
        )
        sessions.append(main_session)
        
        # ========== 阶段 3: 拉伸放松 ==========
        cooldown_actions = self._filter_actions_by_category_and_muscles(
            category="COOLDOWN",
            target_muscles=target_muscles,
            count=3
        )
        
        cooldown_items = [
            self._create_action_item(action, "COOLDOWN")
            for action in cooldown_actions
        ]
        
        cooldown_session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.COOLDOWN,
            sequence_order=3,
            estimated_duration_minutes=sum(item.total_duration_seconds for item in cooldown_items) // 60,
            target_muscles=json.dumps(target_muscles, ensure_ascii=False),
            description=f"{training_part or '增肌'}拉伸放松",
            action_items=cooldown_items
        )
        sessions.append(cooldown_session)
        
        return sessions
    
    def _filter_actions_by_category_and_muscles(
        self,
        category: str,
        target_muscles: List[str],
        count: int = 5
    ) -> List[TrainingAction]:
        """根据类别和肌群筛选动作"""
        actions = self.db.query(TrainingAction).filter(
            TrainingAction.action_category == category
        ).all()
        
        # 按器材可用性筛选
        filtered = []
        for action in actions:
            if action.equipment_id == "none" or action.equipment_id in self.user_equipment_ids:
                # 按肌群匹配度筛选
                action_muscles = action.get_target_muscles_list()
                if self._muscles_match(action_muscles, target_muscles):
                    filtered.append(action)
        
        # 按难度适配
        if self.user.experience_level == "BEGINNER":
            filtered = [a for a in filtered if a.difficulty_level != "ADVANCED"]
        
        return filtered[:count]
    
    def _muscles_match(self, action_muscles: List[str], target_muscles: List[str]) -> bool:
        """检查动作肌群与目标肌群是否匹配"""
        if not action_muscles or not target_muscles:
            return True
        
        for muscle in target_muscles:
            for action_muscle in action_muscles:
                if muscle in action_muscle or action_muscle in muscle:
                    return True
        
        if "全身肌群" in action_muscles or "心肺功能" in action_muscles:
            return True
        
        return False
    
    def _get_cardio_action(self) -> TrainingAction:
        """获取有氧动作（优先跑步机）"""
        # 检查用户是否有跑步机
        has_treadmill = "eq_18" in self.user_equipment_ids
        
        if has_treadmill:
            action = self.db.query(TrainingAction).filter(
                TrainingAction.action_id == "act_023"  # 跑步机爬坡
            ).first()
            if action:
                return action
        
        # 否则返回其他有氧动作
        action = self.db.query(TrainingAction).filter(
            TrainingAction.action_category == "MAIN_CARDIO",
            TrainingAction.equipment_id == "none"
        ).first()
        
        return action or self.db.query(TrainingAction).filter(
            TrainingAction.action_category == "MAIN_CARDIO"
        ).first()
    
    def _create_action_item(
        self,
        action: TrainingAction,
        session_type: str,
        sets: Optional[int] = None,
        reps: Optional[int] = None,
        rest_seconds: Optional[int] = None,
        duration_seconds: Optional[int] = None,
        duration_minutes: Optional[int] = None
    ) -> SessionActionItem:
        """创建动作项"""
        # 计算总时长
        if session_type in ["WARMUP", "COOLDOWN"]:
            total_duration = (sets or 2) * (duration_seconds or action.estimated_seconds or 30)
        elif session_type == "MAIN_STRENGTH":
            total_duration = sets * ((action.estimated_seconds or 3) * reps + rest_seconds) - rest_seconds
        else:  # MAIN_CARDIO
            total_duration = (duration_minutes or 30) * 60
        
        return SessionActionItem(
            item_id=str(uuid.uuid4()),
            action_id=action.action_id,
            sets=sets,
            reps_per_set=reps,
            rest_seconds_default=rest_seconds or 60,  # ✅ V2.1 默认 60 秒
            duration_seconds=duration_seconds,
            duration_minutes=duration_minutes,
            lateral_coeff=1,
            total_duration_seconds=total_duration,
            execution_notes=self._generate_execution_notes(action)
        )
    
    def _generate_execution_notes(self, action: TrainingAction) -> str:
        """生成执行备注"""
        notes = []
        
        if self.user.experience_level == "BEGINNER":
            notes.append("初学者建议从轻重量开始，注重动作标准性")
        
        if action.difficulty_level == "ADVANCED":
            notes.append("该动作难度较高，建议在专业指导下进行")
        
        if action.equipment_id and action.equipment_id != "none":
            equipment = self.db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                notes.append(f"使用器材：{equipment.name}")
        
        if action.safety_tips:
            notes.append(f"注意：{action.safety_tips[:30]}...")
        
        return "；".join(notes) if notes else "按标准动作执行，注意呼吸节奏"