"""
器材管理相关 Pydantic 模型
对应《需求规格说明书》表 2-2、表 2-3 业务对象
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EquipmentCategoryEnum(str, Enum):
    """器材分类枚举"""
    STRENGTH_FREE_WEIGHT = "力量训练 - 自由重量"
    STRENGTH_MACHINE = "力量训练 - 固定器械"
    CARDIO = "有氧器械"
    ACCESSORY = "辅助器材"

class ActionInfoResponse(BaseModel):
    """动作信息响应模型
    对应《需求规格说明书》表 2-4 TrainingAction 对象
    修改：添加 image_url 字段
    """
    action_id: str
    name: str
    action_category: str
    difficulty_level: str
    estimated_seconds: int
    target_muscles: Optional[List[str]] = None
    image_url: Optional[str] = None  # ✅ 新增字段
    video_demo_url: Optional[str] = None  # ✅ 确保此字段存在
    safety_tips: Optional[str] = None  # ✅ 确保此字段存在
    
    class Config:
        from_attributes = True


class EquipmentListResponse(BaseModel):
    """器材列表响应模型"""
    equipment_id: str
    name: str
    category: str
    description: Optional[str] = None
    target_muscles: Optional[List[str]] = None
    image_url: Optional[str] = None  # ✅ 新增字段
    
    class Config:
        from_attributes = True


class GymEquipmentResponse(BaseModel):
    """健身器材详细信息响应模型
    对应《需求规格说明书》表 2-3
    """
    equipment_id: str
    name: str
    category: str
    description: Optional[str] = None
    target_muscles: Optional[List[str]] = None
    image_url: Optional[str] = None
    supported_actions_count: int = 0
    supported_actions: Optional[List[ActionInfoResponse]] = None  # ✅ 新增字段
    
    class Config:
        from_attributes = True


class EquipmentInventoryCreate(BaseModel):
    """创建器材清单请求模型
    对应《需求规格说明书》表 2-2
    """
    location_tag: str = Field(..., min_length=1, max_length=128, description="归属标签")
    description: Optional[str] = Field(None, max_length=512, description="清单描述")
    
    @field_validator('location_tag')
    def validate_location_tag(cls, v):
        """验证归属标签不为空"""
        if not v or len(v.strip()) == 0:
            raise ValueError('归属标签不能为空')
        return v.strip()

class EquipmentInventoryCreateResponse(BaseModel):
    """创建器材清单响应模型
    对应《需求规格说明书》表 2-2
    """
    inventory_id: str
    user_id: str
    location_tag: str
    description: Optional[str] = None
    create_time: datetime
    equipment_count: int = 0
    equipment_list: Optional[List[EquipmentListResponse]] = None
    message: str
    
    class Config:
        from_attributes = True


class EquipmentInventoryUpdate(BaseModel):
    """更新器材清单请求模型"""
    location_tag: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=512)


class EquipmentInventoryResponse(BaseModel):
    """器材清单响应模型
    对应《需求规格说明书》表 2-2
    """
    inventory_id: str
    user_id: str
    location_tag: str
    description: Optional[str] = None
    create_time: datetime
    equipment_count: int = 0
    equipment_list: Optional[List[EquipmentListResponse]] = None
    
    class Config:
        from_attributes = True


class EquipmentAddManualRequest(BaseModel):
    """手动添加器材请求模型"""
    inventory_id: str = Field(..., description="器材清单 ID")
    equipment_id: str = Field(..., description="器材 ID")


class EquipmentAddAutoRequest(BaseModel):
    """自动添加器材请求模型（基于识别结果）"""
    inventory_id: str = Field(..., description="器材清单 ID")
    equipment_id: str = Field(..., description="识别到的器材 ID")
    confidence: float = Field(..., ge=0, le=1, description="识别置信度")


class EquipmentDetectionRequest(BaseModel):
    """器材检测请求模型
    对应《需求规格说明书》3.2 节识别健身器材用例
    """
    image_data: str = Field(..., description="Base64 编码的图片数据")


class EquipmentDetectionResult(BaseModel):
    """器材检测结果模型"""
    equipment_id: str
    name: str
    category: str
    confidence: float
    target_muscles: Optional[List[str]] = None
    box_coordinates: Optional[List[float]] = None


class EquipmentDetectionResponse(BaseModel):
    """器材检测响应模型"""
    results: List[EquipmentDetectionResult]
    detection_time: float  # 检测耗时（秒）
    message: str = "识别成功"