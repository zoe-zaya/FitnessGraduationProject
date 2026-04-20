"""
训练计划业务对象模型
对应需求规格说明书 2.1 版
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum, Date, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from app.utils.db import Base


class PlanTypeEnum(str, enum.Enum):
    """计划类型枚举"""
    FAT_LOSS = "FAT_LOSS"  # 减脂
    MUSCLE_GAIN = "MUSCLE_GAIN"  # 增肌


class SchemeTypeEnum(str, enum.Enum):
    """分化方案枚举（仅增肌计划）"""
    ONE_SPLIT = "ONE_SPLIT"  # 一分化
    TWO_SPLIT = "TWO_SPLIT"  # 二分化
    THREE_SPLIT = "THREE_SPLIT"  # 三分化
    FOUR_SPLIT = "FOUR_SPLIT"  # 四分化


class SessionTypeEnum(str, enum.Enum):
    """阶段类型枚举"""
    WARMUP = "WARMUP"  # 热身
    MAIN = "MAIN"  # 正式训练
    COOLDOWN = "COOLDOWN"  # 拉伸


class ScheduleStatusEnum(str, enum.Enum):
    """日程状态枚举"""
    PLANNED = "PLANNED"  # 计划中
    COMPLETED = "COMPLETED"  # 已完成
    POSTPONED = "POSTPONED"  # 已延后
    REST = "REST"  # 休息日


class TrainingPlan(Base):
    """
    TrainingPlan（训练计划）
    对应需求规格说明书 2.1 版
    业务规则：
    (1) 计划表中不再包含有效期和总时长字段
    (2) 健身目标仅分为减脂和增肌两类
    (3) 计划必须关联有效器材清单
    """
    __tablename__ = "training_plan"
    
    # === 基本属性 ===
    plan_id = Column(String(64), primary_key=True, index=True, comment="计划唯一标识符")
    user_id = Column(String(64), ForeignKey("user.user_id"), nullable=False, index=True, comment="计划归属用户 ID")
    inventory_id = Column(String(64), ForeignKey("equipment_inventory.inventory_id"), nullable=False, index=True, comment="关联器材清单 ID")
    create_time = Column(DateTime, default=datetime.now, comment="计划生成时间")
    
    # === V2.1 新增属性 ===
    plan_type = Column(Enum(PlanTypeEnum), nullable=False, default=PlanTypeEnum.FAT_LOSS, comment="计划类型：减脂/增肌")
    scheme_type = Column(Enum(SchemeTypeEnum), nullable=True, comment="分化方案（仅增肌计划）")
    cycle_rule = Column(String(64), nullable=True, comment="训练循环规则（如练 3 休 1）")
    
    # === 保留属性 ===
    status = Column(String(32), default="active", comment="计划状态：active/expired/archived")
    plan_name = Column(String(128), nullable=True, comment="计划名称")
    fitness_goal = Column(Enum(PlanTypeEnum), nullable=True, comment="健身目标")
    training_part = Column(String(32), nullable=True, comment="训练部位")
    
    # === 业务关系 ===
    user = relationship("User", back_populates="plans")
    inventory = relationship("EquipmentInventory", back_populates="plans")
    sessions = relationship("PlanSession", back_populates="plan", cascade="all, delete-orphan", lazy="select")
    schedules = relationship("TrainingSchedule", back_populates="plan", cascade="all, delete-orphan", lazy="select")
    
    def get_cycle_days(self) -> int:
        """获取循环周期天数"""
        cycle_map = {
            "练 3 休 1": 4,
            "练 2 休 1": 3,
            "练 2 休 1, 练 2 休 2": 7
        }
        return cycle_map.get(self.cycle_rule, 4)


class PlanSession(Base):
    """
    PlanSession（计划阶段）
    对应需求规格说明书 2.1 版
    业务规则：
    (1) 三阶段顺序固定不可调整
    (2) 三个阶段的目标肌群需保持一致性
    """
    __tablename__ = "plan_session"
    
    # === 基本属性 ===
    session_id = Column(String(64), primary_key=True, index=True, comment="阶段唯一标识符")
    plan_id = Column(String(64), ForeignKey("training_plan.plan_id"), nullable=False, index=True, comment="关联计划 ID")
    session_type = Column(Enum(SessionTypeEnum), nullable=False, comment="阶段类型")
    sequence_order = Column(Integer, nullable=False, comment="阶段执行顺序（1=热身，2=正式，3=拉伸）")
    estimated_duration_minutes = Column(Integer, default=0, comment="该阶段预估总时长（分钟）")
    description = Column(Text, nullable=True, comment="阶段说明")
    target_muscles = Column(String(512), nullable=True, comment="该阶段目标肌群列表（JSON 格式）")
    training_part = Column(String(32), nullable=True, comment="训练部位分组标识（如推/腿/拉，用于区分不同训练日）")

    # === 业务关系 ===
    plan = relationship("TrainingPlan", back_populates="sessions")
    action_items = relationship("SessionActionItem", back_populates="session", cascade="all, delete-orphan", lazy="select", order_by="SessionActionItem.sequence_order")

    __table_args__ = (
        CheckConstraint('sequence_order IN (1,2,3)', name='chk_sequence_order'),
    )


class SessionActionItem(Base):
    """
    SessionActionItem（阶段动作项）
    对应需求规格说明书 2.1 版
    业务规则：
    (1) 支持用户记录每组的训练重量
    (2) 休息时长默认 60s，用户可调整（30s 至 5 分钟）
    """
    __tablename__ = "session_action_item"
    
    # === 基本属性 ===
    item_id = Column(String(64), primary_key=True, index=True, comment="动作项唯一标识符")
    session_id = Column(String(64), ForeignKey("plan_session.session_id"), nullable=False, index=True, comment="关联阶段 ID")
    action_id = Column(String(64), ForeignKey("training_action.action_id"), nullable=False, index=True, comment="引用的训练动作 ID")
    sequence_order = Column(Integer, nullable=False, default=1, comment="动作项在阶段内的执行顺序")
    
    # === 力量训练参数 ===
    sets = Column(Integer, nullable=True, comment="组数，范围 1-6 组")
    reps_per_set = Column(Integer, nullable=True, comment="每组次数，仅适用于力量训练")
    rest_seconds_default = Column(Integer, default=60, comment="默认组间休息时间（秒）")  # ✅ V2.1 默认 60 秒
    
    # === 有氧/拉伸参数 ===
    duration_seconds = Column(Integer, nullable=True, comment="单次执行时长（秒）")
    duration_minutes = Column(Integer, nullable=True, comment="有氧动作时长（分钟）")  # ✅ V2.1 新增
    
    # === 通用参数 ===
    lateral_coeff = Column(Integer, default=1, comment="侧数系数")
    total_duration_seconds = Column(Integer, nullable=False, comment="动作项总执行时长（秒）")
    execution_notes = Column(Text, nullable=True, comment="执行备注")
    
    # === V2.1 新增属性 ===
    weight_records = Column(JSON, nullable=True, comment="每组训练的重量记录（kg）")  # ✅ V2.1 新增
    
    # === 业务关系 ===
    session = relationship("PlanSession", back_populates="action_items")
    action = relationship("TrainingAction", back_populates="session_items")
    
    __table_args__ = (
        CheckConstraint('sets >= 1 AND sets <= 6', name='chk_sets_range'),
    )


class TrainingSchedule(Base):
    """
    TrainingSchedule（训练日程）
    V2.1 新增对象，用于管理 7 天训练安排及延后逻辑
    业务规则：
    (1) 页面中只显示从当天开始的 7 天训练安排
    (2) 支持延后训练，可延后一天、两天、三天
    """
    __tablename__ = "training_schedule"
    
    # === 基本属性 ===
    schedule_id = Column(String(64), primary_key=True, index=True, comment="日程唯一标识符")
    plan_id = Column(String(64), ForeignKey("training_plan.plan_id"), nullable=False, index=True, comment="关联计划 ID")
    scheduled_date = Column(Date, nullable=False, comment="计划训练日期")
    session_id = Column(String(64), nullable=True, comment="当次训练对应的阶段 ID")
    status = Column(Enum(ScheduleStatusEnum), default=ScheduleStatusEnum.PLANNED, comment="状态")
    postpone_count = Column(Integer, default=0, comment="延后次数，限制最大延后 3 天")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # === 业务关系 ===
    plan = relationship("TrainingPlan", back_populates="schedules")
    
    def can_postpone(self, days: int) -> bool:
        """检查是否可以延后"""
        if self.postpone_count + days > 3:
            return False
        return True