"""
器材管理服务
处理器材清单和健身器材的业务逻辑
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.equipment import EquipmentInventory, GymEquipment, inventory_equipment_rel


class EquipmentService:
    """器材管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_inventories(self, user_id: str) -> List[EquipmentInventory]:
        """获取用户所有器材清单"""
        return self.db.query(EquipmentInventory).filter(
            EquipmentInventory.user_id == user_id
        ).all()
    
    def get_inventory_detail(self, inventory_id: str, user_id: str) -> Optional[EquipmentInventory]:
        """获取器材清单详情"""
        return self.db.query(EquipmentInventory).filter(
            EquipmentInventory.inventory_id == inventory_id,
            EquipmentInventory.user_id == user_id
        ).first()
    
    def get_inventory_equipment(self, inventory_id: str) -> List[GymEquipment]:
        """获取清单内的所有器材"""
        rels = self.db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == inventory_id
        ).all()
        
        equipment_list = []
        for rel in rels:
            equipment = self.db.query(GymEquipment).filter(
                GymEquipment.equipment_id == rel.equipment_id
            ).first()
            if equipment:
                equipment_list.append(equipment)
        
        return equipment_list
    
    def add_equipment_to_inventory(self, inventory_id: str, equipment_id: str) -> bool:
        """添加器材到清单"""
        # 检查是否已存在
        existing = self.db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == inventory_id,
            inventory_equipment_rel.c.equipment_id == equipment_id
        ).first()
        
        if existing:
            return False
        
        # 添加关联
        new_rel = inventory_equipment_rel.insert().values(
            inventory_id=inventory_id,
            equipment_id=equipment_id
        )
        self.db.execute(new_rel)
        self.db.commit()
        
        return True
    
    def remove_equipment_from_inventory(self, inventory_id: str, equipment_id: str) -> bool:
        """从清单中删除器材"""
        result = self.db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == inventory_id,
            inventory_equipment_rel.c.equipment_id == equipment_id
        ).delete()
        
        self.db.commit()
        
        return result > 0
    
    def search_equipment(self, keyword: str, limit: int = 20) -> List[GymEquipment]:
        """搜索器材"""
        return self.db.query(GymEquipment).filter(
            (GymEquipment.name.like(f"%{keyword}%")) |
            (GymEquipment.category.like(f"%{keyword}%"))
        ).limit(limit).all()