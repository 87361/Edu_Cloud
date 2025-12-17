from pywebio import start_server, config
from pywebio.output import *
from pywebio.input import *
from pywebio.session import *

# ==================== 数据模拟 ====================
COURSES = [
    {'id': 1, 'title': '高级交互设计', 'category': '设计', 'teacher': '王教授', 'progress': 85, 'bg': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', 'desc': '构建以用户为中心的数字体验。'},
    {'id': 2, 'title': 'Vue.js 前端开发', 'category': '编程', 'teacher': '张讲师', 'progress': 40, 'bg': 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 'desc': '深入理解 Vue 3 组合式 API。'},
    {'id': 3, 'title': '数据结构与算法', 'category': '计算机', 'teacher': '李教授', 'progress': 10, 'bg': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)', 'desc': '掌握核心算法逻辑。'},
    {'id': 4, 'title': '数字媒体艺术', 'category': '艺术', 'teacher': '赵老师', 'progress': 60, 'bg': 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)', 'desc': '探索技术与艺术的边界。'},
]

ASSIGNMENTS = [
    {'id': 101, 'course_id': 1, 'title': '期中原型设计', 'deadline': '10月25日', 'status': 'pending', 'desc': '使用Figma完成原型。'},
    {'id': 201, 'course_id': 2, 'title': 'Todo List 开发', 'deadline': '10月24日', 'status': 'pending', 'desc': '使用 Vue 3 完成待办清单。'},
    {'id': 301, 'course_id': 3, 'title': '二叉树遍历', 'deadline': '10月28日', 'status': 'pending', 'desc': '实现前中后序遍历。'},
    {'id': 102, 'course_id': 1, 'title': '用户调研报告', 'deadline': '11月01日', 'status': 'pending', 'desc': '撰写用户画像分析。'},
]

def get_course(cid): return next((c for c in COURSES if c['id'] == cid), None)
def get_todos(): return [a for a in ASSIGNMENTS if a['status'] == 'pending']

# ==================== 样式配置 ====================
# 核心：透明遮罩按钮的样式 (替代之前的 .add_class)
OVERLAY_STYLE = "position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; z-index: 10; cursor: pointer; margin: 0; padding: 0; border: none;"

CSS = """
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
    /* 隐藏滚动条 */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    
    /* 侧边栏和卡片的基础悬停交互 */
    .sidebar-item:hover { background-color: #eff6ff; border-right: 3px solid #3b82f6; }
    .course-card-wrapper:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    
    /* 修复 PyWebIO 默认容器边距 */
    .markdown-body { box-sizing: border-box; min-width: 200px; max-width: 980px; margin: 0 auto; padding: 0; }
    .container { max-width: 100% !important; padding: 0 !important; margin: 0 !important; }
    
    /* 移除 put_scrollable 的默认边框和阴影 */
    .pywebio-scrollable { border: none !important; box-shadow: none !important; outline: none !important; }

    /* ========== 新增：隐藏滚动条的通用类 ========== */
    .no-scrollbar {
        -ms-overflow-style: none;  /* IE and Edge */
        scrollbar-width: none;  /* Firefox */
    }
    .no-scrollbar::-webkit-scrollbar {
        display: none; /* Chrome, Safari and Opera */
    }
    
    /* 隐藏右侧主内容区的滚动条 */
    .main-scroll-container {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    .main-scroll-container::-webkit-scrollbar {
        display: none;
    }
</style>
"""

# ==================== 页面渲染逻辑 ====================

def render_assignment_detail(aid):
    """渲染：作业详情"""
    assign = next((a for a in ASSIGNMENTS if a['id'] == aid), None)
    course = get_course(assign['course_id'])
    
    with use_scope('main_content', clear=True):
        # 面包屑
        put_html(f"""
        <div class="flex items-center text-sm text-gray-500 mb-6">
            <span class="cursor-pointer hover:text-blue-600" onclick="document.getElementById('btn-home').click()">课程大厅</span>
            <i class="fa-solid fa-chevron-right text-xs mx-2"></i>
            <span class="font-bold text-gray-900">作业详情</span>
        </div>
        """)
        
        # 详情卡片
        put_html(f"""
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden max-w-4xl mx-auto animate-fade-in">
            <div class="p-8 border-b border-gray-100">
                <div class="flex justify-between items-start mb-4">
                    <h1 class="text-2xl font-bold text-gray-900">{assign['title']}</h1>
                    <span class="bg-red-50 text-red-600 px-3 py-1 rounded text-sm font-medium">截止: {assign['deadline']}</span>
                </div>
                <div class="text-sm text-gray-500 mb-4">所属课程: {course['title']}</div>
                <p class="text-gray-600 leading-relaxed bg-gray-50 p-4 rounded-lg">
                    {assign['desc']}<br><br>
                    请完成代码编写并打包提交。
                </p>
            </div>
        </div>
        """)
        
        # 上传区
        put_html('<div class="max-w-4xl mx-auto mt-6 bg-white p-6 rounded-xl border border-gray-200">')
        put_html('<h3 class="font-bold mb-4 text-gray-700">提交作业</h3>')
        file_upload(label=None, placeholder="选择文件上传 (.zip)")
        put_button("确认提交", onclick=lambda: toast('提交成功', color='success')).style("margin-top: 15px;")
        put_html('</div>')

def render_course_detail(cid):
    """渲染：课程详情"""
    course = get_course(cid)
    
    with use_scope('main_content', clear=True):
        # 顶部 Banner
        put_html(f"""
        <div class="mb-6 cursor-pointer hover:text-blue-600 text-sm text-gray-500" onclick="document.getElementById('btn-home').click()">
            <i class="fa-solid fa-arrow-left"></i> 返回课程大厅
        </div>
        <div class="bg-white rounded-2xl p-8 shadow-sm mb-8 flex items-start gap-6 border border-gray-100">
            <div style="width: 80px; height: 80px; border-radius: 12px; background: {course['bg']}; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold;">
                {course['title'][0]}
            </div>
            <div class="flex-1">
                <h1 class="text-2xl font-bold mb-2 text-gray-800">{course['title']}</h1>
                <p class="text-gray-600 mb-4 text-sm">{course['desc']}</p>
                <div class="flex gap-2">
                    <span class="bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-xs">进度 {course['progress']}%</span>
                    <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-xs">{course['teacher']}</span>
                </div>
            </div>
        </div>
        <h2 class="text-lg font-bold mb-4 text-gray-800">课程作业</h2>
        """)

        # 作业列表
        for assign in ASSIGNMENTS:
            if assign['course_id'] == cid:
                # 技巧：使用 put_column 创建相对定位容器
                with put_column().style('position: relative; margin-bottom: 12px;'):
                    # 1. 渲染 HTML 内容 (视觉层)
                    put_html(f"""
                    <div class="bg-white p-4 rounded-lg border border-gray-100 hover:border-blue-300 flex justify-between items-center transition-all">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-orange-100 text-orange-500 flex items-center justify-center text-xs">
                                <i class="fa-solid fa-pen"></i>
                            </div>
                            <div>
                                <h3 class="font-bold text-gray-700 text-sm">{assign['title']}</h3>
                                <p class="text-xs text-gray-400">截止: {assign['deadline']}</p>
                            </div>
                        </div>
                        <i class="fa-solid fa-chevron-right text-gray-300"></i>
                    </div>
                    """)
                    # 2. 渲染透明按钮 (交互层) - 使用 .style(OVERLAY_STYLE) 替代 .add_class
                    put_button(" ", onclick=lambda id=assign['id']: render_assignment_detail(id)).style(OVERLAY_STYLE)

def render_dashboard():
    """渲染：课程大厅（修复版 - 使用 CSS Grid）"""
    with use_scope('main_content', clear=True):
        # 1. 顶部标题
        put_html("""
        <header class="mb-6 flex justify-between items-end">
            <div>
                <h1 class="text-2xl font-bold text-gray-900">我的课程</h1>
                <p class="text-gray-500 text-sm mt-1">本学期共修读 4 门课程</p>
            </div>
        </header>
        """)
        
        # 2. 网格容器 (The Grid Container)
        # 固定两列布局，一行显示两门课程
        put_scope('course_grid').style('display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;')
        
        with use_scope('course_grid'):
            for course in COURSES:
                # 3. 卡片容器 (Card Wrapper)
                # 使用 put_column 创建一个独立的盒子，确保 HTML 和 按钮 在同一个父级内
                # 我们给这个 column 加上 relative 定位和卡片样式
                with put_column().style('position: relative; background: white; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; transition: all 0.3s; box-shadow: 0 1px 2px rgba(0,0,0,0.05); height: 100%;'):
                    
                    # 3.1 视觉层 (HTML)
                    put_html(f"""
                        <div style="height: 100px; background: {course['bg']}; position: relative;">
                            <div class="absolute top-2 right-2 bg-white/90 backdrop-blur px-2 py-0.5 rounded text-xs font-bold text-gray-700">
                                {course['progress']}%
                            </div>
                        </div>
                        <div class="p-4">
                            <div class="text-xs font-bold text-blue-500 mb-1">{course['category']}</div>
                            <h3 class="font-bold text-base mb-1 text-gray-800">{course['title']}</h3>
                            <p class="text-xs text-gray-500 line-clamp-2 mb-3 h-8">{course['desc']}</p>
                            <div class="flex items-center text-xs text-gray-400 border-t pt-3">
                                <i class="fa-regular fa-user mr-1"></i> {course['teacher']}
                            </div>
                        </div>
                    """)
                    
                    # 3.2 交互层 (透明遮罩按钮)
                    # 这里的样式必须包含 position: absolute 且宽高 100% 才能覆盖整个卡片
                    put_button(" ", onclick=lambda c=course['id']: render_course_detail(c)).style(OVERLAY_STYLE)

def main():
    # 1. 基础配置
    set_env(title="云邮教学空间", output_animation=False)
    put_html(CSS)

    # 2. 核心布局
    with put_row(size='280px 1fr').style('height: 100vh; overflow: hidden;'):
        
        # ========= 左侧栏 (Sidebar) =========
        with put_column().style('height: 100vh; background: white; border-right: 1px solid #e5e7eb; overflow-y: auto; display: flex; flex-direction: column; z-index: 50;'):
            
            # 用户头
            put_html("""
            <div class="p-6 border-b border-gray-100 flex items-center space-x-3 sticky top-0 bg-white z-10">
                <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold shadow-md">S</div>
                <div>
                    <h2 class="font-bold text-sm text-gray-800">同学你好</h2>
                    <p class="text-xs text-gray-500">学号: 202321xxxx</p>
                </div>
            </div>
            """)
            
            # 导航按钮
            with put_column().style('position: relative; margin: 10px 15px;'):
                put_html('<div class="flex items-center space-x-3 p-3 rounded-lg sidebar-item"><i class="fa-solid fa-house"></i><span class="font-medium text-sm">课程大厅</span></div>')
                # 修复点：使用 .style(OVERLAY_STYLE)
                put_button(" ", onclick=lambda: render_dashboard()).style(OVERLAY_STYLE)
            
            # 隐藏的触发器 (供面包屑返回使用)
            put_html('<div id="btn-home" style="display:none;" onclick="document.querySelector(\'.sidebar-item\').nextElementSibling.click()"></div>')

            # 代办列表
            put_html('<div class="px-6 mt-6 mb-2 text-xs font-bold text-gray-400 uppercase">待办作业</div>')
            
            for todo in get_todos():
                course = get_course(todo['course_id'])
                with put_column().style('position: relative; margin: 0 16px 8px 16px;'):
                    put_html(f"""
                    <div class="p-3 rounded-lg bg-gray-50 border border-gray-100 relative overflow-hidden sidebar-item">
                        <div class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"></div>
                        <div class="pl-2">
                            <div class="flex justify-between items-start mb-1">
                                <span class="text-sm font-medium text-gray-700 line-clamp-1">{todo['title']}</span>
                            </div>
                            <div class="flex justify-between items-center text-xs text-gray-500">
                                <span class="truncate w-20">{course['title']}</span>
                                <span class="text-red-400">{todo['deadline']}</span>
                            </div>
                        </div>
                    </div>
                    """)
                    # 修复点：使用 .style(OVERLAY_STYLE)
                    put_button(" ", onclick=lambda id=todo['id']: render_assignment_detail(id)).style(OVERLAY_STYLE)

        # ========= 右侧栏 (Main Content) =========
        # 修改点：使用 put_column 实现无边框滚动
        put_html('<div class="main-scroll-container" style="height: 100vh; overflow-y: auto; background-color: white;">')
        put_scope('main_content').style('padding: 30px; max-width: 1200px; margin: 0 auto;')
        render_dashboard()
        put_html('</div>')

if __name__ == '__main__':
    start_server(main, port=8080, debug=True, cdn=False)