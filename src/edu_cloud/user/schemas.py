from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CASLogin(BaseModel):
    """直接使用 CAS 登录"""
    cas_username: str  # CAS 用户名（学号）
    cas_password: str  # CAS 密码

class CASBind(BaseModel):
    """绑定 CAS 账户到注册用户"""
    cas_username: str  # CAS 用户名（学号）
    cas_password: str  # CAS 密码

class UserWithCAS(User):
    """包含 CAS 绑定信息的用户模型"""
    cas_username: Optional[str] = None
    cas_is_bound: bool = False
    cas_bound_at: Optional[datetime] = None
