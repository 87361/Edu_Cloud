"""认证服务"""
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..api_client import api_client, APIError
from ..models.user import User
from ..utils.token_manager import token_manager


class AuthService(QObject):
    """认证服务类"""

    login_success = pyqtSignal(User)  # 登录成功信号
    login_failed = pyqtSignal(str)  # 登录失败信号
    logout_success = pyqtSignal()  # 登出成功信号
    user_info_loaded = pyqtSignal(User)  # 用户信息加载成功

    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化认证服务

        Args:
            parent: 父对象
        """
        super().__init__(parent)

    def login(self, username: str, password: str, is_cas: bool = False) -> User:
        """
        登录

        Args:
            username: 用户名或学号
            password: 密码
            is_cas: 是否为CAS登录

        Returns:
            用户对象

        Raises:
            APIError: 登录失败
        """
        if is_cas:
            response = api_client.login_cas(username, password)
        else:
            response = api_client.login(username, password)

        # 登录成功后，获取完整的用户信息（包含role）
        # 因为登录API可能不返回完整的用户信息
        try:
            user_info_response = api_client.get_user_info()
            user_info = user_info_response.get("data", {})
        except Exception:
            # 如果获取失败，尝试从响应中获取（CAS登录可能包含user字段）
            user_info = response.get("user", {}) or response.get("data", {})
        
        return User.from_dict(user_info)

    def logout(self) -> None:
        """登出"""
        try:
            api_client.logout()
        except Exception:
            # 即使API调用失败，也清除本地Token
            pass
        finally:
            token_manager.clear_token()
            self.logout_success.emit()

    def get_current_user(self) -> Optional[User]:
        """
        获取当前登录用户

        Returns:
            用户对象，如果未登录则返回None
        """
        if not token_manager.get_token():
            return None

        try:
            response = api_client.get_user_info()
            user_info = response.get("data", {})
            return User.from_dict(user_info)
        except Exception:
            return None

    def load_user_info(self) -> None:
        """加载用户信息"""
        user = self.get_current_user()
        if user:
            self.user_info_loaded.emit(user)

    def is_logged_in(self) -> bool:
        """
        检查是否已登录

        Returns:
            是否已登录
        """
        return token_manager.get_token() is not None

