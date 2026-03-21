"""
用户资料管理 API
对应《需求规格说明书》3.2 节：编辑身体数据、编辑个人资料用例
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.user import User
from app.schemas.user import (
    UserBodyData, UserProfile, UserResponse,
    SecurityUpdateRequest, SecurityUpdateResponse,
    PhoneUpdateRequest, PhoneUpdateResponse,
    PasswordUpdateRequest, PasswordUpdateResponse
)
from app.core.security import get_current_user, check_user_profile_complete, get_password_hash, verify_password
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

@router.put("/security/phone", response_model=PhoneUpdateResponse, summary="修改手机号")
async def update_phone(
    phone_data: PhoneUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户修改绑定手机号
    对应《需求规格说明书》3.2 节编辑账号与安全用例
    
    业务规则：
    1. 验证旧手机号是否正确（对应用例扩展事件流 4a）
    2. 验证新手机号格式是否正确（对应用例扩展事件流 4b）
    3. 验证新手机号是否已被其他用户注册
    4. 更新数据库中的手机号
    """
    # 1. 验证旧手机号是否与当前用户匹配（对应扩展事件流 4a）
    if phone_data.old_phone != current_user.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="输入的旧手机号不正确，请检查后重试"
        )
    
    # 2. 验证新手机号是否已被其他用户注册
    existing_user = db.query(User).filter(
        User.phone == phone_data.new_phone,
        User.user_id != current_user.user_id  # 排除当前用户
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已被其他用户注册，请更换其他手机号"
        )
    
    # 3. 验证新旧手机号是否相同
    if phone_data.old_phone == phone_data.new_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新手机号不能与旧手机号相同"
        )
    
    # 4. 更新手机号
    old_phone = current_user.phone
    current_user.phone = phone_data.new_phone
    
    db.commit()
    db.refresh(current_user)
    
    # 5. 返回成功响应
    return PhoneUpdateResponse(
        message="手机号修改成功",
        old_phone=old_phone,
        new_phone=phone_data.new_phone
    )

@router.put("/security/password", response_model=PasswordUpdateResponse, summary="修改密码")
async def update_password(
    password_data: PasswordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户修改登录密码
    对应《需求规格说明书》3.2 节编辑账号与安全用例
    
    业务规则：
    1. 验证旧密码是否正确（对应扩展事件流 6a）
    2. 验证新密码复杂度要求（对应扩展事件流 6a）
    3. 验证两次密码是否一致（对应扩展事件流 6b）
    4. 验证新旧密码是否相同
    5. 更新数据库中的密码哈希
    
    安全性要求：
    - 密码使用 bcrypt 加密存储
    - 必须通过 JWT Token 验证用户身份
    - 记录密码修改时间
    """
    # 1. 验证旧密码是否正确（对应扩展事件流 6a）
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="输入的旧密码不正确，请检查后重试"
        )
    
    # 2. 验证新密码与旧密码是否相同
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )
    
    # 3. 验证新密码复杂度（已在 Schema 验证器中完成）
    # Pydantic 会自动验证 password_data.new_password 是否符合复杂度要求
    
    # 4. 验证两次密码是否一致（已在 Schema 验证器中完成）
    # Pydantic 会自动验证 password_data.confirm_password 与 new_password 一致
    
    # 5. 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.update_time = datetime.now()
    
    db.commit()
    db.refresh(current_user)
    
    # 6. 返回成功响应
    return PasswordUpdateResponse(
        message="密码修改成功",
        updated_field="password",
        update_time=datetime.now()
    )

@router.put("/security", response_model=SecurityUpdateResponse, summary="统一安全更新接口")
async def update_security(
    security_data: SecurityUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统一安全更新接口（可选）
    根据 type 字段决定更新手机号或密码
    
    注意：建议分开为两个独立接口（如上），更清晰易维护
    """
    if security_data.type == "phone":
        # 验证旧手机号
        if security_data.old_value != current_user.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="输入的旧手机号不正确"
            )
        
        # 验证新手机号是否被占用
        existing_user = db.query(User).filter(
            User.phone == security_data.new_value,
            User.user_id != current_user.user_id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被其他用户注册"
            )
        
        # 更新手机号
        current_user.phone = security_data.new_value
        db.commit()
        
        return SecurityUpdateResponse(
            message="手机号修改成功",
            updated_field="phone"
        )
    
    elif security_data.type == "password":
        # 验证旧密码
        if not verify_password(security_data.old_value, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="输入的旧密码不正确"
            )
        
        # 更新密码
        current_user.password_hash = get_password_hash(security_data.new_value)
        db.commit()
        
        return SecurityUpdateResponse(
            message="密码修改成功",
            updated_field="password"
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的更新类型"
        )