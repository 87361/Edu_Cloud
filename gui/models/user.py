"""用户数据模型"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """用户数据模型"""

    id: Optional[int] = None
    username: str = ""
    email: Optional[str] = None
    role: Optional[str] = None
    cas_username: Optional[str] = None
    cas_is_bound: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """从字典创建User对象"""
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            email=data.get("email"),
            role=data.get("role", "user"),  # 默认值为'user'
            cas_username=data.get("cas_username"),
            cas_is_bound=data.get("cas_is_bound", False),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {"username": self.username}
        if self.id is not None:
            result["id"] = self.id
        if self.email:
            result["email"] = self.email
        if self.role:
            result["role"] = self.role
        if self.cas_username:
            result["cas_username"] = self.cas_username
        if self.cas_is_bound:
            result["cas_is_bound"] = self.cas_is_bound
        return result

