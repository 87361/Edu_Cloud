"""
PyWebIO个人主页界面 - 最简版本
确保能成功启动和显示
"""
from pywebio import start_server
from pywebio.output import *
from pywebio.input import *
from pywebio.session import *

def main():
    """主函数 - 最简版本"""
    # 清除所有内容
    clear()
    
    # 设置标题
    put_html('<title>云邮教学空间</title>')
    
    # 顶部导航栏
    put_html("""
    <div style="padding: 15px; background: #fff; border-bottom: 1px solid #e0e0e0; margin-bottom: 20px;">
        <h2 style="margin: 0;">☁️ 云邮教学空间 - 个人主页</h2>
    </div>
    """)
    
    # 左侧导航栏
    put_html("""
    <div style="display: flex; gap: 20px;">
        <div style="width: 200px; background: linear-gradient(180deg, #1e3a8a 0%, #6366f1 100%); 
                    padding: 20px; color: white; border-radius: 8px;">
            <div style="padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px; margin-bottom: 10px;">
                🏠 主页
            </div>
            <div style="padding: 10px; margin: 5px 0;">📚 我的课堂</div>
            <div style="padding: 10px; margin: 5px 0;">📋 我的问卷</div>
            <div style="padding: 10px; margin: 5px 0;">📝 我的笔记</div>
        </div>
        
        <div style="flex: 1;">
    """)
    
    # 用户信息卡片
    put_html("""
    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="width: 60px; height: 60px; border-radius: 50%; background: #ccc; 
                        display: flex; align-items: center; justify-content: center; font-size: 24px;">
                👤
            </div>
            <div>
                <div style="font-weight: bold; margin-bottom: 5px;">学生</div>
                <div style="color: #666; font-size: 14px;">学生号: student1</div>
                <div style="color: #0066cc; font-size: 14px; margin-top: 5px;">去绑定邮箱</div>
            </div>
        </div>
    </div>
    """)
    
    # 统计卡片
    put_html("""
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div style="flex: 1; background: white; padding: 20px; border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
            <div style="font-size: 36px; font-weight: bold; color: #0066cc; margin-bottom: 10px;">16</div>
            <div style="color: #666;">课程</div>
        </div>
        <div style="flex: 1; background: white; padding: 20px; border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
            <div style="font-size: 36px; font-weight: bold; color: #0066cc; margin-bottom: 10px;">9</div>
            <div style="color: #666;">待办</div>
        </div>
        <div style="flex: 0 0 250px; background: white; padding: 20px; border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">📦</div>
            <div style="color: #999; font-size: 14px;">暂无更多数据</div>
        </div>
    </div>
    """)
    
    # 本学期课程
    put_html("""
    <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h3 style="margin-top: 0;">本学期课程</h3>
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1; background: #f9f9f9; border-radius: 8px; overflow: hidden;">
                <div style="height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            display: flex; align-items: center; justify-content: center; color: white; font-size: 24px;">
                    📚
                </div>
                <div style="padding: 15px;">
                    <div style="font-weight: bold; margin-bottom: 5px;">形势与政策5</div>
                    <div style="color: #666; font-size: 14px;">教师: 田凤娟</div>
                    <div style="color: #999; font-size: 12px;">马克思主义学院</div>
                </div>
            </div>
            <div style="flex: 1; background: #f9f9f9; border-radius: 8px; overflow: hidden;">
                <div style="height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            display: flex; align-items: center; justify-content: center; color: white; font-size: 24px;">
                    📚
                </div>
                <div style="padding: 15px;">
                    <div style="font-weight: bold; margin-bottom: 5px;">外国文学鉴赏</div>
                    <div style="color: #666; font-size: 14px;">教师: 于奎战</div>
                    <div style="color: #999; font-size: 12px;">人文学院</div>
                </div>
            </div>
            <div style="flex: 1; background: #f9f9f9; border-radius: 8px; overflow: hidden;">
                <div style="height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            display: flex; align-items: center; justify-content: center; color: white; font-size: 24px;">
                    📚
                </div>
                <div style="padding: 15px;">
                    <div style="font-weight: bold; margin-bottom: 5px;">Python程序设计</div>
                    <div style="color: #666; font-size: 14px;">教师: 谢坤</div>
                    <div style="color: #999; font-size: 12px;">计算机学院</div>
                </div>
            </div>
        </div>
        <div style="text-align: right; margin-top: 15px; color: #666;">
            2/6
        </div>
    </div>
    """)
    
    # 待办事项
    put_html("""
    <div style="background: white; padding: 20px; border-radius: 8px;">
        <h3 style="margin-top: 0;">待办</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 20px; color: #0066cc;">☑</div>
                <div>
                    <div style="font-weight: bold;">课程调查问卷</div>
                    <div style="color: #999; font-size: 12px;">2026-01-09 23:59截止</div>
                </div>
            </div>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 20px; color: #0066cc;">☑</div>
                <div>
                    <div style="font-weight: bold;">小组实验</div>
                    <div style="color: #999; font-size: 12px;">2025-12-28 23:59截止</div>
                </div>
            </div>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 20px; color: #0066cc;">☑</div>
                <div>
                    <div style="font-weight: bold;">02-数字练习</div>
                    <div style="color: #999; font-size: 12px;">2025-12-26 23:59截止</div>
                </div>
            </div>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 20px; color: #0066cc;">☑</div>
                <div>
                    <div style="font-weight: bold;">03-字符练习</div>
                    <div style="color: #999; font-size: 12px;">2025-12-26 23:59截止</div>
                </div>
            </div>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 20px; color: #0066cc;">☑</div>
                <div>
                    <div style="font-weight: bold;">04-序列练习</div>
                    <div style="color: #999; font-size: 12px;">2025-12-26 23:59截止</div>
                </div>
            </div>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 20px; color: #0066cc;">☑</div>
                <div>
                    <div style="font-weight: bold;">05-流程控制</div>
                    <div style="color: #999; font-size: 12px;">2025-12-26 23:59截止</div>
                </div>
            </div>
        </div>
        <div style="text-align: right; margin-top: 15px; color: #666;">
            1/2
        </div>
    </div>
    """)
    
    put_html("</div></div>")  # 关闭主内容区和flex容器
    
    # 添加一些说明文字
    put_markdown("""
    ---
    **说明**: 这是最简版本，确保能正常启动和显示。
    
    如果这个版本能正常显示，说明PyWebIO安装和基本功能正常。
    """)


if __name__ == "__main__":
    print("=" * 50)
    print("启动PyWebIO最简版本")
    print("=" * 50)
    print("访问地址: http://localhost:8080")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动PyWebIO服务器
    start_server(main, port=8080, debug=True, cdn=False)

