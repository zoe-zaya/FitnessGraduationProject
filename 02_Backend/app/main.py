"""
FastAPI 应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, user
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于深度学习的健身管理系统后端 API"
)

# 配置 CORS（允许前端小程序访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Fitness Management System API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}