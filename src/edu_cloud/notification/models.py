from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
from ..common.database import Base

# ==========================================
# 1. 数据库模型
# ==========================================

class Notification(Base):
    """系统公告/通知表"""
    __tablename__ = "notifications"

    # 使用学校的 id 作为主键 (e.g. "2000742433166016525")
    id = Column(String, primary_key=True)
    
    # 关联本地用户
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=True)       # newsTitle: "Python程序设计"
    content = Column(Text, nullable=True)       # newsInfo: "老师正在上课..."
    # type: "互动课堂" or "老师发布作业"
    msg_type = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)    # isRead: 0/1
    
    publish_time = Column(DateTime, nullable=True) # newsCopyTime 或 createTime
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# ==========================================
# 2. 数据传输对象 (DTO)
# ==========================================

@dataclass
class ScrapedNotificationData:
    id: str
    title: str
    content: str
    msg_type: str
    is_read: bool
    publish_time: Optional[datetime]