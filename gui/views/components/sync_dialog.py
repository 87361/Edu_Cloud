"""同步作业对话框"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from qfluentwidgets import (
    MessageBoxBase,
    SubtitleLabel,
    BodyLabel,
    StrongBodyLabel,
    PasswordLineEdit,
    PrimaryPushButton,
    PushButton
)

class SyncDialog(MessageBoxBase):
    """
    同步验证对话框
    
    简化逻辑：假设用户已绑定学号，仅需输入密码进行最终确认。
    """

    # 仅需传回密码，学号通过 self.user 获取或在外部处理
    confirmed = pyqtSignal(str) 

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        # 获取学号用于展示，如果没有user对象则显示默认文本
        self.student_id = getattr(user, 'cas_username', '未知账号') if user else '未知账号'
        
        # 初始化界面
        self._setup_ui()
        
        # 设置窗口属性
        self.widget.setMinimumWidth(350)
        # 允许点击遮罩层关闭 (可选，设为True更像原生弹窗，False更强制)
        self.yesButton.setText("开始同步")
        self.cancelButton.setText("取消")

    def _setup_ui(self):
        """构建 Win11 风格的简洁 UI"""
        
        # 1. 标题 (SubtitleLabel 自带原生字体粗细和大小)
        self.title_label = SubtitleLabel("身份验证", self.widget)
        
        # 2. 提示文本容器
        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(4)
        
        # 说明文字
        description = BodyLabel("为了确保数据安全，同步教务系统数据需要验证您的密码。", self.widget)
        description.setWordWrap(True)
        
        # 显示当前绑定的账号 (StrongBodyLabel 加粗显示，强调身份)
        account_info = BodyLabel("当前绑定账号：", self.widget)
        self.account_label = StrongBodyLabel(self.student_id, self.widget)
        
        # 将账号信息横向排列
        # (这里为了布局简单，直接放在描述下方，也可以用 QHBoxLayout 放在一行)
        
        # 3. 密码输入框 (使用 PasswordLineEdit，自带小眼睛图标)
        self.password_edit = PasswordLineEdit(self.widget)
        self.password_edit.setPlaceholderText("请输入教务系统密码")
        self.password_edit.setClearButtonEnabled(True)

        # --- 组装布局 ---
        # MessageBoxBase 使用 viewLayout 来管理中间区域的内容
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(description)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(account_info)
        self.viewLayout.addWidget(self.account_label)
        self.viewLayout.addSpacing(15)
        self.viewLayout.addWidget(self.password_edit)
        self.viewLayout.addSpacing(10)

        # --- 信号绑定 ---
        # 绑定回车键直接提交
        self.password_edit.returnPressed.connect(self._on_confirm)
        
        # 覆盖父类的按钮点击事件
        self.yesButton.clicked.connect(self._on_confirm)
        self.cancelButton.clicked.connect(self.reject)

        # 自动聚焦密码框
        self.password_edit.setFocus()

    def _on_confirm(self):
        """处理确认逻辑"""
        password = self.password_edit.text().strip()

        if not password:
            # 如果密码为空，可以让输入框抖动或变红 (这里简单处理为聚焦)
            self.password_edit.setFocus()
            return

        # 发送信号
        self.confirmed.emit(password)
        self.accept()