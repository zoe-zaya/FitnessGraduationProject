"""
训练计划管理服务
提供训练计划的删除、修改、查询等功能
对应《需求规格说明书》3.2 节生成训练计划用例的扩展功能
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.models.user import User
from app.models.plan import TrainingPlan, PlanSession, SessionActionItem, SessionTypeEnum
from app.models.action import TrainingAction
from app.schemas.plan import (
    PlanNameUpdateRequest,
    ActionItemAddRequest,
    ActionItemUpdateRequest,
    PlanUpdateRequest
)

logger = logging.getLogger(__name__)


class PlanService:
    """训练计划管理服务"""
    
    @staticmethod
    def delete_plan(db: Session, plan_id: str, user_id: str) -> bool:
        """
        删除指定训练计划
        
        参数：
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID（用于权限验证）
        
        返回：
            是否删除成功
        """
        # 1. 验证计划归属
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.plan_id == plan_id,
            TrainingPlan.user_id == user_id
        ).first()
        
        if not plan:
            return False
        
        # 2. 级联删除关联的阶段和动作项（SQLAlchemy cascade 会自动处理）
        db.delete(plan)
        db.commit()
        
        logger.info(f"训练计划删除成功：plan_id={plan_id}, user_id={user_id}")
        return True
    
    @staticmethod
    def update_plan_name(db: Session, plan_id: str, user_id: str, request: PlanNameUpdateRequest) -> Optional[TrainingPlan]:
        """
        修改计划名称
        
        参数：
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            request: 请求数据
        
        返回：
            更新后的计划对象，如果失败返回 None
        """
        # 1. 验证计划归属
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.plan_id == plan_id,
            TrainingPlan.user_id == user_id
        ).first()
        
        if not plan:
            return None
        
        # 2. 更新名称
        plan.plan_name = request.plan_name
        db.commit()
        db.refresh(plan)
        
        logger.info(f"计划名称更新成功：plan_id={plan_id}, new_name={request.plan_name}")
        return plan
    
    @staticmethod
    def add_action_item_to_plan(
        db: Session, 
        plan_id: str, 
        user_id: str, 
        request: ActionItemAddRequest
    ) -> Optional[SessionActionItem]:
        """
        添加指定动作到指定训练计划中
        
        参数：
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            request: 请求数据
        
        返回：
            新创建的动作项对象，如果失败返回 None
        """
        import uuid
        
        # 1. 验证计划归属
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.plan_id == plan_id,
            TrainingPlan.user_id == user_id
        ).first()
        
        if not plan:
            return None
        
        # 2. 验证阶段是否存在且属于该计划
        session = db.query(PlanSession).filter(
            PlanSession.session_id == request.session_id,
            PlanSession.plan_id == plan_id
        ).first()
        
        if not session:
            return None
        
        # 3. 验证动作是否存在
        action = db.query(TrainingAction).filter(
            TrainingAction.action_id == request.action_id
        ).first()
        
        if not action:
            return None
        
        # 4. 验证动作类别与阶段类型匹配
        if session.session_type == SessionTypeEnum.WARMUP and action.action_category != "warmup":
            return None
        if session.session_type == SessionTypeEnum.MAIN and action.action_category not in ["main_strength", "main_cardio"]:
            return None
        if session.session_type == SessionTypeEnum.COOLDOWN and action.action_category != "cooldown":
            return None
        
        # 5. 计算总时长
        total_duration = PlanService._calculate_item_duration(action, request, session.session_type)
        
        # 6. 创建动作项
        new_item = SessionActionItem(
            item_id=str(uuid.uuid4()),
            session_id=request.session_id,
            action_id=request.action_id,
            sets=request.sets,
            reps_per_set=request.reps_per_set,
            rest_seconds=request.rest_seconds,
            duration_seconds=request.duration_seconds,
            lateral_coeff=request.lateral_coeff,
            total_duration_seconds=total_duration,
            execution_notes=request.execution_notes
        )
        
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        # 7. 更新阶段时长
        PlanService._recalculate_session_duration(db, session)
        
        # 8. 更新计划总时长
        PlanService._recalculate_plan_duration(db, plan)
        
        logger.info(f"动作项添加成功：item_id={new_item.item_id}, action_id={request.action_id}")
        return new_item
    
    @staticmethod
    def update_action_item(
        db: Session,
        plan_id: str,
        user_id: str,
        item_id: str,
        request: ActionItemUpdateRequest
    ) -> Optional[SessionActionItem]:
        """
        修改训练计划中指定动作的参数
        
        参数：
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            item_id: 动作项 ID
            request: 请求数据
        
        返回：
            更新后的动作项对象，如果失败返回 None
        """
        # 1. 验证计划归属
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.plan_id == plan_id,
            TrainingPlan.user_id == user_id
        ).first()
        
        if not plan:
            return None
        
        # 2. 验证动作项存在且属于该计划
        item = db.query(SessionActionItem).join(PlanSession).filter(
            SessionActionItem.item_id == item_id,
            PlanSession.plan_id == plan_id
        ).first()
        
        if not item:
            return None
        
        # 3. 获取关联动作信息
        action = db.query(TrainingAction).filter(
            TrainingAction.action_id == item.action_id
        ).first()
        
        if not action:
            return None
        
        # 4. 更新参数（只更新传入的字段）
        if request.sets is not None:
            item.sets = request.sets
        if request.reps_per_set is not None:
            item.reps_per_set = request.reps_per_set
        if request.rest_seconds is not None:
            item.rest_seconds = request.rest_seconds
        if request.duration_seconds is not None:
            item.duration_seconds = request.duration_seconds
        if request.lateral_coeff is not None:
            item.lateral_coeff = request.lateral_coeff
        if request.execution_notes is not None:
            item.execution_notes = request.execution_notes
        
        # 5. 重新计算总时长
        session = db.query(PlanSession).filter(
            PlanSession.session_id == item.session_id
        ).first()
        
        item.total_duration_seconds = PlanService._calculate_item_duration(
            action, item, session.session_type if session else "main"
        )
        
        db.commit()
        db.refresh(item)
        
        # 6. 更新阶段时长
        if session:
            PlanService._recalculate_session_duration(db, session)
            # 7. 更新计划总时长
            PlanService._recalculate_plan_duration(db, plan)
        
        logger.info(f"动作项参数更新成功：item_id={item_id}")
        return item
    
    @staticmethod
    def delete_action_item(db: Session, plan_id: str, user_id: str, item_id: str) -> bool:
        """
        删除指定的健身动作
        
        参数：
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            item_id: 动作项 ID
        
        返回：
            是否删除成功
        """
        # 1. 验证计划归属
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.plan_id == plan_id,
            TrainingPlan.user_id == user_id
        ).first()
        
        if not plan:
            return False
        
        # 2. 验证动作项存在且属于该计划
        item = db.query(SessionActionItem).join(PlanSession).filter(
            SessionActionItem.item_id == item_id,
            PlanSession.plan_id == plan_id
        ).first()
        
        if not item:
            return False
        
        # 3. 记录会话和计划信息用于后续更新
        session_id = item.session_id
        
        # 4. 删除动作项
        db.delete(item)
        db.commit()
        
        # 5. 更新阶段时长
        session = db.query(PlanSession).filter(
            PlanSession.session_id == session_id
        ).first()
        
        if session:
            PlanService._recalculate_session_duration(db, session)
            # 6. 更新计划总时长
            PlanService._recalculate_plan_duration(db, plan)
        
        logger.info(f"动作项删除成功：item_id={item_id}")
        return True
    
    @staticmethod
    def get_plan_detail(db: Session, plan_id: str, user_id: str) -> Optional[TrainingPlan]:
        """
        获取指定训练计划的全部信息
        
        参数：
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
        
        返回：
            计划对象，如果不存在返回 None
        """
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.plan_id == plan_id,
            TrainingPlan.user_id == user_id
        ).first()
        
        return plan
    
    @staticmethod
    def _calculate_item_duration(action: TrainingAction, params, session_type: str) -> int:
        """
        计算动作项总执行时长（秒）
        
        对应《需求规格说明书》表 2-7 totalDurationSeconds 计算规则
        """
        # 获取参数值（兼容请求对象和模型对象）
        if hasattr(params, 'sets'):
            sets = params.sets
            reps = params.reps_per_set
            rest = params.rest_seconds
            duration = params.duration_seconds
            lateral = params.lateral_coeff
        else:
            sets = params.get('sets')
            reps = params.get('reps_per_set')
            rest = params.get('rest_seconds')
            duration = params.get('duration_seconds')
            lateral = params.get('lateral_coeff', 1)
        
        if session_type == SessionTypeEnum.MAIN and action.action_category == "main_strength":
            # 力量训练：sets × (estimatedSeconds × repsPerSet + restSeconds) - restSeconds
            if sets and reps and rest:
                estimated = action.estimated_seconds or 3
                return sets * (estimated * reps + rest) - rest
            return 0
        elif session_type in [SessionTypeEnum.WARMUP, SessionTypeEnum.COOLDOWN]:
            # 热身/拉伸：sets × durationSeconds × lateralCoeff
            if sets and duration:
                return sets * duration * (lateral or 1)
            return 0
        else:  # main_cardio
            # 有氧训练：durationSeconds
            return duration or 0
    
    @staticmethod
    def _recalculate_session_duration(db: Session, session: PlanSession):
        """重新计算阶段总时长"""
        items = db.query(SessionActionItem).filter(
            SessionActionItem.session_id == session.session_id
        ).all()
        
        total_seconds = sum(item.total_duration_seconds for item in items)
        session.estimated_duration_minutes = total_seconds // 60
        
        db.add(session)
        db.commit()
    
    @staticmethod
    def _recalculate_plan_duration(db: Session, plan: TrainingPlan):
        """重新计算计划总时长"""
        sessions = db.query(PlanSession).filter(
            PlanSession.plan_id == plan.plan_id
        ).all()
        
        total_minutes = sum(session.estimated_duration_minutes for session in sessions)
        plan.total_duration_minutes = total_minutes
        
        db.add(plan)
        db.commit()