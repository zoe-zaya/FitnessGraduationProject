"""
训练计划相关 Pydantic 模型
对应需求规格说明书 2.1 版
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ==================== 枚举定义 ====================

class PlanTypeEnum(str, Enum):
    """计划类型"""
    FAT_LOSS = "FAT_LOSS"
    MUSCLE_GAIN = "MUSCLE_GAIN"


class SchemeTypeEnum(str, Enum):
    """分化方案"""
    ONE_SPLIT = "ONE_SPLIT"
    TWO_SPLIT = "TWO_SPLIT"
    THREE_SPLIT = "THREE_SPLIT"
    FOUR_SPLIT = "FOUR_SPLIT"


class SessionTypeEnum(str, Enum):
    """阶段类型"""
    WARMUP = "WARMUP"
    MAIN = "MAIN"
    COOLDOWN = "COOLDOWN"


class ScheduleStatusEnum(str, Enum):
    """日程状态"""
    PLANNED = "PLANNED"
    COMPLETED = "COMPLETED"
    POSTPONED = "POSTPONED"
    REST = "REST"


# ==================== 请求模型 ====================

class PlanGenerateRequest(BaseModel):
    """
    训练计划生成请求模型
    V2.1 修订：支持计划类型和分化方案选择
    """
    inventory_id: str = Field(..., description="目标器材清单 ID")
    plan_type: PlanTypeEnum = Field(..., description="计划类型（减脂/增肌）")
    scheme_type: Optional[SchemeTypeEnum] = Field(None, description="分化方案（仅增肌计划需要）")
    training_part: Optional[str] = Field(None, max_length=32, description="训练部位（增肌计划需要）")
    plan_name: Optional[str] = Field(None, max_length=128, description="计划名称")
    
    class Config:
        use_enum_values = True


class ActionItemAddRequest(BaseModel):
    """添加动作项到训练计划请求模型"""
    session_id: str = Field(..., description="目标阶段 ID")
    action_id: str = Field(..., description="要添加的训练动作 ID")
    sets: Optional[int] = Field(None, ge=1, le=6, description="组数")
    reps_per_set: Optional[int] = Field(None, ge=5, le=20, description="每组次数")
    rest_seconds_default: Optional[int] = Field(60, ge=30, le=300, description="默认休息时长（秒）")  # ✅ V2.1 默认 60 秒
    duration_seconds: Optional[int] = Field(None, ge=10, le=300, description="单次执行时长（秒）")
    duration_minutes: Optional[int] = Field(None, ge=1, le=120, description="有氧动作时长（分钟）")
    execution_notes: Optional[str] = Field(None, max_length=512, description="执行备注")


class ActionItemUpdateRequest(BaseModel):
    """修改动作项参数请求模型"""
    sets: Optional[int] = Field(None, ge=1, le=6, description="组数")
    reps_per_set: Optional[int] = Field(None, ge=5, le=20, description="每组次数")
    rest_seconds_default: Optional[int] = Field(None, ge=30, le=300, description="默认休息时长（秒）")
    duration_seconds: Optional[int] = Field(None, ge=10, le=300, description="单次执行时长（秒）")
    duration_minutes: Optional[int] = Field(None, ge=1, le=120, description="有氧动作时长（分钟）")
    execution_notes: Optional[str] = Field(None, max_length=512, description="执行备注")
    weight_records: Optional[List[float]] = Field(None, description="每组训练重量记录")


class ActionItemReplaceRequest(BaseModel):
    """替换动作项请求模型"""
    new_action_id: str = Field(..., description="新的训练动作 ID")
    keep_params: bool = Field(True, description="是否保留原参数")


class SchedulePostponeRequest(BaseModel):
    """延后训练日程请求模型"""
    days: int = Field(..., ge=1, le=3, description="延后天数（1-3 天）")


class PlanUpdateRequest(BaseModel):
    """更新训练计划基本信息请求模型"""
    plan_name: Optional[str] = Field(None, max_length=128, description="计划名称")
    status: Optional[str] = Field(None, description="计划状态")


# ==================== 响应模型 ====================

class SessionActionItemResponse(BaseModel):
    """阶段动作项响应模型"""
    item_id: str
    action_id: str
    action_name: str
    action_category: str
    difficulty_level: str
    target_muscles: Optional[List[str]] = None
    sequence_order: int = 1
    sets: Optional[int] = None
    reps_per_set: Optional[int] = None
    rest_seconds_default: int = 60  # ✅ V2.1 默认 60 秒
    duration_seconds: Optional[int] = None
    duration_minutes: Optional[int] = None
    lateral_coeff: int = 1
    total_duration_seconds: int
    execution_notes: Optional[str] = None
    weight_records: Optional[List[float]] = None  # ✅ V2.1 新增
    
    class Config:
        from_attributes = True
        use_enum_values = True


class PlanSessionResponse(BaseModel):
    """计划阶段响应模型"""
    session_id: str
    session_type: str
    sequence_order: int
    estimated_duration_minutes: int
    target_muscles: Optional[List[str]] = None
    training_part: Optional[str] = None
    description: Optional[str] = None
    action_items: List[SessionActionItemResponse] = []
    
    class Config:
        from_attributes = True
        use_enum_values = True


class TrainingScheduleResponse(BaseModel):
    """训练日程响应模型"""
    schedule_id: str
    plan_id: str
    scheduled_date: date
    session_type: Optional[str] = None
    training_part: Optional[str] = None
    target_muscles: Optional[List[str]] = None
    status: str
    postpone_count: int = 0
    can_postpone: bool = True
    
    class Config:
        from_attributes = True
        use_enum_values = True


class TrainingPlanResponse(BaseModel):
    """训练计划响应模型"""
    plan_id: str
    user_id: str
    inventory_id: str
    inventory_name: Optional[str] = None
    plan_name: Optional[str] = None
    create_time: datetime
    plan_type: str  # ✅ V2.1 新增
    scheme_type: Optional[str] = None  # ✅ V2.1 新增
    cycle_rule: Optional[str] = None  # ✅ V2.1 新增
    status: str = "active"
    fitness_goal: Optional[str] = None
    training_part: Optional[str] = None
    sessions: List[PlanSessionResponse] = []
    weekly_schedule: Optional[List[TrainingScheduleResponse]] = None  # ✅ V2.1 新增 7 天日程
    
    class Config:
        from_attributes = True
        use_enum_values = True


class PlanListResponse(BaseModel):
    """计划列表响应模型"""
    plan_id: str
    plan_name: str
    inventory_name: str
    plan_type: str  # ✅ V2.1 新增
    scheme_type: Optional[str] = None
    cycle_rule: Optional[str] = None
    create_time: datetime
    status: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class DeleteResponse(BaseModel):
    """删除操作响应模型"""
    message: str


class PostponeResponse(BaseModel):
    """延后操作响应模型"""
    message: str
    new_scheduled_date: date
    remaining_postpone_days: int