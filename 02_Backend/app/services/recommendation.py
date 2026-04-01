"""
动作推荐服务
根据器材识别结果和用户信息智能推荐训练动作
对应《需求规格说明书》3.2 节推荐训练动作用例
《任务书》技术指标：推荐 3-5 个关联训练动作
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Tuple
from app.models.action import TrainingAction, ActionCategoryEnum, DifficultyLevelEnum
from app.models.user import User
from app.models.equipment import GymEquipment
import json


class ActionRecommender:
    """
    动作推荐引擎
    实现器材 - 动作匹配、用户适配过滤、智能排序推荐
    """
    
    # 健身目标权重配置（《需求规格说明书》表 2-1 fitnessGoal）
    GOAL_WEIGHTS = {
        "增肌": {
            "main_strength": 1.5,
            "main_cardio": 0.8,
            "warmup": 1.0,
            "cooldown": 1.0
        },
        "减脂": {
            "main_strength": 0.8,
            "main_cardio": 1.5,
            "warmup": 1.0,
            "cooldown": 1.0
        },
        "塑形": {
            "main_strength": 1.2,
            "main_cardio": 1.2,
            "warmup": 1.0,
            "cooldown": 1.0
        },
        "增强体能": {
            "main_strength": 1.0,
            "main_cardio": 1.0,
            "warmup": 1.2,
            "cooldown": 1.2
        }
    }
    
    # 难度适配权重（《需求规格说明书》2.2.4 业务规则：初学者不推荐高级动作）
    DIFFICULTY_WEIGHTS = {
        ("初学者", "初级"): 1.2,
        ("初学者", "中级"): 0.9,
        ("初学者", "高级"): 0.0,  # 直接过滤
        ("中级", "初级"): 1.1,
        ("中级", "中级"): 1.2,
        ("中级", "高级"): 0.9,
        ("高级", "初级"): 1.0,
        ("高级", "中级"): 1.1,
        ("高级", "高级"): 1.2,
    }
    
    def __init__(self, db: Session, user: User):
        """
        初始化推荐引擎
        
        参数：
            db: 数据库会话
            user: 当前用户对象（包含年龄、性别、健身目标、经验水平等）
        """
        self.db = db
        self.user = user
    
    def recommend_actions(
        self, 
        equipment_id: str, 
        top_k: Optional[int] = None,  # ✅ 改为可选
        action_category: Optional[str] = None,
        include_score: bool = True  # ✅ 新增参数
    ) -> List[Tuple[TrainingAction, float]]:
        """
        智能推荐训练动作（核心方法）
        
        对应《需求规格说明书》3.2 节推荐训练动作用例基本事件流：
        (1) 系统根据识别到的器材 ID，查询所有匹配的训练动作
        (2) 系统结合用户身体数据过滤不适宜动作
        (3) 系统向用户推荐训练动作（不限制数量）
        
        参数：
            equipment_id: 识别到的器材 ID
            top_k: 限制返回数量（可选，不传则返回所有匹配动作）
            action_category: 指定动作类别（可选）
            include_score: 是否计算并返回匹配度评分
        
        返回：
            排序后的（动作，匹配分）列表
        """
        # 步骤 1: 查询器材支持的所有动作
        actions = self._query_actions_by_equipment(equipment_id)
        
        if not actions:
            return []
        
        # 步骤 2: 用户适配过滤（《需求规格说明书》2.2.4 业务规则）
        filtered_actions = self._filter_by_user_profile(actions)
        
        # 步骤 3: 类别过滤（如果指定）
        if action_category:
            filtered_actions = [
                a for a in filtered_actions 
                if a.action_category == action_category
            ]
        
        # 步骤 4: 综合评分排序（如果 include_score 为 True 或需要排序）
        if include_score or top_k is not None:
            scored_actions = [
                (action, self._calculate_match_score(action))
                for action in filtered_actions
            ]
            scored_actions.sort(key=lambda x: x[1], reverse=True)
        else:
            # 不计算评分，直接返回
            scored_actions = [(action, 0.0) for action in filtered_actions]
        
        # 步骤 5: 返回结果（✅ 修改：不限制数量，除非指定 top_k）
        if top_k is not None:
            return scored_actions[:top_k]
        else:
            return scored_actions  # 返回所有匹配动作
    
    def _query_actions_by_equipment(self, equipment_id: str) -> List[TrainingAction]:
        """
        查询器材支持的所有动作
        
        对应《需求规格说明书》2.2.3 GymEquipment.supportedActions
        业务规则：一种器材支持多个动作（如"杠铃"支持深蹲、卧推等 10+ 动作）
        """
        # 查询匹配该器材的动作 + 无器械动作（equipment_id="none"）
        actions = self.db.query(TrainingAction).filter(
            (TrainingAction.equipment_id == equipment_id) |
            (TrainingAction.equipment_id == "none")
        ).all()
        
        return actions
    
    def _filter_by_user_profile(self, actions: List[TrainingAction]) -> List[TrainingAction]:
        """
        根据用户档案过滤不适宜动作
        
        对应《需求规格说明书》2.2.4 业务规则：
        (1) 动作难度需与用户经验水平匹配
        (2) 初学者不推荐高级动作
        
        对应《需求规格说明书》3.2 节推荐训练动作用例基本事件流 (2)：
        系统结合用户身体数据（年龄、体重、健身经验）过滤不适宜动作
        """
        filtered = []
        
        for action in actions:
            # 规则 1: 初学者不推荐高级动作（《需求规格说明书》2.2.4）
            if (self.user.experience_level == "初学者" and 
                action.difficulty_level == "高级"):
                continue
            
            # 规则 2: 年龄适配（可选扩展）
            # 如果用户年龄>60 岁，过滤高冲击动作
            if self.user.age and self.user.age > 60:
                high_impact_actions = ["波比跳", "深蹲跳", "弓步跳", "双摇跳绳"]
                if action.name in high_impact_actions:
                    continue
            
            # 规则 3: 健身目标适配（可选扩展）
            # 如果用户目标是"增肌"，降低纯有氧动作优先级（但不完全过滤）
            
            filtered.append(action)
        
        return filtered
    
    def _calculate_match_score(self, action: TrainingAction) -> float:
        """
        计算动作匹配度评分（核心算法）
        
        评分因子：
        1. 健身目标匹配度（权重 40%）
        2. 难度适配度（权重 30%）
        3. 目标肌群偏好（权重 20%）
        4. 动作热度/使用频率（权重 10%）
        
        参数：
            action: 训练动作对象
        
        返回：
            匹配度评分（0-100）
        """
        score = 100.0  # 基础分
        
        # 因子 1: 健身目标匹配（《需求规格说明书》表 2-1 fitnessGoal）
        goal_weight = self._get_goal_weight(action.action_category)
        score *= goal_weight
        
        # 因子 2: 难度适配（《需求规格说明书》2.2.4）
        difficulty_weight = self._get_difficulty_weight(action.difficulty_level)
        score *= difficulty_weight
        
        # 因子 3: 目标肌群偏好（如果用户有设置）
        if hasattr(self.user, 'preferred_muscles') and self.user.preferred_muscles:
            muscle_bonus = self._calculate_muscle_bonus(action)
            score += muscle_bonus
        
        # 因子 4: 动作热度（基于 estimated_seconds，时长适中的动作更受欢迎）
        popularity_bonus = self._calculate_popularity_bonus(action)
        score += popularity_bonus
        
        return round(score, 2)
    
    def _get_goal_weight(self, action_category: str) -> float:
        """获取健身目标权重"""
        goal_weights = self.GOAL_WEIGHTS.get(
            self.user.fitness_goal, 
            {"main_strength": 1.0, "main_cardio": 1.0, "warmup": 1.0, "cooldown": 1.0}
        )
        return goal_weights.get(action_category, 1.0)
    
    def _get_difficulty_weight(self, difficulty_level: str) -> float:
        """获取难度适配权重"""
        key = (self.user.experience_level, difficulty_level)
        return self.DIFFICULTY_WEIGHTS.get(key, 1.0)
    
    def _calculate_muscle_bonus(self, action: TrainingAction) -> float:
        """计算目标肌群偏好加分"""
        bonus = 0.0
        action_muscles = action.get_target_muscles_list()
        
        for muscle in self.user.preferred_muscles:
            if muscle in action_muscles:
                bonus += 10.0
        
        return bonus
    
    def _calculate_popularity_bonus(self, action: TrainingAction) -> float:
        """
        计算动作热度加分
        基于动作时长：适中的时长更受欢迎
        """
        estimated = action.estimated_seconds or 0
        
        # 力量训练：2-4 秒/次最受欢迎
        if action.action_category == "main_strength":
            if 2 <= estimated <= 4:
                return 5.0
            elif 1 <= estimated <= 5:
                return 2.0
        
        # 有氧训练：30-60 秒最受欢迎
        elif action.action_category == "main_cardio":
            if 30 <= estimated <= 60:
                return 5.0
            elif 20 <= estimated <= 120:
                return 2.0
        
        # 热身/拉伸：20-40 秒最受欢迎
        else:
            if 20 <= estimated <= 40:
                return 5.0
            elif 10 <= estimated <= 60:
                return 2.0
        
        return 0.0
    
    def get_action_detail(self, action_id: str) -> Optional[TrainingAction]:
        """
        获取动作详细信息
        
        对应《需求规格说明书》3.2 节查看动作指导用例
        """
        action = self.db.query(TrainingAction).filter(
            TrainingAction.action_id == action_id
        ).first()
        
        return action
    
    def get_actions_by_category(
        self, 
        equipment_id: str, 
        category: str
    ) -> List[TrainingAction]:
        """
        根据类别获取动作列表
        
        对应《需求规格说明书》2.2.6 PlanSession 业务规则：
        热身阶段仅包含 warmup 类别动作，拉伸阶段仅包含 cooldown 类别动作
        """
        actions = self.db.query(TrainingAction).filter(
            TrainingAction.equipment_id == equipment_id,
            TrainingAction.action_category == category
        ).all()
        
        return actions