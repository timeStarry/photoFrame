from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from pathlib import Path
import os

# 导入自定义模块
from app.routers import watermark, image_management, auth
from app.core.config import settings
from app.core.database import init_db

# 创建FastAPI应用
app = FastAPI(
    title="PhotoFrame 相框服务",
    description="图片水印处理服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
def create_directories():
    directories = [
        "uploads",
        "outputs", 
        "temp",
        "templates",
        "fonts"
    ]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    create_directories()
    await init_db()

# 包含路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(watermark.router, prefix="/api/watermark", tags=["水印"])
app.include_router(image_management.router, prefix="/api/images", tags=["图片管理"])

@app.get("/")
async def root():
    return {
        "message": "PhotoFrame 相框服务",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
