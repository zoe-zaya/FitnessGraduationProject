"""
TrainingPlan（训练计划）、PlanSession（计划阶段）、SessionActionItem（阶段动作项）业务对象模型
对应《需求规格说明书》表 2-5、表 2-6、表 2-7
业务规则：
(1) 计划总时长建议 40-65 分钟（热身 5-10min+ 正式 30-45min+ 拉伸 5-10min）
(2) 三阶段顺序固定不可调整（sequenceOrder=1/2/3）
(3) 参数互斥性：同一动作项不可同时配置 repsPerSet 与 durationSeconds
(4) 总时长自动计算，用户不可手动修改
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from app.utils.db import Base


class SessionTypeEnum(str, enum.Enum):
    """阶段类型枚举，严格限定三类"""
    WARMUP = "warmup"       # 热身激活阶段（必须为首阶段）
    MAIN = "main"           # 正式训练阶段（必须为中间阶段）
    COOLDOWN = "cooldown"   # 拉伸放松阶段（必须为末阶段）


class TrainingPlan(Base):
    """
    TrainingPlan（训练计划）
    对应《需求规格说明书》表 2-5
    """
    __tablename__ = "training_plan"

    # === 表 2-5 定义属性 ===
    plan_id = Column(String(64), primary_key=True, index=True, comment="计划唯一标识符")
    user_id = Column(String(64), ForeignKey("user.user_id"), nullable=False, index=True, comment="计划归属用户 ID")
    inventory_id = Column(String(64), ForeignKey("equipment_inventory.inventory_id"), nullable=False, 
                         index=True, comment="关联器材清单 ID")
    create_time = Column(DateTime, default=datetime.now, comment="计划生成时间")
    valid_days = Column(Integer, default=30, comment="计划有效期（天），默认 30 天")
    total_duration_minutes = Column(Integer, nullable=False, comment="计划总时长（分钟），为三阶段时长之和")
    status = Column(String(32), default="active", comment="计划状态：active/expired/archived")

    # === 业务关系（图 2-1） ===
    # 用户与训练计划：一对多
    user = relationship("User", back_populates="plans")
    # 器材清单与训练计划：一对多
    inventory = relationship("EquipmentInventory", back_populates="plans")
    # 训练计划与计划阶段：一对多有序
    sessions = relationship(
        "PlanSession", 
        back_populates="plan", 
        cascade="all, delete-orphan",
        order_by="PlanSession.sequence_order"
    )

    # === 表 2-5 定义函数（在 Service 层实现） ===
    # generateFromUserAndInventory() -> 由 app/services/plan_generator.py 实现

    def is_expired(self):
        """检查计划是否过期（业务规则 3）"""
        expire_time = self.create_time + timedelta(days=self.valid_days)
        return datetime.now() > expire_time

    def calculate_total_duration(self):
        """汇总三阶段时长"""
        return sum(session.estimated_duration_minutes for session in self.sessions)


class PlanSession(Base):
    """
    PlanSession（计划阶段）
    对应《需求规格说明书》表 2-6
    业务规则：三阶段顺序固定不可调整，符合运动生理学训练原则
    """
    __tablename__ = "plan_session"

    # === 表 2-6 定义属性 ===
    session_id = Column(String(64), primary_key=True, index=True, comment="阶段唯一标识符")
    plan_id = Column(String(64), ForeignKey("training_plan.plan_id"), nullable=False, index=True, comment="关联计划 ID")
    session_type = Column(Enum(SessionTypeEnum), nullable=False, index=True, comment="阶段类型")
    sequence_order = Column(Integer, nullable=False, comment="阶段执行顺序（1=热身，2=正式，3=拉伸）")
    estimated_duration_minutes = Column(Integer, default=0, comment="该阶段预估总时长（分钟）")
    description = Column(Text, nullable=True, comment="阶段说明，如'动态拉伸激活全身肌群'")

    # === 业务关系（图 2-1） ===
    # 训练计划与计划阶段：一对多
    plan = relationship("TrainingPlan", back_populates="sessions")
    # 计划阶段与阶段动作项：一对多
    action_items = relationship(
        "SessionActionItem", 
        back_populates="session", 
        cascade="all, delete-orphan",
        order_by="SessionActionItem.item_id"
    )

    # === 表 2-6 业务规则校验 ===
    __table_args__ = (
        CheckConstraint('sequence_order IN (1, 2, 3)', name='chk_sequence_order'),
        CheckConstraint('''
            (session_type = 'warmup' AND sequence_order = 1) OR
            (session_type = 'main' AND sequence_order = 2) OR
            (session_type = 'cooldown' AND sequence_order = 3)
        ''', name='chk_session_type_order')
    )


class SessionActionItem(Base):
    """
    SessionActionItem（阶段动作项）
    对应《需求规格说明书》表 2-7
    业务规则：
    (1) 参数互斥性：同一动作项不可同时配置 repsPerSet 与 durationSeconds
    (2) 总时长自动计算：totalDurationSeconds 由系统根据参数组合自动计算
    (3) 动作时长估算：力量训练单组时长基于动作类型预设
    """
    __tablename__ = "session_action_item"

    # === 表 2-7 定义属性 ===
    item_id = Column(String(64), primary_key=True, index=True, comment="动作项唯一标识符")
    session_id = Column(String(64), ForeignKey("plan_session.session_id"), nullable=False, index=True, comment="关联阶段 ID")
    action_id = Column(String(64), ForeignKey("training_action.action_id"), nullable=False, index=True, comment="引用的训练动作 ID")
    sets = Column(Integer, nullable=False, default=3, comment="组数，范围 1-6 组")
    reps_per_set = Column(Integer, nullable=True, comment="每组次数，仅适用于力量训练类动作，范围 5-20 次/组")
    rest_seconds = Column(Integer, nullable=True, default=60, comment="组间休息时间（秒），仅适用于力量训练")
    duration_seconds = Column(Integer, nullable=True, comment="单次执行时长（秒）")
    lateral_coeff = Column(Integer, default=1, comment="侧数系数，拉伸/热身动作为 2，否则为 1")
    total_duration_seconds = Column(Integer, nullable=False, comment="【自动计算】动作项总执行时长（秒）")
    execution_notes = Column(Text, nullable=True, comment="执行备注，系统生成的个性化提示")

    # === 业务关系（图 2-1） ===
    # 计划阶段与阶段动作项：一对多
    session = relationship("PlanSession", back_populates="action_items")
    # 训练动作与阶段动作项：多对一
    action = relationship("TrainingAction", back_populates="session_items")

    # === 表 2-7 业务规则校验（参数互斥性） ===
    # 注意：实际互斥逻辑在 Service 层实现，此处为数据库级提示
    __table_args__ = (
        CheckConstraint('sets >= 1 AND sets <= 6', name='chk_sets_range'),
    )

    def calculate_total_duration(self, action_category, estimated_seconds):
        """
        【核心业务规则】自动计算动作项总执行时长
        对应《需求规格说明书》表 2-7 公式
        """
        if action_category in ["main_strength"]:
            # 力量训练：sets × (estimatedSeconds × repsPerSet + restSeconds) - restSeconds
            if self.reps_per_set and estimated_seconds:
                self.total_duration_seconds = self.sets * (estimated_seconds * self.reps_per_set + self.rest_seconds) - self.rest_seconds
            else:
                self.total_duration_seconds = 0
        elif action_category in ["main_cardio"]:
            # 有氧训练：durationSeconds
            self.total_duration_seconds = self.duration_seconds if self.duration_seconds else 0
        else:
            # 热身/拉伸：sets × durationSeconds × lateralCoeff
            if self.duration_seconds:
                self.total_duration_seconds = self.sets * self.duration_seconds * self.lateral_coeff
            else:
                self.total_duration_seconds = 0
        
        return self.total_duration_seconds

    def validate_parameters(self):
        """
        校验参数互斥性（业务规则 1）
        力量训练用 reps_per_set，其他用 duration_seconds
        """
        if self.reps_per_set is not None and self.duration_seconds is not None:
            raise ValueError("参数互斥错误：reps_per_set 与 duration_seconds 不可同时配置")
        return True