"""
User（用户）业务对象模型
对应《需求规格说明书》表 2-1
业务规则：用户首次使用系统时必须完成基本信息录入，否则无法生成个性化训练计划
"""

from sqlalchemy import Column, String, Integer, Double, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.utils.db import Base


class FitnessGoalEnum(str, enum.Enum):
    """健身目标枚举"""
    MUSCLE_GAIN = "增肌"
    FAT_LOSS = "减脂"
    SHAPING = "塑形"
    FITNESS_IMPROVEMENT = "增强体能"


class ExperienceLevelEnum(str, enum.Enum):
    """健身经验水平枚举"""
    BEGINNER = "初学者"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"


class GenderEnum(str, enum.Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(Base):
    __tablename__ = "user"

    # === 表 2-1 定义属性 ===
    user_id = Column(String(64), primary_key=True, index=True, comment="用户唯一标识符，系统自动生成")
    name = Column(String(64), nullable=False, index=True, comment="用户姓名或昵称")
    age = Column(Integer, nullable=True, comment="用户年龄（岁），作为动作难度筛选与安全评估的依据")
    gender = Column(Enum(GenderEnum), nullable=True, comment="用户性别，影响目标肌群训练侧重")
    height = Column(Double, nullable=True, comment="身高（厘米），结合体重计算 BMI")
    weight = Column(Double, nullable=True, comment="体重（千克），结合身高计算 BMI")
    fitness_goal = Column(Enum(FitnessGoalEnum), nullable=True, comment="健身目标，决定训练计划类型")
    experience_level = Column(Enum(ExperienceLevelEnum), nullable=True, comment="健身经验水平，影响动作难度与参数配置")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号，用于登录")
    password_hash = Column(String(256), nullable=False, comment="加密后的密码")
    avatar_url = Column(String(512), nullable=True, comment="头像 URL")
    birthday = Column(DateTime, nullable=True, comment="生日")
    create_time = Column(DateTime, default=datetime.now, comment="账号创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="信息更新时间")

    # === 业务关系（图 2-1） ===
    # 用户与器材清单：一对多
    inventories = relationship("EquipmentInventory", back_populates="user", cascade="all, delete-orphan")
    # 用户与训练计划：一对多
    plans = relationship("TrainingPlan", back_populates="user", cascade="all, delete-orphan")

    # === 表 2-1 定义函数（在 Service 层实现） ===
    # createTrainingPlan() -> 由 app/services/plan_generator.py 实现
    # manageEquipmentInventory() -> 由 app/api/equipment.py 实现

    def calculate_bmi(self):
        """计算 BMI 指数"""
        if self.height and self.weight and self.height > 0:
            return round(self.weight / ((self.height / 100) ** 2), 2)
        return None

    def is_profile_complete(self):
        """检查用户基本信息是否完整（业务规则：首次使用必须录入）"""
        required_fields = [self.age, self.gender, self.height, self.weight, 
                          self.fitness_goal, self.experience_level]
        return all(field is not None for field in required_fields)