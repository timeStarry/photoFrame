from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session
from typing import List
import json

from ..core.database import get_session
from ..models.user import User
from ..models.image import ImageRead
from ..services.auth_service import get_current_active_user
from ..services.image_service import ImageService

router = APIRouter()

@router.post("/upload", response_model=ImageRead, summary="上传图片")
async def upload_image(
    file: UploadFile = File(..., description="图片文件"),
    clean_exif: bool = True,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    上传图片
    
    - **file**: 图片文件 (支持 JPG, PNG, BMP, TIFF)
    - **clean_exif**: 是否清理EXIF信息 (默认: True)
    """
    image = await ImageService.upload_image(file, current_user, session, clean_exif)
    
    # 处理返回数据
    image_data = ImageRead.from_orm(image)
    if image.exif_data:
        try:
            image_data.exif_data = json.loads(image.exif_data)
        except:
            image_data.exif_data = None
    
    return image_data

@router.get("/", response_model=List[ImageRead], summary="获取图片列表")
async def get_images(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """获取当前用户的图片列表"""
    images = ImageService.get_user_images(current_user, session)
    
    result = []
    for image in images:
        image_data = ImageRead.from_orm(image)
        if image.exif_data:
            try:
                image_data.exif_data = json.loads(image.exif_data)
            except:
                image_data.exif_data = None
        result.append(image_data)
    
    return result

@router.get("/{image_id}", response_model=ImageRead, summary="获取图片详情")
async def get_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """获取指定图片的详细信息"""
    image = ImageService.get_image_by_id(image_id, current_user, session)
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    image_data = ImageRead.from_orm(image)
    if image.exif_data:
        try:
            image_data.exif_data = json.loads(image.exif_data)
        except:
            image_data.exif_data = None
    
    return image_data

@router.get("/{image_id}/download", summary="下载图片")
async def download_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """下载指定的图片文件"""
    image = ImageService.get_image_by_id(image_id, current_user, session)
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    return FileResponse(
        path=image.file_path,
        filename=image.original_filename,
        media_type='application/octet-stream'
    )

@router.delete("/{image_id}", summary="删除图片")
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """删除指定的图片"""
    success = ImageService.delete_image(image_id, current_user, session)
    if not success:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    return {"message": "图片删除成功"} 