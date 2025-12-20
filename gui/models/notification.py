"""公告数据模型"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Notification:
    """公告数据模型"""

    id: Optional[int] = None
    title: str = ""
    type: Optional[str] = None
    content: Optional[str] = None
    is_read: bool = False
    time: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """从字典创建Notification对象"""
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            type=data.get("type"),
            content=data.get("content"),
            is_read=data.get("is_read", False),
            time=data.get("time"),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {"title": self.title}
        if self.id is not None:
            result["id"] = self.id
        if self.type:
            result["type"] = self.type
        if self.content:
            result["content"] = self.content
        result["is_read"] = self.is_read
        if self.time:
            result["time"] = self.time
        return result

