"""设置界面"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import (
    ScrollArea,
    SettingCardGroup,
    OptionsSettingCard,
    HyperlinkCard,
    PrimaryPushSettingCard,
    PushSettingCard,
    ExpandLayout,
    FluentIcon as FIF,
    InfoBar,
    setTheme,
    Theme,
    qconfig,
    MessageBox,
    ConfigItem,
)


class SettingInterface(ScrollArea):
    """设置界面：继承自 ScrollArea 以支持长页面"""

    logout_requested = pyqtSignal()  # 登出请求信号

    def __init__(self, parent=None):
        """
        初始化设置界面

        Args:
            parent: 父窗口
        """
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
        self.group_personal.addSettingCard(self.theme_card)

        # 缩放比例 - 暂时移除，避免与主题配置项冲突
        # 如果需要缩放功能，需要正确创建独立的 ConfigItem 并传入验证器
        # self.zoom_card = OptionsSettingCard(...)

        # --- 2. 账户设置组 ---
        self.group_account = SettingCardGroup("账户", self.scroll_widget)

        self.logout_card = PushSettingCard(
            "登出",
            FIF.CLOSE,
            "账户管理",
            "退出当前账号，切换其他账号",
            self.group_account
        )
        self.logout_card.clicked.connect(self._on_logout_clicked)
        self.group_account.addSettingCard(self.logout_card)

        # --- 3. 关于 ---
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
            "关于云邮Mini",
            "当前版本：v1.0.0 Beta",
            self.group_about
        )
        self.about_card.clicked.connect(
            lambda: InfoBar.info("检查更新", "当前已是最新版本", duration=2000, parent=self)
        )

        self.group_about.addSettingCard(self.help_card)
        self.group_about.addSettingCard(self.about_card)

        # 添加到布局
        self.expand_layout.setContentsMargins(30, 30, 30, 30)
        self.expand_layout.setSpacing(20)
        self.expand_layout.addWidget(self.group_personal)
        self.expand_layout.addWidget(self.group_account)
        self.expand_layout.addWidget(self.group_about)

    def on_theme_changed(self, value) -> None:
        """主题改变"""
        # value 是配置项的值，通常是整数索引或 Theme 枚举
        try:
            # 获取配置项的当前值
            if hasattr(value, 'value'):
                # 如果是配置项对象，获取其值
                theme_value = value.value
            else:
                # 直接是值
                theme_value = value
            
            # 转换为 Theme 枚举
            if isinstance(theme_value, Theme):
                setTheme(theme_value)
            elif isinstance(theme_value, int):
                # 整数索引：0=浅色, 1=深色, 2=跟随系统
                theme_map = {
                    0: Theme.LIGHT,
                    1: Theme.DARK,
                    2: Theme.AUTO
                }
                setTheme(theme_map.get(theme_value, Theme.AUTO))
            else:
                # 尝试从字符串解析
                value_str = str(theme_value).lower()
                if "light" in value_str or value_str == "0":
                    setTheme(Theme.LIGHT)
                elif "dark" in value_str or value_str == "1":
                    setTheme(Theme.DARK)
                elif "auto" in value_str or value_str == "2":
                    setTheme(Theme.AUTO)
                else:
                    # 使用配置项的当前值
                    current_theme = qconfig.themeMode.value
                    if isinstance(current_theme, Theme):
                        setTheme(current_theme)
                    elif isinstance(current_theme, int):
                        theme_map = {0: Theme.LIGHT, 1: Theme.DARK, 2: Theme.AUTO}
                        setTheme(theme_map.get(current_theme, Theme.AUTO))
        except Exception as e:
            # 如果解析失败，使用配置项的当前值
            print(f"主题切换失败: {e}, value type: {type(value)}")
            try:
                current_theme = qconfig.themeMode.value
                if isinstance(current_theme, Theme):
                    setTheme(current_theme)
                elif isinstance(current_theme, int):
                    theme_map = {0: Theme.LIGHT, 1: Theme.DARK, 2: Theme.AUTO}
                    setTheme(theme_map.get(current_theme, Theme.AUTO))
            except:
                setTheme(Theme.AUTO)

    def on_zoom_changed(self, value) -> None:
        """缩放改变（目前仅保存配置，不实际应用）"""
        # 缩放选项改变时，只保存配置，不触发主题变化
        # 这里可以添加实际的缩放逻辑，但目前仅保存配置
        try:
            zoom_value = value.value if hasattr(value, 'value') else value
            # 缩放值已自动保存到配置项中
            # 可以在这里添加实际的缩放逻辑
            pass
        except Exception as e:
            print(f"缩放设置失败: {e}")

    def _on_logout_clicked(self) -> None:
        """登出按钮点击"""
        # 确认对话框
        w = MessageBox(
            "确认登出",
            "确定要退出当前账号吗？",
            self
        )
        if w.exec():
            self.logout_requested.emit()

