"""
训练计划生成服务
根据用户身体数据、健身目标、训练部位和器材清单生成个性化三阶段训练计划
对应《需求规格说明书》3.2 节生成训练计划用例
《任务书》技术指标：自动生成包含热身、正式训练、拉伸放松三阶段的科学化个性化训练计划

修订说明：
1. 支持训练部位选择（增肌/塑形目标）
2. 确保三个阶段目标肌群一致
3. 完善时长计算与校验逻辑
4. 使用 target_muscles_list 属性转换器处理肌群列表
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
from app.models.plan import TrainingPlan, PlanSession, SessionActionItem, SessionTypeEnum

logger = logging.getLogger(__name__)


class PlanGenerator:
    """
    训练计划生成引擎（修订版）
    实现器材 - 动作匹配、用户适配过滤、三阶段构建、参数自动配置、肌群一致性校验
    """
    
    # ==================== 训练部位与肌群映射（规则 4） ====================
    TRAINING_PART_MUSCLES = {
        "胸部": ["胸大肌", "三角肌前束", "肱三头肌"],
        "背部": ["背阔肌", "斜方肌", "肱二头肌"],
        "肩部": ["三角肌", "斜方肌", "肩袖肌群"],
        "手臂": ["肱二头肌", "肱三头肌", "前臂肌群"],
        "腿部": ["股四头肌", "腘绳肌", "臀大肌", "小腿三头肌"],
        "臀部": ["臀大肌", "臀中肌", "臀小肌", "腘绳肌"],
        "核心": ["腹直肌", "腹外斜肌", "核心肌群"],
        "全身": ["全身肌群", "心肺功能", "核心肌群"]
    }
    
    # ==================== 阶段时长配置（《需求规格说明书》表 2-5） ====================
    STAGE_CONFIG = {
        "warmup": {"min_minutes": 5, "max_minutes": 10, "action_count": (3, 5)},
        "main_strength": {"min_minutes": 30, "max_minutes": 45, "action_count": (5, 8)},
        "main_cardio": {"min_minutes": 30, "max_minutes": 45, "action_count": (4, 7)},
        "cooldown": {"min_minutes": 5, "max_minutes": 10, "action_count": (3, 5)}
    }
    
    # 总时长要求
    TOTAL_DURATION_MIN = 40  # 分钟
    TOTAL_DURATION_MAX = 65  # 分钟
    
    # ==================== 难度适配权重（《需求规格说明书》2.2.4） ====================
    DIFFICULTY_WEIGHTS = {
        ("初学者", "初级"): 1.2,
        ("初学者", "中级"): 0.9,
        ("初学者", "高级"): 0.0,  # 直接过滤
        ("中级", "初级"): 1.1,
        ("中级", "中级"): 1.2,
        ("中级", "高级"): 0.9,
        ("高级", "初级"): 1.0,
        ("高级", "中级"): 1.1,
        ("高级", "高级"): 1.2,
    }
    
    # ==================== 健身目标权重（《需求规格说明书》表 2-1） ====================
    GOAL_WEIGHTS = {
        "增肌": {
            "main_strength": 1.5,
            "main_cardio": 0.8,
            "warmup": 1.0,
            "cooldown": 1.0
        },
        "减脂": {
            "main_strength": 0.8,
            "main_cardio": 1.5,
            "warmup": 1.0,
            "cooldown": 1.0
        },
        "塑形": {
            "main_strength": 1.2,
            "main_cardio": 1.2,
            "warmup": 1.0,
            "cooldown": 1.0
        },
        "增强体能": {
            "main_strength": 1.0,
            "main_cardio": 1.0,
            "warmup": 1.2,
            "cooldown": 1.2
        }
    }
    
    def __init__(self, db: Session, user: User, inventory_id: str):
        """
        初始化计划生成器
        
        参数：
            db: 数据库会话
            user: 当前用户对象（包含年龄、性别、健身目标、经验水平等）
            inventory_id: 目标器材清单 ID
        """
        self.db = db
        self.user = user
        self.inventory_id = inventory_id
        self.user_equipment_ids = self._get_user_equipment_ids()
    
    def generate_plan(
        self, 
        fitness_goal: Optional[str] = None,
        plan_name: Optional[str] = None,
        training_part: Optional[str] = None
    ) -> TrainingPlan:
        """
        生成个性化训练计划（核心方法 - 修订版）
        
        对应《需求规格说明书》3.2 节生成训练计划用例基本事件流：
        (1) 系统分析用户身体数据与健身目标
        (2) 系统确定训练部位（增肌/塑形需选择，减脂/体能=全身）
        (3) 系统结合目标器材清单筛选可行动作
        (4) 系统按照科学训练原则构建三阶段计划（确保肌群一致）
        (5) 系统为每个动作项自动计算 totalDurationSeconds
        (6) 系统展示完整计划，用户可调整参数
        (7) 用户确认后保存计划至个人档案
        
        参数：
            fitness_goal: 健身目标（可选，默认使用用户设置）
            plan_name: 计划名称（可选，默认根据健身目标自动生成）
            training_part: 训练部位（增肌/塑形必填，减脂/体能默认全身）
        
        返回：
            生成的训练计划对象
        """
        # ========== 步骤 1: 验证前置条件（规则 1） ==========
        self._validate_user_profile()
        self._validate_inventory()
        
        # ========== 步骤 2: 确定健身目标和训练部位（规则 3） ==========
        target_goal = fitness_goal or self.user.fitness_goal
        target_part = self._determine_training_part(target_goal, training_part)
        
        # ========== 步骤 3: 获取训练部位对应的目标肌群列表（规则 4） ==========
        target_muscles = self.TRAINING_PART_MUSCLES.get(target_part, ["全身肌群"])
        logger.info(f"训练部位：{target_part}, 目标肌群：{target_muscles}")
        
        # ========== 步骤 4: 确定正式阶段类别（规则 2） ==========
        main_category = self._get_main_category(target_goal)
        
        # ========== 步骤 5: 创建计划基础信息 ==========
        target_plan_name = plan_name or self._generate_plan_name(target_goal, target_part)
        plan = self._create_plan_base(target_plan_name, target_goal, target_part)
        
        # ========== 步骤 6: 构建三阶段（确保肌群一致 - 规则 4） ==========
        sessions = []
        
        # 阶段 1: 热身激活（sequence_order=1）
        warmup_session = self._build_warmup_session(
            target_muscles=target_muscles,
            sequence_order=1
        )
        sessions.append(warmup_session)
        
        # 阶段 2: 正式训练（sequence_order=2）
        main_session = self._build_main_session(
            category=main_category,
            target_muscles=target_muscles,
            sequence_order=2
        )
        sessions.append(main_session)
        
        # 阶段 3: 拉伸放松（sequence_order=3）
        cooldown_session = self._build_cooldown_session(
            target_muscles=target_muscles,
            sequence_order=3
        )
        sessions.append(cooldown_session)
        
        # ========== 步骤 7: 校验计划总时长（规则 5） ==========
        total_duration = sum(s.estimated_duration_minutes for s in sessions)
        logger.info(f"计划总时长：{total_duration}分钟（要求：{self.TOTAL_DURATION_MIN}-{self.TOTAL_DURATION_MAX}分钟）")
        
        if not (self.TOTAL_DURATION_MIN <= total_duration <= self.TOTAL_DURATION_MAX):
            sessions = self._adjust_sessions_for_duration(sessions, total_duration)
            total_duration = sum(s.estimated_duration_minutes for s in sessions)
        
        # ========== 步骤 8: 关联阶段到计划 ==========
        plan.sessions = sessions
        plan.total_duration_minutes = total_duration
        
        # ========== 步骤 9: 保存计划 ==========
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        logger.info(f"计划生成成功：plan_id={plan.plan_id}, plan_name={plan.plan_name}, "
                   f"fitness_goal={plan.fitness_goal}, training_part={plan.training_part}, "
                   f"total_duration={plan.total_duration_minutes}min")
        
        return plan
    
    def _determine_training_part(self, fitness_goal: str, training_part: Optional[str]) -> str:
        """
        确定训练部位（规则 3）
        
        参数：
            fitness_goal: 健身目标
            training_part: 用户选择的训练部位
        
        返回：
            确定的训练部位
        """
        # 减脂/增强体能：默认为全身
        if fitness_goal in ["减脂", "增强体能"]:
            return training_part or "全身"
        
        # 增肌/塑形：必须指定具体部位
        if fitness_goal in ["增肌", "塑形"]:
            if not training_part or training_part == "全身":
                raise ValueError("增肌/塑形目标需指定具体训练部位（胸部/背部/肩部/手臂/腿部/臀部/核心）")
            return training_part
        
        return training_part or "全身"
    
    def _get_user_equipment_ids(self) -> set:
        """获取用户器材清单中的器材 ID 集合（规则 6）"""
        rels = self.db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == self.inventory_id
        ).all()
        return {rel.equipment_id for rel in rels}
    
    def _validate_user_profile(self):
        """
        验证用户资料完整性（《需求规格说明书》2.2.1 业务规则 - 规则 1）
        用户首次使用系统时必须完成基本信息录入，否则无法生成个性化训练计划
        """
        required_fields = [
            self.user.age,
            self.user.experience_level,
            self.user.fitness_goal
        ]
        if not all(required_fields):
            raise ValueError("请先完善身体数据后再生成训练计划")
    
    def _validate_inventory(self):
        """验证器材清单有效性（规则 1）"""
        inventory = self.db.query(EquipmentInventory).filter(
            EquipmentInventory.inventory_id == self.inventory_id,
            EquipmentInventory.user_id == self.user.user_id
        ).first()
        
        if not inventory:
            raise ValueError("器材清单不存在或无权访问")
        
        if not self.user_equipment_ids:
            raise ValueError("器材清单为空，请先添加器材")
    
    def _generate_plan_name(self, fitness_goal: str, training_part: str) -> str:
        """
        根据健身目标和训练部位自动生成计划名称
        
        参数：
            fitness_goal: 健身目标
            training_part: 训练部位
        
        返回：
            自动生成的计划名称
        """
        goal_to_name = {
            "增肌": f"{training_part}增肌训练计划",
            "减脂": "全身减脂训练计划",
            "塑形": f"{training_part}塑形训练计划",
            "增强体能": "全身体能提升计划"
        }
        
        base_name = goal_to_name.get(fitness_goal, "个性化训练计划")
        date_str = datetime.now().strftime("%m%d")
        return f"{base_name}-{date_str}"
    
    def _create_plan_base(self, plan_name: str, fitness_goal: str, training_part: str) -> TrainingPlan:
        """
        创建计划基础信息（《需求规格说明书》表 2-5）
        
        参数：
            plan_name: 计划名称
            fitness_goal: 健身目标
            training_part: 训练部位
        """
        return TrainingPlan(
            plan_id=str(uuid.uuid4()),
            user_id=self.user.user_id,
            inventory_id=self.inventory_id,
            plan_name=plan_name,
            fitness_goal=fitness_goal,
            training_part=training_part,  # ✅ 新增：存储训练部位
            create_time=datetime.now(),
            valid_days=30,
            total_duration_minutes=0
        )
    
    def _get_main_category(self, fitness_goal: str) -> str:
        """
        根据健身目标获取正式训练阶段类别（《需求规格说明书》表 2-6 - 规则 2）
        增肌/塑形 → main_strength（力量训练）
        减脂/增强体能 → main_cardio（有氧训练）
        """
        if fitness_goal in ["增肌", "塑形"]:
            return "main_strength"
        else:
            return "main_cardio"
    
    def _build_warmup_session(self, target_muscles: List[str], sequence_order: int) -> PlanSession:
        """
        构建热身阶段（《需求规格说明书》表 2-6 - 规则 2、规则 4）
        业务规则：
        (1) 热身阶段仅包含 warmup 类别动作
        (2) 动作目标肌群必须与训练部位一致
        """
        config = self.STAGE_CONFIG["warmup"]
        
        # 筛选热身动作（按类别 + 器材 + 肌群）
        actions = self._filter_actions_by_category_equipment_muscles(
            category="warmup",
            target_muscles=target_muscles
        )
        
        # 按难度适配用户经验（规则 7）
        actions = self._filter_by_difficulty(actions)
        
        # 选择指定数量的动作
        selected_actions = self._select_actions(actions, config["action_count"])
        
        # 构建动作项
        action_items = [
            self._create_action_item(action, "warmup")
            for action in selected_actions
        ]
        
        # 计算阶段时长
        duration_minutes = sum(item.total_duration_seconds for item in action_items) // 60
        duration_minutes = max(config["min_minutes"], min(duration_minutes, config["max_minutes"]))
        
        # ✅ 使用属性转换器设置 target_muscles_list，自动序列化为 JSON 字符串
        session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.WARMUP,
            sequence_order=sequence_order,
            estimated_duration_minutes=duration_minutes,
            target_muscles_list=target_muscles,  # ✅ 使用属性转换器
            action_items=action_items,
            description=f"针对{', '.join(target_muscles[:2])}的动态拉伸激活，预防运动损伤"
        )
        
        return session
    
    def _build_main_session(self, category: str, target_muscles: List[str], sequence_order: int) -> PlanSession:
        """
        构建正式训练阶段（《需求规格说明书》表 2-6 - 规则 2、规则 4）
        业务规则：
        (1) 正式训练阶段根据用户目标选择 main_cardio（减脂）或 main_strength（增肌）动作
        (2) 动作目标肌群必须与训练部位一致
        """
        config = self.STAGE_CONFIG[category]
        
        # 筛选正式训练动作（按类别 + 器材 + 肌群）
        actions = self._filter_actions_by_category_equipment_muscles(
            category=category,
            target_muscles=target_muscles
        )
        
        # 按难度适配 + 目标肌群匹配度排序
        actions = self._filter_by_difficulty(actions)
        actions = self._sort_by_muscle_match(actions, target_muscles)
        
        # 选择指定数量的动作
        selected_actions = self._select_actions(actions, config["action_count"])
        
        # 构建动作项（力量训练需配置组数/次数/休息）
        action_items = [
            self._create_action_item(action, category)
            for action in selected_actions
        ]
        
        # 计算阶段时长
        duration_minutes = sum(item.total_duration_seconds for item in action_items) // 60
        duration_minutes = max(config["min_minutes"], min(duration_minutes, config["max_minutes"]))
        
        description = "力量训练" if category == "main_strength" else "有氧训练"
        
        # ✅ 使用属性转换器设置 target_muscles_list，自动序列化为 JSON 字符串
        session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.MAIN,
            sequence_order=sequence_order,
            estimated_duration_minutes=duration_minutes,
            target_muscles_list=target_muscles,  # ✅ 使用属性转换器
            action_items=action_items,
            description=f"针对{', '.join(target_muscles[:2])}的{description}"
        )
        
        return session
    
    def _build_cooldown_session(self, target_muscles: List[str], sequence_order: int) -> PlanSession:
        """
        构建拉伸阶段（《需求规格说明书》表 2-6 - 规则 2、规则 4）
        业务规则：
        (1) 拉伸阶段仅包含 cooldown 类别动作
        (2) 动作目标肌群必须与训练部位一致
        """
        config = self.STAGE_CONFIG["cooldown"]
        
        # 筛选拉伸动作（按类别 + 器材 + 肌群）
        actions = self._filter_actions_by_category_equipment_muscles(
            category="cooldown",
            target_muscles=target_muscles
        )
        
        # 按难度适配
        actions = self._filter_by_difficulty(actions)
        
        # 选择指定数量的动作
        selected_actions = self._select_actions(actions, config["action_count"])
        
        # 构建动作项
        action_items = [
            self._create_action_item(action, "cooldown")
            for action in selected_actions
        ]
        
        # 计算阶段时长
        duration_minutes = sum(item.total_duration_seconds for item in action_items) // 60
        duration_minutes = max(config["min_minutes"], min(duration_minutes, config["max_minutes"]))
        
        # ✅ 使用属性转换器设置 target_muscles_list，自动序列化为 JSON 字符串
        session = PlanSession(
            session_id=str(uuid.uuid4()),
            session_type=SessionTypeEnum.COOLDOWN,
            sequence_order=sequence_order,
            estimated_duration_minutes=duration_minutes,
            target_muscles_list=target_muscles,  # ✅ 使用属性转换器
            action_items=action_items,
            description=f"针对{', '.join(target_muscles[:2])}的静态拉伸放松，促进恢复"
        )
        
        return session
    
    def _filter_actions_by_category_equipment_muscles(
        self, 
        category: str, 
        target_muscles: List[str]
    ) -> List[TrainingAction]:
        """
        根据类别、器材可用性和目标肌群筛选动作（规则 4、规则 6）
        
        参数：
            category: 动作类别（warmup/main_strength/main_cardio/cooldown）
            target_muscles: 目标肌群列表
        
        返回：
            筛选后的动作列表
        """
        # 1. 按类别筛选
        actions = self.db.query(TrainingAction).filter(
            TrainingAction.action_category == category
        ).all()
        
        # 2. 按器材可用性筛选（规则 6）
        filtered = []
        for action in actions:
            if action.equipment_id == "none" or action.equipment_id in self.user_equipment_ids:
                filtered.append(action)
        
        # 3. 按目标肌群筛选（规则 4 - 关键修改）
        muscle_filtered = []
        for action in filtered:
            action_muscles = action.get_target_muscles_list()
            # 检查动作的目标肌群是否与训练部位的目标肌群有交集
            if self._muscles_match(action_muscles, target_muscles):
                muscle_filtered.append(action)
        
        logger.debug(f"类别={category}, 筛选前={len(actions)}, 器材筛选后={len(filtered)}, 肌群筛选后={len(muscle_filtered)}")
        
        return muscle_filtered
    
    def _muscles_match(self, action_muscles: List[str], target_muscles: List[str]) -> bool:
        """
        检查动作肌群与目标肌群是否匹配（规则 4）
        
        参数：
            action_muscles: 动作的目标肌群
            target_muscles: 训练部位的目标肌群
        
        返回：
            是否匹配
        """
        if not action_muscles or not target_muscles:
            return True  # 无肌群信息时默认匹配
        
        # 检查是否有交集
        for muscle in target_muscles:
            for action_muscle in action_muscles:
                if muscle in action_muscle or action_muscle in muscle:
                    return True
        
        # 特殊处理：全身肌群匹配所有
        if "全身肌群" in action_muscles or "心肺功能" in action_muscles:
            return True
        
        return False
    
    def _filter_by_difficulty(self, actions: List[TrainingAction]) -> List[TrainingAction]:
        """
        根据用户经验水平过滤动作难度（《需求规格说明书》2.2.4 业务规则 - 规则 7）
        动作难度需与用户经验水平匹配（初学者不推荐高级动作）
        """
        if self.user.experience_level == "初学者":
            return [a for a in actions if a.difficulty_level != "高级"]
        elif self.user.experience_level == "中级":
            return actions  # 中级用户可包含高级动作，在排序时降权
        return actions
    
    def _sort_by_muscle_match(self, actions: List[TrainingAction], target_muscles: List[str]) -> List[TrainingAction]:
        """
        按目标肌群匹配度排序动作（规则 4）
        
        参数：
            actions: 动作列表
            target_muscles: 目标肌群列表
        
        返回：
            排序后的动作列表
        """
        def muscle_match_score(action):
            score = 0
            action_muscles = action.get_target_muscles_list()
            for target_muscle in target_muscles:
                for action_muscle in action_muscles:
                    if target_muscle in action_muscle or action_muscle in target_muscle:
                        score += 10
            return score
        
        return sorted(actions, key=muscle_match_score, reverse=True)
    
    def _select_actions(self, actions: List[TrainingAction], count_range: tuple) -> List[TrainingAction]:
        """从候选动作中选择指定数量的动作"""
        min_count, max_count = count_range
        count = min(max_count, len(actions))
        count = max(min_count, count)  # 确保至少选择最小数量
        return actions[:count]
    
    def _create_action_item(self, action: TrainingAction, category: str) -> SessionActionItem:
        """
        创建阶段动作项并自动配置参数（《需求规格说明书》表 2-7）
        业务规则：
        (1) 参数互斥性：同一动作项不可同时配置 repsPerSet 与 durationSeconds
        (2) 总时长自动计算：totalDurationSeconds 由系统根据参数组合自动计算
        """
        # 根据动作类别和用户经验配置参数
        params = self._configure_action_params(action, category)
        
        # 计算总时长（《需求规格说明书》表 2-7 公式）
        total_duration = self._calculate_total_duration(action, params, category)
        
        # 生成个性化执行备注
        execution_notes = self._generate_execution_notes(action, params)
        
        return SessionActionItem(
            item_id=str(uuid.uuid4()),
            action_id=action.action_id,
            sets=params.get("sets"),
            reps_per_set=params.get("reps"),
            rest_seconds=params.get("rest"),
            duration_seconds=params.get("duration"),
            lateral_coeff=1,
            total_duration_seconds=total_duration,
            execution_notes=execution_notes
        )
    
    def _configure_action_params(self, action: TrainingAction, category: str) -> Dict:
        """
        根据动作类别和用户经验配置执行参数（《需求规格说明书》表 2-7）
        力量训练：配置 sets/reps/rest
        有氧/热身/拉伸：配置 duration
        """
        level = self.user.experience_level
        
        if category == "main_strength":
            # 力量训练参数配置
            if level == "初学者":
                return {"sets": 2, "reps": 10, "rest": 90}
            elif level == "中级":
                return {"sets": 3, "reps": 12, "rest": 60}
            else:  # 高级
                return {"sets": 4, "reps": 15, "rest": 45}
        else:
            # 有氧/热身/拉伸：使用动作预设时长
            return {"duration": action.estimated_seconds or 30}
    
    def _calculate_total_duration(self, action: TrainingAction, params: Dict, category: str) -> int:
        """
        计算动作项总执行时长（秒）
        对应《需求规格说明书》表 2-7 totalDurationSeconds 计算规则：
        • 力量训练：sets × (estimatedSeconds × repsPerSet + restSeconds) - restSeconds
        • 有氧训练：durationSeconds
        • 热身/拉伸：sets × durationSeconds × lateralCoeff
        """
        if category == "main_strength":
            # 力量训练
            sets = params["sets"]
            reps = params["reps"]
            rest = params["rest"]
            estimated = action.estimated_seconds or 3
            return sets * (estimated * reps + rest) - rest
        elif category in ["warmup", "cooldown"]:
            # 热身/拉伸
            sets = params.get("sets", 2)
            duration = params["duration"]
            lateral = 1
            return sets * duration * lateral
        else:  # main_cardio
            # 有氧训练
            return params["duration"]
    
    def _generate_execution_notes(self, action: TrainingAction, params: Dict) -> str:
        """
        生成个性化执行备注（《需求规格说明书》表 2-7 executionNotes）
        根据用户数据生成的个性化提示（如"初学者可减少 1 组"）
        """
        notes = []
        
        # 根据用户经验生成提示
        if self.user.experience_level == "初学者":
            notes.append("初学者建议从轻重量开始，注重动作标准性")
        
        # 根据动作难度生成提示
        if action.difficulty_level == "高级":
            notes.append("该动作难度较高，建议在专业指导下进行")
        
        # 根据器材类型生成提示
        if action.equipment_id != "none":
            equipment = self.db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                notes.append(f"使用器材：{equipment.name}")
        
        # 根据安全提示生成备注
        if action.safety_tips:
            notes.append(f"注意：{action.safety_tips[:30]}...")
        
        return "；".join(notes) if notes else "按标准动作执行，注意呼吸节奏"
    
    def _adjust_sessions_for_duration(self, sessions: List[PlanSession], current_duration: int) -> List[PlanSession]:
        """
        调整阶段动作数量以满足总时长要求（《需求规格说明书》表 2-5 - 规则 5）
        计划总时长建议 40-65 分钟（热身 5-10min+ 正式 30-45min+ 拉伸 5-10min）
        """
        if current_duration < self.TOTAL_DURATION_MIN:
            # 时长过短，增加正式阶段动作
            main_session = next((s for s in sessions if s.session_type == SessionTypeEnum.MAIN), None)
            if main_session and main_session.action_items:
                # 复制最后一个动作
                extra_item = main_session.action_items[-1]
                main_session.action_items.append(extra_item)
                main_session.estimated_duration_minutes += extra_item.total_duration_seconds // 60
        elif current_duration > self.TOTAL_DURATION_MAX:
            # 时长过长，减少正式阶段动作
            main_session = next((s for s in sessions if s.session_type == SessionTypeEnum.MAIN), None)
            if main_session and len(main_session.action_items) > 3:
                removed = main_session.action_items.pop()
                main_session.estimated_duration_minutes -= removed.total_duration_seconds // 60
        
        return sessions