# 定义数据库表(Topic, Post)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional
from ..common.database import Base

# ==========================================
# 1. 数据库模型
# ==========================================

class DiscussionTopic(Base):
    """讨论区主题（帖子）"""
    __tablename__ = "discussion_topics"

    # 使用学校的 id 作为主键
    id = Column(String, primary_key=True) 
    
    # 关联课程 (siteId)
    course_id = Column(String, index=True, nullable=False)
    
    title = Column(String, nullable=True)       # 标题
    author_name = Column(String, nullable=True) # 发帖人姓名
    content = Column(Text, nullable=True)       # 正文(HTML)
    
    view_count = Column(Integer, default=0)     # 浏览量
    reply_count = Column(Integer, default=0)    # 回复数
    like_count = Column(Integer, default=0)     # 点赞数
    
    created_at = Column(DateTime, nullable=True) # 发帖时间
    updated_at = Column(DateTime, nullable=True) # 最后更新

class DiscussionPost(Base):
    """讨论区回复（楼层）"""
    __tablename__ = "discussion_posts"

    id = Column(String, primary_key=True)
    
    # 关联主题 (Topic ID)
    topic_id = Column(String, ForeignKey("discussion_topics.id"), nullable=False)
    
    author_name = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    floor = Column(Integer, default=1)          # 楼层号
    is_teacher = Column(Boolean, default=False) # 是否老师回复
    
    created_at = Column(DateTime, nullable=True)

# ==========================================
# 2. 数据传输对象 (DTO)
# ==========================================

@dataclass
class ScrapedPostData:
    id: str
    author_name: str
    content: str
    floor: int
    created_at: Optional[datetime]

@dataclass
class ScrapedTopicData:
    id: str
    course_id: str
    title: str
    author_name: str
    content: str
    view_count: int
    reply_count: int
    like_count: int
    created_at: Optional[datetime]
    # 包含的回复列表
    posts: List[ScrapedPostData]