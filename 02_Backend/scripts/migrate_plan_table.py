"""
TrainingPlan 表结构迁移脚本（V2）
添加 training_part 字段
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"

def migrate_plan_table_v2():
    """执行表结构迁移"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("🔍 检查 training_plan 表结构...")
            
            # 检查 training_part 字段是否存在
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'training_plan' 
                AND COLUMN_NAME = 'training_part'
            """), {"schema": settings.MYSQL_DB})
            
            training_part_exists = result.fetchone() is not None
            
            if not training_part_exists:
                print("➕ 添加 training_part 字段...")
                conn.execute(text("""
                    ALTER TABLE training_plan 
                    ADD COLUMN training_part VARCHAR(32) NULL COMMENT '训练部位（胸部/背部/肩部/手臂/腿部/臀部/核心/全身）'
                """))
                print("✅ training_part 字段添加成功")
            else:
                print("⚠️  training_part 字段已存在，跳过")
            
            # 检查 PlanSession 表的 target_muscles 字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'plan_session' 
                AND COLUMN_NAME = 'target_muscles'
            """), {"schema": settings.MYSQL_DB})
            
            target_muscles_exists = result.fetchone() is not None
            
            if not target_muscles_exists:
                print("➕ 添加 plan_session.target_muscles 字段...")
                conn.execute(text("""
                    ALTER TABLE plan_session 
                    ADD COLUMN target_muscles VARCHAR(512) NULL COMMENT '该阶段目标肌群列表（JSON 格式）'
                """))
                print("✅ plan_session.target_muscles 字段添加成功")
            else:
                print("⚠️  plan_session.target_muscles 字段已存在，跳过")
            
            conn.commit()
            
            # 验证迁移结果
            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'training_plan'
                ORDER BY ORDINAL_POSITION
            """), {"schema": settings.MYSQL_DB})
            
            print("\n📋 training_plan 表结构:")
            for row in result:
                print(f"   - {row[0]}: {row[1]}({row[2]}) - {row[3]}")
            
            print("\n✅ 表结构迁移完成")
            
    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("  TrainingPlan 表结构迁移脚本（V2）")
    print("  添加 training_part 和 plan_session.target_muscles 字段")
    print("=" * 60)
    migrate_plan_table_v2()
    print("=" * 60)