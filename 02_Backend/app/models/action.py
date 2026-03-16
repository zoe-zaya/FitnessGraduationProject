"""
TrainingAction（训练动作）业务对象模型
对应《需求规格说明书》表 2-4
业务规则：
(1) 系统预置不小于 100 个标准训练动作，覆盖四类动作类别
(2) 动作推荐时需校验用户器材清单是否包含所需器材
(3) 动作难度需与用户经验水平匹配（初学者不推荐高级动作）
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.utils.db import Base
from datetime import datetime
from sqlalchemy import DateTime


class ActionCategoryEnum(str, enum.Enum):
    """动作类别枚举，决定动作在训练计划中的适用阶段"""
    WARMUP = "warmup"           # 热身激活阶段
    MAIN_CARDIO = "main_cardio"   # 正式训练 - 有氧（减脂）
    MAIN_STRENGTH = "main_strength"  # 正式训练 - 力量（增肌）
    COOLDOWN = "cooldown"       # 拉伸放松阶段


class DifficultyLevelEnum(str, enum.Enum):
    """动作难度等级枚举"""
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"


class TrainingAction(Base):
    __tablename__ = "training_action"

    # === 表 2-4 定义属性 ===
    action_id = Column(String(64), primary_key=True, index=True, comment="动作唯一标识符，系统预定义")
    name = Column(String(128), nullable=False, index=True, comment="动作标准名称")
    action_category = Column(Enum(ActionCategoryEnum), nullable=False, index=True, 
                            comment="动作类别，决定适用阶段")
    target_muscles = Column(String(512), nullable=True, comment="目标肌群列表，JSON 格式")
    difficulty_level = Column(Enum(DifficultyLevelEnum), nullable=False, index=True, 
                             comment="动作难度等级")
    equipment_id = Column(String(64), ForeignKey("gym_equipment.equipment_id"), 
                         nullable=True, index=True, comment="关联器材 ID，无器械动作为'none'")
    estimated_seconds = Column(Integer, nullable=True, comment="单次估算时长（秒），用于力量训练")
    video_demo_url = Column(String(512), nullable=True, comment="标准动作演示视频资源地址")
    safety_tips = Column(Text, nullable=True, comment="安全注意事项与常见错误纠正提示")
    create_time = Column(DateTime, default=datetime.now, comment="记录创建时间")

    # === 业务关系（图 2-1） ===
    # 健身器材与训练动作：一对多
    equipment = relationship("GymEquipment", back_populates="actions")
    # 训练动作与阶段动作项：一对多
    session_items = relationship("SessionActionItem", back_populates="action", lazy="select")

    def get_target_muscles_list(self):
        """解析目标肌群 JSON 字符串为列表"""
        import json
        if self.target_muscles:
            try:
                return json.loads(self.target_muscles)
            except:
                return []
        return []

    def is_suitable_for_user(self, experience_level):
        """
        校验动作是否适合用户经验水平（业务规则 3）
        初学者不推荐高级动作
        """
        if experience_level == "初学者":
            return self.difficulty_level in [DifficultyLevelEnum.BEGINNER, DifficultyLevelEnum.INTERMEDIATE]
        elif experience_level == "中级":
            return self.difficulty_level != DifficultyLevelEnum.ADVANCED
        return True  # 高级用户可执行所有动作