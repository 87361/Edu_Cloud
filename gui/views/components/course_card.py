"""课程卡片组件"""
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt6.QtGui import QColor

from qfluentwidgets import (
    CardWidget,
    SubtitleLabel,
    CaptionLabel,
    ProgressBar,
)

from ...models.course import Course


class CourseCard(CardWidget):
    """
    课程卡片组件 - 使用 CardWidget 获得自带的圆角、边框和阴影
    """

    clicked = pyqtSignal(Course)  # 点击信号

    def __init__(self, course: Course, progress: Optional[float] = None, color_hex: str = "#0078D4", parent=None):
        """
        初始化课程卡片

        Args:
            course: 课程对象
            progress: 进度（0.0-1.0），如果为None则显示"---"（表示没有作业）
            color_hex: 装饰色条颜色
            parent: 父组件
        """
        super().__init__(parent)
        self.course = course
        self.setFixedSize(260, 160)  # 固定卡片大小
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 布局
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(20, 20, 20, 20)

        # 1. 顶部色条 (装饰)
        self.color_strip = QFrame()
        self.color_strip.setFixedHeight(4)
        self.color_strip.setStyleSheet(
            f"background-color: {color_hex}; border-radius: 2px;"
        )

        # 2. 标题
        self.title_lbl = SubtitleLabel(course.name or "未知课程", self)
        # 3. 讲师
        teacher_text = course.teacher or "未知讲师"
        self.teacher_lbl = CaptionLabel(f"讲师: {teacher_text}", self)
        self.teacher_lbl.setTextColor(QColor(150, 150, 150), QColor(200, 200, 200))

        # 4. 进度条（根据作业完成率计算，如果没有作业则显示"---"）
        self.progress_lbl = CaptionLabel("", self)
        self.progress_bar = ProgressBar(self)
        
        if progress is None:
            # 没有作业，显示"---"
            self.progress_lbl.setText("进度 ---")
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(False)  # 隐藏进度条
        else:
            # 有作业，显示完成率
            self.progress_lbl.setText(f"进度 {int(progress*100)}%")
            self.progress_bar.setValue(int(progress * 100))
            self.progress_bar.setCustomBarColor(QColor(color_hex), QColor(color_hex))
            self.progress_bar.setVisible(True)  # 显示进度条

        # 添加到布局
        self.v_layout.addWidget(self.color_strip)
        self.v_layout.addSpacing(5)
        self.v_layout.addWidget(self.title_lbl)
        self.v_layout.addWidget(self.teacher_lbl)
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.progress_lbl)
        self.v_layout.addWidget(self.progress_bar)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 发射带参数的 clicked 信号
            self.clicked.emit(self.course)
        # 不调用父类的 mouseReleaseEvent，避免发射无参数的 clicked 信号
        # super().mouseReleaseEvent(event)

