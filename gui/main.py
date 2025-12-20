"""GUI应用主入口"""
import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication

from qfluentwidgets import setTheme, Theme

from .views.login_window import LoginWindow
from .views.main_window import MainWindow
from .services.auth_service import AuthService
from .utils.token_manager import token_manager


class EduCloudApp:
    """教育云应用"""

    def __init__(self):
        """初始化应用"""
        # 设置高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        self.app = QApplication(sys.argv)

        # 设置主题 - 从配置文件读取，如果没有则使用默认值
        from qfluentwidgets import qconfig
        try:
            # 读取配置的主题模式
            theme_mode = qconfig.themeMode.value
            if isinstance(theme_mode, Theme):
                setTheme(theme_mode)
            elif isinstance(theme_mode, int):
                theme_map = {0: Theme.LIGHT, 1: Theme.DARK, 2: Theme.AUTO}
                setTheme(theme_map.get(theme_mode, Theme.AUTO))
            else:
                setTheme(Theme.AUTO)  # 默认跟随系统
        except:
            # 如果读取失败，使用默认值
            setTheme(Theme.AUTO)

        self.auth_service = AuthService()

        # 检查是否已登录
        if token_manager.get_token():
            # 获取用户信息判断角色（使用数据库中的role字段）
            try:
                user = self.auth_service.get_current_user()
                if user and user.role == 'admin':
                    # 管理员账户，显示管理员窗口
                    self._show_admin_window()
                elif user:
                    # 普通用户，显示主窗口
                    self._show_main_window()
                else:
                    # Token无效或已过期，清除token并显示登录窗口
                    token_manager.clear_token()
                    self._show_login_window()
            except Exception as e:
                # 获取用户信息失败，清除token并显示登录窗口
                import logging
                logging.error(f"获取用户信息失败: {e}")
                token_manager.clear_token()
                self._show_login_window()
        else:
            self._show_login_window()

    def _show_login_window(self) -> None:
        """显示登录窗口"""
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self._on_login_success)
        self.login_window.show()

    def _show_main_window(self) -> None:
        """显示主窗口"""
        self.main_window = MainWindow()
        # 连接登出信号
        self.main_window.logout_requested.connect(self._on_logout_requested)
        self.main_window.show()

    def _show_admin_window(self) -> None:
        """显示管理员窗口"""
        from .views.admin_window import AdminWindow
        self.admin_window = AdminWindow()
        # 连接登出信号
        self.admin_window.logout_requested.connect(self._on_logout_requested)
        self.admin_window.show()

    def _on_login_success(self) -> None:
        """登录成功"""
        if hasattr(self, "login_window"):
            self.login_window.close()
        
        # 获取用户信息，根据数据库中的role字段判断角色
        try:
            user = self.auth_service.get_current_user()
            if user and user.role == 'admin':
                # 管理员账户，显示管理员窗口
                self._show_admin_window()
            else:
                # 普通用户，显示主窗口
                self._show_main_window()
        except Exception as e:
            import logging
            logging.error(f"登录后获取用户信息失败: {e}")
            # 如果获取失败，默认显示主窗口
            self._show_main_window()

    def _on_logout_requested(self) -> None:
        """登出请求"""
        if hasattr(self, "main_window"):
            self.main_window.close()
        if hasattr(self, "admin_window"):
            self.admin_window.close()
        self._show_login_window()

    def run(self) -> int:
        """
        运行应用

        Returns:
            退出代码
        """
        return self.app.exec()


def main() -> None:
    """主函数"""
    app = EduCloudApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
