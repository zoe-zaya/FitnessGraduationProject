"""
用户资料管理 API
对应《需求规格说明书》3.2 节：编辑身体数据、编辑个人资料用例
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.user import User
from app.schemas.user import UserBodyData, UserProfile, UserResponse
from app.core.security import get_current_user, check_user_profile_complete
from datetime import datetime

router = APIRouter(prefix="/api/user", tags=["用户管理"])


@router.put("/body-data", response_model=UserResponse, summary="编辑身体数据")
async def update_body_data(
    body_data: UserBodyData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户编辑身体数据
    对应《需求规格说明书》3.2 节编辑身体数据用例
    """
    # 更新用户身体数据，但排除年龄字段，因为它由生日自动计算
    if body_data.gender is not None:
        current_user.gender = body_data.gender
    if body_data.height is not None:
        current_user.height = body_data.height
    if body_data.weight is not None:
        current_user.weight = body_data.weight
    if body_data.fitness_goal is not None:
        current_user.fitness_goal = body_data.fitness_goal
    if body_data.experience_level is not None:
        current_user.experience_level = body_data.experience_level
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        user_id=current_user.user_id,
        name=current_user.name,
        phone=current_user.phone,
        age=current_user.calculate_age(),  # 这里返回的是通过生日计算的年龄
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


@router.put("/profile", response_model=UserResponse, summary="编辑个人资料")
async def update_profile(
    profile: UserProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户编辑个人资料
    修改点：生日更新时自动重新计算年龄
    对应《需求规格说明书》3.2 节编辑个人资料用例
    """
    # 检查昵称是否重复
    if profile.name is not None and profile.name != current_user.name:
        existing_user = db.query(User).filter(
            User.name == profile.name,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="昵称已存在，请输入其他昵称"
            )
        current_user.name = profile.name
    
    # 头像更改
    if profile.avatar_url is not None:
        current_user.avatar_url = profile.avatar_url
    
    # 更新生日
    if profile.birthday is not None:
        # 将 date 转换为 datetime 存储
        current_user.birthday = datetime.combine(profile.birthday, datetime.min.time())
        # 同步更新年龄字段 (满足需求 1：生日更新则重新计算年龄并写入数据库)
        current_user.update_age_from_birthday()
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        user_id=current_user.user_id,
        name=current_user.name,
        phone=current_user.phone,
        age=current_user.calculate_age(),  # 这里返回的是通过生日计算的年龄
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


@router.get("/check-profile-complete", summary="检查用户资料是否完整")
async def check_profile_complete(
    current_user: User = Depends(get_current_user)
):
    """
    检查用户基本信息是否完整
    对应《需求规格说明书》2.2.1 业务规则：
    用户首次使用系统时必须完成基本信息录入，否则无法生成个性化训练计划
    """
    is_complete = check_user_profile_complete(current_user)
    return {
        "is_complete": is_complete,
        "message": "资料完整" if is_complete else "请先完善身体数据"
    }