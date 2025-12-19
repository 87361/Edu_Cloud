"""
数据库迁移脚本：为User表添加role字段
如果role字段已存在，则跳过
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from sqlalchemy import text, inspect
from src.edu_cloud.common.database import engine, SessionLocal
from src.edu_cloud.user.models import User

def migrate_add_role_field():
    """添加role字段到User表"""
    db = SessionLocal()
    try:
        # 检查role字段是否已存在
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'role' in columns:
            print("role字段已存在，跳过迁移")
            return True
        
        print("开始添加role字段...")
        
        # 添加role字段，默认值为'user'
        db.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL"))
        db.commit()
        
        # 为role字段创建索引
        try:
            db.execute(text("CREATE INDEX ix_users_role ON users(role)"))
            db.commit()
        except Exception as e:
            print(f"创建索引时出错（可能已存在）: {str(e)}")
            db.rollback()
        
        print("成功: role字段已添加")
        
        # 显示当前用户统计
        total_users = db.query(User).count()
        admin_users = db.query(User).filter(User.role == 'admin').count()
        regular_users = db.query(User).filter(User.role == 'user').count()
        
        print(f"\n用户统计:")
        print(f"  总用户数: {total_users}")
        print(f"  管理员: {admin_users}")
        print(f"  普通用户: {regular_users}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"错误: 迁移失败: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("数据库迁移：添加role字段")
    print("=" * 50)
    success = migrate_add_role_field()
    sys.exit(0 if success else 1)

