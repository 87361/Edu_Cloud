"""作业详情界面"""
from typing import Optional
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QTextBrowser
from PyQt6.QtGui import QColor

from qfluentwidgets import (
    TransparentToolButton,
    TitleLabel,
    BodyLabel,
    SubtitleLabel,
    ElevatedCardWidget,
    PrimaryPushButton,
    PushButton,
    TextEdit,
    FluentIcon as FIF,
    InfoBar,
)

from ..models.assignment import Assignment
from ..services.assignment_service import AssignmentService
from ..services.async_service import AsyncService


class AssignmentDetailInterface(QWidget):
    """作业详情界面"""

    back_signal = pyqtSignal()  # 返回信号

    def __init__(self, parent=None):
        """
        初始化作业详情界面

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.assignment: Optional[Assignment] = None
        self.assignment_service = AssignmentService()
        self.async_service = AsyncService()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

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

        # 描述卡片（使用QTextBrowser支持HTML显示）
        self.desc_card = ElevatedCardWidget(self)
        self.desc_layout = QVBoxLayout(self.desc_card)
        self.desc_layout.setContentsMargins(20, 20, 20, 20)
        self.desc_browser = QTextBrowser(self.desc_card)
        self.desc_browser.setReadOnly(True)
        self.desc_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        self.desc_browser.setPlaceholderText("作业描述内容...")
        self.desc_browser.setMinimumHeight(200)
        self.desc_layout.addWidget(self.desc_browser)

        # 文件上传区域
        file_layout = QHBoxLayout()
        self.file_label = BodyLabel("未选择文件", self)
        self.file_label.setTextColor(QColor(150, 150, 150), QColor(150, 150, 150))
        self.select_file_btn = PushButton("选择文件", self)
        self.select_file_btn.clicked.connect(self._on_select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch(1)
        file_layout.addWidget(self.select_file_btn)

        # 输入框（文本提交，可选）
        self.input_label = SubtitleLabel("提交内容（可选）", self)
        self.text_edit = TextEdit(self)
        self.text_edit.setPlaceholderText("在此处输入你的答案（或上传文件）...")
        self.text_edit.setFixedHeight(150)

        # 提交按钮
        self.submit_btn = PrimaryPushButton("提交作业", self)
        self.submit_btn.clicked.connect(self._on_submit)
        
        self.selected_file_path: Optional[str] = None

        # 组装
        layout.addLayout(header_layout)
        layout.addWidget(self.info_lbl)
        layout.addSpacing(10)
        layout.addWidget(self.desc_card)
        layout.addSpacing(10)
        layout.addLayout(file_layout)
        layout.addSpacing(10)
        layout.addWidget(self.input_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.submit_btn)
        layout.addStretch(1)

    def _connect_signals(self) -> None:
        """连接信号"""
        self.assignment_service.assignment_loaded.connect(
            self._on_assignment_loaded
        )
        self.assignment_service.load_failed.connect(self._on_load_failed)
        self.assignment_service.submit_success.connect(self._on_submit_success)
        self.assignment_service.submit_failed.connect(self._on_submit_failed)

    def update_data(self, assignment: Assignment) -> None:
        """
        更新作业数据

        Args:
            assignment: 作业对象
        """
        self.assignment = assignment
        self.title.setText(assignment.title)
        deadline = assignment.get_deadline_display()
        self.info_lbl.setText(
            f"{assignment.course_name}  •  截止日期: {deadline}"
        )
        # 使用HTML格式显示描述（如果description是HTML，直接显示；否则作为纯文本）
        description = assignment.description or "无描述"
        if description.strip().startswith("<"):
            # 看起来是HTML格式
            self.desc_browser.setHtml(description)
        else:
            # 纯文本格式，转换为HTML显示
            from html import escape
            escaped_text = escape(description)
            # 将换行符转换为<br>
            html_text = escaped_text.replace("\n", "<br>")
            self.desc_browser.setHtml(f"<div style='font-family: Microsoft YaHei, Arial; font-size: 14px; line-height: 1.6;'>{html_text}</div>")
        self.text_edit.clear()
        self.selected_file_path = None
        self.file_label.setText("未选择文件")
        self.file_label.setTextColor(QColor(150, 150, 150), QColor(150, 150, 150))

        # 如果已提交，禁用提交按钮
        if assignment.is_submitted():
            self.submit_btn.setEnabled(False)
            self.submit_btn.setText("已提交")
            self.text_edit.setEnabled(False)
            self.select_file_btn.setEnabled(False)
        else:
            self.submit_btn.setEnabled(True)
            self.submit_btn.setText("提交作业")
            self.text_edit.setEnabled(True)
            self.select_file_btn.setEnabled(True)

    def load_assignment(self, assignment_id: int) -> None:
        """
        加载作业详情

        Args:
            assignment_id: 作业ID
        """
        def load_func():
            try:
                return self.assignment_service.load_assignment(assignment_id)
            except Exception as e:
                self.assignment_service.load_failed.emit(str(e))
                raise

        self.async_service.execute_async(
            load_func, self._on_assignment_loaded, self._on_load_failed
        )

    def _on_assignment_loaded(self, assignment: Assignment) -> None:
        """作业加载成功（从详情接口获取的完整数据）"""
        # 更新所有数据，包括完整的description
        self.update_data(assignment)

    def _on_load_failed(self, error_msg: str) -> None:
        """加载失败"""
        self.title.setText("加载失败")
        InfoBar.error("错误", error_msg, duration=2000, parent=self)

    def _on_select_file(self) -> None:
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择作业文件",
            "",
            "ZIP文件 (*.zip);;所有文件 (*.*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            file_name = Path(file_path).name
            self.file_label.setText(file_name)
            self.file_label.setTextColor(Qt.GlobalColor.white, Qt.GlobalColor.white)

    def _on_submit(self) -> None:
        """提交按钮点击"""
        if not self.assignment:
            return

        # 检查是否有文件或文本内容
        content = self.text_edit.toPlainText().strip()
        if not self.selected_file_path and not content:
            InfoBar.warning(
                "提示", "请选择文件或输入提交内容", duration=2000, parent=self
            )
            return

        # 优先使用文件上传
        if self.selected_file_path:
            self._submit_file()
        elif content:
            # 如果没有文件但有文本内容，提示用户
            InfoBar.warning(
                "提示", "请选择文件进行提交（文本提交功能待实现）", duration=2000, parent=self
            )

    def _submit_file(self) -> None:
        """提交文件"""
        if not self.selected_file_path or not self.assignment or not self.assignment.id:
            return

        # 检查文件是否存在
        if not Path(self.selected_file_path).exists():
            InfoBar.error("错误", "文件不存在，请重新选择", duration=2000, parent=self)
            return

        # 禁用按钮
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("提交中...")

        def submit_func():
            try:
                return self.assignment_service.submit_assignment(
                    self.assignment.id, self.selected_file_path
                )
            except Exception as e:
                self.assignment_service.submit_failed.emit(str(e))
                raise

        self.async_service.execute_async(
            submit_func, self._on_submit_success, self._on_submit_failed
        )

    def _on_submit_success(self) -> None:
        """提交成功"""
        InfoBar.success(
            title="提交成功",
            content="你的作业已成功上传至服务器。",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBar.ToastPosition.TOP_RIGHT,
            duration=2000,
            parent=self,
        )
        # 延迟一点返回，体验更好
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(500, self.back_signal.emit)

    def _on_submit_failed(self, error_msg: str) -> None:
        """提交失败"""
        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("提交作业")
        InfoBar.error("错误", error_msg, duration=2000, parent=self)
