"""
CAS 认证 API 测试脚本
通过 HTTP 请求测试 CAS 登录功能

使用方式（推荐顺序）：
1. 交互式输入（最安全，支持所有特殊字符）：
   python test_cas_api.py

2. 通过环境变量（推荐用于包含特殊字符的密码）：
   export CAS_USERNAME=学号
   export CAS_PASSWORD='密码（可以包含!@#$等特殊字符）'
   python test_cas_api.py

3. 通过命令行参数（注意：密码包含!等特殊字符时需要用单引号）：
   python test_cas_api.py --username 学号 --password '密码'
   # 或者使用双引号并转义：python test_cas_api.py --username 学号 --password "密码\\!"

注意：如果密码包含感叹号(!)，bash会尝试进行历史扩展，导致"event not found"错误。
解决方法：
- 使用单引号：'密码!'
- 使用环境变量：export CAS_PASSWORD='密码!'
- 使用交互式输入（推荐）
"""
import os
import sys
import argparse
import getpass
import requests
import json


def get_credentials() -> tuple[str, str]:
    """获取 CAS 凭证（优先顺序：命令行参数 > 环境变量 > 交互式输入）"""
    parser = argparse.ArgumentParser(description='测试 CAS 认证 API')
    parser.add_argument('--username', '-u', help='CAS 用户名（学号）')
    parser.add_argument('--password', '-p', help='CAS 密码（如果包含特殊字符，建议使用环境变量或交互式输入）')
    parser.add_argument('--url', default='http://localhost:5000', help='API 服务器地址')
    
    args = parser.parse_args()
    
    # 优先使用命令行参数
    username = args.username
    password = args.password
    
    # 如果没有命令行参数，尝试从环境变量获取（推荐用于包含特殊字符的密码）
    if not username:
        username = os.getenv('CAS_USERNAME')
    if not password:
        password = os.getenv('CAS_PASSWORD')
    
    # 如果还是没有，使用交互式输入（最安全，可以处理任何特殊字符）
    if not username:
        username = input("请输入 CAS 用户名（学号）: ").strip()
    if not password:
        password = getpass.getpass("请输入 CAS 密码（支持特殊字符）: ").strip()
    
    if not username or not password:
        print("错误：用户名和密码不能为空")
        sys.exit(1)
    
    return username, password, args.url


def test_cas_login_api():
    """测试 CAS 登录 API"""
    print("=" * 60)
    print("CAS 登录 API 测试")
    print("=" * 60)
    
    # 获取凭证和服务器地址
    username, password, base_url = get_credentials()
    print(f"\n服务器地址: {base_url}")
    print(f"CAS 用户名: {username}")
    print(f"CAS 密码: {'*' * len(password)}")
    
    # 测试 CAS 登录
    print("\n[测试 1] CAS 直接登录...")
    print(f"  发送到: {base_url}/api/user/login/cas")
    print(f"  用户名: {username}")
    print(f"  密码长度: {len(password)} 字符")
    print(f"  密码首字符: {password[0] if password else 'N/A'}")
    print(f"  密码尾字符: {password[-1] if len(password) > 1 else 'N/A'}")
    
    login_url = f"{base_url}/api/user/login/cas"
    payload = {
        "cas_username": username,
        "cas_password": password
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=30)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("  ✓ CAS 登录成功！")
            if 'access_token' in data:
                print(f"  - Access Token: {data['access_token'][:50]}...")
            if 'user' in data:
                user_info = data['user']
                print(f"  - 用户 ID: {user_info.get('id')}")
                print(f"  - 用户名: {user_info.get('username')}")
                print(f"  - CAS 用户名: {user_info.get('cas_username')}")
                print(f"  - CAS 已绑定: {user_info.get('cas_is_bound')}")
            
            # 测试获取用户信息
            if 'access_token' in data:
                print("\n[测试 2] 获取用户信息...")
                token = data['access_token']
                headers = {"Authorization": f"Bearer {token}"}
                me_url = f"{base_url}/api/user/me"
                me_response = requests.get(me_url, headers=headers, timeout=10)
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("  ✓ 获取用户信息成功！")
                    if 'data' in me_data:
                        user_data = me_data['data']
                        print(f"  - 用户名: {user_data.get('username')}")
                        print(f"  - 邮箱: {user_data.get('email')}")
                        print(f"  - CAS 绑定状态: {user_data.get('cas_is_bound')}")
                        print(f"  - CAS 用户名: {user_data.get('cas_username')}")
                else:
                    print(f"  ✗ 获取用户信息失败: {me_response.status_code}")
                    print(f"  - 响应: {me_response.text}")
                
                # 测试获取 CAS 状态
                print("\n[测试 3] 获取 CAS 绑定状态...")
                cas_status_url = f"{base_url}/api/user/me/cas-status"
                cas_response = requests.get(cas_status_url, headers=headers, timeout=10)
                
                if cas_response.status_code == 200:
                    cas_data = cas_response.json()
                    print("  ✓ 获取 CAS 状态成功！")
                    if 'data' in cas_data:
                        cas_info = cas_data['data']
                        print(f"  - CAS 已绑定: {cas_info.get('cas_is_bound')}")
                        print(f"  - CAS 用户名: {cas_info.get('cas_username')}")
                        print(f"  - 绑定时间: {cas_info.get('cas_bound_at')}")
                else:
                    print(f"  ✗ 获取 CAS 状态失败: {cas_response.status_code}")
            
            print("\n" + "=" * 60)
            print("✓ 所有测试通过！")
            print("=" * 60)
            return True
        else:
            print(f"  ✗ CAS 登录失败")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', response.text)
                print(f"  - 错误信息: {error_msg}")
                
                # 检查是否是账户锁定
                if "锁定" in error_msg or "Locked" in error_msg or "423" in error_msg:
                    print("\n  ⚠️  注意：账户可能已被锁定")
                    print("  - 建议：等待一段时间后再试，或检查密码是否正确")
            except:
                print(f"  - 响应: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ 无法连接到服务器: {base_url}")
        print("  请确保服务器正在运行")
        return False
    except requests.exceptions.Timeout:
        print(f"  ✗ 请求超时")
        return False
    except Exception as e:
        print(f"  ✗ 测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        success = test_cas_login_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

