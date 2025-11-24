from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..common.database import get_db
from ..common.security import verify_password, get_password_hash
from . import models, schemas
router = APIRouter()
@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 检查用户是否已存在
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # 验证用户
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 登录成功，设置一个简单的session cookie
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(key="session_token", value=db_user.username, httponly=True)
    return response
@router.get("/me", response_model=schemas.User)
def read_users_me(db: Session = Depends(get_db)):
    # 这个API暂时用于测试，之后需要从cookie中获取用户信息
    return {"message": "This endpoint needs to be secured with session validation."}