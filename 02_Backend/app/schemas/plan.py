"""
训练计划相关 Pydantic 模型
对应《需求规格说明书》表 2-5/2-6/2-7 业务对象
修订：支持训练计划管理功能（删除/修改/查询）
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 训练部位枚举 ====================
class TrainingPartEnum(str):
    """训练部位枚举（增肌/塑形目标使用）"""
    CHEST = "胸部"
    BACK = "背部"
    SHOULDERS = "肩部"
    ARMS = "手臂"
    LEGS = "腿部"
    GLUTES = "臀部"
    CORE = "核心"
    FULL_BODY = "全身"  # 减脂/体能默认使用


# ==================== 请求模型 ====================
class PlanGenerateRequest(BaseModel):
    """训练计划生成请求模型"""
    inventory_id: str = Field(..., description="目标器材清单 ID")
    fitness_goal: Optional[str] = Field(
        None, 
        description="健身目标（增肌/减脂/塑形/增强体能），可选，默认使用用户设置"
    )
    plan_name: Optional[str] = Field(
        None, 
        max_length=128,
        description="计划名称（可选，默认根据健身目标自动生成）"
    )
    training_part: Optional[str] = Field(
        None,
        description="训练部位（增肌/塑形目标必填：胸部/背部/肩部/手臂/腿部/臀部/核心；减脂/体能可选，默认全身）"
    )
    
    @classmethod
    def validate_training_part(cls, values):
        """验证训练部位与健身目标的匹配性"""
        fitness_goal = values.get('fitness_goal')
        training_part = values.get('training_part')
        
        valid_parts = ["胸部", "背部", "肩部", "手臂", "腿部", "臀部", "核心", "全身"]
        
        if training_part and training_part not in valid_parts:
            raise ValueError(f"无效的训练部位，可选值：{valid_parts}")
        
        if fitness_goal in ["增肌", "塑形"] and training_part == "全身":
            raise ValueError("增肌/塑形目标需指定具体训练部位（胸部/背部/肩部/手臂/腿部/臀部/核心）")
        
        if fitness_goal in ["减脂", "增强体能"] and not training_part:
            values['training_part'] = "全身"
        
        return values


class PlanNameUpdateRequest(BaseModel):
    """修改计划名称请求模型"""
    plan_name: str = Field(..., min_length=1, max_length=128, description="新的计划名称")


class ActionItemAddRequest(BaseModel):
    """添加动作项到训练计划请求模型"""
    session_id: str = Field(..., description="目标阶段 ID")
    action_id: str = Field(..., description="要添加的训练动作 ID")
    sets: Optional[int] = Field(None, ge=1, le=6, description="组数，仅适用于力量训练")
    reps_per_set: Optional[int] = Field(None, ge=5, le=20, description="每组次数，仅适用于力量训练")
    rest_seconds: Optional[int] = Field(None, ge=15, le=120, description="组间休息时间（秒），仅适用于力量训练")
    duration_seconds: Optional[int] = Field(None, ge=10, le=300, description="单次执行时长（秒），适用于有氧/热身/拉伸")
    lateral_coeff: int = Field(1, ge=1, le=2, description="侧数系数，用于拉伸/热身动作")
    execution_notes: Optional[str] = Field(None, max_length=512, description="执行备注")


class ActionItemUpdateRequest(BaseModel):
    """修改动作项参数请求模型"""
    sets: Optional[int] = Field(None, ge=1, le=6, description="组数，仅适用于力量训练")
    reps_per_set: Optional[int] = Field(None, ge=5, le=20, description="每组次数，仅适用于力量训练")
    rest_seconds: Optional[int] = Field(None, ge=15, le=120, description="组间休息时间（秒），仅适用于力量训练")
    duration_seconds: Optional[int] = Field(None, ge=10, le=300, description="单次执行时长（秒），适用于有氧/热身/拉伸")
    lateral_coeff: Optional[int] = Field(None, ge=1, le=2, description="侧数系数，用于拉伸/热身动作")
    execution_notes: Optional[str] = Field(None, max_length=512, description="执行备注")


class PlanUpdateRequest(BaseModel):
    """更新训练计划基本信息请求模型"""
    plan_name: Optional[str] = Field(None, max_length=128, description="计划名称")
    valid_days: Optional[int] = Field(None, ge=1, le=365, description="计划有效期（天）")


# ==================== 响应模型 ====================
class SessionActionItemResponse(BaseModel):
    """阶段动作项响应模型"""
    item_id: str
    action_id: str
    action_name: str
    action_category: str
    difficulty_level: str
    target_muscles: Optional[List[str]] = None
    sets: Optional[int] = None
    reps_per_set: Optional[int] = None
    rest_seconds: Optional[int] = None
    duration_seconds: Optional[int] = None
    lateral_coeff: int = 1
    total_duration_seconds: int
    execution_notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class PlanSessionResponse(BaseModel):
    """计划阶段响应模型"""
    session_id: str
    session_type: str  # warmup/main/cooldown
    sequence_order: int  # 1/2/3
    estimated_duration_minutes: int
    target_muscles: Optional[List[str]] = None
    description: Optional[str] = None
    action_items: List[SessionActionItemResponse] = []
    
    class Config:
        from_attributes = True


class TrainingPlanResponse(BaseModel):
    """训练计划响应模型"""
    plan_id: str
    user_id: str
    inventory_id: str
    inventory_name: Optional[str] = None
    plan_name: Optional[str] = None
    create_time: datetime
    valid_days: int = 30
    total_duration_minutes: int
    fitness_goal: Optional[str] = None
    training_part: Optional[str] = None
    status: str = "active"
    is_expired: bool = False
    sessions: List[PlanSessionResponse] = []
    
    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    """计划列表响应模型"""
    plan_id: str
    plan_name: str
    inventory_name: str
    fitness_goal: str
    training_part: str
    total_duration_minutes: int
    create_time: datetime
    is_expired: bool
    
    class Config:
        from_attributes = True


class DeleteResponse(BaseModel):
    """删除操作响应模型"""
    message: str