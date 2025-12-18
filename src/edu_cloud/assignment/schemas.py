# src/edu_cloud/assignment/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 基础模型
class AssignmentBase(BaseModel):
    course_name: str
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    is_submitted: bool = False

# 创建时需要的字段
class AssignmentCreate(AssignmentBase):
    pass

# 更新时允许只改部分字段
class AssignmentUpdate(BaseModel):
    course_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_submitted: Optional[bool] = None
    score: Optional[str] = None