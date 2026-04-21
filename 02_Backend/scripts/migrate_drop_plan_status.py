"""
删除 training_plan 表的 status 字段
该字段在 V2.1 版中不再使用
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"

def migrate_drop_plan_status():
    """删除 training_plan 表的 status 字段"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    try:
        with engine.connect() as conn:
            print("=" * 60)
            print("  删除 training_plan.status 字段")
            print("=" * 60)

            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('training_plan')]

            if 'status' in columns:
                conn.execute(text("ALTER TABLE training_plan DROP COLUMN status"))
                conn.commit()
                print("   ✅ 删除 status 字段")
            else:
                print("   ⚠️  status 字段不存在，跳过")

            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :schema
                AND TABLE_NAME = 'training_plan'
                ORDER BY ORDINAL_POSITION
            """), {"schema": settings.MYSQL_DB})

            print("\n   training_plan 表字段:")
            for row in result:
                print(f"      - {row[0]}: {row[1]} - {row[2]}")

            print("\n" + "=" * 60)
            print("  ✅ 迁移完成")
            print("=" * 60)

    except Exception as e:
        print(f"\n❌ 迁移失败：{e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    migrate_drop_plan_status()
