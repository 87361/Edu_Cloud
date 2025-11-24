from fastapi import FastAPI
from sqlalchemy.orm import Session
# 关键修改：导入路径从 src 目录开始
from edu_cloud.common.database import engine, Base, get_db
from edu_cloud.user import models as user_models
from edu_cloud.user.api import router as user_router
# 创建所有数据库表
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Edu Cloud API",
    description="A multi-user replica of BUPT's Ucloud system.",
    version="0.1.0",
)
# 包含用户相关的API路由
app.include_router(user_router, prefix="/api/user", tags=["user"])
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Edu Cloud API. Go to /docs for API documentation."}