"""
训练计划模块数据库迁移脚本（V2.1 版）
根据需求规格说明书 2.1 版更新表结构
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"

def migrate_plan_v2():
    """执行 V2.1 版表结构迁移"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("=" * 60)
            print("  训练计划模块数据库迁移（V2.1 版）")
            print("=" * 60)
            
            # ========== 1. 修改 training_plan 表 ==========
            print("\n📋 修改 training_plan 表...")
            
            # 获取当前表结构
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('training_plan')]
            
            # 删除旧字段（MySQL 不支持 IF EXISTS，需先检查是否存在）
            if 'valid_days' in columns:
                conn.execute(text("ALTER TABLE training_plan DROP COLUMN valid_days"))
                print("   ✅ 删除 valid_days 字段")
            else:
                print("   ⚠️  valid_days 字段不存在，跳过")
            
            if 'total_duration_minutes' in columns:
                conn.execute(text("ALTER TABLE training_plan DROP COLUMN total_duration_minutes"))
                print("   ✅ 删除 total_duration_minutes 字段")
            else:
                print("   ⚠️  total_duration_minutes 字段不存在，跳过")
            
            if 'plan_type' not in columns:
                conn.execute(text("""
                    ALTER TABLE training_plan 
                    ADD COLUMN plan_type ENUM('FAT_LOSS', 'MUSCLE_GAIN') NOT NULL DEFAULT 'FAT_LOSS' COMMENT '计划类型：减脂/增肌'
                """))
                print("   ✅ 新增 plan_type 字段")
            else:
                print("   ⚠️  plan_type 字段已存在，跳过")

            if 'scheme_type' not in columns:
                conn.execute(text("""
                    ALTER TABLE training_plan 
                    ADD COLUMN scheme_type ENUM('ONE_SPLIT', 'TWO_SPLIT', 'THREE_SPLIT', 'FOUR_SPLIT') NULL COMMENT '分化方案（仅增肌计划）'
                """))
                print("   ✅ 新增 scheme_type 字段")
            else:
                print("   ⚠️  scheme_type 字段已存在，跳过")

            if 'cycle_rule' not in columns:
                conn.execute(text("""
                    ALTER TABLE training_plan 
                    ADD COLUMN cycle_rule VARCHAR(64) NULL COMMENT '训练循环规则（如练 3 休 1）'
                """))
                print("   ✅ 新增 cycle_rule 字段")
            else:
                print("   ⚠️  cycle_rule 字段已存在，跳过")
            
            # 修改 fitness_goal 字段约束（如果已存在则跳过）
            try:
                conn.execute(text("""
                    ALTER TABLE training_plan 
                    MODIFY COLUMN fitness_goal ENUM('FAT_LOSS', 'MUSCLE_GAIN') NULL COMMENT '健身目标'
                """))
                print("   ✅ 修改 fitness_goal 字段约束")
            except Exception as e:
                print(f"   ⚠️  fitness_goal 字段修改可能已存在：{e}")
            
            # ========== 2. 修改 session_action_item 表 ==========
            print("\n📋 修改 session_action_item 表...")
            
            columns = [col['name'] for col in inspector.get_columns('session_action_item')]
            
            if 'rest_seconds_default' not in columns:
                conn.execute(text("""
                    ALTER TABLE session_action_item 
                    ADD COLUMN rest_seconds_default INT DEFAULT 60 COMMENT '默认组间休息时间（秒）'
                """))
                print("   ✅ 新增 rest_seconds_default 字段")
            else:
                print("   ⚠️  rest_seconds_default 字段已存在，跳过")
            
            if 'weight_records' not in columns:
                conn.execute(text("""
                    ALTER TABLE session_action_item 
                    ADD COLUMN weight_records JSON NULL COMMENT '每组训练重量记录'
                """))
                print("   ✅ 新增 weight_records 字段")
            else:
                print("   ⚠️  weight_records 字段已存在，跳过")
            
            if 'duration_minutes' not in columns:
                conn.execute(text("""
                    ALTER TABLE session_action_item 
                    ADD COLUMN duration_minutes INT NULL COMMENT '有氧动作时长（分钟）'
                """))
                print("   ✅ 新增 duration_minutes 字段")
            else:
                print("   ⚠️  duration_minutes 字段已存在，跳过")

            if 'sequence_order' not in columns:
                conn.execute(text("""
                    ALTER TABLE session_action_item
                    ADD COLUMN sequence_order INT NOT NULL DEFAULT 1 COMMENT '动作项在阶段内的执行顺序'
                """))
                print("   ✅ 新增 sequence_order 字段")
            else:
                print("   ⚠️  sequence_order 字段已存在，跳过")
            
            # ========== 3. 修改 plan_session 表 ==========
            print("\n📋 修改 plan_session 表...")

            columns = [col['name'] for col in inspector.get_columns('plan_session')]

            if 'training_part' not in columns:
                conn.execute(text("""
                    ALTER TABLE plan_session
                    ADD COLUMN training_part VARCHAR(32) NULL COMMENT '训练部位分组标识（如推/腿/拉，用于区分不同训练日）'
                """))
                print("   ✅ 新增 training_part 字段")
            else:
                print("   ⚠️  training_part 字段已存在，跳过")

            # ========== 4. 创建 training_schedule 表 ==========
            print("\n📋 创建 training_schedule 表...")
            
            if 'training_schedule' not in inspector.get_table_names():
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS training_schedule (
                        schedule_id VARCHAR(64) NOT NULL COMMENT '日程唯一标识符',
                        plan_id VARCHAR(64) NOT NULL COMMENT '关联计划 ID',
                        scheduled_date DATE NOT NULL COMMENT '计划训练日期',
                        session_id VARCHAR(64) NULL COMMENT '当次训练对应的阶段 ID',
                        status ENUM('PLANNED', 'COMPLETED', 'POSTPONED', 'REST') DEFAULT 'PLANNED' COMMENT '状态',
                        postpone_count INT DEFAULT 0 COMMENT '延后次数',
                        create_time DATETIME DEFAULT NULL COMMENT '创建时间',
                        update_time DATETIME DEFAULT NULL COMMENT '更新时间',
                        PRIMARY KEY (schedule_id),
                        KEY ix_training_schedule_plan_id (plan_id),
                        KEY ix_training_schedule_scheduled_date (scheduled_date),
                        CONSTRAINT fk_schedule_plan FOREIGN KEY (plan_id) REFERENCES training_plan(plan_id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='训练日程表'
                """))
                print("   ✅ training_schedule 表创建成功")
            else:
                print("   ⚠️  training_schedule 表已存在，跳过")
            
            conn.commit()
            
            # ========== 4. 验证迁移结果 ==========
            print("\n📋 验证表结构...")
            
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
            
            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'session_action_item'
                ORDER BY ORDINAL_POSITION
            """), {"schema": settings.MYSQL_DB})
            
            print("\n   session_action_item 表字段:")
            for row in result:
                print(f"      - {row[0]}: {row[1]} - {row[2]}")

            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'plan_session'
                ORDER BY ORDINAL_POSITION
            """), {"schema": settings.MYSQL_DB})

            print("\n   plan_session 表字段:")
            for row in result:
                print(f"      - {row[0]}: {row[1]} - {row[2]}")

            if 'training_schedule' in inspector.get_table_names():
                result = conn.execute(text("""
                    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = :schema 
                    AND TABLE_NAME = 'training_schedule'
                    ORDER BY ORDINAL_POSITION
                """), {"schema": settings.MYSQL_DB})
                
                print("\n   training_schedule 表字段:")
                for row in result:
                    print(f"      - {row[0]}: {row[1]} - {row[2]}")
            
            print("\n" + "=" * 60)
            print("  ✅ 数据库迁移完成")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ 迁移失败：{e}")
        # 回滚事务
        conn.rollback()
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    migrate_plan_v2()