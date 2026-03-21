"""
用户相关 Pydantic 模型
用于请求/响应数据验证，对应《需求规格说明书》表 2-1
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Literal
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

# === 忘记密码相关 ✅ ===
class SendVerificationCodeRequest(BaseModel):
    """发送验证码请求模型"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")


class SendVerificationCodeResponse(BaseModel):
    """发送验证码响应模型"""
    message: str
    expire_seconds: int = 300  # 验证码有效期 5 分钟


class VerifyCodeRequest(BaseModel):
    """验证验证码请求模型"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    code: str = Field(..., min_length=6, max_length=6, description="6 位验证码")


class VerifyCodeResponse(BaseModel):
    """验证验证码响应模型"""
    message: str
    is_valid: bool

class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    # verification_code: str = Field(..., min_length=6, max_length=6, description="验证码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., min_length=8, description="确认密码")
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        """新密码复杂度校验（对应扩展事件流 6a）"""
        if len(v) < 8:
            raise ValueError('密码长度需大于 8 个字符')
        if not any(c.isupper() for c in v):
            raise ValueError('密码需包含大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码需包含小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码需包含数字')
        if not any(c in '!@#$%^&*()_+-=' for c in v):
            raise ValueError('密码需包含特殊符号')
        return v
    
    @field_validator('confirm_password')
    def validate_confirm_password(cls, v, info):
        """确认密码校验（对应扩展事件流 6b）"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('确认密码与新密码不一致，请重新输入')
        return v
    
class ResetPasswordResponse(BaseModel):
    """重置密码响应模型"""
    message: str

# === 用户信息相关 ===
class UserBodyData(BaseModel):
    """用户身体数据请求模型"""
    gender: Optional[GenderEnum] = Field(None, description="性别")
    height: Optional[float] = Field(None, ge=50, le=250, description="身高 (厘米)")
    weight: Optional[float] = Field(None, ge=20, le=300, description="体重 (千克)")
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


# === 账号安全相关 ===
class SecurityUpdateType(str, Enum):
    """安全更新类型枚举"""
    PHONE = "phone"
    PASSWORD = "password"


class SecurityUpdateRequest(BaseModel):
    """
    账号安全更新请求模型
    对应《需求规格说明书》3.2 节编辑账号与安全用例
    """
    type: SecurityUpdateType = Field(..., description="更新类型：phone 或 password")
    old_value: str = Field(..., min_length=1, description="旧手机号或旧密码")
    new_value: str = Field(..., min_length=1, description="新手机号或新密码")
    confirm_value: str = Field(..., min_length=1, description="确认新手机号或新密码")
    
    @field_validator('old_value')
    def validate_old_value(cls, v, info):
        """验证旧值格式"""
        data = info.data
        if data.get('type') == 'phone':
            # 旧手机号验证
            if len(v) != 11 or not v.isdigit():
                raise ValueError('旧手机号格式不正确，请输入 11 位数字')
        return v
    
    @field_validator('new_value')
    def validate_new_value(cls, v, info):
        """验证新值格式"""
        data = info.data
        if data.get('type') == 'phone':
            # 新手机号验证
            if len(v) != 11 or not v.isdigit():
                raise ValueError('新手机号格式不正确，请输入 11 位数字')
            # 检查是否以 1 开头
            if not v.startswith('1'):
                raise ValueError('手机号必须以 1 开头')
        else:
            # 新密码验证
            if len(v) < 8:
                raise ValueError('密码长度需大于 8 个字符')
            if not any(c.isupper() for c in v):
                raise ValueError('密码需包含大写字母')
            if not any(c.islower() for c in v):
                raise ValueError('密码需包含小写字母')
            if not any(c.isdigit() for c in v):
                raise ValueError('密码需包含数字')
            if not any(c in '!@#$%^&*()_+-=' for c in v):
                raise ValueError('密码需包含特殊符号')
        return v
    
    @field_validator('confirm_value')
    def validate_confirm_value(cls, v, info):
        """验证确认值与新值一致"""
        data = info.data
        if v != data.get('new_value'):
            if data.get('type') == 'phone':
                raise ValueError('两次输入的新手机号不一致')
            else:
                raise ValueError('两次输入的新密码不一致')
        return v


class SecurityUpdateResponse(BaseModel):
    """账号安全更新响应模型"""
    message: str
    updated_field: str

#===推荐账号与安全分开为两个独立接口（如下），更清晰易维护 ===
#===修改手机号相关 ===
class PhoneUpdateRequest(BaseModel):
    """
    简化版手机号更新请求（推荐）
    更清晰的字段定义
    """
    old_phone: str = Field(..., min_length=11, max_length=11, description="当前手机号")
    new_phone: str = Field(..., min_length=11, max_length=11, description="新手机号")
    
    @field_validator('old_phone', 'new_phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if len(v) != 11 or not v.isdigit():
            raise ValueError('手机号格式不正确，请输入 11 位数字')
        if not v.startswith('1'):
            raise ValueError('手机号必须以 1 开头')
        return v


class PhoneUpdateResponse(BaseModel):
    """手机号更新响应模型"""
    message: str
    old_phone: str
    new_phone: str

###修改密码相关 ===
class PasswordUpdateRequest(BaseModel):
    """
    密码修改请求模型
    对应《需求规格说明书》3.2 节编辑账号与安全用例
    """
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., min_length=8, description="确认密码")
    
    @field_validator('old_password')
    def validate_old_password(cls, v):
        """验证旧密码不为空"""
        if not v or len(v.strip()) == 0:
            raise ValueError('旧密码不能为空')
        return v
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        """
        验证新密码复杂度
        对应《需求规格说明书》3.2 节扩展事件流 6a：
        密码长度需大于 8 个字符，包含大写字母、小写字母、数字和特殊符号
        """
        if len(v) < 8:
            raise ValueError('密码长度需大于 8 个字符')
        if not any(c.isupper() for c in v):
            raise ValueError('密码需包含大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码需包含小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码需包含数字')
        if not any(c in '!@#$%^&*()_+-=' for c in v):
            raise ValueError('密码需包含特殊符号 (!@#$%^&*()_+-=)')
        return v
    
    @field_validator('confirm_password')
    def validate_confirm_password(cls, v, info):
        """
        验证确认密码与新密码一致
        对应《需求规格说明书》3.2 节扩展事件流 6b
        """
        data = info.data
        if v != data.get('new_password'):
            raise ValueError('两次输入的密码不一致，请重新输入')
        return v


class PasswordUpdateResponse(BaseModel):
    """密码修改响应模型"""
    message: str
    updated_field: str = "password"
    update_time: datetime
