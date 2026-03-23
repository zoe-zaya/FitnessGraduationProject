"""
器材管理 API
对应《需求规格说明书》3.2 节：
- 识别健身器材
- 管理健身房
- 添加器材（自动/手动）
- 查看器材
- 删除器材
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import time
import base64
import io

from app.utils.db import get_db
from app.models.user import User
from app.models.equipment import EquipmentInventory, GymEquipment, inventory_equipment_rel
from app.models.action import TrainingAction
from app.schemas.equipment import (
    EquipmentInventoryCreate, EquipmentInventoryCreateResponse, EquipmentInventoryUpdate, EquipmentInventoryResponse,
    GymEquipmentResponse, EquipmentAddManualRequest, EquipmentAddAutoRequest, EquipmentListResponse,
    EquipmentDetectionResponse, EquipmentDetectionResult
)
from app.core.security import get_current_user
from app.services.detection import EquipmentDetector
from app.services.equipment import EquipmentService

router = APIRouter(prefix="/api/equipment", tags=["器材管理"])


# ==================== 健身器材检测 ====================

@router.post("/detect", response_model=EquipmentDetectionResponse, summary="识别健身器材")
async def detect_equipment(
    image: UploadFile = File(..., description="上传的健身器材图片"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    识别健身器材
    对应《需求规格说明书》3.2 节识别健身器材用例
    
    业务规则：
    1. 识别准确率不低于 85%（《任务书》技术指标）
    2. 单次识别响应时间不超过 2 秒（《任务书》技术指标）
    3. 置信度低于 70% 时提示用户调整拍摄角度重试（《需求规格说明书》2.2.3）
    4. 若图像中存在多个器材，列出所有识别到的器材（《需求规格说明书》扩展事件流 4a）
    """
    start_time = time.time()
    
    try:
        # 1. 读取并验证图片
        contents = await image.read()
        if not contents or len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片数据为空"
            )
        
        # 2. 调用检测服务
        detector = EquipmentDetector()
        detection_results = detector.detect(contents)
        print(f"检测结果: {detection_results}")
        
        # 3. 计算检测耗时
        detection_time = time.time() - start_time
        
        # 4. 验证响应时间（《任务书》要求<2 秒）
        if detection_time > 2.0:
            message = "检测耗时过长，请重试"
            print(f"警告：检测耗时{detection_time:.2f}秒，超过 2 秒限制")
        
        # 若detection_results为空数组，说明未识别到器材
        if not detection_results:
            return EquipmentDetectionResponse(
                results=[],
                detection_time=round(time.time() - start_time, 3),
                message="未识别到器材，请调整拍摄角度重试"
            )

        # 5. 构建响应结果，仅保留置信度最高的结果
        results = []
        if detection_results:
            best_result = max(detection_results, key=lambda det: det['confidence'])
            equipment = db.query(GymEquipment).filter(
            GymEquipment.equipment_id == best_result['equipment_id']
            ).first()
            
            if equipment:
                results = [EquipmentDetectionResult(
                    equipment_id=best_result['equipment_id'],
                    name=equipment.name,
                    category=equipment.category,
                    confidence=best_result['confidence'],
                    target_muscles=equipment.get_target_muscles_list(),
                    box_coordinates=best_result.get('box')
                )]
        else:
            results = []
        
        # 6. 检查置信度（《需求规格说明书》2.2.3 业务规则）
        for result in results:
            if result.confidence < 0.7:
                return EquipmentDetectionResponse(
                    results=results,
                    detection_time=round(detection_time, 3),
                    message="识别不确定，请调整拍摄角度重试"
                )
            else:
                return EquipmentDetectionResponse(
                    results=results,
                    detection_time=round(detection_time, 3),
                    message="识别成功"
                )
        
    except Exception as e:
        print(f"检测失败：{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="器材识别失败，请重试"
        )


# ==================== 健身房（器材清单）管理 ====================

@router.post("/createGym", response_model=EquipmentInventoryCreateResponse, summary="创建健身房")
async def create_inventory(
    inventory_data: EquipmentInventoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建健身房
    对应《需求规格说明书》3.2 节管理健身房用例
    
    业务规则：
    1. 用户可创建多个健身房（《需求规格说明书》2.2.2）
    2. 创建时必须指定归属标签（《需求规格说明书》2.2.2）
    3. 标签可重复使用（如多个用户可创建同名"家附近健身房"清单）
    """
    import uuid
    from datetime import datetime
    
    # 1. 创建器材清单
    inventory_id = str(uuid.uuid4())
    
    new_inventory = EquipmentInventory(
        inventory_id=inventory_id,
        user_id=current_user.user_id,
        location_tag=inventory_data.location_tag,
        description=inventory_data.description,
        create_time=datetime.now()
    )
    
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    
    return EquipmentInventoryCreateResponse(
        inventory_id=new_inventory.inventory_id,
        user_id=new_inventory.user_id,
        location_tag=new_inventory.location_tag,
        description=new_inventory.description,
        create_time=new_inventory.create_time,
        equipment_count=0,
        message="健身房创建成功"
    )


@router.get("/getAllGym", response_model=List[EquipmentInventoryResponse], summary="获取当前用户所有健身房")
async def get_user_inventories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有健身房
    对应《需求规格说明书》3.2 节管理健身房用例
    """
    inventories = db.query(EquipmentInventory).filter(
        EquipmentInventory.user_id == current_user.user_id
    ).all()
    
    response_list = []
    for inv in inventories:
        # 查询每个清单的器材数量
        equipment_count = db.query(inventory_equipment_rel).filter(
            inventory_equipment_rel.c.inventory_id == inv.inventory_id
        ).count()
        
        response_list.append(EquipmentInventoryResponse(
            inventory_id=inv.inventory_id,
            user_id=inv.user_id,
            location_tag=inv.location_tag,
            description=inv.description,
            create_time=inv.create_time,
            equipment_count=equipment_count
        ))
    
    return response_list


@router.get("/getGym/{inventory_id}", response_model=EquipmentInventoryResponse, summary="获取指定健身房详情")
async def get_inventory_detail(
    inventory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定健身房的详细信息
    对应《需求规格说明书》3.2 节查看器材用例
    """
    # 1. 验证权限
    inventoryUserId = db.query(EquipmentInventory).filter(
        EquipmentInventory.user_id == current_user.user_id
    ).first()

    # 2. 器材清单是否存在
    inventory = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == inventory_id
    ).first()
    
    if not inventoryUserId:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问"
        )
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健身房不存在"
        )
    
    # 2. 查询清单内的器材
    equipment_list = []
    rels = db.query(inventory_equipment_rel).filter(
        inventory_equipment_rel.c.inventory_id == inventory_id
    ).all()
    
    for rel in rels:
        equipment = db.query(GymEquipment).filter(
            GymEquipment.equipment_id == rel.equipment_id
        ).first()
        if equipment:
            equipment_list.append(EquipmentListResponse(
                equipment_id=equipment.equipment_id,
                name=equipment.name,
                category=equipment.category,
                description=equipment.description,
                target_muscles=equipment.get_target_muscles_list()
            ))
    
    return EquipmentInventoryResponse(
        inventory_id=inventory.inventory_id,
        user_id=inventory.user_id,
        location_tag=inventory.location_tag,
        description=inventory.description,
        create_time=inventory.create_time,
        equipment_count=len(equipment_list),
        equipment_list=equipment_list
    )


@router.put("/editGym/{inventory_id}", response_model=EquipmentInventoryCreateResponse, summary="更新健身房信息")
async def update_inventory(
    inventory_id: str,
    inventory_data: EquipmentInventoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新健身房信息
    对应《需求规格说明书》3.2 节管理健身房扩展事件流 1a
    """
    
    inventory = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == inventory_id,
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    checkUserID = db.query(EquipmentInventory).filter(
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    if not checkUserID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问"
        )
    checkGymID = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == inventory_id
    ).first()
    
    if not checkGymID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健身房不存在"
        )
    
    # 2. 更新字段
    if inventory_data.location_tag is not None:
        inventory.location_tag = inventory_data.location_tag
    if inventory_data.description is not None:
        inventory.description = inventory_data.description
    
    db.commit()
    db.refresh(inventory)
    
    # 3. 查询器材数量
    equipment_count = db.query(inventory_equipment_rel).filter(
        inventory_equipment_rel.c.inventory_id == inventory_id
    ).count()
    
    return EquipmentInventoryCreateResponse(
        inventory_id=inventory.inventory_id,
        user_id=inventory.user_id,
        location_tag=inventory.location_tag,
        description=inventory.description,
        create_time=inventory.create_time,
        equipment_count=equipment_count,
        message="健身房信息更新成功"
    )


@router.delete("/deleteGym/{inventory_id}", summary="删除健身房")
async def delete_inventory(
    inventory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除健身房
    对应《需求规格说明书》3.2 节管理健身房扩展事件流 1b
    """
    # 1. 验证器材清单归属
    checkUserID = db.query(EquipmentInventory).filter(
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    if not checkUserID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问"
        )
    
    # 1. 验证器材清单是否存在
    checkGymID = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == inventory_id
    ).first()
    
    if not checkGymID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健身房不存在"
        )
    
    # 2. 删除关联关系
    db.query(inventory_equipment_rel).filter(
        inventory_equipment_rel.c.inventory_id == inventory_id
    ).delete()
    
    # 3. 删除健身房
    successDelete = db.query(EquipmentInventory).filter(
        EquipmentInventory.user_id == current_user.user_id,
        EquipmentInventory.inventory_id == inventory_id
    ).delete()
    if successDelete == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除健身房失败，请重试"
        )
    db.commit()
    return {"message": "健身房删除成功"}


# ==================== 器材添加（自动/手动） ====================

@router.post("/addEquipment/{inventory_id}/manual", summary="手动添加器材到健身房")
async def add_equipment_manual(
    inventory_id: str,
    request: EquipmentAddManualRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    手动添加器材到健身房
    对应《需求规格说明书》3.2 节添加器材——手动添加用例
    
    业务规则：
    1. 用户通过关键词搜索系统器材库（《需求规格说明书》基本事件流 1-2）
    2. 选择目标器材后手动加入健身房（《需求规格说明书》基本事件流 3-4）
    """
    # 1. 验证健身房是否存在
    checkGymID = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == inventory_id
    ).first()
    
    if not checkGymID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健身房不存在"
        ) 
     # 2. 验证是否有权限访问该健身房   
    checkUserID = db.query(EquipmentInventory).filter(
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    if not checkUserID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问"
        )
    
    # 3. 验证器材是否在器材库中
    equipment = db.query(GymEquipment).filter(
        GymEquipment.equipment_id == request.equipment_id
    ).first()
    
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到搜索的器材"
        )
    
    # 4. 检查是否已存在
    existing = db.query(inventory_equipment_rel).filter(
        inventory_equipment_rel.c.inventory_id == inventory_id,
        inventory_equipment_rel.c.equipment_id == request.equipment_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该器材已在健身房中"
        )
    
    # 5. 添加关联关系
    new_rel = inventory_equipment_rel.insert().values(
        inventory_id=inventory_id,
        equipment_id=request.equipment_id
    )
    db.execute(new_rel)
    db.commit()
    
    return {"message": "器材添加成功", "equipment_name": equipment.name}


@router.post("/addEquipment/{inventory_id}/auto", summary="自动添加器材到健身房（基于识别）")
async def add_equipment_auto(
    inventory_id: str,
    request: EquipmentAddAutoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    自动添加器材到健身房（基于识别结果）
    对应《需求规格说明书》3.2 节添加器材——自动添加用例
    
    业务规则：
    1. 基于器材识别结果添加（《需求规格说明书》2.2.2）
    2. 置信度低于 70% 时提示用户确认（《需求规格说明书》2.2.3）
    """
    # 1. 验证置信度（《需求规格说明书》2.2.3 业务规则）
    if request.confidence < 0.7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未识别到器材，请调整拍摄角度重试"
        )
    
    # 2. 验证器材清单归属
    inventory = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == inventory_id,
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健身房不存在或无权访问"
        )
    
    # 3. 验证器材是否存在
    equipment = db.query(GymEquipment).filter(
        GymEquipment.equipment_id == request.equipment_id
    ).first()
    
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到识别的器材"
        )
    
    # 4. 检查是否已存在
    existing = db.query(inventory_equipment_rel).filter(
        inventory_equipment_rel.c.inventory_id == inventory_id,
        inventory_equipment_rel.c.equipment_id == request.equipment_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该器材已在健身房中"
        )
    
    # 5. 添加关联关系
    new_rel = inventory_equipment_rel.insert().values(
        inventory_id=inventory_id,
        equipment_id=request.equipment_id
    )
    db.execute(new_rel)
    db.commit()
    
    return {
        "message": "器材添加成功",
        "equipment_name": equipment.name,
        "confidence": request.confidence
    }


# ==================== 器材查询与删除 ====================

@router.get("/getEquipmentById/{equipment_id}", response_model=GymEquipmentResponse, summary="根据器材ID查看器材详细信息")
async def get_equipment_detail(
    equipment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据器材 ID 查询器材的名称、分类、描述、目标肌群、支持的动作列表
    对应《需求规格说明书》3.2 节查看器材用例
    返回：器材名称、分类、描述、目标肌群、支持的动作列表
    """
    equipment = db.query(GymEquipment).filter(
        GymEquipment.equipment_id == equipment_id
    ).first()
    
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到搜索的器材"
        )
    
    # 查询支持的动作数量
    actions_count = db.query(TrainingAction).filter(
        TrainingAction.equipment_id == equipment_id
    ).count()
    
    return GymEquipmentResponse(
        equipment_id=equipment.equipment_id,
        name=equipment.name,
        category=equipment.category,
        description=equipment.description,
        target_muscles=equipment.get_target_muscles_list(),
        image_url=equipment.image_url,
        supported_actions_count=actions_count
    )


@router.get("/getEquipmentByKey/search", response_model=List[GymEquipmentResponse], summary="根据关键词搜索器材")
async def search_equipment(
    keyword: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    搜索器材（用于手动添加）：根据关键词模糊匹配器材名称和分类
    对应《需求规格说明书》3.2 节添加器材——手动添加用例步骤 1-2
    返回：匹配的器材列表（名称、分类、描述、目标肌群、支持的动作数量）
    """
    # 1. 验证关键词
    #print(f"搜索关键词: {keyword}, 长度: {len(keyword)}")
    if not keyword or len(keyword.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="搜索关键词不能为空"
        )
    
    # 2. 模糊搜索器材名称和分类
    equipments = db.query(GymEquipment).filter(
        (GymEquipment.name.like(f"%{keyword}%"))|(GymEquipment.category.like(f"%{keyword}%"))
    ).limit(21).all()
    
    # 3. 检查是否有结果
    if not equipments:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="未找到匹配的器材"
        )
    
    # 4. 构建响应
    response_list = []
    for eq in equipments:
        actions_count = db.query(TrainingAction).filter(
            TrainingAction.equipment_id == eq.equipment_id
        ).count()
        
        response_list.append(GymEquipmentResponse(
            equipment_id=eq.equipment_id,
            name=eq.name,
            category=eq.category,
            description=eq.description,
            target_muscles=eq.get_target_muscles_list(),
            image_url=eq.image_url,
            supported_actions_count=actions_count
        ))
    
    return response_list


@router.delete("/deleteEquipment/{inventory_id}/{equipment_id}", summary="从健身房中删除器材")
async def remove_equipment(
    inventory_id: str,
    equipment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从指定健身房中删除器材
    对应《需求规格说明书》3.2 节删除器材用例
    """
    # 1. 验证器材清单归属
    checkUserID = db.query(EquipmentInventory).filter(
        EquipmentInventory.user_id == current_user.user_id
    ).first()
    
    if not checkUserID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问"
        )
    
    # 2. 验证健身房是否存在
    checkGymID = db.query(EquipmentInventory).filter(
        EquipmentInventory.inventory_id == inventory_id
    ).first()
    
    if not checkGymID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健身房不存在"
        )
    # 3. 验证器材是否在健身房中
    inventory_equipment = db.query(inventory_equipment_rel).filter(
        inventory_equipment_rel.c.inventory_id == inventory_id,
        inventory_equipment_rel.c.equipment_id == equipment_id
    ).first()
    if not inventory_equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="器材未在该健身房中"
        )
    # 4. 删除
    successDelete = db.query(inventory_equipment_rel).filter(
        inventory_equipment_rel.c.inventory_id == inventory_id,
        inventory_equipment_rel.c.equipment_id == equipment_id
    ).delete()
    if successDelete == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除器材失败，请重试"
        )
    db.commit()
    return {"message": "器材删除成功"}