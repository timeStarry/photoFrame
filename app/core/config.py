from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 应用设置
    app_name: str = "PhotoFrame 相框服务"
    debug: bool = True
    
    # 数据库设置
    database_url: str = "sqlite:///./photoframe.db"
    
    # JWT设置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7天
    
    # 文件上传设置
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    temp_dir: str = "./temp"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    
    # 水印设置
    default_font_path: str = "./fonts/default.ttf"
    watermark_opacity: float = 0.8
    
    class Config:
        env_file = ".env"

settings = Settings() 