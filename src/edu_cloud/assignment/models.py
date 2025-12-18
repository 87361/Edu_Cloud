# src/edu_cloud/assignment/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from ..common.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    # 1. 基础ID
    id = Column(Integer, primary_key=True, index=True)
    
    # 2. 归属权：这个作业属于哪个用户？(关联 users 表的 id)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 3. 业务字段
    course_name = Column(String, index=True)    # 课程名称，如 "Python程序设计"
    title = Column(String, nullable=False)      # 作业标题
    description = Column(Text, nullable=True)   # 作业详情描述
    deadline = Column(DateTime, nullable=True)  # 截止时间
    
    # 4. 状态
    is_submitted = Column(Boolean, default=False) # 是否已提交
    score = Column(String, nullable=True)         # 分数/等级
    
    # 5. 记录创建时间
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))