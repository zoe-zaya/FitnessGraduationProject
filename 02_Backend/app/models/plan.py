"""
训练计划业务对象模型
对应《需求规格说明书》表 2-5/2-6/2-7
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import json
from app.utils.db import Base


class TrainingPlan(Base):
    """
    TrainingPlan（训练计划）
    对应《需求规格说明书》表 2-5
    业务规则：
    (1) 计划必须关联有效器材清单，确保所有推荐动作均可在目标健身房执行
    (2) 计划总时长建议 40-65 分钟（热身 5-10min+ 正式 30-45min+ 拉伸 5-10min）
    (3) 计划过期后系统提示"建议根据当前身体状态重新生成计划"
    """
    __tablename__ = "training_plan"
    
    # === 表 2-5 定义属性 ===
    plan_id = Column(String(64), primary_key=True, index=True, comment="计划唯一标识符")
    user_id = Column(String(64), ForeignKey("user.user_id"), nullable=False, index=True, comment="计划归属用户 ID")
    inventory_id = Column(String(64), ForeignKey("equipment_inventory.inventory_id"), nullable=False, index=True, comment="关联器材清单 ID")
    create_time = Column(DateTime, default=datetime.now, comment="计划生成时间")
    valid_days = Column(Integer, default=30, comment="计划有效期（天）")
    total_duration_minutes = Column(Integer, default=0, comment="计划总时长（分钟）")
    
    # === ✅ 新增字段 ===
    plan_name = Column(String(128), nullable=True, comment="计划名称（如'增肌周计划'、'减脂周计划'）")
    fitness_goal = Column(String(32), nullable=True, comment="健身目标（增肌/减脂/塑形/增强体能）")
    training_part = Column(String(32), nullable=True, comment="训练部位（胸部/背部/肩部/手臂/腿部/臀部/核心/全身）")
    
    status = Column(String(16), default="active", comment="计划状态（active/expired/archived）")
    
    # === 业务关系（图 2-1） ===
    # 用户与训练计划：一对多
    user = relationship("User", back_populates="plans")
    # 器材清单与训练计划：一对多
    inventory = relationship("EquipmentInventory", back_populates="plans")
    # 训练计划与计划阶段：一对多
    sessions = relationship("PlanSession", back_populates="plan", cascade="all, delete-orphan", lazy="select")
    
    def is_expired(self) -> bool:
        """检查计划是否过期"""
        if not self.create_time:
            return True
        expire_time = self.create_time + timedelta(days=self.valid_days)
        return datetime.now() > expire_time


class PlanSession(Base):
    """
    PlanSession（计划阶段）
    对应《需求规格说明书》表 2-6
    业务规则：
    (1) 三阶段顺序固定不可调整，符合运动生理学训练原则
    (2) 热身阶段仅包含 warmup 类别动作，拉伸阶段仅包含 cooldown 类别动作
    (3) 正式训练阶段根据用户目标选择 main_cardio（减脂）或 main_strength（增肌）动作
    """
    __tablename__ = "plan_session"
    
    # === 表 2-6 定义属性 ===
    session_id = Column(String(64), primary_key=True, index=True, comment="阶段唯一标识符")
    plan_id = Column(String(64), ForeignKey("training_plan.plan_id"), nullable=False, index=True, comment="关联计划 ID")
    session_type = Column(String(32), nullable=False, comment="阶段类型（warmup/main/cooldown）")
    sequence_order = Column(Integer, nullable=False, comment="阶段执行顺序（1=热身，2=正式，3=拉伸）")
    estimated_duration_minutes = Column(Integer, default=0, comment="该阶段预估总时长（分钟）")
    target_muscles = Column(String(512), nullable=True, comment="该阶段目标肌群列表（JSON 格式）")  # ✅ 存储 JSON 字符串
    description = Column(Text, nullable=True, comment="阶段描述说明")
    
    # === 业务关系 ===
    plan = relationship("TrainingPlan", back_populates="sessions")
    action_items = relationship("SessionActionItem", back_populates="session", cascade="all, delete-orphan", lazy="select")
    
    # === ✅ 新增：属性转换器（列表 ↔ JSON 字符串） ===
    @property
    def target_muscles_list(self):
        """将数据库中的 JSON 字符串解析为列表"""
        if not self.target_muscles:
            return []
        try:
            return json.loads(self.target_muscles)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @target_muscles_list.setter
    def target_muscles_list(self, value):
        """将列表序列化为 JSON 字符串存入数据库"""
        if isinstance(value, list):
            self.target_muscles = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, str):
            self.target_muscles = value
        else:
            self.target_muscles = None


class SessionActionItem(Base):
    """
    SessionActionItem（阶段动作项）
    对应《需求规格说明书》表 2-7
    业务规则：
    (1) 参数互斥性：同一动作项不可同时配置 repsPerSet 与 durationSeconds
    (2) 总时长自动计算：totalDurationSeconds 由系统根据参数组合自动计算
    (3) 动作时长估算：力量训练单组时长基于动作类型预设，用户不可调整
    """
    __tablename__ = "session_action_item"
    
    # === 表 2-7 定义属性 ===
    item_id = Column(String(64), primary_key=True, index=True, comment="动作项唯一标识符")
    session_id = Column(String(64), ForeignKey("plan_session.session_id"), nullable=False, index=True, comment="关联阶段 ID")
    action_id = Column(String(64), ForeignKey("training_action.action_id"), nullable=False, index=True, comment="引用的训练动作 ID")
    # ✅ 修改：允许 sets/reps_per_set/rest_seconds 为 NULL（仅力量训练使用）
    sets = Column(Integer, nullable=True, comment="组数，范围 1-6 组，仅适用于力量训练类动作")
    reps_per_set = Column(Integer, nullable=True, comment="每组次数，仅适用于力量训练类动作")
    rest_seconds = Column(Integer, nullable=True, comment="组间休息时间（秒），仅适用于力量训练类动作")
    duration_seconds = Column(Integer, nullable=True, comment="单次执行时长（秒）")
    lateral_coeff = Column(Integer, default=1, comment="侧数系数，用于拉伸/热身动作")
    total_duration_seconds = Column(Integer, nullable=False, comment="动作项总执行时长（秒）")
    execution_notes = Column(Text, nullable=True, comment="执行备注，个性化提示")
    
    # === 业务关系 ===
    session = relationship("PlanSession", back_populates="action_items")
    action = relationship("TrainingAction", back_populates="session_items")


class SessionTypeEnum:
    """阶段类型枚举"""
    WARMUP = "warmup"
    MAIN = "main"
    COOLDOWN = "cooldown"