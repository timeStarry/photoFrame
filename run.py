#!/usr/bin/env python3
"""
PhotoFrame 相框服务启动脚本
"""

import uvicorn
import os
from pathlib import Path

def create_directories():
    """创建必要的目录"""
    directories = [
        "uploads",
        "outputs",
        "temp",
        "templates",
        "fonts"
    ]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 目录 {directory}/ 已创建")

def main():
    """主启动函数"""
    print("=" * 50)
    print("  PhotoFrame 相框服务")
    print("=" * 50)
    
    # 创建目录
    print("\n📁 初始化目录结构...")
    create_directories()
    
    # 启动服务
    print("\n🚀 启动服务...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔄 Redoc文档: http://localhost:8000/redoc")
    print("💫 服务状态: http://localhost:8000/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 