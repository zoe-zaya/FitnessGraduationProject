"""
外键约束调试脚本
检查 training_action 中引用的 equipment_id 是否存在于 gym_equipment 中
"""
# ==================== 添加以下代码解决模块导入问题 ====================
import sys
import os
from pathlib import Path

# 获取项目根目录（02_Backend 目录）
project_root = Path(__file__).resolve().parent.parent
# 将项目根目录添加到 sys.path
sys.path.insert(0, str(project_root))
# ====================================================================

from app.utils.db import SessionLocal
from app.models.equipment import GymEquipment
from app.models.action import TrainingAction

def debug_foreign_key():
    db = SessionLocal()
    
    try:
        # 1. 获取所有器材 ID
        equipment_ids = {eq.equipment_id for eq in db.query(GymEquipment.equipment_id).all()}
        print(f"✅ gym_equipment 表中有 {len(equipment_ids)} 个器材 ID")
        
        # 2. 检查动作脚本中引用的器材 ID（模拟）
        from scripts.seed_actions import ACTIONS_DATA
        action_equipment_ids = {action["equipment_id"] for action in ACTIONS_DATA}
        print(f"✅ 动作脚本引用了 {len(action_equipment_ids)} 个器材 ID")
        
        # 3. 找出不存在的引用
        missing = action_equipment_ids - equipment_ids
        if missing:
            print(f"❌ 以下器材 ID 在数据库中不存在：{missing}")
            print("💡 请先运行 seed_equipment.py 导入器材数据")
        else:
            print("✅ 所有器材引用均有效")
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_foreign_key()