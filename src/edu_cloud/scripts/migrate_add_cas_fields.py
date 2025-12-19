"""
数据库迁移脚本：添加 CAS 绑定相关字段
运行此脚本将为 users 表添加 CAS 相关字段
"""
import sqlite3
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.edu_cloud.common.config import settings

def migrate_database():
    """添加 CAS 相关字段到 users 表"""
    # 从 database_url 中提取数据库路径
    # SQLite URL 格式: sqlite:///./app.db
    db_path = settings.database_url.replace('sqlite:///', '').replace('./', '')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        print("首次运行，表将在应用启动时自动创建")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations = []
        
        # 添加 cas_username 字段
        if 'cas_username' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN cas_username VARCHAR")
            migrations.append("CREATE INDEX IF NOT EXISTS ix_users_cas_username ON users(cas_username)")
        
        # 添加 cas_password_encrypted 字段
        if 'cas_password_encrypted' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN cas_password_encrypted VARCHAR")
        
        # 添加 cas_bound_at 字段
        if 'cas_bound_at' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN cas_bound_at DATETIME")
        
        # 添加 cas_is_bound 字段
        if 'cas_is_bound' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN cas_is_bound BOOLEAN DEFAULT 0")
        
        if migrations:
            print(f"开始执行 {len(migrations)} 个迁移...")
            for migration in migrations:
                print(f"执行: {migration}")
                cursor.execute(migration)
            
            conn.commit()
            print("迁移完成！")
        else:
            print("所有字段已存在，无需迁移")
            
    except sqlite3.Error as e:
        conn.rollback()
        print(f"迁移失败: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("CAS 字段迁移脚本")
    print("=" * 50)
    migrate_database()

