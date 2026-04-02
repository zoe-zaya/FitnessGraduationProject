"""
训练计划相关 Pydantic 模型
对应《需求规格说明书》表 2-5/2-6/2-7 业务对象
修订：支持训练部位选择，确保三阶段肌群一致
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
    """
    训练计划生成请求模型
    对应《需求规格说明书》3.2 节生成训练计划用例
    修订：新增 training_part 字段
    """
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
        
        # 增肌/塑形必须指定训练部位（不能为全身）
        if fitness_goal in ["增肌", "塑形"] and training_part == "全身":
            raise ValueError("增肌/塑形目标需指定具体训练部位（胸部/背部/肩部/手臂/腿部/臀部/核心）")
        
        # 减脂/体能默认为全身
        if fitness_goal in ["减脂", "增强体能"] and not training_part:
            values['training_part'] = "全身"
        
        return values


class SessionActionItemResponse(BaseModel):
    """
    阶段动作项响应模型
    对应《需求规格说明书》表 2-7
    """
    item_id: str
    action_id: str
    action_name: str
    action_category: str
    difficulty_level: str
    target_muscles: Optional[List[str]] = None  # ✅ 新增：目标肌群
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
    """
    计划阶段响应模型
    对应《需求规格说明书》表 2-6
    修订：target_muscles 使用 List[str] 类型（通过属性转换器解析）
    """
    session_id: str
    session_type: str  # warmup/main/cooldown
    sequence_order: int  # 1/2/3
    estimated_duration_minutes: int
    target_muscles: Optional[List[str]] = None  # ✅ 使用列表类型，通过属性转换器解析
    description: Optional[str] = None
    action_items: List[SessionActionItemResponse] = []
    
    class Config:
        from_attributes = True


class TrainingPlanResponse(BaseModel):
    """
    训练计划响应模型
    对应《需求规格说明书》表 2-5
    修订：新增 training_part 字段
    """
    plan_id: str
    user_id: str
    inventory_id: str
    inventory_name: Optional[str] = None
    plan_name: Optional[str] = None
    create_time: datetime
    valid_days: int = 30
    total_duration_minutes: int
    fitness_goal: Optional[str] = None
    training_part: Optional[str] = None  # ✅ 新增：训练部位
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
    training_part: str  # ✅ 新增：训练部位
    total_duration_minutes: int
    create_time: datetime
    is_expired: bool
    
    class Config:
        from_attributes = True


class PlanUpdateRequest(BaseModel):
    """更新训练计划请求模型"""
    plan_name: Optional[str] = Field(None, max_length=128)
    valid_days: Optional[int] = Field(None, ge=1, le=365)