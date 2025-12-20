import sys
import os
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QStackedWidget,
)
from PyQt6.QtGui import QColor, QIcon

from PyQt6.QtCore import QUrl, QDate
from PyQt6.QtGui import QDesktopServices
from qfluentwidgets import (
    CalendarPicker, PushButton, ToolButton, 
    SettingCardGroup, SwitchSettingCard, OptionsSettingCard, HyperlinkCard, PrimaryPushSettingCard,
    ExpandLayout, qconfig
)

# 先创建 QApplication，避免 Fluent 组件内部提前构造 QWidget 时出现错误
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
app = QApplication(sys.argv)

# 引入 Fluent Widgets 组件（此时 QApplication 已存在）
from qfluentwidgets import (  # noqa: E402
    FluentWindow,
    SubtitleLabel,
    TitleLabel,
    BodyLabel,
    CaptionLabel,
    CardWidget,
    ElevatedCardWidget,
    ProgressBar,
    PrimaryPushButton,
    TextEdit,
    ScrollArea,
    FlowLayout,
    InfoBar,
    TransparentToolButton,
    FluentIcon as FIF,
    setTheme,
    Theme,
)

# 设置主题依赖于已创建的 QApplication
setTheme(Theme.DARK)

class CourseCard(CardWidget):
    """
    课程卡片组件 - 使用 CardWidget 获得自带的圆角、边框和阴影
    """
    def __init__(self, title, teacher, progress, color_hex, parent=None):
        super().__init__(parent)
        self.setFixedSize(260, 160) # 固定卡片大小

        # 布局
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(20, 20, 20, 20)

        # 1. 顶部色条 (装饰)
        self.color_strip = QFrame()
        self.color_strip.setFixedHeight(4)
        self.color_strip.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
        
        # 2. 标题
        self.title_lbl = SubtitleLabel(title, self)
        # 3. 讲师
        self.teacher_lbl = CaptionLabel(f"讲师: {teacher}", self)
        self.teacher_lbl.setTextColor(QColor(150, 150, 150), QColor(200, 200, 200))
        
        # 4. 进度条
        self.progress_lbl = CaptionLabel(f"进度 {int(progress*100)}%", self)
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setValue(int(progress * 100))
        self.progress_bar.setCustomBarColor(QColor(color_hex), QColor(color_hex))

        # 添加到布局
        self.v_layout.addWidget(self.color_strip)
        self.v_layout.addSpacing(5)
        self.v_layout.addWidget(self.title_lbl)
        self.v_layout.addWidget(self.teacher_lbl)
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.progress_lbl)
        self.v_layout.addWidget(self.progress_bar)

class AssignmentDetailView(QWidget):
    """
    作业详情与提交页面
    """
    back_signal = pyqtSignal() # 返回信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)
        self.v_layout.setSpacing(15)

        # 顶部：返回按钮 + 标题
        header_layout = QHBoxLayout()
        self.back_btn = TransparentToolButton(FIF.RETURN, self)
        self.back_btn.clicked.connect(self.back_signal.emit)
        self.title = TitleLabel("作业标题", self)
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title)
        header_layout.addStretch(1)

        self.info_lbl = BodyLabel("课程信息 | DDL", self)
        self.info_lbl.setTextColor(QColor(120, 120, 120), QColor(180, 180, 180))

        # 描述卡片
        self.desc_card = ElevatedCardWidget(self)
        self.desc_layout = QVBoxLayout(self.desc_card)
        self.desc_lbl = BodyLabel("作业描述内容...", self.desc_card)
        self.desc_lbl.setWordWrap(True)
        self.desc_layout.addWidget(self.desc_lbl)

        # 输入框
        self.input_label = SubtitleLabel("提交内容", self)
        self.text_edit = TextEdit(self)
        self.text_edit.setPlaceholderText("在此处输入你的答案...")
        self.text_edit.setFixedHeight(200)

        # 提交按钮
        self.submit_btn = PrimaryPushButton("提交作业", self)
        self.submit_btn.clicked.connect(self.on_submit)

        # 组装
        self.v_layout.addLayout(header_layout)
        self.v_layout.addWidget(self.info_lbl)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.desc_card)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.input_label)
        self.v_layout.addWidget(self.text_edit)
        self.v_layout.addWidget(self.submit_btn)
        self.v_layout.addStretch(1)

    def update_data(self, data):
        self.title.setText(data['task'])
        self.info_lbl.setText(f"{data['course']}  •  截止日期: {data['ddl']}")
        self.desc_lbl.setText(data['desc'])
        self.text_edit.clear()

    def on_submit(self):
        # 弹出现代化提示框
        InfoBar.success(
            title='提交成功',
            content='你的作业已成功上传至服务器。',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBar.ToastPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        # 延迟一点返回，体验更好
        self.back_signal.emit()


class WorkspaceInterface(QWidget):
    """
    核心工作区：包含左侧作业列表 + 右侧内容区
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 主布局：水平分割
        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(0)

        # --- 左侧栏：作业列表 ---
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(280)
        self.left_panel.setStyleSheet("background-color: transparent; border-right: 1px solid rgba(255, 255, 255, 0.1);")
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(10, 20, 10, 20)
        
        self.left_title = SubtitleLabel("待办作业", self.left_panel)
        self.left_layout.addWidget(self.left_title)
        self.left_layout.addSpacing(10)

        # 作业列表滚动区
        self.task_scroll = ScrollArea(self.left_panel)
        self.task_scroll.setStyleSheet("background: transparent; border: none;")
        self.task_container = QWidget()
        self.task_v_layout = QVBoxLayout(self.task_container)
        self.task_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.task_scroll.setWidget(self.task_container)
        self.task_scroll.setWidgetResizable(True)
        self.left_layout.addWidget(self.task_scroll)

        # --- 右侧栏：使用 StackedWidget 切换 课程墙/详情页 ---
        self.right_stack = QStackedWidget()
        
        # 页面 1: 课程瀑布流
        self.course_page = QWidget()
        self.course_scroll = ScrollArea(self.course_page)
        self.course_scroll.setWidgetResizable(True)
        self.course_scroll.setStyleSheet("background: transparent; border: none;")
        
        self.course_container = QWidget()
        # 关键：使用 FlowLayout 实现瀑布流
        self.flow_layout = FlowLayout(self.course_container, needAni=True) 
        self.flow_layout.setContentsMargins(30, 30, 30, 30)
        self.flow_layout.setVerticalSpacing(20)
        self.flow_layout.setHorizontalSpacing(20)
        
        self.course_scroll.setWidget(self.course_container)
        
        # 将 scroll 放入 course_page 的布局
        course_layout = QVBoxLayout(self.course_page)
        course_layout.setContentsMargins(0,0,0,0)
        course_layout.addWidget(self.course_scroll)

        # 页面 2: 详情页
        self.detail_page = AssignmentDetailView()
        self.detail_page.back_signal.connect(self.show_course_wall)

        self.right_stack.addWidget(self.course_page)
        self.right_stack.addWidget(self.detail_page)

        self.h_layout.addWidget(self.left_panel)
        self.h_layout.addWidget(self.right_stack)

        # --- 加载数据 ---
        self.load_data()

    def load_data(self):
        # 模拟课程数据
        courses = [
            ("高等数学", "Prof. Wang", 0.75, "#0078D4"),
            ("计算机科学导论", "Dr. Smith", 0.45, "#107C10"),
            ("Python 程序设计", "Guido", 0.90, "#FFB900"),
            ("线性代数", "Dr. Li", 0.20, "#E81123"),
            ("数字电路", "Prof. Chen", 0.60, "#B4009E"),
            ("机器学习基础", "Andrew", 0.10, "#008272"),
        ]
        
        for c in courses:
            card = CourseCard(*c)
            self.flow_layout.addWidget(card)

        # 模拟作业数据
        assignments = [
             {"id": 1, "course": "高等数学", "task": "微积分 Chapter 3", "ddl": "10-25", "desc": "完成第三章所有偶数习题。"},
             {"id": 2, "course": "计算机科学", "task": "Lab 2: 二进制", "ddl": "10-26", "desc": "编写进制转换器。"},
             {"id": 3, "course": "Python", "task": "爬虫大作业", "ddl": "11-01", "desc": "爬取任意网站前10条数据。"},
        ]

        for task in assignments:
            # 使用 ElevatedCardWidget 作为列表项，增加质感
            item_card = ElevatedCardWidget()
            item_card.setFixedHeight(70)
            item_card.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # 列表项布局
            layout = QVBoxLayout(item_card)
            layout.setContentsMargins(15, 10, 15, 10)
            
            t_lbl = BodyLabel(task["task"], item_card)
            c_lbl = CaptionLabel(f"{task['course']} | {task['ddl']}", item_card)
            c_lbl.setTextColor(QColor(150,150,150), QColor(150,150,150))
            
            layout.addWidget(t_lbl)
            layout.addWidget(c_lbl)

            # 点击事件绑定
            # 注意：PyQt 中 connect 需要用闭包处理循环变量
            item_card.mouseReleaseEvent = lambda event, t=task: self.show_detail(t)
            
            self.task_v_layout.addWidget(item_card)

    def show_detail(self, task_data):
        self.detail_page.update_data(task_data)
        # 切换堆叠页面动画
        self.right_stack.setCurrentIndex(1)

    def show_course_wall(self):
        self.right_stack.setCurrentIndex(0)

class ScheduleItemCard(CardWidget):
    """
    日程表中的单节课程/事件卡片
    """
    def __init__(self, time_range, title, room, color_stripe="#0078D4", parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)  # 修复：设置完整的边距
        layout.setSpacing(15)

        # 1. 左侧装饰条 (颜色区分课程类型)
        self.stripe = QFrame(self)
        self.stripe.setFixedWidth(6)
        self.stripe.setStyleSheet(f"background-color: {color_stripe}; border-top-left-radius: 8px; border-bottom-left-radius: 8px;")
        
        # 2. 时间区域
        self.time_container = QWidget(self)
        self.time_container.setFixedWidth(100)
        time_layout = QVBoxLayout(self.time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        start_time, end_time = time_range.split('-')
        self.lbl_start = BodyLabel(start_time, self.time_container)
        self.lbl_start.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.lbl_end = CaptionLabel(end_time, self.time_container)
        self.lbl_end.setTextColor(QColor(150, 150, 150), QColor(160, 160, 160))
        
        time_layout.addWidget(self.lbl_start)
        time_layout.addWidget(self.lbl_end)

        # 3. 内容区域
        self.content_container = QWidget(self)
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.lbl_title = SubtitleLabel(title, self.content_container)
        self.lbl_room = CaptionLabel(f"📍 {room}", self.content_container)
        
        content_layout.addWidget(self.lbl_title)
        content_layout.addWidget(self.lbl_room)

        # 4. 右侧状态按钮 (例如签到)
        self.btn_action = ToolButton(FIF.CHECKBOX, self)
        self.btn_action.setToolTip("标记为已完成")

        layout.addWidget(self.stripe)
        layout.addWidget(self.time_container)
        layout.addWidget(self.content_container, 1) # 占据剩余空间
        layout.addWidget(self.btn_action)


class ScheduleInterface(QWidget):
    """
    日程表界面：顶部日历选择 + 底部时间轴列表
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)
        self.v_layout.setSpacing(20)

        # --- 顶部控制栏 ---
        top_bar = QHBoxLayout()
        
        self.lbl_header = TitleLabel("今日日程", self)
        
        # 日历选择器
        self.calendar_picker = CalendarPicker(self)
        self.calendar_picker.setText("选择日期")
        self.calendar_picker.setDate(QDate.currentDate())
        self.calendar_picker.dateChanged.connect(self.on_date_changed)
        
        # 回到今天按钮
        self.btn_today = PushButton("回到今天", self)
        self.btn_today.clicked.connect(lambda: self.calendar_picker.setDate(QDate.currentDate()))

        top_bar.addWidget(self.lbl_header)
        top_bar.addStretch(1)
        top_bar.addWidget(self.calendar_picker)
        top_bar.addWidget(self.btn_today)

        # --- 日程列表滚动区 ---
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.v_layout.addLayout(top_bar)
        self.v_layout.addWidget(self.scroll_area)

        # 初始化加载
        self.load_schedule(QDate.currentDate())

    def on_date_changed(self, date):
        self.lbl_header.setText(f"{date.month()}月{date.day()}日 的日程")
        self.load_schedule(date)

    def load_schedule(self, date):
        # 清空当前列表
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 模拟数据逻辑 (实际应从数据库读取)
        # 这里做一个简单的奇偶判断来模拟不同日期的课程
        if date.day() % 2 == 0:
            events = [
                ("08:00-09:35", "高等数学 (Calculus)", "3-201 阶梯教室", "#0078D4"),
                ("10:00-11:35", "大学英语 IV", "5-102 语音室", "#EA005E"),
                ("14:00-16:00", "游泳课", "北区体育馆", "#00CC6A"),
            ]
        else:
            events = [
                ("09:00-11:00", "Python 程序设计", "信息楼 Lab-4", "#FFB900"),
                ("13:30-15:05", "线性代数", "3-105", "#E81123"),
                ("19:00-21:00", "ACM 集训队训练", "科技楼 505", "#8E8CD8"),
            ]
            
        if not events:
            # 空状态
            self.scroll_layout.addWidget(BodyLabel("今天没有课，好好休息吧！ 🎉", self))
            return

        for time, title, room, color in events:
            card = ScheduleItemCard(time, title, room, color)
            self.scroll_layout.addWidget(card)


class SettingInterface(ScrollArea):
    """
    设置界面：继承自 ScrollArea 以支持长页面
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scroll_widget = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widget)
        
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)
        self.setStyleSheet("background: transparent; border: none;")

        # --- 1. 个性化设置组 ---
        self.group_personal = SettingCardGroup("个性化", self.scroll_widget)
        
        # 主题切换
        self.theme_card = OptionsSettingCard(
            qconfig.themeMode,
            FIF.BRUSH,
            "应用主题",
            "切换深色或浅色模式",
            texts=["浅色", "深色", "跟随系统"],
            parent=self.group_personal
        )
        self.theme_card.optionChanged.connect(self.on_theme_changed)

        # 缩放比例 (仅演示 UI，不做实际逻辑)
        self.zoom_card = OptionsSettingCard(
            qconfig.themeMode, # 这里仅借用配置项演示
            FIF.ZOOM_IN,
            "界面缩放",
            "调整界面显示大小",
            texts=["100%", "125%", "150%"],
            parent=self.group_personal
        )
        self.group_personal.addSettingCard(self.theme_card)
        self.group_personal.addSettingCard(self.zoom_card)

        # --- 2. 关于 ---
        self.group_about = SettingCardGroup("关于", self.scroll_widget)
        
        self.help_card = HyperlinkCard(
            "https://github.com/zhiyiYo/PyQt-Fluent-Widgets",
            "打开帮助文档",
            FIF.HELP,
            "帮助与反馈",
            "发现 Bug 或有新功能建议？",
            self.group_about
        )
        
        self.about_card = PrimaryPushSettingCard(
            "检查更新",
            FIF.INFO,
            "关于 Student Space",
            "当前版本：v1.2.0 Beta",
            self.group_about
        )
        self.about_card.clicked.connect(lambda: InfoBar.info("检查更新", "当前已是最新版本", duration=2000, parent=self))

        self.group_about.addSettingCard(self.help_card)
        self.group_about.addSettingCard(self.about_card)

        # 添加到布局
        self.expand_layout.setContentsMargins(30, 30, 30, 30)
        self.expand_layout.setSpacing(20)
        self.expand_layout.addWidget(self.group_personal)
        self.expand_layout.addWidget(self.group_about)

    def on_theme_changed(self, value):
        # 实时切换主题逻辑
        if value.text() == "浅色":
            setTheme(Theme.LIGHT)
        elif value.text() == "深色":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.AUTO)


class MainWindow(FluentWindow):
    """
    主窗口框架
    """
    def __init__(self):
        super().__init__()
        
        # 1. 窗口基础设置
        self.setWindowTitle("Student Space Pro")
        self.resize(1200, 800)
        
        # 开启 Mica 特效 (Windows 11 有效)
        self.windowEffect.setMicaEffect(self.winId())

        # 2. 创建子界面
        self.workspace = WorkspaceInterface(self)
        self.schedule_interface = ScheduleInterface(self)
        self.setting_interface = SettingInterface(self)

        # 设置 objectName（必须，否则 addSubInterface 会报错）
        self.workspace.setObjectName("workspace")
        self.schedule_interface.setObjectName("schedule")
        self.setting_interface.setObjectName("setting")
        
        # 3. 添加到左侧导航栏
        self.addSubInterface(self.workspace, FIF.EDUCATION, "我的课业")
        self.addSubInterface(self.schedule_interface, FIF.CALENDAR, "日程表")
        self.addSubInterface(self.setting_interface, FIF.SETTING, "设置")

        # 默认选中第一个
        self.navigationInterface.setCurrentItem(self.workspace.objectName())

if __name__ == '__main__':
    # 显示主窗口并进入事件循环
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
