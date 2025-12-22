"""日程表界面"""
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame

from qfluentwidgets import (
    TitleLabel,
    BodyLabel,
    CaptionLabel,
    CardWidget,
    CalendarPicker,
    PushButton,
    ScrollArea,
    FluentIcon as FIF,
)

from PyQt6.QtGui import QColor


class ScheduleItemCard(CardWidget):
    """日程表中的单节课程/事件卡片"""

    def __init__(self, time_range: str, title: str, room: str, color_stripe: str = "#0078D4", parent=None):
        """
        初始化日程项卡片

        Args:
            time_range: 时间范围，格式 "08:00-09:35"
            title: 课程/事件标题
            room: 地点
            color_stripe: 装饰色条颜色
            parent: 父组件
        """
        super().__init__(parent)
        self.setFixedHeight(80)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # 1. 左侧装饰条 (颜色区分课程类型)
        self.stripe = QFrame(self)
        self.stripe.setFixedWidth(6)
        self.stripe.setStyleSheet(
            f"background-color: {color_stripe}; "
            "border-top-left-radius: 8px; "
            "border-bottom-left-radius: 8px;"
        )

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

        self.lbl_title = BodyLabel(title, self.content_container)
        self.lbl_room = CaptionLabel(f"📍 {room}", self.content_container)

        content_layout.addWidget(self.lbl_title)
        content_layout.addWidget(self.lbl_room)

        layout.addWidget(self.stripe)
        layout.addWidget(self.time_container)
        layout.addWidget(self.content_container, 1)  # 占据剩余空间


class ScheduleInterface(QWidget):
    """日程表界面：顶部日历选择 + 底部时间轴列表"""

    def __init__(self, parent=None):
        """
        初始化日程表界面

        Args:
            parent: 父窗口
        """
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
        self.btn_today.clicked.connect(
            lambda: self.calendar_picker.setDate(QDate.currentDate())
        )

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

    def on_date_changed(self, date: QDate) -> None:
        """日期改变"""
        self.lbl_header.setText(f"{date.month()}月{date.day()}日 的日程")
        self.load_schedule(date)

    def load_schedule(self, date: QDate) -> None:
        """
        加载日程

        Args:
            date: 日期
        """
        # 清空当前列表
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        # 模拟数据逻辑 (实际应从数据库或课程数据中读取)
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
            empty_label = BodyLabel("今天没有课，好好休息吧！ 🎉", self.scroll_widget)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return

        for time, title, room, color in events:
            card = ScheduleItemCard(time, title, room, color, self.scroll_widget)
            self.scroll_layout.addWidget(card)


