"""课程数据模型"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Course:
    """课程数据模型"""

    id: Optional[int] = None
    name: str = ""
    teacher: Optional[str] = None
    term: Optional[str] = None
    pic_url: Optional[str] = None
    dept: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Course":
        """从字典创建Course对象"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            teacher=data.get("teacher"),
            term=data.get("term"),
            pic_url=data.get("pic_url"),
            dept=data.get("dept"),
            description=data.get("description"),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {"name": self.name}
        if self.id is not None:
            result["id"] = self.id
        if self.teacher:
            result["teacher"] = self.teacher
        if self.term:
            result["term"] = self.term
        if self.pic_url:
            result["pic_url"] = self.pic_url
        if self.dept:
            result["dept"] = self.dept
        if self.description:
            result["description"] = self.description
        return result


