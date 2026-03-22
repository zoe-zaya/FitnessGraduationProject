"""
器材数据初始化脚本
预置 20 类常见健身器材（《任务书》技术指标）
对应《需求规格说明书》表 2-3 健身器材业务对象
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

from sqlalchemy.orm import Session
from app.utils.db import SessionLocal, engine
from app.models.equipment import GymEquipment
import uuid
import json


# 20 类预置健身器材数据（对应用户提供的器材列表）
EQUIPMENT_DATA = [
    {
        "equipment_id": "eq_001",
        "name": "卷腹机",
        "category": "力量训练 - 固定器械",
        "description": "专门用于腹部卷腹训练的固定器械，可调节阻力，适合核心肌群强化训练",
        "target_muscles": ["腹直肌", "腹外斜肌", "核心肌群"]
    },
    {
        "equipment_id": "eq_002",
        "name": "杠铃",
        "category": "力量训练 - 自由重量",
        "description": "基础自由重量训练器材，可进行深蹲、硬拉、卧推、推举等多种复合动作",
        "target_muscles": ["全身肌群", "核心肌群", "下肢肌群", "上肢肌群"]
    },
    {
        "equipment_id": "eq_003",
        "name": "卧推凳",
        "category": "辅助器材",
        "description": "配合哑铃或杠铃进行卧推训练的辅助器材，可调节角度进行上斜、平板、下斜卧推",
        "target_muscles": ["胸大肌", "三角肌前束", "肱三头肌"]
    },
    {
        "equipment_id": "eq_004",
        "name": "龙门架",
        "category": "力量训练 - 固定器械",
        "description": "多功能绳索训练器械，可进行夹胸、下拉、划船等多种拉力动作，训练角度灵活",
        "target_muscles": ["胸大肌", "背阔肌", "三角肌", "肱二头肌"]
    },
    {
        "equipment_id": "eq_005",
        "name": "坐姿推胸机",
        "category": "力量训练 - 固定器械",
        "description": "胸部训练固定器械，轨迹固定更安全，适合初学者进行胸部力量训练",
        "target_muscles": ["胸大肌", "三角肌前束", "肱三头肌"]
    },
    {
        "equipment_id": "eq_006",
        "name": "椭圆机",
        "category": "有氧器械",
        "description": "低冲击有氧训练设备，模拟跑步动作但保护膝关节，适合减脂和心肺功能训练",
        "target_muscles": ["心肺功能", "下肢肌群", "臀大肌"]
    },
    {
        "equipment_id": "eq_007",
        "name": "哑铃",
        "category": "力量训练 - 自由重量",
        "description": "自由重量训练器材，可用于多种孤立和复合动作，训练灵活度高",
        "target_muscles": ["全身肌群", "上肢肌群", "下肢肌群"]
    },
    {
        "equipment_id": "eq_008",
        "name": "哈克深蹲机",
        "category": "力量训练 - 固定器械",
        "description": "下肢力量训练固定器械，固定轨迹进行深蹲动作，主要锻炼股四头肌和臀大肌",
        "target_muscles": ["股四头肌", "臀大肌", "腘绳肌"]
    },
    {
        "equipment_id": "eq_009",
        "name": "臀部外展/内收机",
        "category": "力量训练 - 固定器械",
        "description": "专门训练臀部和大腿内外侧肌群的固定器械，可分别进行外展和内收动作",
        "target_muscles": ["臀中肌", "臀小肌", "大腿内收肌群", "大腿外展肌群"]
    },
    {
        "equipment_id": "eq_010",
        "name": "动感单车",
        "category": "有氧器械",
        "description": "室内自行车有氧训练设备，可调节阻力进行高强度间歇训练，适合减脂和心肺功能提升",
        "target_muscles": ["心肺功能", "股四头肌", "腘绳肌", "臀大肌"]
    },
    {
        "equipment_id": "eq_011",
        "name": "壶铃",
        "category": "力量训练 - 自由重量",
        "description": "动态力量训练器材，适合爆发力训练和功能性训练，可进行摇摆、抓举、挺举等动作",
        "target_muscles": ["核心肌群", "臀大肌", "肩部", "下肢肌群"]
    },
    {
        "equipment_id": "eq_012",
        "name": "高位下拉器",
        "category": "力量训练 - 固定器械",
        "description": "背部训练器械，主要锻炼背阔肌，可进行正握、反握、窄握等多种握法",
        "target_muscles": ["背阔肌", "肱二头肌", "三角肌后束", "斜方肌"]
    },
    {
        "equipment_id": "eq_013",
        "name": "腿弯举机",
        "category": "力量训练 - 固定器械",
        "description": "孤立锻炼腘绳肌（大腿后侧）的器械，可进行坐姿或俯卧腿弯举",
        "target_muscles": ["腘绳肌", "股二头肌", "半腱肌", "半膜肌"]
    },
    {
        "equipment_id": "eq_014",
        "name": "腿部推蹬机",
        "category": "力量训练 - 固定器械",
        "description": "下肢复合力量训练器械，可进行大重量的腿部推蹬训练，主要锻炼股四头肌和臀大肌",
        "target_muscles": ["股四头肌", "臀大肌", "腘绳肌", "小腿三头肌"]
    },
    {
        "equipment_id": "eq_015",
        "name": "划船机",
        "category": "有氧器械",
        "description": "全身有氧训练设备，模拟划船动作，可同时锻炼心肺功能和背部肌群",
        "target_muscles": ["背阔肌", "心肺功能", "核心肌群", "肱二头肌"]
    },
    {
        "equipment_id": "eq_016",
        "name": "肩部推举机",
        "category": "力量训练 - 固定器械",
        "description": "肩部训练固定器械，轨迹固定更安全，主要锻炼三角肌前束和中束",
        "target_muscles": ["三角肌前束", "三角肌中束", "肱三头肌", "上斜方肌"]
    },
    {
        "equipment_id": "eq_017",
        "name": "史密斯机",
        "category": "力量训练 - 固定器械",
        "description": "固定轨迹的杠铃训练器械，适合深蹲、卧推、推举等复合动作，安全性高",
        "target_muscles": ["胸大肌", "三角肌", "肱三头肌", "股四头肌", "臀大肌"]
    },
    {
        "equipment_id": "eq_018",
        "name": "登山机",
        "category": "有氧器械",
        "description": "模拟登山动作的有氧训练设备，可调节阻力进行高强度心肺训练",
        "target_muscles": ["心肺功能", "下肢肌群", "臀大肌", "核心肌群"]
    },
    {
        "equipment_id": "eq_019",
        "name": "跑步机",
        "category": "有氧器械",
        "description": "室内有氧训练设备，可调节速度和坡度进行跑步或快走训练，适合减脂和心肺功能提升",
        "target_muscles": ["心肺功能", "下肢肌群", "臀大肌", "小腿三头肌"]
    },
    {
        "equipment_id": "eq_020",
        "name": "瑜伽垫",
        "category": "辅助器材",
        "description": "瑜伽、普拉提、拉伸等训练的辅助器材，提供缓冲和防滑功能",
        "target_muscles": ["全身肌群", "核心肌群", "柔韧性"]
    }
]


def seed_equipment():
    """
    初始化器材数据
    对应《任务书》技术指标：支持不少于 20 类常见健身器材
    """
    db = SessionLocal()
    
    try:
        # 1. 检查是否已存在数据
        existing_count = db.query(GymEquipment).count()
        if existing_count > 0:
            print(f"⚠️  数据库中已有{existing_count}条器材数据")
            print("如需重新初始化，请先清空 gym_equipment 表")
            return
        
        # 2. 插入预置数据
        for eq_data in EQUIPMENT_DATA:
            equipment = GymEquipment(
                equipment_id=eq_data["equipment_id"],
                name=eq_data["name"],
                category=eq_data["category"],
                description=eq_data["description"],
                target_muscles=json.dumps(eq_data["target_muscles"], ensure_ascii=False)
            )
            db.add(equipment)
        
        db.commit()
        
        # 3. 验证插入结果
        final_count = db.query(GymEquipment).count()
        print(f"✅ 器材数据初始化完成")
        print(f"📊 共导入 {final_count} 条器材记录")
        print(f"📋 器材分类统计:")
        
        # 统计各类器材数量
        categories = {}
        for eq in EQUIPMENT_DATA:
            cat = eq["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            print(f"   - {cat}: {count} 类")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败：{e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  健身器材数据初始化脚本")
    print("  对应《需求规格说明书》表 2-3 健身器材业务对象")
    print("=" * 60)
    seed_equipment()
    print("=" * 60)