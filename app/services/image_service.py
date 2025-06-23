import os
import uuid
import json
from typing import Optional, Dict, Any
from pathlib import Path
from PIL import Image as PILImage
import exifread
from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from ..core.config import settings
from ..models.image import Image, ImageCreate, ImageStatus
from ..models.user import User

class ImageService:
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> None:
        """验证上传的图片文件"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 检查文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式。支持的格式: {', '.join(settings.allowed_extensions)}"
            )
        
        # 检查文件大小
        if hasattr(file, 'size') and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"文件大小超过限制 ({settings.max_file_size / 1024 / 1024:.1f}MB)"
            )
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """生成唯一的文件名"""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_ext}"
    
    @staticmethod
    def extract_exif_data(file_path: str) -> Optional[Dict[str, Any]]:
        """提取EXIF信息"""
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                exif_dict = {}
                
                for tag in tags.keys():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                        try:
                            exif_dict[tag] = str(tags[tag])
                        except:
                            pass
                
                return exif_dict if exif_dict else None
        except Exception:
            return None
    
    @staticmethod
    def clean_exif_data(file_path: str, output_path: str) -> None:
        """清理EXIF信息"""
        try:
            with PILImage.open(file_path) as img:
                # 移除EXIF数据
                data = list(img.getdata())
                image_without_exif = PILImage.new(img.mode, img.size)
                image_without_exif.putdata(data)
                image_without_exif.save(output_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"清理EXIF数据失败: {str(e)}")
    
    @staticmethod
    async def upload_image(
        file: UploadFile, 
        user: User, 
        session: Session,
        clean_exif: bool = True
    ) -> Image:
        """上传图片"""
        # 验证文件
        ImageService.validate_image_file(file)
        
        # 生成文件名和路径
        filename = ImageService.generate_unique_filename(file.filename)
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / filename
        
        try:
            # 保存原始文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # 获取图片信息
            with PILImage.open(file_path) as img:
                width, height = img.size
                format_type = img.format
            
            # 提取EXIF信息
            exif_data = ImageService.extract_exif_data(str(file_path))
            
            # 如果需要清理EXIF，创建清理后的副本
            if clean_exif and exif_data:
                cleaned_filename = f"cleaned_{filename}"
                cleaned_path = upload_dir / cleaned_filename
                ImageService.clean_exif_data(str(file_path), str(cleaned_path))
                # 使用清理后的文件作为主文件
                os.replace(cleaned_path, file_path)
            
            # 创建数据库记录
            file_size = os.path.getsize(file_path)
            image_data = ImageCreate(
                filename=filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                width=width,
                height=height,
                format=format_type,
                user_id=user.id,
                status=ImageStatus.UPLOADED
            )
            
            image = Image(**image_data.dict())
            if exif_data:
                image.exif_data = json.dumps(exif_data, ensure_ascii=False)
            
            session.add(image)
            session.commit()
            session.refresh(image)
            
            return image
            
        except Exception as e:
            # 清理已上传的文件
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
    
    @staticmethod
    def get_user_images(user: User, session: Session) -> list[Image]:
        """获取用户的图片列表"""
        statement = select(Image).where(Image.user_id == user.id).order_by(Image.created_at.desc())
        return session.exec(statement).all()
    
    @staticmethod
    def get_image_by_id(image_id: int, user: User, session: Session) -> Optional[Image]:
        """根据ID获取图片"""
        statement = select(Image).where(Image.id == image_id, Image.user_id == user.id)
        return session.exec(statement).first()
    
    @staticmethod
    def delete_image(image_id: int, user: User, session: Session) -> bool:
        """删除图片"""
        image = ImageService.get_image_by_id(image_id, user, session)
        if not image:
            return False
        
        # 删除文件
        try:
            if Path(image.file_path).exists():
                Path(image.file_path).unlink()
        except Exception:
            pass
        
        # 删除数据库记录
        session.delete(image)
        session.commit()
        return True 