"""作业数据模型"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Assignment:
    """作业数据模型"""

    id: int
    title: str
    course_name: str
    description: str
    deadline: Optional[str]
    status: str
    score: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Assignment":
        """从字典创建Assignment对象"""
        return cls(
            id=data.get("id", 0),
            title=data.get("title", "无标题"),
            course_name=data.get("course_name", "未知课程"),
            description=data.get("description", ""),
            deadline=data.get("deadline"),
            status=data.get("status", "未提交"),
            score=data.get("score"),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "course_name": self.course_name,
            "description": self.description,
            "deadline": self.deadline,
            "status": self.status,
            "score": self.score,
        }

    def is_submitted(self) -> bool:
        """检查是否已提交"""
        return self.status == "已提交"

    def get_deadline_display(self) -> str:
        """获取截止时间显示文本"""
        if not self.deadline or self.deadline == "无截止日期":
            return "无截止日期"
        try:
            dt = datetime.fromisoformat(self.deadline.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return self.deadline

