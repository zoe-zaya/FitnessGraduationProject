# verify_tables.py
from app.utils.db import engine
from sqlalchemy import inspect

def verify_tables():
    """验证数据库表是否创建成功"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("=" * 50)
    print("✅ 数据库表创建验证报告")
    print("=" * 50)
    print(f"📊 共创建 {len(tables)} 张表")
    print("-" * 50)
    
    # 期望创建的 9 张表（7 个业务对象 + 1 个关联表 + alembic 版本表）
    expected_tables = [
        "user",                      # 用户
        "equipment_inventory",       # 器材清单
        "gym_equipment",             # 健身器材
        "training_action",           # 训练动作
        "training_plan",             # 训练计划
        "plan_session",              # 计划阶段
        "session_action_item",       # 阶段动作项
        "inventory_equipment_rel",   # 器材清单与器材关联表
    ]
    
    for table in expected_tables:
        if table in tables:
            print(f"✅ {table}")
        else:
            print(f"❌ {table} (缺失)")
    
    print("=" * 50)
    
    # 检查是否全部创建
    missing = set(expected_tables) - set(tables)
    if not missing:
        print("🎉 所有表创建成功！")
    else:
        print(f"⚠️  缺失表：{missing}")
    
    return len(missing) == 0

if __name__ == "__main__":
    verify_tables()