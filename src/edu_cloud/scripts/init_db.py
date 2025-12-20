"""
数据库初始化脚本
用于初始化数据库表结构，运行必要的迁移，并可选择创建初始数据

使用方法:
    python -m src.edu_cloud.scripts.init_db [--skip-migrations] [--create-admin]
"""
import sys
import os
import argparse

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.edu_cloud.common.database import engine, Base, SessionLocal
from src.edu_cloud.user.models import User, TokenBlacklist
from src.edu_cloud.assignment.models import Assignment
from src.edu_cloud.course.models import Course, CourseResource
from src.edu_cloud.discussion.models import DiscussionTopic, DiscussionPost
from src.edu_cloud.notification.models import Notification

# 导入所有模型以确保它们被注册到Base.metadata
# 这些导入会触发模型的注册
import src.edu_cloud.user.models
import src.edu_cloud.assignment.models
import src.edu_cloud.course.models
import src.edu_cloud.discussion.models
import src.edu_cloud.notification.models


def init_database(skip_migrations: bool = False):
    """
    初始化数据库
    
    Args:
        skip_migrations: 是否跳过迁移脚本
    """
    print("=" * 60)
    print("数据库初始化")
    print("=" * 60)
    
    try:
        # 1. 创建所有表
        print("\n[1/3] 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建完成")
        
        # 2. 运行迁移脚本（如果需要）
        if not skip_migrations:
            print("\n[2/3] 运行数据库迁移...")
            try:
                from src.edu_cloud.scripts.migrate_add_role_field import migrate_add_role_field
                if migrate_add_role_field():
                    print("✓ role字段迁移完成")
                else:
                    print("⚠ role字段迁移跳过或失败")
            except Exception as e:
                print(f"⚠ role字段迁移出错: {str(e)}")
            
            try:
                from src.edu_cloud.scripts.migrate_add_cas_fields import migrate_database
                if migrate_database():
                    print("✓ CAS字段迁移完成")
                else:
                    print("⚠ CAS字段迁移跳过或失败")
            except Exception as e:
                print(f"⚠ CAS字段迁移出错: {str(e)}")
        else:
            print("\n[2/3] 跳过数据库迁移（--skip-migrations）")
        
        # 3. 显示数据库状态
        print("\n[3/3] 检查数据库状态...")
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            admin_count = db.query(User).filter(User.role == 'admin').count()
            assignment_count = db.query(Assignment).count()
            course_count = db.query(Course).count()
            
            print(f"✓ 数据库状态:")
            print(f"  - 用户总数: {user_count}")
            print(f"  - 管理员数: {admin_count}")
            print(f"  - 作业数: {assignment_count}")
            print(f"  - 课程数: {course_count}")
        finally:
            db.close()
        
        print("\n" + "=" * 60)
        print("✓ 数据库初始化完成！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ 数据库初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='初始化数据库')
    parser.add_argument(
        '--skip-migrations',
        action='store_true',
        help='跳过运行迁移脚本'
    )
    parser.add_argument(
        '--create-admin',
        action='store_true',
        help='创建管理员账号（交互式）'
    )
    
    args = parser.parse_args()
    
    # 初始化数据库
    success = init_database(skip_migrations=args.skip_migrations)
    
    # 如果需要，创建管理员
    if success and args.create_admin:
        print("\n" + "=" * 60)
        print("创建管理员账号")
        print("=" * 60)
        from src.edu_cloud.scripts.create_admin import create_admin
        create_admin()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

