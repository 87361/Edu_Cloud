from pywebio import start_server, config
from pywebio.output import *
from pywebio.input import *
from pywebio.session import *
import threading

# ==================== 数据模拟 (保持不变) ====================
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
    {'id': 202, 'course_id': 2, 'title': '组件库封装', 'deadline': '12月10日', 'status': 'completed', 'desc': '封装一个通用的 Button 组件。'},
]

# ==================== 全局状态管理 (保持不变) ====================
_local_storage = threading.local()

def _get_storage():
    if not hasattr(_local_storage, 'data'):
        _local_storage.data = {}
    return _local_storage.data

def get_current_course_id(): return _get_storage().get('current_course_id', None)
def set_current_course_id(cid): _get_storage()['current_course_id'] = cid
def get_current_assignment_id(): return _get_storage().get('current_assignment_id', None)
def set_current_assignment_id(aid): _get_storage()['current_assignment_id'] = aid

def get_course(cid): return next((c for c in COURSES if c['id'] == cid), None)
def get_todos(): return sorted([a for a in ASSIGNMENTS if a['status'] == 'pending'], key=lambda x: x['deadline'])
def get_assignment(aid): return next((a for a in ASSIGNMENTS if a['id'] == aid), None)

# ==================== 样式配置 ====================
CSS = """
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
    /* ... (保留你之前的滚动条样式) ... */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    .sidebar-item:hover { background-color: #eff6ff; border-right: 3px solid #3b82f6; }
    .sidebar-item:hover i { color: #3b82f6; transform: scale(1.1); }
    .course-card-wrapper:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    .markdown-body { box-sizing: border-box; min-width: 200px; max-width: 980px; margin: 0 auto; padding: 0; }
    .container { max-width: 100% !important; padding: 0 !important; margin: 0 !important; }
    .pywebio-scrollable { border: none !important; box-shadow: none !important; outline: none !important; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .main-scroll-container { -ms-overflow-style: none; scrollbar-width: none; }
    .main-scroll-container::-webkit-scrollbar { display: none; }

    /* ========== 新增：自定义上传区域样式 ========== */
    
    /* 1. 隐藏 input_group 默认的 label */
    #pywebio-scope-upload_area label { display: none; }
    
    /* 2. 将文件输入框容器变成虚线大框 */
    #pywebio-scope-upload_area .form-control {
        height: 200px;                 /* 高度撑开 */
        border: 2px dashed #cbd5e1;    /* 虚线边框 */
        background-color: #f8fafc;     /* 浅灰背景 */
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    /* 悬停效果 */
    #pywebio-scope-upload_area .form-control:hover {
        border-color: #3b82f6;
        background-color: #eff6ff;
    }
    
    /* 3. 使用伪元素添加背景图标和文字（模拟图2的效果） */
    #pywebio-scope-upload_area .form-control::after {
        content: '点击上传文件 或 拖拽文件到此处';
        font-family: system-ui, -apple-system, sans-serif;
        color: #64748b;
        font-weight: 500;
        position: absolute;
        bottom: 60px; /* 文字位置 */
        pointer-events: none; /* 让点击穿透到 input */
    }
    
    /* 添加云朵图标 (利用 FontAwesome 的 unicode) */
    #pywebio-scope-upload_area .form-control::before {
        content: '\\f093'; /* fa-upload 图标 */
        font-family: 'Font Awesome 6 Free';
        font-weight: 900;
        font-size: 40px;
        color: #94a3b8;
        position: absolute;
        top: 50px; /* 图标位置 */
        pointer-events: none;
    }

    /* 4. 这里的 input[type=file] 实际上需要透明覆盖在整个区域上 */
    #pywebio-scope-upload_area input[type="file"] {
        height: 100%;
        width: 100%;
        opacity: 0; /* 完全透明 */
        cursor: pointer;
    }

    /* 5. 定制底部按钮栏：右对齐 */
    #pywebio-scope-upload_area .pywebio-actions {
        justify-content: flex-end; /* 按钮靠右 */
        margin-top: 20px;
        padding: 0;
    }
    
    /* 6. 定制提交按钮样式 */
    #pywebio-scope-upload_area button[type="submit"] {
        background-color: #2563eb;
        border-color: #2563eb;
        padding: 8px 24px;
        border-radius: 6px;
        font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    #pywebio-scope-upload_area button[type="submit"]:hover {
        background-color: #1d4ed8;
    }
</style>
"""

# ==================== 核心修复：隐形触发器 ====================
def put_hidden_trigger(trigger_name, callback):
    """
    创建一个真正隐形的触发器。
    原理：
    1. 使用 put_scope 创建一个 div 容器，ID 会自动变成 'pywebio-scope-{trigger_name}'
    2. 使用 .style('display: none') 将这个容器完全从页面布局中移除
    3. 在容器内放入按钮
    """
    # 1. 创建容器并隐藏 (PyWebIO 会自动添加 'pywebio-scope-' 前缀)
    put_scope(trigger_name).style('display: none;')
    
    # 2. 在隐藏的容器里放入按钮
    with use_scope(trigger_name):
        put_button("trigger", onclick=callback)

# ==================== 页面渲染逻辑 ====================
def render_assignment_detail(aid):
    assign = get_assignment(aid)
    if not assign: return render_dashboard()
    
    course = get_course(assign['course_id'])
    if not course: return render_dashboard()
    
    set_current_course_id(course['id'])
    set_current_assignment_id(aid)
    
    with use_scope('main_content', clear=True):
        # 面包屑 (保持不变)
        put_html(f"""
        <div class="flex items-center text-sm text-gray-500 mb-6">
            <span class="cursor-pointer hover:text-blue-600" onclick="document.querySelector('#pywebio-scope-trigger-home-nav button').click()">课程大厅</span>
            <i class="fa-solid fa-chevron-right text-xs mx-2"></i>
            <span class="font-bold text-gray-900">作业详情</span>
        </div>
        """)
        put_hidden_trigger('trigger-home-nav', lambda: render_dashboard())

        # 详情卡片 (保持不变)
        put_html(f"""
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden max-w-4xl mx-auto animate-fade-in mb-6">
            <div class="p-8 border-b border-gray-100">
                <div class="flex justify-between items-start mb-4">
                    <h1 class="text-2xl font-bold text-gray-900">{assign['title']}</h1>
                    <span class="bg-red-50 text-red-600 px-3 py-1 rounded text-sm font-medium">截止: {assign['deadline']}</span>
                </div>
                <div class="text-sm text-gray-500 mb-4">所属课程: {course['title']}</div>
                <p class="text-gray-600 leading-relaxed bg-gray-50 p-4 rounded-lg">
                    {assign['desc']}<br><br>
                    请阅读附件中的PDF文档，并根据要求完成代码编写。最终提交一个 .zip 压缩包。
                </p>
            </div>
        </div>
        """)
        
        # === 新的提交区域 (Target UI) ===
        # 1. 渲染卡片外壳
        put_html('<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden max-w-4xl mx-auto p-8">')
        put_html('<h3 class="font-bold text-gray-800 mb-4">提交作业</h3>')
        
        # 2. 使用 scope 包裹上传区域，这样我们的 CSS 才能精准打击
        with use_scope('upload_area'):
            # 使用 input_group，使用关键字参数 inputs
            # 注意：file_upload 的第一个参数是 label（标签），name 参数指定字段名
            submission = input_group(
                inputs=[
                    # label 为空字符串，因为我们用 CSS 隐藏了它，并用伪元素重写了提示文字
                    file_upload(label="", name="file_content", accept=".zip"),
                ]
            )
        
        put_html('</div>') # 闭合卡片 div

        # === 提交后的逻辑处理 ===
        # 当用户点击"确认提交"后，代码才会继续执行到这里
        if submission and submission.get('file_content'):
            file_data = submission['file_content']
            filename = file_data['filename']
            file_size = len(file_data['content']) / 1024
            
            # 显示成功提示
            toast(f"成功提交: {filename} ({file_size:.1f} KB)", color='success')
            
            # (可选) 你可以在这里添加保存文件的逻辑
            # import os
            # os.makedirs("uploads", exist_ok=True)
            # with open(f"uploads/{filename}", "wb") as f:
            #     f.write(file_data['content'])
            
            # 刷新页面显示
            render_assignment_detail(aid)

def render_course_detail(cid):
    course = get_course(cid)
    if not course: return render_dashboard()
    
    set_current_course_id(cid)
    set_current_assignment_id(None)
    
    with use_scope('main_content', clear=True):
        # 顶部 Banner
        put_html(f"""
        <div class="mb-6 cursor-pointer hover:text-blue-600 text-sm text-gray-500" onclick="document.querySelector('#pywebio-scope-trigger-back-home button').click()">
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
        put_hidden_trigger('trigger-back-home', lambda: render_dashboard())

        # 作业列表
        for assign in ASSIGNMENTS:
            if assign['course_id'] == cid:
                assign_id = assign['id']
                # 修复：选择器加上 #pywebio-scope- 前缀
                put_html(f"""
                <div onclick="document.querySelector('#pywebio-scope-trigger-assign-{assign_id} button').click()" class="bg-white p-4 rounded-lg border border-gray-100 hover:border-blue-300 flex justify-between items-center transition-all cursor-pointer" style="margin-bottom: 12px;">
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
                put_hidden_trigger(f'trigger-assign-{assign_id}', lambda aid=assign_id: render_assignment_detail(aid))

def render_dashboard():
    set_current_course_id(None)
    set_current_assignment_id(None)
    
    with use_scope('main_content', clear=True):
        put_html("""
        <header class="mb-6 flex justify-between items-end">
            <div>
                <h1 class="text-2xl font-bold text-gray-900">我的课程</h1>
                <p class="text-gray-500 text-sm mt-1">本学期共修读 4 门课程</p>
            </div>
        </header>
        """)
        
        put_scope('course_grid').style('display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;')
        
        with use_scope('course_grid'):
            for course in COURSES:
                course_id = course['id']
                # 修复：选择器加上 #pywebio-scope- 前缀
                put_html(f"""
                    <div onclick="document.querySelector('#pywebio-scope-trigger-course-{course_id} button').click()" style="position: relative; background: white; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; transition: all 0.3s; box-shadow: 0 1px 2px rgba(0,0,0,0.05); height: 100%; cursor: pointer;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 15px -3px rgba(0,0,0,0.1)'" onmouseout="this.style.transform=''; this.style.boxShadow='0 1px 2px rgba(0,0,0,0.05)'">
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
                    </div>
                """)
                put_hidden_trigger(f'trigger-course-{course_id}', lambda cid=course_id: render_course_detail(cid))

def render_sidebar():
    """渲染左侧边栏"""
    with use_scope('sidebar', clear=True):
        put_html("""
        <div class="p-6 border-b border-gray-100 flex items-center space-x-3 sticky top-0 bg-white z-10">
            <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold shadow-md">S</div>
            <div>
                <h2 class="font-bold text-sm text-gray-800">同学你好</h2>
                <p class="text-xs text-gray-500">学号: 202321xxxx</p>
            </div>
        </div>
        """)
        
        # 导航按钮修复
        put_html('<div onclick="document.querySelector(\'#pywebio-scope-trigger-sidebar-home button\').click()" class="flex items-center space-x-3 p-3 rounded-lg sidebar-item transition-colors cursor-pointer" style="margin: 10px 15px;"><i class="fa-solid fa-house transition-transform"></i><span class="font-medium text-sm">课程大厅</span></div>')
        put_hidden_trigger('trigger-sidebar-home', lambda: render_dashboard())
        
        todos = get_todos()
        put_html(f'<div class="px-6 mt-6 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">待办作业 ({len(todos)})</div>')
        
        if not todos:
            put_html('<div class="px-6 text-xs text-gray-400">暂无待办作业</div>')
        else:
            for todo in todos:
                course = get_course(todo['course_id'])
                if not course: continue
                
                urgency_color = 'bg-blue-400'
                urgency_text_color = 'text-gray-500'
                if '10月24' in todo['deadline'] or '10月25' in todo['deadline']:
                    urgency_color = 'bg-red-500'
                    urgency_text_color = 'text-red-500 font-bold'
                elif '10月28' in todo['deadline']:
                    urgency_color = 'bg-orange-400'
                
                todo_id = todo['id']
                course_id = todo['course_id']
                # 侧边栏待办点击修复
                put_html(f"""
                <div onclick="document.querySelector('#pywebio-scope-trigger-todo-{todo_id} button').click()" class="group p-3 rounded-lg border border-transparent hover:border-blue-100 hover:bg-blue-50 relative overflow-hidden sidebar-item transition-all cursor-pointer" style="margin: 0 16px 8px 16px;">
                    <div class="absolute left-0 top-0 bottom-0 w-1 {urgency_color}"></div>
                    <div class="pl-2">
                        <div class="flex justify-between items-start mb-1">
                            <span class="text-sm font-medium line-clamp-1 group-hover:text-blue-700 text-gray-700">{todo['title']}</span>
                        </div>
                        <div class="flex justify-between items-center text-xs">
                            <span class="text-gray-500 truncate w-20">{course['title']}</span>
                            <span class="{urgency_text_color}">{todo['deadline']}</span>
                        </div>
                    </div>
                </div>
                """)
                
                def make_todo_handler(tid, cid):
                    def handler():
                        set_current_course_id(cid)
                        render_assignment_detail(tid)
                    return handler
                
                put_hidden_trigger(f'trigger-todo-{todo_id}', make_todo_handler(todo_id, course_id))

def main():
    set_env(title="云邮教学空间", output_animation=False)
    put_html(CSS)

    with put_row(size='280px 1fr').style('height: 100vh; overflow: hidden;'):
        # Sidebar
        with put_column().style('height: 100vh; background: white; border-right: 1px solid #e5e7eb; overflow-y: auto; display: flex; flex-direction: column; z-index: 50;'):
            render_sidebar()

        # Main Content
        put_html('<div class="main-scroll-container" style="height: 100vh; overflow-y: auto; background-color: white;">')
        put_scope('main_content').style('padding: 30px; max-width: 1200px; margin: 0 auto;')
        render_dashboard()
        put_html('</div>')

if __name__ == '__main__':
    start_server(main, port=8080, debug=True, cdn=False)