"""
启动脚本：同时运行Flask API和PyWebIO界面
"""
import subprocess
import sys
import time
import os
from threading import Thread

def start_flask():
    """启动Flask API服务器"""
    print("正在启动Flask API服务器...")
    subprocess.run([sys.executable, "main.py"])

def start_pywebio():
    """启动PyWebIO界面服务器"""
    print("正在启动PyWebIO界面服务器...")
    time.sleep(2)  # 等待Flask启动
    subprocess.run([sys.executable, "web_ui.py"])

if __name__ == "__main__":
    print("=" * 50)
    print("云邮教学空间 - 启动服务")
    print("=" * 50)
    print("\nFlask API服务器: http://localhost:5000")
    print("PyWebIO界面: http://localhost:8080")
    print("\n按 Ctrl+C 停止服务\n")
    
    # 在后台线程启动Flask
    flask_thread = Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # 在主线程启动PyWebIO（这样Ctrl+C可以正确停止）
    try:
        start_pywebio()
    except KeyboardInterrupt:
        print("\n\n正在停止服务...")
        sys.exit(0)



