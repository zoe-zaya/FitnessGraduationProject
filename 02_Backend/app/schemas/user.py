"""
用户相关 Pydantic 模型
用于请求/响应数据验证，对应《需求规格说明书》表 2-1
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class FitnessGoalEnum(str, Enum):
    """健身目标枚举"""
    MUSCLE_GAIN = "增肌"
    FAT_LOSS = "减脂"
    SHAPING = "塑形"
    FITNESS_IMPROVEMENT = "增强体能"


class ExperienceLevelEnum(str, Enum):
    """健身经验水平枚举"""
    BEGINNER = "初学者"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"


class GenderEnum(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# === 注册相关 ===
class UserRegister(BaseModel):
    """用户注册请求模型"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=8, description="密码")
    confirm_password: str = Field(..., min_length=8, description="确认密码")
    
    @field_validator('password')
    def validate_password(cls, v):
        """密码复杂度校验（对应《需求规格说明书》3.2 节扩展事件流）"""
        if len(v) < 8:
            raise ValueError('密码长度需大于 8 个字符')
        if not any(c.isupper() for c in v):
            raise ValueError('密码需包含大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码需包含小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码需包含数字')
        if not any(c in '!@#$%^&*()_+-=' for c in v):
            raise ValueError('密码需包含特殊符号!@#$%^&*()_+-=')
        return v
    
    @field_validator('confirm_password')
    def validate_confirm_password(cls, v, info):
        """确认密码校验"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('确认密码与密码不一致，请重新输入')
        return v


class UserRegisterResponse(BaseModel):
    """用户注册响应模型"""
    message: str
    user_id: str


# === 登录相关 ===
class UserLogin(BaseModel):
    """用户登录请求模型"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., description="密码")


class UserLoginResponse(BaseModel):
    """用户登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    user_info: dict


# === 用户信息相关 ===
class UserBodyData(BaseModel):
    """用户身体数据请求模型"""
    gender: Optional[GenderEnum] = Field(None, description="性别")
    height: Optional[float] = Field(None, ge=160, le=250, description="身高 (厘米)")
    weight: Optional[float] = Field(None, ge=60, le=300, description="体重 (千克)")
    fitness_goal: Optional[FitnessGoalEnum] = Field(None, description="健身目标")
    experience_level: Optional[ExperienceLevelEnum] = Field(None, description="健身经验水平")


class UserProfile(BaseModel):
    """用户个人资料请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=64, description="昵称")
    avatar_url: Optional[str] = Field(None, max_length=512, description="头像 URL")
    birthday: Optional[date] = Field(None, description="生日")


class UserResponse(BaseModel):
    """用户信息响应模型"""
    user_id: str
    name: str
    phone: str
    age: Optional[int]
    gender: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    bmi: Optional[float]
    fitness_goal: Optional[str]
    experience_level: Optional[str]
    avatar_url: Optional[str]
    birthday: Optional[date]
    create_time: datetime
    
    class Config:
        from_attributes = True