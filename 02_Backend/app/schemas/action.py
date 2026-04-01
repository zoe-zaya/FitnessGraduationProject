"""
训练动作相关 Pydantic 模型
对应《需求规格说明书》表 2-4 TrainingAction 业务对象
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ActionRecommendationRequest(BaseModel):
    """
    动作推荐请求模型
    对应《需求规格说明书》3.2 节推荐训练动作用例
    修改：top_k 改为可选参数，不限制返回数量
    """
    equipment_id: str = Field(..., description="识别到的器材 ID")
    action_category: Optional[str] = Field(
        None, 
        description="指定动作类别（warmup/main_cardio/main_strength/cooldown）"
    )
    top_k: Optional[int] = Field(
        None, 
        ge=1, 
        description="限制返回数量（可选，不传则返回所有匹配动作）"
    )
    # ✅ 新增：是否返回匹配评分
    include_score: bool = Field(
        True, 
        description="是否在响应中返回匹配度评分（默认返回）"
    )

class ActionRecommendationResponse(BaseModel):
    """
    动作推荐响应模型
    对应《需求规格说明书》3.2 节推荐训练动作用例
    每个动作附带：动作名称与目标肌群、动作类别标识、难度等级标识、
    标准动作演示视频/图片、安全注意事项
    """
    action_id: str
    name: str
    action_category: str
    difficulty_level: str
    target_muscles: Optional[List[str]] = None
    equipment_name: Optional[str] = None
    video_demo_url: Optional[str] = None
    image_url: Optional[str] = None
    safety_tips: Optional[str] = None
    estimated_seconds: int
    match_score: float = 0.0  # 匹配度评分（用于排序）
    
    class Config:
        from_attributes = True


class ActionDetailResponse(BaseModel):
    """
    动作详细信息响应模型
    对应《需求规格说明书》3.2 节查看动作指导用例
    """
    action_id: str
    name: str
    action_category: str
    difficulty_level: str
    target_muscles: Optional[List[str]] = None
    equipment_id: str
    equipment_name: Optional[str] = None
    video_demo_url: Optional[str] = None
    image_url: Optional[str] = None
    safety_tips: Optional[str] = None
    estimated_seconds: int
    sets_range: str = "3-4 组"  # 建议组数范围
    reps_range: str = "8-12 次/组"  # 建议次数范围（力量训练）
    duration_range: str = "30-60 秒"  # 建议时长范围（有氧/拉伸）
    
    class Config:
        from_attributes = True

class ActionQueryRequest(BaseModel):
    """
    动作查询请求模型
    支持按类别和/或目标肌群筛选
    对应《需求规格说明书》3.2 节查看动作指导用例
    """
    action_category: Optional[str] = Field(
        None, 
        description="动作类别（warmup/main_cardio/main_strength/cooldown）"
    )
    target_muscle: Optional[str] = Field(
        None, 
        description="目标肌群（如'胸大肌'、'股四头肌'、'核心肌群'等）"
    )
    
    @field_validator('action_category')
    def validate_action_category(cls, v):
        """验证动作类别"""
        if v is not None:
            valid_categories = ["warmup", "main_cardio", "main_strength", "cooldown"]
            if v not in valid_categories:
                raise ValueError(f"无效的动作类别，可选值：{valid_categories}")
        return v


class ActionInfoResponse(BaseModel):
    """
    动作信息响应模型
    对应《需求规格说明书》表 2-4 TrainingAction 对象
    """
    action_id: str
    name: str
    action_category: str
    difficulty_level: str
    target_muscles: Optional[List[str]] = None
    equipment_id: str
    equipment_name: Optional[str] = None
    video_demo_url: Optional[str] = None
    image_url: Optional[str] = None
    safety_tips: Optional[str] = None
    estimated_seconds: int
    
    class Config:
        from_attributes = True


class ActionLibraryResponse(BaseModel):
    """
    动作库响应模型
    用于返回所有动作列表
    """
    total_count: int
    actions: List[ActionInfoResponse]
    category_stats: dict  # 各类别动作数量统计
    
    class Config:
        from_attributes = True