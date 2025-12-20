from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
from ..common.database import Base

# ==========================================
# 1. 数据库模型 (用于存库)
# ==========================================
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    # 归属权
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 业务字段
    course_name = Column(String, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # 状态
    is_submitted = Column(Boolean, default=False)
    score = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# ==========================================
# 2. 数据传输对象 (DTO) - 用于 Scraper 返回数据
# ==========================================
@dataclass
class ScrapedAssignmentData:
    """
    这是一个纯数据类，用于 Scraper 模块向 API 模块传递抓取到的数据。
    使用 dataclass 可以避免使用字典传值带来的 key 拼写错误问题。
    """
    course_name: str
    title: str
    description: str
    deadline: Optional[datetime]
    is_submitted: bool
    score: str
    
    # 唯一标识符生成逻辑 (用于去重)
    @property
    def unique_key(self) -> str:
        return f"{self.course_name}_{self.title}"