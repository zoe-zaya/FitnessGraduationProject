"""
核心配置文件
读取 .env 环境变量，提供全局配置访问
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    系统配置类
    从 .env 文件读取环境变量
    """
    
    # === 数据库配置 ===
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "fitness_db"
    
    # === 安全配置 ===
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # === 模型配置 ===
    MODEL_PATH: str = "app/resources/models/best.onnx"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # === 应用配置 ===
    APP_NAME: str = "Fitness Management System"
    APP_VERSION: str = "1.0"
    DEBUG: bool = True
    
    class Config:
        # 指定 .env 文件路径
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局 settings 实例
settings = Settings()


# 打印配置信息（调试用，生产环境请关闭）
if __name__ == "__main__":
    print("=== 当前配置 ===")
    print(f"数据库：{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}")
    print(f"模型路径：{settings.MODEL_PATH}")
    print(f"置信度阈值：{settings.CONFIDENCE_THRESHOLD}")