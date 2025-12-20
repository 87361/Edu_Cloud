"""讨论数据模型"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DiscussionTopic:
    """讨论主题数据模型"""

    id: Optional[int] = None
    title: str = ""
    author: Optional[str] = None
    reply_count: int = 0
    view_count: int = 0
    created_at: Optional[str] = None
    content: Optional[str] = None
    replies: List[dict] = None

    def __post_init__(self):
        if self.replies is None:
            self.replies = []

    @classmethod
    def from_dict(cls, data: dict) -> "DiscussionTopic":
        """从字典创建DiscussionTopic对象"""
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            author=data.get("author"),
            reply_count=data.get("reply_count", 0),
            view_count=data.get("view_count", 0),
            created_at=data.get("created_at"),
            content=data.get("content"),
            replies=data.get("replies", []),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {"title": self.title}
        if self.id is not None:
            result["id"] = self.id
        if self.author:
            result["author"] = self.author
        result["reply_count"] = self.reply_count
        result["view_count"] = self.view_count
        if self.created_at:
            result["created_at"] = self.created_at
        if self.content:
            result["content"] = self.content
        if self.replies:
            result["replies"] = self.replies
        return result

