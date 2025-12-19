"""
直接测试 BUPT_Auth，不通过 API
用于调试 CAS 认证问题
"""
import sys
import getpass
from buptmw import BUPT_Auth

def test_direct():
    print("=" * 60)
    print("直接测试 BUPT_Auth")
    print("=" * 60)
    
    # 获取凭证
    username = input("请输入 CAS 用户名（学号）: ").strip()
    password = getpass.getpass("请输入 CAS 密码: ").strip()
    
    print(f"\n用户名: {username}")
    print(f"密码长度: {len(password)}")
    print(f"密码首字符: {repr(password[0]) if password else 'N/A'}")
    print(f"密码尾字符: {repr(password[-1]) if len(password) > 1 else 'N/A'}")
    print(f"密码完整内容（调试用）: {repr(password)}")
    
    print("\n正在初始化 BUPT_Auth...")
    try:
        auth = BUPT_Auth(cas={"username": username, "password": password})
        print("✓ BUPT_Auth 对象创建成功")
        
        # 检查 CAS 状态
        print(f"\n检查 CAS 状态...")
        print(f"  auth.cas 存在: {hasattr(auth, 'cas')}")
        
        if hasattr(auth, 'cas'):
            print(f"  auth.cas.status: {auth.cas.status}")
            print(f"  auth.cas.status 类型: {type(auth.cas.status)}")
            
            # 尝试获取更多信息
            if hasattr(auth.cas, 'message'):
                print(f"  auth.cas.message: {auth.cas.message}")
            if hasattr(auth.cas, 'error'):
                print(f"  auth.cas.error: {auth.cas.error}")
            if hasattr(auth.cas, '__dict__'):
                print(f"  auth.cas 所有属性: {dir(auth.cas)}")
            
            if auth.cas.status is True:
                print("\n✓ CAS 认证成功！")
                
                # 尝试获取 Ucloud
                print("\n尝试获取 Ucloud Session...")
                try:
                    ucloud = auth.get_Ucloud()
                    print("✓ Ucloud Session 获取成功")
                    
                    # 测试访问
                    resp = ucloud.get("https://ucloud.bupt.edu.cn/ykt-site/site/user/current", timeout=10)
                    print(f"✓ 测试接口访问成功，状态码: {resp.status_code}")
                    
                except Exception as e:
                    print(f"✗ Ucloud Session 获取失败: {e}")
            else:
                print(f"\n✗ CAS 认证失败")
                print(f"  状态: {auth.cas.status}")
        else:
            print("✗ 无法访问 auth.cas 属性")
            
    except Exception as e:
        print(f"\n✗ 发生错误")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        test_direct()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)

