# test_login.py
#测试用的，现在不用管


from buptmw import BUPT_Auth

# === 填入你的真实账号密码 ===
USERNAME = ""
PASSWORD = ""
# ===========================

print("1. 正在初始化 BUPT_Auth...")
try:
    auth = {
        "username": USERNAME,
        "password": PASSWORD
    }
    user = BUPT_Auth(cas=auth)
    print("2. 初始化成功，正在尝试连接 Ucloud...")
    
    # 这一步是真正发起网络请求的地方
    ucloud = user.get_Ucloud()
    print("3. Ucloud 登录成功！Session 对象:", ucloud)
    
    # 试着访问一下
    resp = ucloud.get("https://ucloud.bupt.edu.cn/ykt-site/site/user/current")
    print("4. 测试接口返回状态码:", resp.status_code)
    print("5. 返回内容片段:", resp.text[:100])

except Exception as e:
    print("\nXXX 发生错误 XXX")
    print(f"错误类型: {type(e)}")
    print(f"错误详情: {e}")