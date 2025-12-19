"""
创建管理员账号的脚本
使用方法: python -m src.edu_cloud.scripts.create_admin [username] [password] [email]
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.edu_cloud.common.database import SessionLocal, engine, Base
from src.edu_cloud.user.models import User
from src.edu_cloud.common.security import get_password_hash
import getpass

def create_admin(username: str = None, password: str = None, email: str = None):
    """
    创建管理员账号
    
    Args:
        username: 管理员用户名（如果为None，则提示输入）
        password: 管理员密码（如果为None，则提示输入）
        email: 管理员邮箱（可选）
    """
    # 确保数据库表已创建
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 获取用户名
        if not username:
            username = input("请输入管理员用户名: ").strip()
            if not username:
                print("错误: 用户名不能为空")
                return False
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"错误: 用户名 '{username}' 已存在")
            if existing_user.role == 'admin':
                print(f"用户 '{username}' 已经是管理员")
            else:
                # 询问是否要将现有用户升级为管理员
                response = input(f"是否要将用户 '{username}' 升级为管理员? (y/n): ").strip().lower()
                if response == 'y':
                    existing_user.role = 'admin'
                    db.commit()
                    print(f"成功: 用户 '{username}' 已升级为管理员")
                    return True
                else:
                    print("操作已取消")
                    return False
            return False
        
        # 获取密码
        if not password:
            password = getpass.getpass("请输入管理员密码: ")
            password_confirm = getpass.getpass("请再次输入密码: ")
            if password != password_confirm:
                print("错误: 两次输入的密码不一致")
                return False
            if len(password) < 6:
                print("错误: 密码长度至少为6个字符")
                return False
        
        # 获取邮箱（可选）
        if not email:
            email_input = input("请输入管理员邮箱（可选，直接回车跳过）: ").strip()
            email = email_input if email_input else None
        
        # 创建管理员用户
        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role='admin',
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"成功: 管理员账号 '{username}' 已创建")
        print(f"用户ID: {admin_user.id}")
        if email:
            print(f"邮箱: {email}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"错误: 创建管理员账号失败: {str(e)}")
        return False
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 50)
    print("创建管理员账号")
    print("=" * 50)
    
    # 从命令行参数获取信息
    username = sys.argv[1] if len(sys.argv) > 1 else None
    password = sys.argv[2] if len(sys.argv) > 2 else None
    email = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = create_admin(username, password, email)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

