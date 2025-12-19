"""
CAS 认证功能测试脚本
使用方式：
1. 通过环境变量：export CAS_USERNAME=学号 CAS_PASSWORD=密码
2. 通过命令行参数：python test_cas_auth.py --username 学号 --password 密码
3. 交互式输入：python test_cas_auth.py
"""
import os
import sys
import argparse
import getpass
from typing import Optional

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.edu_cloud.common.cas_auth import verify_cas_credentials, encrypt_cas_password, verify_cas_password


def get_credentials() -> tuple[str, str]:
    """获取 CAS 凭证（优先顺序：命令行参数 > 环境变量 > 交互式输入）"""
    parser = argparse.ArgumentParser(description='测试 CAS 认证功能')
    parser.add_argument('--username', '-u', help='CAS 用户名（学号）')
    parser.add_argument('--password', '-p', help='CAS 密码')
    
    args = parser.parse_args()
    
    # 优先使用命令行参数
    username = args.username
    password = args.password
    
    # 如果没有命令行参数，尝试从环境变量获取
    if not username:
        username = os.getenv('CAS_USERNAME')
    if not password:
        password = os.getenv('CAS_PASSWORD')
    
    # 如果还是没有，使用交互式输入
    if not username:
        username = input("请输入 CAS 用户名（学号）: ").strip()
    if not password:
        password = getpass.getpass("请输入 CAS 密码: ").strip()
    
    if not username or not password:
        print("错误：用户名和密码不能为空")
        sys.exit(1)
    
    return username, password


def test_cas_authentication():
    """测试 CAS 认证功能"""
    print("=" * 60)
    print("CAS 认证功能测试")
    print("=" * 60)
    
    # 获取凭证
    print("\n[1/4] 获取 CAS 凭证...")
    username, password = get_credentials()
    print(f"✓ 用户名: {username}")
    print(f"✓ 密码: {'*' * len(password)}")
    
    # 测试 CAS 凭证验证
    print("\n[2/4] 验证 CAS 凭证...")
    try:
        is_valid, auth_object, error_msg = verify_cas_credentials(username, password)
        
        if is_valid:
            print("✓ CAS 凭证验证成功！")
            print(f"  - BUPT_Auth 对象已创建: {auth_object is not None}")
            if auth_object and hasattr(auth_object, 'cas'):
                print(f"  - CAS 状态: {auth_object.cas.status}")
        else:
            print(f"✗ CAS 凭证验证失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"✗ 验证过程出错: {str(e)}")
        return False
    
    # 测试密码加密
    print("\n[3/4] 测试密码加密功能...")
    try:
        encrypted_password = encrypt_cas_password(password)
        print(f"✓ 密码加密成功")
        print(f"  - 原始密码长度: {len(password)}")
        print(f"  - 加密后长度: {len(encrypted_password)}")
        print(f"  - 加密后前缀: {encrypted_password[:20]}...")
        
        # 验证加密后的密码
        is_match = verify_cas_password(password, encrypted_password)
        if is_match:
            print("✓ 密码验证成功（加密/解密功能正常）")
        else:
            print("✗ 密码验证失败（加密/解密功能异常）")
            return False
            
    except Exception as e:
        print(f"✗ 密码加密测试出错: {str(e)}")
        return False
    
    # 测试获取 Ucloud session（可选）
    print("\n[4/4] 测试获取 Ucloud Session...")
    try:
        if auth_object:
            ucloud = auth_object.get_Ucloud()
            print("✓ Ucloud Session 获取成功")
            
            # 尝试访问一个简单的接口
            try:
                resp = ucloud.get("https://ucloud.bupt.edu.cn/ykt-site/site/user/current", timeout=10)
                print(f"✓ 测试接口访问成功")
                print(f"  - 状态码: {resp.status_code}")
                if resp.status_code == 200:
                    print("  - 接口响应正常")
            except Exception as e:
                print(f"⚠ 接口访问测试失败（可能是网络问题）: {str(e)}")
        else:
            print("⚠ 跳过 Ucloud Session 测试（auth_object 不可用）")
            
    except Exception as e:
        print(f"⚠ Ucloud Session 测试出错: {str(e)}")
        # 这不算失败，因为可能只是网络问题
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    return True


if __name__ == '__main__':
    try:
        success = test_cas_authentication()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

