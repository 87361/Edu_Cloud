import requests
from pywebio import start_server, config
from pywebio.output import *
from pywebio.input import *
from pywebio.session import *

# ----------------------------------------------------------------------
# 1. 图标资源 (SVG字符串，保持不变)
# ----------------------------------------------------------------------
ICONS = {
    "home": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px;height:20px;"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" /></svg>""",
    "book": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px;height:20px;"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>""",
    "clipboard": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px;height:20px;"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" /></svg>""",
    "pencil": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px;height:20px;"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>""",
    "star": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px;height:20px;"><path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" /></svg>""",
    "speaker": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px;height:20px;"><path stroke-linecap="round" stroke-linejoin="round" d="M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 110-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.996.946 1.828 1.909 2.296l4.718 2.36a.75.75 0 001.073-.67V4.28a.75.75 0 00-1.073-.67l-4.718 2.36c-.963.468-1.656 1.3-1.909 2.297m0 9.18a12.798 12.798 0 01-.685-9.18m11.135 12.45a2.25 2.25 0 00-2.25-2.25h-2.25a2.25 2.25 0 00-2.25 2.25v.75a2.25 2.25 0 002.25 2.25h2.25a2.25 2.25 0 002.25-2.25v-.75z" /></svg>""",
    "check": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:16px;height:16px;"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>""",
    "box": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="#e0e0e0" style="width:80px;height:80px;"><path stroke-linecap="round" stroke-linejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" /></svg>""",
    "user": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:30px;height:30px;color:#ccc;"><path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clip-rule="evenodd" /></svg>"""
}

# ----------------------------------------------------------------------
# 2. 样式定义 (CSS, 保持不变)
# ----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    body { background-color: #f4f7fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; color: #333; }
    .header-bar { background: linear-gradient(90deg, #101d52 0%, #1e3a8a 100%); color: white; height: 64px; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .sidebar-container { background: white; min-height: calc(100vh - 84px); border-radius: 12px; padding: 16px 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
    .sidebar-btn { padding: 12px 16px; color: #555; cursor: pointer; border-radius: 8px; margin-bottom: 4px; display: flex; align-items: center; gap: 12px; transition: all 0.2s ease; font-size: 14px; font-weight: 500; }
    .sidebar-btn:hover { background-color: #f0f5ff; color: #1e5eff; transform: translateX(4px); }
    .sidebar-btn.active { background-color: #e6f0ff; color: #1e5eff; font-weight: bold; }
    .card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box; border: 1px solid rgba(0,0,0,0.02); transition: transform 0.2s; }
    .card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
    .course-card { background: white; border-radius: 12px; overflow: hidden; height: 100%; border: 1px solid #eee; transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
    .course-card:hover { transform: translateY(-4px); box-shadow: 0 12px 20px rgba(0,0,0,0.08); }
    .course-cover { height: 90px; display: flex; align-items: center; justify-content: center; color: white; font-size: 32px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .todo-item { display: flex; align-items: center; background: #fff; padding: 14px; border-radius: 10px; margin-bottom: 12px; border: 1px solid #f0f0f0; transition: 0.2s; }
    .todo-item:hover { border-color: #dbeafe; background: #f8fafc; }
    .todo-icon { width: 32px; height: 32px; background: #eff6ff; color: #3b82f6; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 14px; flex-shrink: 0; }
    .text-title { font-weight: 700; font-size: 16px; color: #1f2937; margin-bottom: 4px; }
    .text-sub { color: #6b7280; font-size: 13px; }
    .stat-num { font-size: 32px; color: #2563eb; font-weight: 800; line-height: 1.2; }
    .pywebio { padding: 0 !important; }
    .btn-icon { background:transparent; border:1px solid #e5e7eb; border-radius:6px; color:#6b7280; width:24px; height:24px; display:flex; align-items:center; justify-content:center; cursor:pointer;}
    .btn-icon:hover { background:#f3f4f6; color:#111; }
</style>
"""

# 数据保持不变
MOCK_COURSES = [
    {"id": 1, "course_name": "形势与政策5", "teacher_name": "田凤娟", "department": "马克思主义学院", "color": "#e08c8c"},
    {"id": 2, "course_name": "外国文学鉴赏", "teacher_name": "于奎战", "department": "人文学院", "color": "#8cc495"},
    {"id": 3, "course_name": "Python程序设计", "teacher_name": "谢坤", "department": "计算机学院", "color": "#333333"},
    {"id": 4, "course_name": "数据结构", "teacher_name": "张教授", "department": "计算机学院", "color": "#5d75cf"},
    {"id": 5, "course_name": "计算机网络", "teacher_name": "李教授", "department": "计算机学院", "color": "#7a5ba6"},
]
MOCK_TODOS = [
    {"id": 1, "title": "课程调查问卷", "due_date": "2026-01-09"},
    {"id": 2, "title": "小组实验", "due_date": "2025-12-28"},
    {"id": 3, "title": "02-数字练习", "due_date": "2025-12-26"},
    {"id": 4, "title": "03-字符练习", "due_date": "2025-12-26"},
    {"id": 5, "title": "04-序列练习", "due_date": "2025-12-26"},
    {"id": 6, "title": "05-流程控制", "due_date": "2025-12-26"},
    {"id": 7, "title": "作业1：算法设计", "due_date": "2025-12-30"},
    {"id": 8, "title": "实验报告", "due_date": "2026-01-05"},
]

# ----------------------------------------------------------------------
# 3. 渲染组件函数 (保持不变)
# ----------------------------------------------------------------------
def render_sidebar():
    menu = [
        ("主页", "home", True), ("我的课堂", "book", False), ("我的问卷", "clipboard", False),
        ("我的笔记", "pencil", False), ("学生评教", "star", False), ("信息员", "speaker", False)
    ]
    html = '<div class="sidebar-container">'
    for title, icon, active in menu:
        cls = "sidebar-btn active" if active else "sidebar-btn"
        html += f'<div class="{cls}">{ICONS[icon]} <span>{title}</span></div>'
    html += '</div>'
    put_html(html)

def render_course_grid(courses, page=1):
    per_page = 3
    start = (page - 1) * per_page
    page_courses = courses[start:start + per_page]
    
    html = '<div style="display: flex; gap: 20px; height: 210px;">'
    for c in page_courses:
        html += f"""
        <div style="flex:1; min-width: 0;">
            <div class="course-card">
                <div class="course-cover" style="background:{c['color']};">{c['course_name'][0]}</div>
                <div style="padding: 16px;">
                    <div class="text-title" style="font-size:15px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{c['course_name']}">{c['course_name']}</div>
                    <div class="text-sub" style="margin-top:4px;">{c['teacher_name']}</div>
                    <div class="text-sub" style="font-size:12px; color:#9ca3af; margin-top:2px;">{c['department']}</div>
                </div>
            </div>
        </div>
        """
    html += '</div>'
    put_html(html)

def render_todo_grid(todos, page=1):
    per_page = 6
    start = (page - 1) * per_page
    page_todos = todos[start:start + per_page]
    
    left = page_todos[0::2]
    right = page_todos[1::2]
    
    with put_row(size="50% 50%").style("gap: 20px"):
        for col_data in [left, right]:
            with put_column():
                for t in col_data:
                    put_html(f"""
                    <div class="todo-item">
                        <div class="todo-icon">{ICONS['check']}</div>
                        <div style="flex-grow:1; min-width:0;">
                            <div class="text-title" style="font-size:14px; font-weight:600;">{t['title']}</div>
                            <div class="text-sub" style="font-size:12px; margin-top:2px;">{t['due_date']} 截止</div>
                        </div>
                    </div>""")

# ----------------------------------------------------------------------
# 4. 核心逻辑修改区域
# ----------------------------------------------------------------------

def refresh_center_area():
    """刷新中间内容区"""
    c_page = getattr(local, 'c_page', 1) or 1
    t_page = getattr(local, 't_page', 1) or 1
    
    clear('center_scope')
    with use_scope('center_scope'):
        # 【修改点1】顶部统计区：改为 3 列布局 (1fr 1fr 1fr)，限制高度并增加底部间距
        with put_row(size="1fr 1fr 1fr").style("gap: 20px; margin-bottom: 32px;"):
            # 1.1 个人信息卡 - 限制高度和内容
            put_html(f"""
            <div class="card" style="display:flex; align-items:center; height: 160px; overflow: hidden; padding: 16px;">
                <div style="width:60px; height:60px; background:#f3f4f6; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-right:16px; flex-shrink: 0;">
                    {ICONS['user']}
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div class="text-title" style="font-size:18px; line-height:1.3;">张三 <span style="font-size:11px; font-weight:normal; background:#e0e7ff; color:#3730a3; padding:2px 6px; border-radius:4px; margin-left:6px;">学生</span></div>
                    <div class="text-sub" style="margin-top:4px; font-size:12px;">学号: 202321xxxx</div>
                    <a href="#" style="font-size:12px; color:#2563eb; text-decoration:none; display:inline-block; margin-top:4px;">去绑定邮箱 &rarr;</a>
                </div>
            </div>""")
            
            # 1.2 课程统计卡 - 限制高度
            put_html(f"""
            <div class="card" style="display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; height: 160px; padding: 16px;">
                <div class="stat-num" style="font-size:28px;">{len(MOCK_COURSES)}</div>
                <div class="text-sub" style="font-size:13px; margin-top:4px;">本学期课程</div>
            </div>""")

            # 【修改点2】新增：待办统计卡 - 限制高度
            put_html(f"""
            <div class="card" style="display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; height: 160px; padding: 16px;">
                <div class="stat-num" style="color: #d97706; font-size:28px;">{len(MOCK_TODOS)}</div>
                <div class="text-sub" style="font-size:13px; margin-top:4px;">待办事项</div>
            </div>""")

        # 2. 课程列表区 (保持不变)
        with put_column().style("background:white; border-radius:12px; padding:24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);"):
            with put_row().style("align-items: center; justify-content: space-between; margin-bottom: 20px;"):
                put_html('<div class="text-title" style="font-size:18px;">本学期课程</div>')
                with put_row().style("width: auto; gap: 8px; align-items: center;"):
                    put_text(f"{c_page}/{max(1, (len(MOCK_COURSES)+2)//3)}").style("color:#9ca3af; font-size: 13px;")
                    put_button('<', onclick=lambda: change_page('c', -1), color='light', small=True).style("padding: 2px 8px;")
                    put_button('>', onclick=lambda: change_page('c', 1), color='light', small=True).style("padding: 2px 8px;")
            render_course_grid(MOCK_COURSES, c_page)

        # 3. 待办事项区 (保持不变)
        with put_column().style("background:white; border-radius:12px; padding:24px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);"):
            with put_row().style("align-items: center; justify-content: space-between; margin-bottom: 20px;"):
                put_html(f'<div class="text-title" style="font-size:18px;">待办事项 <span style="background:#fee2e2; color:#b91c1c; font-size:12px; padding:2px 8px; border-radius:10px; vertical-align:middle;">{len(MOCK_TODOS)}</span></div>')
                with put_row().style("width: auto; gap: 8px; align-items: center;"):
                    put_text(f"{t_page}/{max(1, (len(MOCK_TODOS)+5)//6)}").style("color:#9ca3af; font-size: 13px;")
                    put_button('<', onclick=lambda: change_page('t', -1), color='light', small=True).style("padding: 2px 8px;")
                    put_button('>', onclick=lambda: change_page('t', 1), color='light', small=True).style("padding: 2px 8px;")
            render_todo_grid(MOCK_TODOS, t_page)

def change_page(type, delta):
    if type == 'c':
        curr = getattr(local, 'c_page', 1) or 1
        total = (len(MOCK_COURSES) + 2) // 3
        local.c_page = max(1, min(total, curr + delta))
    else:
        curr = getattr(local, 't_page', 1) or 1
        total = (len(MOCK_TODOS) + 5) // 6
        local.t_page = max(1, min(total, curr + delta))
    refresh_center_area()

# ----------------------------------------------------------------------
# 5. 主入口布局修改
# ----------------------------------------------------------------------
@config(title="云邮教学空间 Pro", theme="yeti")
def main():
    if not hasattr(local, 'c_page'): local.c_page = 1
    if not hasattr(local, 't_page'): local.t_page = 1
    
    put_html(CUSTOM_CSS)
    
    # 顶部导航 (保持不变)
    put_html(f"""
    <div class="header-bar">
        <div style="font-size: 18px; font-weight: 700; display:flex; align-items:center; gap:10px;">
            {ICONS['book']} 云邮教学空间
        </div>
        <div style="display: flex; gap: 24px; align-items: center; font-size: 14px; opacity:0.9;">
            <span>📅 2025秋季</span>
            <span>🔔</span>
            <div style="display:flex; align-items:center; gap:8px; background:rgba(255,255,255,0.1); padding:4px 12px; border-radius:20px;">
                <div style="width:24px; height:24px; background:white; border-radius:50%;"></div>
                <span>学生 ▼</span>
            </div>
        </div>
    </div>
    """)

    # 【修改点3】核心布局重构：明确的三栏结构
    # size="200px 1fr 240px": 左侧固定200px，右侧固定240px，中间自适应占满剩余空间
    # align-items: stretch: 确保三列高度自动对齐
    with put_row(size="200px 1fr 240px").style("max-width: 1440px; margin: 24px auto; padding: 0 24px; align-items: stretch; gap: 24px;"):
        
        # 左栏：侧边栏
        with put_column():
            render_sidebar()

        # 中栏：核心内容区
        with put_column():
            put_scope('center_scope')
            refresh_center_area()

        # 右栏：访问历史
        # 移除固定高度，依靠 stretch 和 .card 的 height:100% 自动撑开
        with put_column():
            put_html(f"""
            <div class="card" style="text-align: center; display:flex; flex-direction:column;">
                <div class="text-title" style="text-align: left; margin-bottom: 60px;">访问历史</div>
                <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center; align-items:center; opacity:0.6;">
                    {ICONS['box']}
                    <div class="text-sub" style="margin-top:20px;">暂无更多数据</div>
                </div>
            </div>
            """)

if __name__ == "__main__":
    start_server(main, port=8080, debug=True)