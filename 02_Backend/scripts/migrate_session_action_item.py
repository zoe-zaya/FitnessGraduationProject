"""
SessionActionItem 表结构迁移脚本
修改 sets/reps_per_set/rest_seconds 字段允许为 NULL
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"

def migrate_session_action_item():
    """执行表结构迁移"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("🔍 检查 session_action_item 表结构...")
            
            # 修改 sets 字段允许为 NULL
            conn.execute(text("""
                ALTER TABLE session_action_item 
                MODIFY COLUMN sets INT NULL COMMENT '组数，范围 1-6 组，仅适用于力量训练类动作'
            """))
            print("✅ sets 字段修改成功")
            
            # 修改 reps_per_set 字段允许为 NULL
            conn.execute(text("""
                ALTER TABLE session_action_item 
                MODIFY COLUMN reps_per_set INT NULL COMMENT '每组次数，仅适用于力量训练类动作'
            """))
            print("✅ reps_per_set 字段修改成功")
            
            # 修改 rest_seconds 字段允许为 NULL
            conn.execute(text("""
                ALTER TABLE session_action_item 
                MODIFY COLUMN rest_seconds INT NULL COMMENT '组间休息时间（秒），仅适用于力量训练类动作'
            """))
            print("✅ rest_seconds 字段修改成功")
            
            conn.commit()
            
            # 验证迁移结果
            result = conn.execute(text("""
                SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'session_action_item'
                AND COLUMN_NAME IN ('sets', 'reps_per_set', 'rest_seconds')
            """), {"schema": settings.MYSQL_DB})
            
            print("\n📋 session_action_item 字段状态:")
            for row in result:
                print(f"   - {row[0]}: NULLABLE={row[1]} - {row[2]}")
            
            print("\n✅ 表结构迁移完成")
            
    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("  SessionActionItem 表结构迁移脚本")
    print("  修改 sets/reps_per_set/rest_seconds 允许为 NULL")
    print("=" * 60)
    migrate_session_action_item()
    print("=" * 60)
    