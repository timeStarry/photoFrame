from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List

from ..core.database import get_session
from ..models.user import User
from ..models.watermark import (
    WatermarkTemplate, WatermarkTemplateCreate, WatermarkTemplateRead,
    WatermarkTemplateUpdate, WatermarkRequest
)
from ..services.auth_service import get_current_active_user
from ..services.watermark_service import WatermarkService

router = APIRouter()

# 水印模板管理
@router.post("/templates", response_model=WatermarkTemplateRead, summary="创建水印模板")
async def create_template(
    template_data: WatermarkTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """创建新的水印模板"""
    template = WatermarkTemplate(**template_data.dict(), user_id=current_user.id)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template

@router.get("/templates", response_model=List[WatermarkTemplateRead], summary="获取水印模板列表")
async def get_templates(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """获取用户的水印模板列表（包括公共模板）"""
    statement = select(WatermarkTemplate).where(
        (WatermarkTemplate.user_id == current_user.id) | 
        (WatermarkTemplate.is_public == True)
    ).order_by(WatermarkTemplate.created_at.desc())
    
    templates = session.exec(statement).all()
    return templates

@router.get("/templates/{template_id}", response_model=WatermarkTemplateRead, summary="获取水印模板详情")
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """获取指定水印模板的详细信息"""
    statement = select(WatermarkTemplate).where(
        WatermarkTemplate.id == template_id,
        (WatermarkTemplate.user_id == current_user.id) | 
        (WatermarkTemplate.is_public == True)
    )
    template = session.exec(statement).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="水印模板不存在")
    
    return template

@router.put("/templates/{template_id}", response_model=WatermarkTemplateRead, summary="更新水印模板")
async def update_template(
    template_id: int,
    template_data: WatermarkTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """更新指定的水印模板"""
    statement = select(WatermarkTemplate).where(
        WatermarkTemplate.id == template_id,
        WatermarkTemplate.user_id == current_user.id
    )
    template = session.exec(statement).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="水印模板不存在或无权限")
    
    # 更新字段
    for key, value in template_data.dict(exclude_unset=True).items():
        setattr(template, key, value)
    
    session.add(template)
    session.commit()
    session.refresh(template)
    return template

@router.delete("/templates/{template_id}", summary="删除水印模板")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """删除指定的水印模板"""
    statement = select(WatermarkTemplate).where(
        WatermarkTemplate.id == template_id,
        WatermarkTemplate.user_id == current_user.id
    )
    template = session.exec(statement).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="水印模板不存在或无权限")
    
    session.delete(template)
    session.commit()
    return {"message": "水印模板删除成功"}

# 水印处理
@router.post("/process", summary="处理水印")
async def process_watermark(
    request: WatermarkRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    为图片添加水印
    
    - **image_id**: 目标图片ID
    - **template_id**: 水印模板ID (可选)
    - **custom_text**: 自定义水印文字 (可选)
    - **custom_config**: 自定义配置 (可选)
    """
    output_path = await WatermarkService.process_watermark(request, current_user, session)
    
    return {
        "message": "水印处理完成",
        "output_path": output_path
    }

@router.get("/download/{filename}", summary="下载水印图片")
async def download_watermarked_image(filename: str):
    """下载处理后的水印图片"""
    from pathlib import Path
    from ..core.config import settings
    
    file_path = Path(settings.output_dir) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='image/jpeg'
    )

# 预设模板接口
@router.get("/presets", summary="获取预设模板")
async def get_preset_templates():
    """获取系统预设的水印模板信息"""
    presets = [
        {
            "name": "经典白框",
            "description": "简洁优雅的白色相框，适合各种照片",
            "frame_type": "white_frame",
            "watermark_type": "artistic"
        },
        {
            "name": "模糊艺术框",
            "description": "模糊背景的艺术相框，营造浅景深效果",
            "frame_type": "blur_frame", 
            "watermark_type": "artistic"
        },
        {
            "name": "景深色卡框",
            "description": "渐变色彩的专业相框，突出主体",
            "frame_type": "depth_color_card",
            "watermark_type": "artistic"
        }
    ]
    
    return {"presets": presets} 