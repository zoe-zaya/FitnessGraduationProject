"""
用户认证相关 API
对应《需求规格说明书》3.2 节：注册、登录、忘记密码用例
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.utils.db import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister, UserRegisterResponse, UserLogin, UserLoginResponse, UserResponse
)
from app.core.security import (
    get_password_hash, verify_password, create_access_token, get_current_user
)
import uuid
import random

router = APIRouter(prefix="/api/auth", tags=["用户认证"])


@router.post("/register", response_model=UserRegisterResponse, summary="用户注册")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册账号
    对应《需求规格说明书》3.2 节注册用例
    """
    # 检查手机号是否已注册
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册，请直接登录"
        )
    
    # 创建新用户
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        user_id=user_id,
        name=f"用户{user_id[:6]}",  # 默认昵称
        phone=user_data.phone,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserRegisterResponse(
        message="注册成功",
        user_id=user_id
    )


@router.post("/login", response_model=UserLoginResponse, summary="用户登录")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录系统
    对应《需求规格说明书》3.2 节登录用例
    """
    # 验证手机号是否存在
    user = db.query(User).filter(User.phone == user_data.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号未注册，请先注册"
        )
    
    # 验证密码
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误，请重试"
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "user_id": user.user_id,
            "name": user.name,
            "phone": user.phone
        }
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    """
    return UserResponse(
        user_id=current_user.user_id,
        name=current_user.name,
        phone=current_user.phone,
        age=current_user.calculate_age(),
        gender=current_user.gender.value if current_user.gender else None,
        height=current_user.height,
        weight=current_user.weight,
        bmi=current_user.calculate_bmi(),
        fitness_goal=current_user.fitness_goal.value if current_user.fitness_goal else None,
        experience_level=current_user.experience_level.value if current_user.experience_level else None,
        avatar_url=current_user.avatar_url,
        birthday=current_user.birthday,
        create_time=current_user.create_time
    )