# 定义数据库表(Course, Resource) + 数据传输类(Dataclass)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional
from ..common.database import Base

# ==========================================
# 1. 数据库模型 (SQLAlchemy)
# ==========================================

class Course(Base):
    """课程主表"""
    __tablename__ = "courses"

    # 直接使用学校的 siteId 作为主键，方便对应
    id = Column(String, primary_key=True, index=True) 
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 关联本地用户
    
    name = Column(String, nullable=False)        # 课程名 (Python程序设计)
    course_code = Column(String, nullable=True)  # 课程代码 (3132133010)
    term_name = Column(String, nullable=True)    # 学期 (2025秋季)
    teacher = Column(String, nullable=True)      # 教师姓名
    dept_name = Column(String, nullable=True)    # 开课学院
    pic_url = Column(String, nullable=True)      # 封面图
    description = Column(Text, nullable=True)    # 课程简介 (HTML)
    
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CourseResource(Base):
    """课程资料/讲义表"""
    __tablename__ = "course_resources"

    id = Column(String, primary_key=True) # 使用学校的 resourceId
    course_id = Column(String, ForeignKey("courses.id"), nullable=False) # 关联课程
    
    title = Column(String, nullable=False)       # 资料标题 (第01章 Python概述)
    file_type = Column(String, nullable=True)    # 文件类型 (pptx, pdf)
    file_size = Column(String, nullable=True)    # 文件大小 (3.26MB)
    download_url = Column(String, nullable=True) # 下载链接
    
    parent_section = Column(String, nullable=True) # 所属章节 (用于分组显示)
    created_at = Column(DateTime, nullable=True)   # 资源上传时间

# ==========================================
# 2. 数据传输对象 (DTO) - 用于 Scraper 返回清洗后的数据
# ==========================================

@dataclass
class ScrapedResourceData:
    resource_id: str
    title: str
    file_type: str
    file_size: str
    download_url: str
    parent_section: str  # 例如 "第一章"
    upload_time: Optional[datetime]

@dataclass
class ScrapedCourseData:
    site_id: str
    name: str
    course_code: str
    term_name: str
    teacher_name: str
    dept_name: str
    pic_url: str
    description: str
    # 课程包含的资源列表
    resources: List[ScrapedResourceData]