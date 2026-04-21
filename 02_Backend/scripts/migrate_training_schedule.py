"""
TrainingSchedule 表结构迁移脚本
新增 actual_duration_seconds 字段
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"

def migrate_training_schedule():
    """执行表结构迁移"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("🔍 检查 training_schedule 表结构...")
            
            result = conn.execute(text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'training_schedule'
                AND COLUMN_NAME = 'actual_duration_seconds'
            """), {"schema": settings.MYSQL_DB})
            
            if result.fetchone():
                print("✅ actual_duration_seconds 字段已存在，跳过迁移")
                return
            
            conn.execute(text("""
                ALTER TABLE training_schedule 
                ADD COLUMN actual_duration_seconds INT NULL COMMENT '实际训练时长（秒）'
            """))
            print("✅ actual_duration_seconds 字段添加成功")
            
            conn.commit()
            
            verify_result = conn.execute(text("""
                SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'training_schedule'
                AND COLUMN_NAME = 'actual_duration_seconds'
            """), {"schema": settings.MYSQL_DB})
            
            print("\n📋 training_schedule 字段状态:")
            for row in verify_result:
                print(f"   - {row[0]}: NULLABLE={row[1]} - {row[2]}")
            
            print("\n✅ 表结构迁移完成")
            
    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("  TrainingSchedule 表结构迁移脚本")
    print("  新增 actual_duration_seconds 字段")
    print("=" * 60)
    migrate_training_schedule()
    print("=" * 60)
