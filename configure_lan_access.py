#!/usr/bin/env python3
"""
局域网访问配置工具
帮助用户快速配置客户端连接到局域网内的服务器
"""
import json
import sys
import os
from pathlib import Path

def get_config_path():
    """获取配置文件路径"""
    config_dir = Path.home() / ".edu_cloud_gui"
    config_file = config_dir / "config.json"
    return config_dir, config_file

def get_current_config():
    """获取当前配置"""
    config_dir, config_file = get_config_path()
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  读取配置文件失败: {e}")
            return {}
    return {}

def save_config(server_ip, port=5000):
    """保存配置"""
    config_dir, config_file = get_config_path()
    
    # 确保目录存在
    config_dir.mkdir(exist_ok=True)
    
    config = {
        "api_base_url": f"http://{server_ip}:{port}",
        "api_timeout": 30
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ 配置已保存到: {config_file}")
        print(f"   API地址: {config['api_base_url']}")
        return True
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False

def test_connection(server_ip, port=5000):
    """测试连接"""
    import urllib.request
    import urllib.error
    
    url = f"http://{server_ip}:{port}/health"
    print(f"\n🔍 正在测试连接: {url}")
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'EduCloud-Config-Tool/1.0')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                print(f"✅ 连接成功！")
                print(f"   服务器响应: {data}")
                return True
            else:
                print(f"⚠️  服务器返回状态码: {response.status}")
                return False
    except urllib.error.URLError as e:
        print(f"❌ 连接失败: {e}")
        print(f"   请检查：")
        print(f"   1. 服务器IP地址是否正确")
        print(f"   2. 后端服务是否正在运行")
        print(f"   3. 防火墙是否允许端口 {port}")
        print(f"   4. 客户端和服务器是否在同一局域网")
        return False
    except Exception as e:
        print(f"❌ 测试连接时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("EduCloud 局域网访问配置工具")
    print("=" * 60)
    
    # 显示当前配置
    current_config = get_current_config()
    if current_config:
        print(f"\n📋 当前配置:")
        print(f"   API地址: {current_config.get('api_base_url', '未设置')}")
    else:
        print(f"\n📋 当前配置: 未设置（使用默认值: http://localhost:5000）")
    
    # 获取服务器IP
    print(f"\n请输入服务器IP地址:")
    print(f"  示例: 192.168.1.100 或 10.129.27.34")
    
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
        print(f"  使用命令行参数: {server_ip}")
    else:
        server_ip = input("  服务器IP: ").strip()
    
    if not server_ip:
        print("❌ IP地址不能为空")
        return
    
    # 验证IP格式（简单验证）
    parts = server_ip.split('.')
    if len(parts) != 4:
        print("❌ IP地址格式不正确，应为: x.x.x.x")
        return
    
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                raise ValueError()
    except ValueError:
        print("❌ IP地址格式不正确")
        return
    
    # 获取端口（可选）
    port = 5000
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"⚠️  端口参数无效，使用默认端口 5000")
    else:
        port_input = input(f"  端口 (默认5000，直接回车使用默认值): ").strip()
        if port_input:
            try:
                port = int(port_input)
            except ValueError:
                print(f"⚠️  端口格式无效，使用默认端口 5000")
                port = 5000
    
    # 测试连接
    if test_connection(server_ip, port):
        # 保存配置
        print(f"\n💾 保存配置...")
        if save_config(server_ip, port):
            print(f"\n🎉 配置完成！")
            print(f"\n下一步:")
            print(f"  1. 启动GUI应用: python start_gui.py")
            print(f"  2. 使用新的API地址登录")
        else:
            print(f"\n❌ 配置保存失败，请手动编辑配置文件")
    else:
        # 即使连接失败，也询问是否保存配置
        print(f"\n⚠️  连接测试失败，但您仍然可以保存配置稍后使用")
        save_anyway = input("是否仍然保存配置？(y/n): ").strip().lower()
        if save_anyway == 'y':
            if save_config(server_ip, port):
                print(f"\n✅ 配置已保存，但连接测试失败")
                print(f"   请检查服务器设置后重试")
            else:
                print(f"\n❌ 配置保存失败")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

