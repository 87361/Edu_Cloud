"""作业卡片组件"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QColor

from qfluentwidgets import (
    ElevatedCardWidget,
    BodyLabel,
    CaptionLabel,
    FluentIcon as FIF,
)


class AssignmentCard(ElevatedCardWidget):
    """作业列表项卡片组件"""

    clicked = pyqtSignal(int)  # 点击信号，传递作业ID

    def __init__(self, assignment, parent=None):
        """
        初始化作业卡片

        Args:
            assignment: Assignment对象
            parent: 父组件
        """
        super().__init__(parent)
        self.assignment = assignment
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # 标题
        title_text = (
            f"{self.assignment.course_name} - {self.assignment.title}"
        )
        self.title_label = BodyLabel(title_text, self)
        layout.addWidget(self.title_label)

        # 截止时间和分数
        deadline = self.assignment.get_deadline_display()
        score = self.assignment.score or "未评分"
        info_text = f"截止: {deadline} | 分数: {score}"
        self.info_label = CaptionLabel(info_text, self)
        self.info_label.setTextColor(QColor(150, 150, 150), QColor(150, 150, 150))
        layout.addWidget(self.info_label)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.clicked.emit(self.assignment.id)
        super().mousePressEvent(event)

