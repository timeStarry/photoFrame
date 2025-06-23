from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from ..core.database import get_session
from ..models.user import User, UserCreate, UserRead
from ..services.auth_service import (
    authenticate_user, create_user, create_access_token, 
    get_current_active_user
)
from ..services.watermark_service import WatermarkService

router = APIRouter()

@router.post("/register", response_model=UserRead, summary="用户注册")
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """用户注册"""
    user = create_user(session, user_data)
    
    # 为新用户创建默认水印模板
    WatermarkService.create_default_templates(user, session)
    
    return user

@router.post("/login", summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """用户登录"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

@router.get("/me", response_model=UserRead, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user 