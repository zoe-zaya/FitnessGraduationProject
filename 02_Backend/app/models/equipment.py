"""
EquipmentInventory（器材清单）与 GymEquipment（健身器材）业务对象模型
对应《需求规格说明书》表 2-2、表 2-3
业务规则：
(1) 用户可创建多个器材清单，每个清单对应一个物理健身房
(2) 系统预置不少于 20 类的常见健身器材的标准信息库
(3) 器材识别准确率要求不低于 85%，单次识别响应时间不超过 2 秒
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.db import Base


# === 器材清单与健身器材的多对多关联表 ===
inventory_equipment_rel = Table(
    "inventory_equipment_rel",
    Base.metadata,
    Column("inventory_id", String(64), ForeignKey("equipment_inventory.inventory_id"), primary_key=True),
    Column("equipment_id", String(64), ForeignKey("gym_equipment.equipment_id"), primary_key=True),
    comment="器材清单与健身器材关联表"
)


class EquipmentInventory(Base):
    """
    EquipmentInventory（器材清单）
    对应《需求规格说明书》表 2-2
    """
    __tablename__ = "equipment_inventory"

    # === 表 2-2 定义属性 ===
    inventory_id = Column(String(64), primary_key=True, index=True, comment="器材清单唯一标识符")
    user_id = Column(String(64), ForeignKey("user.user_id"), nullable=False, index=True, comment="关联用户 ID")
    location_tag = Column(String(128), nullable=False, index=True, comment="归属标签，如'家附近健身房'")
    description = Column(Text, nullable=True, comment="清单描述信息")
    create_time = Column(DateTime, default=datetime.now, comment="清单创建时间")

    # === 业务关系（图 2-1） ===
    # 用户与器材清单：一对多
    user = relationship("User", back_populates="inventories")
    # 器材清单与健身器材：多对多
    equipment_list = relationship(
        "GymEquipment",
        secondary=inventory_equipment_rel,
        back_populates="inventories",
        lazy="select"
    )
    # 器材清单与训练计划：一对多
    plans = relationship("TrainingPlan", back_populates="inventory", cascade="all, delete-orphan")

    # === 表 2-2 定义函数（在 Service 层实现） ===
    # addEquipmentAuto() -> 由 app/services/detection.py 配合实现
    # addEquipmentManual() -> 由 app/api/equipment.py 实现
    # removeEquipment() -> 由 app/api/equipment.py 实现


class GymEquipment(Base):
    """
    GymEquipment（健身器材）
    对应《需求规格说明书》表 2-3
    系统预置不少于 20 类常见健身器材
    """
    __tablename__ = "gym_equipment"

    # === 表 2-3 定义属性 ===
    equipment_id = Column(String(64), primary_key=True, index=True, comment="器材唯一标识符，系统预定义")
    name = Column(String(128), nullable=False, index=True, comment="器材标准名称，如'史密斯机'")
    category = Column(String(64), nullable=False, index=True, comment="器材分类")
    description = Column(Text, nullable=True, comment="器材功能描述与使用场景说明")
    target_muscles = Column(String(512), nullable=True, comment="目标肌群列表，JSON 格式存储")
    image_url = Column(String(512), nullable=True, comment="器材示意图 URL")
    create_time = Column(DateTime, default=datetime.now, comment="记录创建时间")

    # === 业务关系（图 2-1） ===
    # 健身器材与器材清单：多对多
    inventories = relationship(
        "EquipmentInventory",
        secondary=inventory_equipment_rel,
        back_populates="equipment_list"
    )
    # 健身器材与训练动作：一对多
    actions = relationship("TrainingAction", back_populates="equipment", lazy="select")

    # === 表 2-3 定义函数（在 Service 层实现） ===
    # detectFromImage() -> 由 app/services/detection.py 实现（调用 YOLOv5 模型）

    def get_target_muscles_list(self):
        """解析目标肌群 JSON 字符串为列表"""
        import json
        if self.target_muscles:
            try:
                return json.loads(self.target_muscles)
            except:
                return []
        return []