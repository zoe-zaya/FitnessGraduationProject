"""
训练计划生成与管理 API（V2.1 版）
对应需求规格说明书 2.1 版
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.utils.db import get_db
from app.models.user import User
from app.models.plan import TrainingPlan, TrainingSchedule, ScheduleStatusEnum
from app.models.equipment import EquipmentInventory
from app.models.action import TrainingAction
from app.schemas.plan import (
    PlanGenerateRequest,
    TrainingPlanResponse,
    PlanListResponse,
    PlanSessionResponse,
    SessionActionItemResponse,
    TrainingScheduleResponse,
    PlanUpdateRequest,
    ActionItemAddRequest,
    ActionItemUpdateRequest,
    ActionItemReplaceRequest,
    SchedulePostponeRequest,
    DeleteResponse,
    PostponeResponse
)
from app.core.security import get_current_user
from app.services.plan_generator_v2 import PlanGeneratorV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plan/v2", tags=["训练计划 V2"])


# ==================== 计划生成 ====================

@router.post("/generate", response_model=TrainingPlanResponse, summary="生成训练计划（V2.1）")
async def generate_training_plan(
    request: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成训练计划（V2.1 版）
    
    前置条件：
    - 用户已录入身体基本数据和健身目标
    - 用户至少拥有一个健身房的器材信息
    - 增肌计划需指定分化方案
    
    返回：
    完整的训练计划，包含三阶段详情及 7 天日程安排
    """
    # 1. 验证器材清单归属
    inventory = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == request.inventory_id,
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="器材清单不存在或无权访问"
        )
    
    # 2. 初始化计划生成器
    generator = PlanGeneratorV2(
        db=db,
        user=current_user,
        inventory_id=request.inventory_id
    )
    
    try:
        # 3. 执行计划生成
        logger.info(f"开始生成计划：user_id={current_user.user_id}, "
                   f"plan_type={request.plan_type}, scheme_type={request.scheme_type}")
        
        plan = generator.generate_plan(
            plan_type=request.plan_type,
            scheme_type=request.scheme_type,
            training_part=request.training_part,
            plan_name=request.plan_name
        )
        
        # 4. 构建响应
        return _build_plan_response(plan, db)
        
    except ValueError as e:
        logger.warning(f"计划生成验证失败：{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"计划生成异常：{type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计划生成失败：{str(e)}"
        )


# ==================== 计划查询 ====================

@router.get("/getAllPlan", response_model=List[PlanListResponse], summary="获取用户所有训练计划")
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
        inventory = db.query(EquipmentInventory).filter(
            EquipmentInventory.inventory_id == plan.inventory_id
        ).first()
        inventory_name = inventory.location_tag if inventory else "未知健身房"
        
        response_list.append(PlanListResponse(
            plan_id=plan.plan_id,
            plan_name=plan.plan_name or "未命名计划",
            inventory_name=inventory_name,
            plan_type=plan.plan_type.value if plan.plan_type else "FAT_LOSS",
            scheme_type=plan.scheme_type.value if plan.scheme_type else None,
            cycle_rule=plan.cycle_rule,
            create_time=plan.create_time,
            status=plan.status
        ))
    
    return response_list


@router.get("/getPlan/{plan_id}", response_model=TrainingPlanResponse, summary="获取训练计划详情")
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


@router.get("/schedule/{plan_id}", response_model=List[TrainingScheduleResponse], summary="获取 7 天训练日程")
async def get_weekly_schedule(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取从当天开始的 7 天训练安排"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    today = datetime.now().date()
    end_date = today + timedelta(days=7)
    
    schedules = db.query(TrainingSchedule).filter(
        TrainingSchedule.plan_id == plan_id,
        TrainingSchedule.scheduled_date >= today,
        TrainingSchedule.scheduled_date <= end_date
    ).order_by(TrainingSchedule.scheduled_date).all()
    
    response_list = []
    for schedule in schedules:
        session_type = None
        training_part = None
        target_muscles = None
        if schedule.session_id:
            from app.models.plan import PlanSession
            session = db.query(PlanSession).filter(
                PlanSession.session_id == schedule.session_id
            ).first()
            if session:
                session_type = session.session_type.value if session.session_type else None
                training_part = session.training_part
                if session.target_muscles:
                    import json as _json
                    try:
                        target_muscles = _json.loads(session.target_muscles)
                    except:
                        target_muscles = None

        response_list.append(TrainingScheduleResponse(
            schedule_id=schedule.schedule_id,
            plan_id=schedule.plan_id,
            scheduled_date=schedule.scheduled_date,
            session_type=session_type,
            training_part=training_part,
            target_muscles=target_muscles,
            status=schedule.status.value if schedule.status else "PLANNED",
            postpone_count=schedule.postpone_count,
            can_postpone=schedule.can_postpone(1)
        ))
    
    return response_list


# ==================== 计划管理 ====================

@router.put("/updatePlan/{plan_id}", response_model=TrainingPlanResponse, summary="更新训练计划基本信息")
async def update_plan(
    plan_id: str,
    request: PlanUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新训练计划基本信息"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    if request.plan_name is not None:
        plan.plan_name = request.plan_name
    if request.status is not None:
        plan.status = request.status
    
    db.commit()
    db.refresh(plan)
    
    return _build_plan_response(plan, db)


@router.delete("/deletePlan/{plan_id}", response_model=DeleteResponse, summary="删除训练计划")
async def delete_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除训练计划"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    try:
        # 先删除关联的动作项和阶段
        from app.models.plan import PlanSession, SessionActionItem, TrainingSchedule
        
        # 删除关联的训练日程
        db.query(TrainingSchedule).filter(
            TrainingSchedule.plan_id == plan_id
        ).delete()
        
        # 删除关联的阶段和动作项
        sessions = db.query(PlanSession).filter(
            PlanSession.plan_id == plan_id
        ).all()
        
        for session in sessions:
            # 删除关联的动作项
            db.query(SessionActionItem).filter(
                SessionActionItem.session_id == session.session_id
            ).delete()
            # 删除阶段
            db.delete(session)
        
        # 最后删除训练计划
        db.delete(plan)
        db.commit()
        
        return DeleteResponse(message="训练计划删除成功")
        
    except Exception as e:
        db.rollback()
        if "foreign key constraint" in str(e):
            if "plan_session" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="删除失败：请先删除关联的计划阶段"
                )
            elif "session_action_item" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="删除失败：请先删除关联的动作项"
                )
            elif "training_schedule" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="删除失败：请先删除关联的训练日程"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"删除失败：存在外键约束，请先处理相关数据"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除失败：{str(e)}"
            )


# ==================== 动作项管理 ====================

@router.post("/addAction/{plan_id}", response_model=SessionActionItemResponse, summary="添加动作项")
async def add_action_item(
    plan_id: str,
    request: ActionItemAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加指定动作到训练计划"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )
    
    # 验证动作是否符合器材约束
    action = db.query(TrainingAction).filter(
        TrainingAction.action_id == request.action_id
    ).first()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动作不存在"
        )
    
    # 检查器材可用性
    from app.models.equipment import inventory_equipment_rel
    if action.equipment_id and action.equipment_id != "none":
        has_equipment = db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == plan.inventory_id,
            inventory_equipment_rel.c.equipment_id == action.equipment_id
        ).first()
        
        if not has_equipment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该动作所需器材您当前健身房未配备"
            )
    
    # 创建动作项
    import uuid
    from app.models.plan import SessionActionItem
    
    total_duration = request.duration_minutes * 60 if request.duration_minutes else (request.sets or 2) * (request.duration_seconds or 30)
    
    new_item = SessionActionItem(
        item_id=str(uuid.uuid4()),
        session_id=request.session_id,
        action_id=request.action_id,
        sets=request.sets,
        reps_per_set=request.reps_per_set,
        rest_seconds_default=request.rest_seconds_default or 60,
        duration_seconds=request.duration_seconds,
        duration_minutes=request.duration_minutes,
        lateral_coeff=1,
        total_duration_seconds=total_duration,
        execution_notes=request.execution_notes
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return SessionActionItemResponse(
        item_id=new_item.item_id,
        action_id=new_item.action_id,
        action_name=action.name,
        action_category=action.action_category.value if action.action_category else "unknown",
        difficulty_level=action.difficulty_level.value if action.difficulty_level else "unknown",
        target_muscles=action.get_target_muscles_list(),
        sequence_order=new_item.sequence_order,
        sets=new_item.sets,
        reps_per_set=new_item.reps_per_set,
        rest_seconds_default=new_item.rest_seconds_default,
        duration_seconds=new_item.duration_seconds,
        duration_minutes=new_item.duration_minutes,
        lateral_coeff=new_item.lateral_coeff,
        total_duration_seconds=new_item.total_duration_seconds,
        execution_notes=new_item.execution_notes
    )


@router.put("/updateAction/{plan_id}/{item_id}", response_model=SessionActionItemResponse, summary="修改动作项参数")
async def update_action_item(
    plan_id: str,
    item_id: str,
    request: ActionItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改训练计划中指定动作的参数"""
    from app.models.plan import SessionActionItem, PlanSession
    
    item = db.query(SessionActionItem).join(PlanSession).filter(
        SessionActionItem.item_id == item_id,
        PlanSession.plan_id == plan_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动作项不存在或无权修改"
        )
    
    # 更新参数
    if request.sets is not None:
        item.sets = request.sets
    if request.reps_per_set is not None:
        item.reps_per_set = request.reps_per_set
    if request.rest_seconds_default is not None:
        item.rest_seconds_default = request.rest_seconds_default
    if request.duration_seconds is not None:
        item.duration_seconds = request.duration_seconds
    if request.duration_minutes is not None:
        item.duration_minutes = request.duration_minutes
    if request.execution_notes is not None:
        item.execution_notes = request.execution_notes
    if request.weight_records is not None:
        item.weight_records = request.weight_records
    
    db.commit()
    db.refresh(item)
    
    action = db.query(TrainingAction).filter(
        TrainingAction.action_id == item.action_id
    ).first()
    
    return SessionActionItemResponse(
        item_id=item.item_id,
        action_id=item.action_id,
        action_name=action.name if action else "未知动作",
        action_category=action.action_category.value if action and action.action_category else "unknown",
        difficulty_level=action.difficulty_level.value if action and action.difficulty_level else "unknown",
        target_muscles=action.get_target_muscles_list() if action else [],
        sequence_order=item.sequence_order,
        sets=item.sets,
        reps_per_set=item.reps_per_set,
        rest_seconds_default=item.rest_seconds_default,
        duration_seconds=item.duration_seconds,
        duration_minutes=item.duration_minutes,
        lateral_coeff=item.lateral_coeff,
        total_duration_seconds=item.total_duration_seconds,
        execution_notes=item.execution_notes,
        weight_records=item.weight_records
    )


@router.delete("/deleteAction/{plan_id}/{item_id}", response_model=DeleteResponse, summary="删除动作项")
async def delete_action_item(
    plan_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除训练动作"""
    from app.models.plan import SessionActionItem, PlanSession
    
    item = db.query(SessionActionItem).join(PlanSession).filter(
        SessionActionItem.item_id == item_id,
        PlanSession.plan_id == plan_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动作项不存在或无权删除"
        )
    
    db.delete(item)
    db.commit()
    
    return DeleteResponse(message="动作项删除成功")


@router.post("/replaceAction/{plan_id}/{item_id}", response_model=SessionActionItemResponse, summary="替换动作项")
async def replace_action_item(
    plan_id: str,
    item_id: str,
    request: ActionItemReplaceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """替换训练动作"""
    from app.models.plan import SessionActionItem, PlanSession
    from app.models.equipment import inventory_equipment_rel

    item = db.query(SessionActionItem).join(PlanSession).filter(
        SessionActionItem.item_id == item_id,
        PlanSession.plan_id == plan_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动作项不存在"
        )
    
    new_action = db.query(TrainingAction).filter(
        TrainingAction.action_id == request.new_action_id
    ).first()
    
    if not new_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新动作不存在"
        )

    # 检查新动作的器材可用性
    if new_action.equipment_id and new_action.equipment_id != "none":
        has_equipment = db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == plan.inventory_id,
            inventory_equipment_rel.c.equipment_id == new_action.equipment_id
        ).first()

        if not has_equipment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该动作所需器材您当前健身房未配备"
            )

    # 更新动作 ID
    item.action_id = request.new_action_id
    
    # 如果保留参数，更新执行备注
    if request.keep_params:
        item.execution_notes = f"原动作已替换为：{new_action.name}"
    
    db.commit()
    db.refresh(item)
    
    return SessionActionItemResponse(
        item_id=item.item_id,
        action_id=item.action_id,
        action_name=new_action.name,
        action_category=new_action.action_category.value if new_action.action_category else "unknown",
        difficulty_level=new_action.difficulty_level.value if new_action.difficulty_level else "unknown",
        target_muscles=new_action.get_target_muscles_list(),
        sequence_order=item.sequence_order,
        sets=item.sets,
        reps_per_set=item.reps_per_set,
        rest_seconds_default=item.rest_seconds_default,
        duration_seconds=item.duration_seconds,
        duration_minutes=item.duration_minutes,
        lateral_coeff=item.lateral_coeff,
        total_duration_seconds=item.total_duration_seconds,
        execution_notes=item.execution_notes,
        weight_records=item.weight_records
    )


# ==================== 日程管理 ====================

@router.post("/postponeSchedule/{plan_id}/{schedule_id}", response_model=PostponeResponse, summary="延后训练")
async def postpone_schedule(
    plan_id: str,
    schedule_id: str,
    request: SchedulePostponeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    延后训练（支持 1-3 天）
    
    逻辑：将指定训练日延后 N 天，原日期变为休息日，
    该训练日之后的所有日程整体后移 N 天。
    """
    import uuid
    
    schedule = db.query(TrainingSchedule).join(TrainingPlan).filter(
        TrainingSchedule.schedule_id == schedule_id,
        TrainingSchedule.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练日程不存在或无权访问"
        )
    
    if schedule.status == ScheduleStatusEnum.REST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="休息日不可延后"
        )
    
    if not schedule.can_postpone(request.days):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已达到最大延后次数限制（最多 3 天）"
        )
    
    postpone_date = schedule.scheduled_date
    days = request.days
    
    later_schedules = db.query(TrainingSchedule).filter(
        TrainingSchedule.plan_id == plan_id,
        TrainingSchedule.scheduled_date > postpone_date
    ).order_by(TrainingSchedule.scheduled_date).all()
    
    for s in later_schedules:
        s.scheduled_date = s.scheduled_date + timedelta(days=days)
    
    schedule.scheduled_date = postpone_date + timedelta(days=days)
    schedule.postpone_count += days
    schedule.status = ScheduleStatusEnum.POSTPONED
    
    rest_schedule = TrainingSchedule(
        schedule_id=str(uuid.uuid4()),
        plan_id=plan_id,
        scheduled_date=postpone_date,
        status=ScheduleStatusEnum.REST
    )
    db.add(rest_schedule)
    
    db.commit()
    db.refresh(schedule)
    
    remaining_days = 3 - schedule.postpone_count
    
    return PostponeResponse(
        message=f"训练已延后{request.days}天",
        new_scheduled_date=schedule.scheduled_date,
        remaining_postpone_days=remaining_days
    )


# ==================== 辅助函数 ====================

def _build_plan_response(plan: TrainingPlan, db: Session) -> TrainingPlanResponse:
    """构建计划响应对象"""
    # 查询器材清单名称
    inventory = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == plan.inventory_id
    ).first()
    inventory_name = inventory.location_tag if inventory else "未知健身房"
    
    # 构建阶段响应
    sessions_response = []
    fat_loss_part_order = {"推": 0, "腿": 1, "拉": 2}
    for session in sorted(plan.sessions, key=lambda s: (
        fat_loss_part_order.get(s.training_part, 99) if s.training_part else 0,
        s.sequence_order
    )):
        action_items_response = []
        for item in session.action_items:
            action = db.query(TrainingAction).filter(
                TrainingAction.action_id == item.action_id
            ).first()
            
            action_items_response.append(SessionActionItemResponse(
                item_id=item.item_id,
                action_id=item.action_id,
                action_name=action.name if action else "未知动作",
                action_category=action.action_category.value if action and action.action_category else "unknown",
                difficulty_level=action.difficulty_level.value if action and action.difficulty_level else "unknown",
                target_muscles=action.get_target_muscles_list() if action else [],
                sequence_order=item.sequence_order,
                sets=item.sets,
                reps_per_set=item.reps_per_set,
                rest_seconds_default=item.rest_seconds_default,
                duration_seconds=item.duration_seconds,
                duration_minutes=item.duration_minutes,
                lateral_coeff=item.lateral_coeff,
                total_duration_seconds=item.total_duration_seconds,
                execution_notes=item.execution_notes,
                weight_records=item.weight_records
            ))
        
        import json
        sessions_response.append(PlanSessionResponse(
            session_id=session.session_id,
            session_type=session.session_type.value if session.session_type else "WARMUP",
            sequence_order=session.sequence_order,
            estimated_duration_minutes=session.estimated_duration_minutes,
            target_muscles=json.loads(session.target_muscles) if session.target_muscles else [],
            training_part=session.training_part,
            description=session.description,
            action_items=action_items_response
        ))
    
    # 构建 7 天日程响应
    today = datetime.now().date()
    schedules = db.query(TrainingSchedule).filter(
        TrainingSchedule.plan_id == plan.plan_id,
        TrainingSchedule.scheduled_date >= today
    ).order_by(TrainingSchedule.scheduled_date).all()
    
    weekly_schedule = []
    for schedule in schedules:
        session_type = None
        training_part = None
        target_muscles = None
        if schedule.session_id:
            from app.models.plan import PlanSession
            session = db.query(PlanSession).filter(
                PlanSession.session_id == schedule.session_id
            ).first()
            if session:
                session_type = session.session_type.value if session.session_type else None
                training_part = session.training_part
                if session.target_muscles:
                    import json as _json
                    try:
                        target_muscles = _json.loads(session.target_muscles)
                    except:
                        target_muscles = None

        weekly_schedule.append(TrainingScheduleResponse(
            schedule_id=schedule.schedule_id,
            plan_id=schedule.plan_id,
            scheduled_date=schedule.scheduled_date,
            session_type=session_type,
            training_part=training_part,
            target_muscles=target_muscles,
            status=schedule.status.value if schedule.status else "PLANNED",
            postpone_count=schedule.postpone_count,
            can_postpone=schedule.can_postpone(1)
        ))
    
    return TrainingPlanResponse(
        plan_id=plan.plan_id,
        user_id=plan.user_id,
        inventory_id=plan.inventory_id,
        inventory_name=inventory_name,
        plan_name=plan.plan_name,
        create_time=plan.create_time,
        plan_type=plan.plan_type.value if plan.plan_type else "FAT_LOSS",
        scheme_type=plan.scheme_type.value if plan.scheme_type else None,
        cycle_rule=plan.cycle_rule,
        status=plan.status,
        fitness_goal=plan.fitness_goal.value if plan.fitness_goal else None,
        training_part=plan.training_part,
        sessions=sessions_response,
        weekly_schedule=weekly_schedule
    )