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
    allow_origins=[
        "http://localhost:5173",      # Vite 开发服务器
        "http://127.0.0.1:5173",      # Vite 开发服务器 (IP 形式)
        "http://localhost:8080",      # 其他可能的开发端口
        "https://your-production-domain.com",  # 生产环境域名（后续添加）
        "*",                          # ⚠️ 开发环境可临时使用 * 允许所有来源，生产环境请指定具体域名
    ],  # 生产环境应限制具体域名
    allow_credentials=True,         # 允许携带凭证（如 Cookie、Authorization）
    allow_methods=["*"],            # 允许所有 HTTP 方法（GET、POST、PUT、DELETE 等）
    allow_headers=["*"],            # 允许所有请求头
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