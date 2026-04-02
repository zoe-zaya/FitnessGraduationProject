"""
训练计划生成 API
对应《需求规格说明书》3.2 节生成训练计划用例
修订：支持训练部位选择，确保三阶段肌群一致
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.utils.db import get_db
from app.models.user import User
from app.models.plan import TrainingPlan
from app.models.equipment import EquipmentInventory, GymEquipment
from app.models.action import TrainingAction
from app.schemas.plan import (
    PlanGenerateRequest,
    TrainingPlanResponse,
    PlanListResponse,
    PlanSessionResponse,
    SessionActionItemResponse,
    PlanUpdateRequest
)
from app.core.security import get_current_user
from app.services.plan_generator import PlanGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plan", tags=["训练计划"])


@router.post("/generate", response_model=TrainingPlanResponse, summary="生成训练计划")
async def generate_training_plan(
    request: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据用户身体数据、健身目标、训练部位和器材清单生成个性化训练计划
    
    对应《需求规格说明书》3.2 节生成训练计划用例
    
    前置条件：
    - 用户已录入身体基本数据和健身目标
    - 用户至少拥有一个健身房的器材信息
    - 增肌/塑形目标需指定训练部位（胸部/背部/肩部/手臂/腿部/臀部/核心）
    - 减脂/体能目标默认为全身训练
    
    返回：
    完整的三阶段训练计划，包含：
    - 计划基础信息（ID、名称、有效期、总时长、训练部位）
    - 健身目标（存储在计划中）
    - 三阶段结构（热身→正式→拉伸，目标肌群一致）
    - 每个阶段的动作项列表及执行参数
    - 个性化执行备注
    """
    # 1. 验证器材清单归属
    inventory = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == request.inventory_id,
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    if not inventory:
        logger.warning(f"器材清单不存在：inventory_id={request.inventory_id}, user_id={current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="器材清单不存在或无权访问"
        )
    
    # 2. 验证训练部位与健身目标的匹配性
    fitness_goal = request.fitness_goal or current_user.fitness_goal
    training_part = request.training_part
    
    if fitness_goal in ["增肌", "塑形"] and (not training_part or training_part == "全身"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="增肌/塑形目标需指定具体训练部位（胸部/背部/肩部/手臂/腿部/臀部/核心）"
        )
    
    # 3. 初始化计划生成器
    generator = PlanGenerator(
        db=db,
        user=current_user,
        inventory_id=request.inventory_id
    )
    
    try:
        # 4. 执行计划生成（传入 fitness_goal、plan_name、training_part）
        logger.info(f"开始生成计划：user_id={current_user.user_id}, inventory_id={request.inventory_id}, "
                   f"fitness_goal={fitness_goal}, training_part={training_part}")
        
        plan = generator.generate_plan(
            fitness_goal=fitness_goal,
            plan_name=request.plan_name,
            training_part=training_part
        )
        
        # 5. 构建响应
        logger.info(f"计划生成成功：plan_id={plan.plan_id}, plan_name={plan.plan_name}, "
                   f"fitness_goal={plan.fitness_goal}, training_part={plan.training_part}, "
                   f"total_duration={plan.total_duration_minutes}min")
        
        return _build_plan_response(plan, db)
        
    except ValueError as e:
        # 业务验证错误
        logger.warning(f"计划生成验证失败：{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # 记录详细异常堆栈
        logger.error(f"计划生成异常：{type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计划生成失败：{str(e)}"
        )


@router.get("/", response_model=List[PlanListResponse], summary="获取用户所有训练计划")
async def get_user_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有训练计划列表"""
    plans = db.query(TrainingPlan).filter(
        TrainingPlan.user_id == current_user.user_id
    ).order_by(TrainingPlan.create_time.desc()).all()
    
    response_list = []
    for plan in plans:
        # 查询器材清单名称
        inventory = db.query(EquipmentInventory).filter(
            EquipmentInventory.inventory_id == plan.inventory_id
        ).first()
        inventory_name = inventory.location_tag if inventory else "未知健身房"
        
        response_list.append(PlanListResponse(
            plan_id=plan.plan_id,
            plan_name=plan.plan_name or "未命名计划",
            inventory_name=inventory_name,
            fitness_goal=plan.fitness_goal or "未设置",
            training_part=plan.training_part or "全身",  # ✅ 新增：训练部位
            total_duration_minutes=plan.total_duration_minutes,
            create_time=plan.create_time,
            is_expired=_is_plan_expired(plan)
        ))
    
    return response_list


@router.get("/{plan_id}", response_model=TrainingPlanResponse, summary="获取训练计划详情")
async def get_plan_detail(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定训练计划的详细信息"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    return _build_plan_response(plan, db)


@router.put("/{plan_id}", response_model=TrainingPlanResponse, summary="更新训练计划")
async def update_plan(
    plan_id: str,
    request: PlanUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新训练计划信息（名称、有效期等）"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    # 更新字段
    if request.plan_name is not None:
        plan.plan_name = request.plan_name
    if request.valid_days is not None:
        plan.valid_days = request.valid_days
    
    db.commit()
    db.refresh(plan)
    
    return _build_plan_response(plan, db)


@router.delete("/{plan_id}", summary="删除训练计划")
async def delete_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除指定训练计划"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    db.delete(plan)
    db.commit()
    
    return {"message": "训练计划删除成功"}


@router.post("/{plan_id}/extend", summary="延长计划有效期")
async def extend_plan_validity(
    plan_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """延长训练计划有效期"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    plan.valid_days += days
    db.commit()
    
    return {"message": f"计划有效期已延长{days}天"}


# ==================== 辅助函数 ====================

def _is_plan_expired(plan: TrainingPlan) -> bool:
    """检查计划是否过期"""
    if not plan.create_time:
        return True
    expire_time = plan.create_time + timedelta(days=plan.valid_days)
    return datetime.now() > expire_time


def _build_plan_response(plan: TrainingPlan, db: Session) -> TrainingPlanResponse:
    """
    构建计划响应对象
    注意：fitness_goal 和 training_part 从 plan 对象获取
    target_muscles 通过属性转换器解析为列表
    """
    # 查询器材清单名称
    inventory = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == plan.inventory_id
    ).first()
    inventory_name = inventory.location_tag if inventory else "未知健身房"
    
    # 构建阶段响应
    sessions_response = []
    for session in sorted(plan.sessions, key=lambda s: s.sequence_order):
        action_items_response = []
        for item in session.action_items:
            # 查询动作信息
            action = db.query(TrainingAction).filter(
                TrainingAction.action_id == item.action_id
            ).first()
            
            action_items_response.append(SessionActionItemResponse(
                item_id=item.item_id,
                action_id=item.action_id,
                action_name=action.name if action else "未知动作",
                action_category=action.action_category if action else "unknown",
                difficulty_level=action.difficulty_level if action else "未知",
                target_muscles=action.get_target_muscles_list() if action else [],  # ✅ 新增：目标肌群
                sets=item.sets,
                reps_per_set=item.reps_per_set,
                rest_seconds=item.rest_seconds,
                duration_seconds=item.duration_seconds,
                lateral_coeff=item.lateral_coeff,
                total_duration_seconds=item.total_duration_seconds,
                execution_notes=item.execution_notes
            ))
        
        # ✅ 使用属性转换器解析 target_muscles 为列表
        sessions_response.append(PlanSessionResponse(
            session_id=session.session_id,
            session_type=session.session_type,
            sequence_order=session.sequence_order,
            estimated_duration_minutes=session.estimated_duration_minutes,
            target_muscles=session.target_muscles_list,  # ✅ 使用属性转换器解析为列表
            description=session.description,
            action_items=action_items_response
        ))
    
    return TrainingPlanResponse(
        plan_id=plan.plan_id,
        user_id=plan.user_id,
        inventory_id=plan.inventory_id,
        inventory_name=inventory_name,
        plan_name=plan.plan_name,
        create_time=plan.create_time,
        valid_days=plan.valid_days,
        total_duration_minutes=plan.total_duration_minutes,
        fitness_goal=plan.fitness_goal,
        training_part=plan.training_part,  # ✅ 新增：训练部位
        status=plan.status,
        sessions=sessions_response,
        is_expired=_is_plan_expired(plan)
    )