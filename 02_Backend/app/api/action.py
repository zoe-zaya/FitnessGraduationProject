"""
动作推荐与查询 API
对应《需求规格说明书》3.2 节：
- 推荐训练动作
- 查看动作指导
- 查询动作库
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.utils.db import get_db
from app.models.user import User
from app.models.equipment import GymEquipment
from app.models.action import TrainingAction
from app.schemas.action import (
    ActionRecommendationRequest,
    ActionRecommendationResponse,
    ActionDetailResponse,
    ActionQueryRequest,
    ActionInfoResponse,
    ActionLibraryResponse,
    ReplaceRecommendResponse
)
from app.core.security import get_current_user
from app.services.recommendation import ActionRecommender

router = APIRouter(prefix="/api/action", tags=["动作管理"])


@router.post("/recommend", response_model=List[ActionRecommendationResponse], summary="推荐训练动作")
async def recommend_actions(
    request: ActionRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据器材识别结果和用户信息推荐训练动作
    
    对应《需求规格说明书》3.2 节推荐训练动作用例
    
    前置条件：
    - 系统已完成器材识别且用户已录入基本身体信息
    
    返回：
    匹配的训练动作列表（不限制数量），每个动作附带：
    - 动作名称与目标肌群
    - 动作类别标识（热身/有氧/力量/拉伸）
    - 难度等级标识
    - 标准动作演示视频/图片
    - 安全注意事项
    
    业务规则：
    1. 推荐算法需综合考虑目标肌群匹配度、动作难度分级、适用人群特征及用户个性化需求
    2. 初学者不推荐高级动作（《需求规格说明书》2.2.4）
    3. 返回数量不限制（根据匹配结果动态返回）
    """
    # 1. 验证用户资料完整性（《需求规格说明书》2.2.1 业务规则）
    if not all([
        current_user.age,
        current_user.experience_level,
        current_user.fitness_goal
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先完善身体数据后再生成动作推荐"
        )
    
    # 2. 初始化推荐引擎
    recommender = ActionRecommender(db=db, user=current_user)
    
    # 3. 执行推荐算法
    recommended_actions = recommender.recommend_actions(
        equipment_id=request.equipment_id,
        top_k=request.top_k,  # ✅ 可选参数
        action_category=request.action_category,
        include_score=request.include_score  # ✅ 新增参数
    )
    
    # 4. 检查推荐结果
    if not recommended_actions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到匹配的训练动作，请尝试其他器材"
        )
    
    # 5. 构建响应（《需求规格说明书》3.2 节要求的信息）
    response_list = []
    for action, match_score in recommended_actions:
        # 查询器材名称
        equipment_name = None
        if action.equipment_id and action.equipment_id != "none":
            equipment = db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                equipment_name = equipment.name
        
        response_list.append(ActionRecommendationResponse(
            action_id=action.action_id,
            name=action.name,
            action_category=action.action_category,
            difficulty_level=action.difficulty_level,
            target_muscles=action.get_target_muscles_list(),
            equipment_name=equipment_name,
            video_demo_url=action.video_demo_url,
            image_url=getattr(action, 'image_url', None),
            safety_tips=action.safety_tips,
            estimated_seconds=action.estimated_seconds,
            match_score=match_score if request.include_score else 0.0  # ✅ 条件返回评分
        ))
    
    return response_list

#前端中没有调用
@router.get("/recommend", response_model=List[ActionRecommendationResponse], summary="推荐训练动作（GET 版本）")
async def recommend_actions_get(
    equipment_id: str = Query(..., description="识别到的器材 ID"),
    action_category: Optional[str] = Query(None, description="指定动作类别"),
    top_k: Optional[int] = Query(None, ge=1, description="限制返回数量（可选）"),
    include_score: bool = Query(False, description="是否返回匹配度评分"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET 版本的推荐接口（便于前端直接 URL 调用）
    功能与 POST 版本相同
    """
    request = ActionRecommendationRequest(
        equipment_id=equipment_id,
        action_category=action_category,
        top_k=top_k,
        include_score=include_score
    )
    
    # 调用 POST 版本的逻辑
    return await recommend_actions(request, current_user, db)

@router.get("/detail/{action_id}", response_model=ActionDetailResponse, summary="查看动作指导")
async def get_action_detail(
    action_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查看每个训练动作的具体指导
    
    对应《需求规格说明书》3.2 节查看动作指导用例
    
    前置条件：
    - 用户已获得动作推荐或已生成训练计划
    
    返回：
    - 动作名称、类别、主要锻炼肌群
    - 标准动作演示视频（多角度）
    - 分步动作要领说明
    - 常见错误姿势示例及纠正方法
    - 建议执行参数（组数/次数/时长范围）
    - 安全注意事项
    """
    recommender = ActionRecommender(db=db, user=current_user)
    
    action = recommender.get_action_detail(action_id)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动作不存在"
        )
    
    # 查询器材名称
    equipment_name = None
    if action.equipment_id and action.equipment_id != "none":
        equipment = db.query(GymEquipment).filter(
            GymEquipment.equipment_id == action.equipment_id
        ).first()
        if equipment:
            equipment_name = equipment.name
    
    # 根据动作类别设置建议参数范围
    sets_range = "3-4 组"
    reps_range = "8-12 次/组"
    duration_range = "30-60 秒"
    
    if action.action_category == "main_strength":
        sets_range = "3-5 组"
        reps_range = "8-15 次/组"
    elif action.action_category == "main_cardio":
        duration_range = "30-120 秒"
    elif action.action_category in ["warmup", "cooldown"]:
        sets_range = "2-3 组"
        duration_range = "20-40 秒"
    
    return ActionDetailResponse(
        action_id=action.action_id,
        name=action.name,
        action_category=action.action_category,
        difficulty_level=action.difficulty_level,
        target_muscles=action.get_target_muscles_list(),
        equipment_id=action.equipment_id,
        equipment_name=equipment_name,
        video_demo_url=action.video_demo_url,
        image_url=getattr(action, 'image_url', None),
        safety_tips=action.safety_tips,
        estimated_seconds=action.estimated_seconds,
        sets_range=sets_range,
        reps_range=reps_range,
        duration_range=duration_range
    )

#前端中没有调用
@router.get("/category/{equipment_id}", response_model=List[ActionRecommendationResponse], summary="按类别获取动作")
async def get_actions_by_category(
    equipment_id: str,
    category: str = Query(..., description="动作类别（warmup/main_cardio/main_strength/cooldown）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据器材 ID 和动作类别获取动作列表
    
    对应《需求规格说明书》2.2.6 PlanSession 业务规则：
    热身阶段仅包含 warmup 类别动作，拉伸阶段仅包含 cooldown 类别动作
    """
    # 验证类别
    valid_categories = ["warmup", "main_cardio", "main_strength", "cooldown"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的动作类别，可选值：{valid_categories}"
        )
    
    recommender = ActionRecommender(db=db, user=current_user)
    actions = recommender.get_actions_by_category(equipment_id, category)
    
    if not actions:
        return []
    
    # 构建响应
    response_list = []
    for action in actions:
        equipment_name = None
        if action.equipment_id and action.equipment_id != "none":
            equipment = db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                equipment_name = equipment.name
        
        response_list.append(ActionRecommendationResponse(
            action_id=action.action_id,
            name=action.name,
            action_category=action.action_category,
            difficulty_level=action.difficulty_level,
            target_muscles=action.get_target_muscles_list(),
            equipment_name=equipment_name,
            video_demo_url=action.video_demo_url,
            image_url=getattr(action, 'image_url', None),
            safety_tips=action.safety_tips,
            estimated_seconds=action.estimated_seconds
        ))
    
    return response_list

#前端中没有调用
@router.post("/query", response_model=List[ActionInfoResponse], summary="按类别和/或肌群查询动作")
async def query_actions(
    request: ActionQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据动作类别和/或目标肌群查询动作列表
    
    支持三种参数组合：
    1. 参数类别为空，参数肌群不为空 → 查询指定肌群的所有动作
    2. 参数类别不为空，参数肌群为空 → 查询指定类别的所有动作
    3. 参数类别和肌群均不为空 → 查询指定类别且包含指定肌群的动作
    
    对应《需求规格说明书》3.2 节查看动作指导用例
    
    返回：
    - 动作名称、类别、难度
    - 目标肌群列表
    - 关联器材信息
    - 演示视频 URL
    - 安全注意事项
    """
    # 1. 构建查询条件
    query = db.query(TrainingAction)
    
    # 条件 1: 动作类别过滤
    if request.action_category:
        query = query.filter(TrainingAction.action_category == request.action_category)
    
    # 条件 2: 目标肌群过滤（JSON 字段模糊匹配）
    if request.target_muscle:
        # MySQL JSON 字段查询：target_muscles 包含指定肌群
        query = query.filter(
            TrainingAction.target_muscles.like(f'%"{request.target_muscle}"%')
        )
    
    # 2. 执行查询
    actions = query.all()
    
    # 3. 检查是否有结果
    if not actions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到匹配的动作，请尝试其他筛选条件"
        )
    
    # 4. 构建响应（关联器材名称）
    response_list = []
    for action in actions:
        # 查询器材名称
        equipment_name = None
        if action.equipment_id and action.equipment_id != "none":
            equipment = db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                equipment_name = equipment.name
        
        response_list.append(ActionInfoResponse(
            action_id=action.action_id,
            name=action.name,
            action_category=action.action_category,
            difficulty_level=action.difficulty_level,
            target_muscles=action.get_target_muscles_list(),
            equipment_id=action.equipment_id,
            equipment_name=equipment_name,
            video_demo_url=action.video_demo_url,
            image_url=getattr(action, 'image_url', None),
            safety_tips=action.safety_tips,
            estimated_seconds=action.estimated_seconds
        ))
    
    return response_list

#前端中没有调用
@router.get("/query", response_model=List[ActionInfoResponse], summary="按类别和/或肌群查询动作（GET 版本）")
async def query_actions_get(
    action_category: Optional[str] = Query(None, description="动作类别（warmup/main_cardio/main_strength/cooldown）"),
    target_muscle: Optional[str] = Query(None, description="目标肌群（如'胸大肌'、'股四头肌'等）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET 版本的查询接口（便于前端直接 URL 调用）
    功能与 POST 版本相同
    """
    # ✅ 添加验证错误捕获
    from pydantic import ValidationError
    
    try:
        request = ActionQueryRequest(
            action_category=action_category,
            target_muscle=target_muscle
        )
    except ValidationError as e:
        # 提取第一个错误信息
        error_detail = e.errors()[0]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail['msg']
        )
    
    # 调用 POST 版本的逻辑
    return await query_actions(request, current_user, db)


@router.get("/library", response_model=ActionLibraryResponse, summary="获取动作库所有动作")
async def get_action_library(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取动作库中所有的训练动作
    
    对应《任务书》技术指标：动作推荐库规模不少于 100 个标准动作
    
    返回：
    - 动作总数
    - 所有动作列表（包含完整信息）
    - 各类别动作数量统计
    """
    # 1. 查询所有动作
    actions = db.query(TrainingAction).all()
    
    # 2. 检查是否有数据
    if not actions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动作库为空，请先初始化动作数据"
        )
    
    # 3. 统计各类别动作数量
    category_stats = {
        "warmup": 0,
        "main_cardio": 0,
        "main_strength": 0,
        "cooldown": 0
    }
    
    # 4. 构建响应列表
    response_list = []
    for action in actions:
        # 统计类别
        if action.action_category in category_stats:
            category_stats[action.action_category] += 1
        
        # 查询器材名称
        equipment_name = None
        if action.equipment_id and action.equipment_id != "none":
            equipment = db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                equipment_name = equipment.name
        
        response_list.append(ActionInfoResponse(
            action_id=action.action_id,
            name=action.name,
            action_category=action.action_category,
            difficulty_level=action.difficulty_level,
            target_muscles=action.get_target_muscles_list(),
            equipment_id=action.equipment_id,
            equipment_name=equipment_name,
            video_demo_url=action.video_demo_url,
            image_url=getattr(action, 'image_url', None),
            safety_tips=action.safety_tips,
            estimated_seconds=action.estimated_seconds
        ))
    
    return ActionLibraryResponse(
        total_count=len(response_list),
        actions=response_list,
        category_stats=category_stats
    )


@router.get("/replace-recommend/{action_id}", response_model=List[ReplaceRecommendResponse], summary="推荐可替换动作")
async def replace_recommend_actions(
    action_id: str,
    plan_id: str = Query(..., description="当前训练计划 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据原动作的目标肌群和用户健身房器材推荐可替换动作
    
    推荐逻辑：
    1. 查询原动作的目标肌群和动作类别
    2. 获取用户健身房的所有器材
    3. 查询同类别的所有动作，排除原动作自身
    4. 筛选器材在用户健身房中的动作
    5. 按肌群相似度排序返回
    """
    from app.models.plan import TrainingPlan
    from app.models.equipment import EquipmentInventory, inventory_equipment_rel

    original_action = db.query(TrainingAction).filter(
        TrainingAction.action_id == action_id
    ).first()

    if not original_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原动作不存在"
        )

    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )

    inventory_equipments = db.query(inventory_equipment_rel.c.equipment_id).filter(
        inventory_equipment_rel.c.inventory_id == plan.inventory_id
    ).all()
    user_equipment_ids = {eq[0] for eq in inventory_equipments}

    original_muscles = set(original_action.get_target_muscles_list())

    candidate_actions = db.query(TrainingAction).filter(
        TrainingAction.action_category == original_action.action_category,
        TrainingAction.action_id != action_id
    ).all()

    scored_actions = []
    for action in candidate_actions:
        if action.equipment_id and action.equipment_id != "none":
            if action.equipment_id not in user_equipment_ids:
                continue

        action_muscles = set(action.get_target_muscles_list())
        if original_muscles:
            intersection = original_muscles & action_muscles
            similarity = len(intersection) / len(original_muscles)
        else:
            similarity = 0.0

        scored_actions.append((action, similarity))

    scored_actions.sort(key=lambda x: x[1], reverse=True)

    response_list = []
    for action, similarity in scored_actions:
        equipment_name = None
        if action.equipment_id and action.equipment_id != "none":
            equipment = db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                equipment_name = equipment.name

        response_list.append(ReplaceRecommendResponse(
            action_id=action.action_id,
            name=action.name,
            action_category=action.action_category.value if action.action_category else "unknown",
            difficulty_level=action.difficulty_level.value if action.difficulty_level else "unknown",
            target_muscles=action.get_target_muscles_list(),
            equipment_id=action.equipment_id,
            equipment_name=equipment_name,
            video_demo_url=action.video_demo_url,
            image_url=getattr(action, 'image_url', None),
            safety_tips=action.safety_tips,
            estimated_seconds=action.estimated_seconds or 0,
            muscle_similarity=round(similarity, 2)
        ))

    return response_list


@router.get("/add-recommend/{session_id}", response_model=List[ReplaceRecommendResponse], summary="推荐可添加动作")
async def add_recommend_actions(
    session_id: str,
    plan_id: str = Query(..., description="当前训练计划 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据阶段的目标肌群、动作类别和用户健身房器材推荐可添加的动作

    推荐逻辑：
    1. 查询阶段的目标肌群和阶段类型
    2. 根据阶段类型映射动作类别
    3. 获取用户健身房的所有器材
    4. 查询符合类别的动作，筛选器材在用户健身房中的动作
    5. 排除该阶段已添加的动作
    6. 按肌群相似度排序返回
    """
    from app.models.plan import TrainingPlan, PlanSession, SessionActionItem
    from app.models.equipment import EquipmentInventory, inventory_equipment_rel

    session = db.query(PlanSession).filter(
        PlanSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阶段不存在"
        )

    plan = db.query(TrainingPlan).filter(
        TrainingPlan.plan_id == plan_id,
        TrainingPlan.user_id == current_user.user_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练计划不存在或无权访问"
        )

    inventory_equipments = db.query(inventory_equipment_rel.c.equipment_id).filter(
        inventory_equipment_rel.c.inventory_id == plan.inventory_id
    ).all()
    user_equipment_ids = {eq[0] for eq in inventory_equipments}

    existing_action_ids = {
        item[0] for item in db.query(SessionActionItem.action_id).filter(
            SessionActionItem.session_id == session_id
        ).all()
    }

    category_map = {
        "WARMUP": ["warmup"],
        "MAIN": ["main_strength", "main_cardio"],
        "COOLDOWN": ["cooldown"]
    }
    target_categories = category_map.get(session.session_type, [])

    candidate_actions = db.query(TrainingAction).filter(
        TrainingAction.action_category.in_(target_categories)
    ).all()

    session_muscles = set()
    if session.target_muscles:
        import json
        try:
            session_muscles = set(json.loads(session.target_muscles))
        except (json.JSONDecodeError, TypeError):
            session_muscles = set()

    scored_actions = []
    for action in candidate_actions:
        if action.action_id in existing_action_ids:
            continue

        if action.equipment_id and action.equipment_id != "none":
            if action.equipment_id not in user_equipment_ids:
                continue

        action_muscles = set(action.get_target_muscles_list())
        if session_muscles:
            intersection = session_muscles & action_muscles
            similarity = len(intersection) / len(session_muscles)
        else:
            similarity = 0.0

        scored_actions.append((action, similarity))

    scored_actions.sort(key=lambda x: x[1], reverse=True)

    response_list = []
    for action, similarity in scored_actions:
        equipment_name = None
        if action.equipment_id and action.equipment_id != "none":
            equipment = db.query(GymEquipment).filter(
                GymEquipment.equipment_id == action.equipment_id
            ).first()
            if equipment:
                equipment_name = equipment.name

        response_list.append(ReplaceRecommendResponse(
            action_id=action.action_id,
            name=action.name,
            action_category=action.action_category.value if action.action_category else "unknown",
            difficulty_level=action.difficulty_level.value if action.difficulty_level else "unknown",
            target_muscles=action.get_target_muscles_list(),
            equipment_id=action.equipment_id,
            equipment_name=equipment_name,
            video_demo_url=action.video_demo_url,
            image_url=getattr(action, 'image_url', None),
            safety_tips=action.safety_tips,
            estimated_seconds=action.estimated_seconds or 0,
            muscle_similarity=round(similarity, 2)
        ))

    return response_list


@router.get("/muscles", response_model=List[str], summary="获取所有目标肌群列表")
async def get_all_muscles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取动作库中所有不重复的目标肌群列表
    
    用于前端筛选器的肌群选项展示
    """
    actions = db.query(TrainingAction).all()
    
    # 收集所有肌群
    all_muscles = set()
    for action in actions:
        muscles = action.get_target_muscles_list()
        all_muscles.update(muscles)
    
    # 排序返回
    return sorted(list(all_muscles))