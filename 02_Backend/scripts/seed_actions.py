"""
训练动作数据初始化脚本
预置不少于 100 个标准训练动作（《任务书》技术指标）
对应《需求规格说明书》表 2-4 TrainingAction 业务对象
动作覆盖四类：warmup、main_cardio、main_strength、cooldown
"""
# ==================== 添加以下代码解决模块导入问题 ====================
import sys
import os
from pathlib import Path

# 获取项目根目录（02_Backend 目录）
project_root = Path(__file__).resolve().parent.parent
# 将项目根目录添加到 sys.path
sys.path.insert(0, str(project_root))
# ====================================================================

from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.action import TrainingAction, ActionCategoryEnum, DifficultyLevelEnum
import json


# 100 个预置训练动作数据
# 分类统计：warmup(20) + main_cardio(25) + main_strength(45) + cooldown(10) = 100
ACTIONS_DATA = [
    # ==================== 热身动作 (warmup) - 20 个 ====================
    {
        "action_id": "act_001",
        "name": "开合跳",
        "action_category": "warmup",
        "target_muscles": ["全身肌群", "心肺功能"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/jumping_jacks.mp4",
        "image_url": "jumping_jacks.png",
        "safety_tips": "保持膝盖微屈，落地轻柔，避免膝盖过度内扣"
    },
    {
        "action_id": "act_002",
        "name": "高抬腿",
        "action_category": "warmup",
        "target_muscles": ["髋屈肌", "股四头肌", "心肺功能"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/high_knees.mp4",
        "image_url": "high_knees.png",
        "safety_tips": "保持上身挺直，核心收紧，膝盖尽量抬高至髋部水平"
    },
    {
        "action_id": "act_003",
        "name": "手臂绕环",
        "action_category": "warmup",
        "target_muscles": ["三角肌", "肩袖肌群"],
        "difficulty_level": "初级",
        "equipment_id": "none",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/arm_circles.mp4",
        "image_url": "arm_circles.png",
        "safety_tips": "动作幅度由小到大，避免快速甩臂造成肩部损伤"
    },
    {
        "action_id": "act_004",
        "name": "动态弓步走",
        "action_category": "warmup",
        "target_muscles": ["股四头肌", "臀大肌", "腘绳肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 40,
        "video_demo_url": "/videos/warmup/walking_lunges.mp4",
        "image_url": "walking_lunges.png",
        "safety_tips": "前膝不超过脚尖，后膝接近地面但不触碰，保持躯干稳定"
    },
    {
        "action_id": "act_005",
        "name": "躯干旋转",
        "action_category": "warmup",
        "target_muscles": ["腹外斜肌", "核心肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/torso_twist.mp4",
        "image_url": "torso_twist.png",
        "safety_tips": "双脚固定，用核心带动上半身旋转，避免过度用力"
    },
    {
        "action_id": "act_006",
        "name": "踝关节绕环",
        "action_category": "warmup",
        "target_muscles": ["小腿三头肌", "踝关节"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 20,
        "video_demo_url": "/videos/warmup/ankle_circles.mp4",
        "image_url": "ankle_circles.png",
        "safety_tips": "动作缓慢控制，顺时针和逆时针各 10 次"
    },
    {
        "action_id": "act_007",
        "name": "腕关节绕环",
        "action_category": "warmup",
        "target_muscles": ["前臂肌群", "腕关节"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 20,
        "video_demo_url": "/videos/warmup/wrist_circles.mp4",
        "image_url": "wrist_circles.png",
        "safety_tips": "双手十指交叉，缓慢旋转腕关节"
    },
    {
        "action_id": "act_008",
        "name": "颈部拉伸",
        "action_category": "warmup",
        "target_muscles": ["斜方肌", "胸锁乳突肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 20,
        "video_demo_url": "/videos/warmup/neck_stretch.mp4",
        "image_url": "neck_stretch.png",
        "safety_tips": "动作轻柔缓慢，避免快速转头造成眩晕"
    },
    {
        "action_id": "act_009",
        "name": "肩部绕环",
        "action_category": "warmup",
        "target_muscles": ["三角肌", "斜方肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/shoulder_circles.mp4",
        "image_url": "shoulder_circles.png",
        "safety_tips": "向前向后各 15 次，动作幅度逐渐增大"
    },
    {
        "action_id": "act_010",
        "name": "髋关节绕环",
        "action_category": "warmup",
        "target_muscles": ["髋关节", "臀肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/hip_circles.mp4",
        "image_url": "hip_circles.png",
        "safety_tips": "双手叉腰，顺时针和逆时针各 15 次"
    },
    {
        "action_id": "act_011",
        "name": "动态侧弓步",
        "action_category": "warmup",
        "target_muscles": ["大腿内收肌", "股四头肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 40,
        "video_demo_url": "/videos/warmup/lateral_lunges.mp4",
        "image_url": "lateral_lunges.png",
        "safety_tips": "保持一脚伸直一脚弯曲，重心缓慢移动"
    },
    {
        "action_id": "act_012",
        "name": "毛毛虫爬",
        "action_category": "warmup",
        "target_muscles": ["腘绳肌", "核心肌群", "肩部"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 40,
        "video_demo_url": "/videos/warmup/inchworm.mp4",
        "image_url": "inchworm.png",
        "safety_tips": "从站姿开始，双手向前爬至平板支撑位，再爬回"
    },
    {
        "action_id": "act_013",
        "name": "踢臀跑",
        "action_category": "warmup",
        "target_muscles": ["腘绳肌", "心肺功能"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/butt_kicks.mp4",
        "image_url": "butt_kicks.png",
        "safety_tips": "脚跟尽量触碰臀部，保持上身稳定"
    },
    {
        "action_id": "act_014",
        "name": "波比跳（简化版）",
        "action_category": "warmup",
        "target_muscles": ["全身肌群", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 40,
        "video_demo_url": "/videos/warmup/burpee_modified.mp4",
        "image_url": "burpee_modified.png",
        "safety_tips": "可省略俯卧撑部分，重点在于全身协调激活"
    },
    {
        "action_id": "act_015",
        "name": "猫牛式",
        "action_category": "warmup",
        "target_muscles": ["脊柱", "核心肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/cat_cow.mp4",
        "image_url": "cat_cow.png",
        "safety_tips": "配合呼吸，吸气时塌腰抬头，呼气时拱背低头"
    },
    {
        "action_id": "act_016",
        "name": "世界最佳拉伸",
        "action_category": "warmup",
        "target_muscles": ["髋屈肌", "胸椎", "腘绳肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 40,
        "video_demo_url": "/videos/warmup/world_greatest_stretch.mp4",
        "image_url": "world_greatest_stretch.png",
        "safety_tips": "结合弓步、胸椎旋转和腘绳肌拉伸的复合动作"
    },
    {
        "action_id": "act_017",
        "name": "跳绳（无绳）",
        "action_category": "warmup",
        "target_muscles": ["小腿三头肌", "心肺功能"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/warmup/jump_rope_simulation.mp4",
        "image_url": "jump_rope_simulation.png",
        "safety_tips": "前脚掌着地，膝盖微屈缓冲，手腕转动模拟摇绳"
    },
    {
        "action_id": "act_018",
        "name": "平板支撑转体",
        "action_category": "warmup",
        "target_muscles": ["核心肌群", "腹斜肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 40,
        "video_demo_url": "/videos/warmup/plank_twist.mp4",
        "image_url": "plank_twist.png",
        "safety_tips": "保持核心收紧，转体时避免臀部过度晃动"
    },
    {
        "action_id": "act_019",
        "name": "动态胸椎伸展",
        "action_category": "warmup",
        "target_muscles": ["胸椎", "背阔肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/warmup/thoracic_extension.mp4",
        "image_url": "thoracic_extension.png",
        "safety_tips": "侧卧位，上方手臂缓慢向后打开，眼睛跟随手部移动"
    },
    {
        "action_id": "act_020",
        "name": "原地小跑",
        "action_category": "warmup",
        "target_muscles": ["心肺功能", "下肢肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/warmup/jogging_in_place.mp4",
        "image_url": "jogging_in_place.png",
        "safety_tips": "保持轻松节奏，逐步提高心率"
    },
    
    # ==================== 有氧动作 (main_cardio) - 25 个 ====================
    {
        "action_id": "act_021",
        "name": "跑步机慢跑",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "下肢肌群", "臀大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_18",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/treadmill_jog.mp4",
        "image_url": "treadmill_jog.png",
        "safety_tips": "保持正确跑姿，步幅适中，避免过度前倾或后仰"
    },
    {
        "action_id": "act_022",
        "name": "跑步机快走",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "下肢肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_18",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/treadmill_walk.mp4",
        "image_url": "treadmill_walk.png",
        "safety_tips": "适合初学者，速度 5-6km/h，保持手臂自然摆动"
    },
    {
        "action_id": "act_023",
        "name": "跑步机爬坡",
        "action_category": "main_cardio",
        "target_muscles": ["臀大肌", "腘绳肌", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_18",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/treadmill_incline.mp4",
        "image_url": "treadmill_incline.png",
        "safety_tips": "坡度 8-12%，速度 4-5km/h，避免扶手依赖"
    },
    {
        "action_id": "act_024",
        "name": "椭圆机训练",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "下肢肌群", "上肢肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_5",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/elliptical.mp4",
        "image_url": "elliptical.png",
        "safety_tips": "全脚掌踩实踏板，配合手臂推拉，保持节奏稳定"
    },
    {
        "action_id": "act_025",
        "name": "椭圆机阻力训练",
        "action_category": "main_cardio",
        "target_muscles": ["下肢肌群", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_5",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/elliptical_resistance.mp4",
        "image_url": "elliptical_resistance.png",
        "safety_tips": "增加阻力级别，保持动作幅度完整"
    },
    {
        "action_id": "act_026",
        "name": "动感单车骑行",
        "action_category": "main_cardio",
        "target_muscles": ["股四头肌", "腘绳肌", "心肺功能"],
        "difficulty_level": "初级",
        "equipment_id": "eq_9",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/spinning.mp4",
        "image_url": "spinning.png",
        "safety_tips": "调整座椅高度至髋部水平，保持核心收紧"
    },
    {
        "action_id": "act_027",
        "name": "动感单车冲刺",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "下肢肌群"],
        "difficulty_level": "高级",
        "equipment_id": "eq_9",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/spinning_sprint.mp4",
        "image_url": "spinning_sprint.png",
        "safety_tips": "高强度间歇，注意呼吸节奏，避免过度疲劳"
    },
    {
        "action_id": "act_028",
        "name": "划船机训练",
        "action_category": "main_cardio",
        "target_muscles": ["背阔肌", "心肺功能", "核心肌群"],
        "difficulty_level": "中级",
        "equipment_id": "eq_14",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/rowing.mp4",
        "image_url": "rowing.png",
        "safety_tips": "动作顺序：腿→躯干→手臂，回位时顺序相反"
    },
    {
        "action_id": "act_029",
        "name": "划船机间歇训练",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "全身肌群"],
        "difficulty_level": "高级",
        "equipment_id": "eq_14",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/rowing_interval.mp4",
        "image_url": "rowing_interval.png",
        "safety_tips": "高强度 1 分钟 + 低强度 1 分钟，循环进行"
    },
    {
        "action_id": "act_030",
        "name": "登山机训练",
        "action_category": "main_cardio",
        "target_muscles": ["下肢肌群", "臀大肌", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_17",
        "estimated_seconds": 300,
        "video_demo_url": "/videos/cardio/stair_climber.mp4",
        "image_url": "stair_climber.png",
        "safety_tips": "保持直立姿势，避免过度依赖扶手"
    },
    {
        "action_id": "act_031",
        "name": "登山机快速攀登",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "下肢肌群"],
        "difficulty_level": "高级",
        "equipment_id": "eq_17",
        "estimated_seconds": 120,
        "video_demo_url": "/videos/cardio/stair_climber_fast.mp4",
        "image_url": "stair_climber_fast.png",
        "safety_tips": "提高步频，保持呼吸稳定"
    },
    {
        "action_id": "act_032",
        "name": "开合跳（有氧版）",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "全身肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/jumping_jacks_cardio.mp4",
        "image_url": "jumping_jacks_cardio.png",
        "safety_tips": "保持节奏稳定，持续 1 分钟以上"
    },
    {
        "action_id": "act_033",
        "name": "高抬腿跑",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "髋屈肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/high_knees_run.mp4",
        "image_url": "high_knees_run.png",
        "safety_tips": "快速交替抬腿，保持上身稳定"
    },
    {
        "action_id": "act_034",
        "name": "波比跳",
        "action_category": "main_cardio",
        "target_muscles": ["全身肌群", "心肺功能"],
        "difficulty_level": "高级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/burpee.mp4",
        "image_url": "burpee.png",
        "safety_tips": "完整动作包含俯卧撑，注意核心收紧"
    },
    {
        "action_id": "act_035",
        "name": "战绳波浪",
        "action_category": "main_cardio",
        "target_muscles": ["肩部", "核心肌群", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_16",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/battle_rope_waves.mp4",
        "image_url": "battle_rope_waves.png",
        "safety_tips": "双臂交替或同时挥动，保持核心稳定"
    },
    {
        "action_id": "act_036",
        "name": "战绳重摔",
        "action_category": "main_cardio",
        "target_muscles": ["核心肌群", "肩部", "心肺功能"],
        "difficulty_level": "高级",
        "equipment_id": "eq_16",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/battle_rope_slam.mp4",
        "image_url": "battle_rope_slam.png",
        "safety_tips": "用力将绳子摔向地面，利用爆发力"
    },
    {
        "action_id": "act_037",
        "name": "壶铃摇摆",
        "action_category": "main_cardio",
        "target_muscles": ["臀大肌", "腘绳肌", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_10",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/kettlebell_swing.mp4",
        "image_url": "kettlebell_swing.png",
        "safety_tips": "用髋部爆发力驱动，避免用手臂 lifting"
    },
    {
        "action_id": "act_038",
        "name": "跳绳",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "小腿三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 120,
        "video_demo_url": "/videos/cardio/jump_rope.mp4",
        "image_url": "jump_rope.png",
        "safety_tips": "前脚掌着地，手腕转动摇绳，保持节奏"
    },
    {
        "action_id": "act_039",
        "name": "双摇跳绳",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "下肢肌群"],
        "difficulty_level": "高级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/double_under.mp4",
        "image_url": "double_under.png",
        "safety_tips": "需要较高协调性，跳起时快速摇绳两圈"
    },
    {
        "action_id": "act_040",
        "name": "滑雪跳",
        "action_category": "main_cardio",
        "target_muscles": ["下肢肌群", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/skater_jump.mp4",
        "image_url": "skater_jump.png",
        "safety_tips": "左右跳跃，后腿交叉，保持平衡"
    },
    {
        "action_id": "act_041",
        "name": "登山者",
        "action_category": "main_cardio",
        "target_muscles": ["核心肌群", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/mountain_climber.mp4",
        "image_url": "mountain_climber.png",
        "safety_tips": "平板支撑位，快速交替提膝"
    },
    {
        "action_id": "act_042",
        "name": "深蹲跳",
        "action_category": "main_cardio",
        "target_muscles": ["股四头肌", "臀大肌", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/squat_jump.mp4",
        "image_url": "squat_jump.png",
        "safety_tips": "深蹲后爆发跳起，落地缓冲"
    },
    {
        "action_id": "act_043",
        "name": "弓步跳",
        "action_category": "main_cardio",
        "target_muscles": ["下肢肌群", "心肺功能"],
        "difficulty_level": "高级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/lunge_jump.mp4",
        "image_url": "lunge_jump.png",
        "safety_tips": "空中交换双腿位置，注意落地稳定"
    },
    {
        "action_id": "act_044",
        "name": "平板支撑开合跳",
        "action_category": "main_cardio",
        "target_muscles": ["核心肌群", "心肺功能"],
        "difficulty_level": "中级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cardio/plank_jack.mp4",
        "image_url": "plank_jack.png",
        "safety_tips": "平板支撑位，双脚开合跳，保持核心稳定"
    },
    {
        "action_id": "act_045",
        "name": "原地冲刺跑",
        "action_category": "main_cardio",
        "target_muscles": ["心肺功能", "下肢肌群"],
        "difficulty_level": "高级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cardio/sprint_in_place.mp4",
        "image_url": "sprint_in_place.png",
        "safety_tips": "最大速度冲刺，注意呼吸控制"
    },
    
    # ==================== 力量动作 (main_strength) - 45 个 ====================
    # 杠铃相关 (eq_1) - 8 个
    {
        "action_id": "act_046",
        "name": "杠铃深蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌", "腘绳肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_1",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/barbell_squat.mp4",
        "image_url": "barbell_squat.png",
        "safety_tips": "杠铃置于斜方肌，膝盖与脚尖方向一致，下蹲至大腿平行地面"
    },
    {
        "action_id": "act_047",
        "name": "杠铃硬拉",
        "action_category": "main_strength",
        "target_muscles": ["腘绳肌", "臀大肌", "下背部"],
        "difficulty_level": "中级",
        "equipment_id": "eq_1",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/barbell_deadlift.mp4",
        "image_url": "barbell_deadlift.png",
        "safety_tips": "保持背部挺直，杠铃贴近小腿，用髋部驱动"
    },
    {
        "action_id": "act_048",
        "name": "杠铃卧推",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌", "三角肌前束", "肱三头肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_1",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/barbell_bench_press.mp4",
        "image_url": "barbell_bench_press.png",
        "safety_tips": "肩胛骨收紧，杠铃下落至乳头连线，推起时呼气"
    },
    {
        "action_id": "act_049",
        "name": "杠铃划船",
        "action_category": "main_strength",
        "target_muscles": ["背阔肌", "斜方肌", "肱二头肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_1",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/barbell_row.mp4",
        "image_url": "barbell_row.png",
        "safety_tips": "上身前倾 45 度，杠铃拉向腹部，避免腰部代偿"
    },
    {
        "action_id": "act_050",
        "name": "杠铃推举",
        "action_category": "main_strength",
        "target_muscles": ["三角肌", "肱三头肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_1",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/barbell_overhead_press.mp4",
        "image_url": "barbell_overhead_press.png",
        "safety_tips": "核心收紧，避免腰部过度后仰，杠铃推过头顶"
    },
    {
        "action_id": "act_051",
        "name": "杠铃弯举",
        "action_category": "main_strength",
        "target_muscles": ["肱二头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_1",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/barbell_curl.mp4",
        "image_url": "barbell_curl.png",
        "safety_tips": "大臂固定，仅前臂运动，避免身体晃动借力"
    },
    {
        "action_id": "act_052",
        "name": "杠铃箭步蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_1",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/barbell_lunge.mp4",
        "image_url": "barbell_lunge.png",
        "safety_tips": "保持躯干直立，前后膝均呈 90 度"
    },
    {
        "action_id": "act_053",
        "name": "杠铃臀推",
        "action_category": "main_strength",
        "target_muscles": ["臀大肌", "腘绳肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_1",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/barbell_hip_thrust.mp4",
        "image_url": "barbell_hip_thrust.png",
        "safety_tips": "上背部靠在凳上，杠铃置于髋部，顶峰收缩"
    },
    
    # 哑铃相关 (eq_6) - 8 个
    {
        "action_id": "act_054",
        "name": "哑铃深蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_6",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/dumbbell_squat.mp4",
        "image_url": "dumbbell_squat.png",
        "safety_tips": "双手持哑铃于身体两侧，保持核心收紧"
    },
    {
        "action_id": "act_055",
        "name": "哑铃卧推",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌", "三角肌前束"],
        "difficulty_level": "初级",
        "equipment_id": "eq_6",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/dumbbell_bench_press.mp4",
        "image_url": "dumbbell_bench_press.png",
        "safety_tips": "需配合卧推凳 (eq_2)，哑铃下落至胸部两侧"
    },
    {
        "action_id": "act_056",
        "name": "哑铃划船",
        "action_category": "main_strength",
        "target_muscles": ["背阔肌", "肱二头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_6",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/dumbbell_row.mp4",
        "image_url": "dumbbell_row.png",
        "safety_tips": "单臂支撑于凳上，另一手持哑铃拉向髋部"
    },
    {
        "action_id": "act_057",
        "name": "哑铃推举",
        "action_category": "main_strength",
        "target_muscles": ["三角肌", "肱三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_6",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/dumbbell_shoulder_press.mp4",
        "image_url": "dumbbell_shoulder_press.png",
        "safety_tips": "可坐姿或站姿，哑铃推过头顶"
    },
    {
        "action_id": "act_058",
        "name": "哑铃侧平举",
        "action_category": "main_strength",
        "target_muscles": ["三角肌中束"],
        "difficulty_level": "初级",
        "equipment_id": "eq_6",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/dumbbell_lateral_raise.mp4",
        "image_url": "dumbbell_lateral_raise.png",
        "safety_tips": "手臂微屈，抬至肩部水平，避免耸肩"
    },
    {
        "action_id": "act_059",
        "name": "哑铃弯举",
        "action_category": "main_strength",
        "target_muscles": ["肱二头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_6",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/dumbbell_curl.mp4",
        "image_url": "dumbbell_curl.png",
        "safety_tips": "可交替或同时进行，保持大臂固定"
    },
    {
        "action_id": "act_060",
        "name": "哑铃弓步蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_6",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/dumbbell_lunge.mp4",
        "image_url": "dumbbell_lunge.png",
        "safety_tips": "双手持哑铃，前后腿均呈 90 度"
    },
    {
        "action_id": "act_061",
        "name": "哑铃俯身飞鸟",
        "action_category": "main_strength",
        "target_muscles": ["三角肌后束", "斜方肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_6",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/dumbbell_reverse_fly.mp4",
        "image_url": "dumbbell_reverse_fly.png",
        "safety_tips": "上身前倾，手臂向两侧打开，挤压肩胛骨"
    },
    
    # 史密斯机相关 (eq_16) - 6 个
    {
        "action_id": "act_062",
        "name": "史密斯深蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_16",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/smith_squat.mp4",
        "image_url": "smith_squat.png",
        "safety_tips": "固定轨迹更安全，适合初学者学习深蹲动作"
    },
    {
        "action_id": "act_063",
        "name": "史密斯卧推",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌", "肱三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_16",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/smith_bench_press.mp4",
        "image_url": "smith_bench_press.png",
        "safety_tips": "需配合卧推凳，杠铃下落至胸部中部"
    },
    {
        "action_id": "act_064",
        "name": "史密斯推举",
        "action_category": "main_strength",
        "target_muscles": ["三角肌", "肱三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_16",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/smith_shoulder_press.mp4",
        "image_url": "smith_shoulder_press.png",
        "safety_tips": "坐姿进行，固定轨迹减少肩部压力"
    },
    {
        "action_id": "act_065",
        "name": "史密斯硬拉",
        "action_category": "main_strength",
        "target_muscles": ["腘绳肌", "臀大肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_16",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/smith_deadlift.mp4",
        "image_url": "smith_deadlift.png",
        "safety_tips": "固定轨迹有助于保持正确姿势"
    },
    {
        "action_id": "act_066",
        "name": "史密斯提踵",
        "action_category": "main_strength",
        "target_muscles": ["小腿三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_16",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/smith_calf_raise.mp4",
        "image_url": "smith_calf_raise.png",
        "safety_tips": "前脚掌踩实，充分拉伸和收缩小腿"
    },
    {
        "action_id": "act_067",
        "name": "史密斯弓步蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_16",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/smith_lunge.mp4",
        "image_url": "smith_lunge.png",
        "safety_tips": "固定轨迹帮助保持平衡"
    },
    
    # 龙门架相关 (eq_3) - 6 个
    {
        "action_id": "act_068",
        "name": "龙门架夹胸",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌", "三角肌前束"],
        "difficulty_level": "中级",
        "equipment_id": "eq_3",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/cable_fly.mp4",
        "image_url": "cable_fly.png",
        "safety_tips": "手臂微屈，感受胸肌收缩，避免肩部代偿"
    },
    {
        "action_id": "act_069",
        "name": "龙门架下拉",
        "action_category": "main_strength",
        "target_muscles": ["背阔肌", "肱二头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_3",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/cable_lat_pulldown.mp4",
        "image_url": "cable_lat_pulldown.png",
        "safety_tips": "宽握下拉至锁骨位置，避免身体后仰"
    },
    {
        "action_id": "act_070",
        "name": "龙门架划船",
        "action_category": "main_strength",
        "target_muscles": ["背阔肌", "斜方肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_3",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/cable_row.mp4",
        "image_url": "cable_row.png",
        "safety_tips": "坐姿划船，拉向腹部，挤压肩胛骨"
    },
    {
        "action_id": "act_071",
        "name": "龙门架三头下压",
        "action_category": "main_strength",
        "target_muscles": ["肱三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_3",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/cable_tricep_pushdown.mp4",
        "image_url": "cable_tricep_pushdown.png",
        "safety_tips": "大臂固定，仅前臂下压"
    },
    {
        "action_id": "act_072",
        "name": "龙门架面拉",
        "action_category": "main_strength",
        "target_muscles": ["三角肌后束", "斜方肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_3",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/cable_face_pull.mp4",
        "image_url": "cable_face_pull.png",
        "safety_tips": "拉向面部，外旋肩部，改善圆肩"
    },
    {
        "action_id": "act_073",
        "name": "龙门架二头弯举",
        "action_category": "main_strength",
        "target_muscles": ["肱二头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_3",
        "estimated_seconds": 2,
        "video_demo_url": "/videos/strength/cable_bicep_curl.mp4",
        "image_url": "cable_bicep_curl.png",
        "safety_tips": "使用直杆或绳索，保持大臂固定"
    },
    
    # 固定器械相关 - 11 个
    {
        "action_id": "act_074",
        "name": "坐姿推胸",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌", "肱三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_4",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/chest_press.mp4",
        "image_url": "chest_press.png",
        "safety_tips": "调整座椅高度，把手与胸部齐平"
    },
    {
        "action_id": "act_075",
        "name": "高位下拉",
        "action_category": "main_strength",
        "target_muscles": ["背阔肌", "肱二头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_11",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/lat_pulldown.mp4",
        "image_url": "lat_pulldown.png",
        "safety_tips": "宽握下拉，避免身体过度后仰"
    },
    {
        "action_id": "act_076",
        "name": "腿弯举",
        "action_category": "main_strength",
        "target_muscles": ["腘绳肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_12",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/leg_curl.mp4",
        "image_url": "leg_curl.png",
        "safety_tips": "俯卧或坐姿，充分收缩腘绳肌"
    },
    {
        "action_id": "act_077",
        "name": "腿部推蹬",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_13",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/leg_press.mp4",
        "image_url": "leg_press.png",
        "safety_tips": "双脚与肩同宽，膝盖不超过脚尖"
    },
    {
        "action_id": "act_078",
        "name": "肩部推举",
        "action_category": "main_strength",
        "target_muscles": ["三角肌", "肱三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_15",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/shoulder_press_machine.mp4",
        "image_url": "shoulder_press_machine.png",
        "safety_tips": "调整座椅，把手与肩部齐平"
    },
    {
        "action_id": "act_079",
        "name": "卷腹",
        "action_category": "main_strength",
        "target_muscles": ["腹直肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_0",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/abdominal_crunch.mp4",
        "image_url": "abdominal_crunch.png",
        "safety_tips": "用腹部发力，避免颈部代偿"
    },
    {
        "action_id": "act_080",
        "name": "哈克深蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_7",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/hack_squat.mp4",
        "image_url": "hack_squat.png",
        "safety_tips": "背部贴紧靠垫，下蹲至大腿平行"
    },
    {
        "action_id": "act_081",
        "name": "臀部外展",
        "action_category": "main_strength",
        "target_muscles": ["臀中肌", "臀小肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_8",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/hip_abduction.mp4",
        "image_url": "hip_abduction.png",
        "safety_tips": "坐姿，双腿向外打开，感受臀部外侧发力"
    },
    {
        "action_id": "act_082",
        "name": "臀部内收",
        "action_category": "main_strength",
        "target_muscles": ["大腿内收肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_8",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/hip_adduction.mp4",
        "image_url": "hip_adduction.png",
        "safety_tips": "坐姿，双腿向内夹紧"
    },
    {
        "action_id": "act_083",
        "name": "蝴蝶机夹胸",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_14",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/pec_fly_machine.mp4",
        "image_url": "pec_fly_machine.png",
        "safety_tips": "调整座椅，手臂与胸部齐平，感受胸肌收缩"
    },
    {
        "action_id": "act_084",
        "name": "引体向上",
        "action_category": "main_strength",
        "target_muscles": ["背阔肌", "肱二头肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_18",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/pull_up.mp4",
        "image_url": "pull_up.png",
        "safety_tips": "正握或反握，下巴过杠，控制下落速度"
    },
    
    # 壶铃相关 (eq_10) - 3 个
    {
        "action_id": "act_085",
        "name": "壶铃高脚杯深蹲",
        "action_category": "main_strength",
        "target_muscles": ["股四头肌", "臀大肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_10",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/kettlebell_goblet_squat.mp4",
        "image_url": "kettlebell_goblet_squat.png",
        "safety_tips": "双手托住壶铃于胸前，保持躯干直立"
    },
    {
        "action_id": "act_086",
        "name": "壶铃推举",
        "action_category": "main_strength",
        "target_muscles": ["三角肌", "肱三头肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_10",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/kettlebell_press.mp4",
        "image_url": "kettlebell_press.png",
        "safety_tips": "从肩部位置推起，核心收紧"
    },
    {
        "action_id": "act_087",
        "name": "壶铃土耳其起立",
        "action_category": "main_strength",
        "target_muscles": ["核心肌群", "全身肌群"],
        "difficulty_level": "高级",
        "equipment_id": "eq_10",
        "estimated_seconds": 5,
        "video_demo_url": "/videos/strength/kettlebell_turkish_getup.mp4",
        "image_url": "kettlebell_turkish_getup.png",
        "safety_tips": "复杂动作，需分步练习，保持壶铃稳定"
    },
    
    # 卧推凳相关 (eq_2) - 3 个
    {
        "action_id": "act_088",
        "name": "上斜哑铃卧推",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌上束", "三角肌前束"],
        "difficulty_level": "中级",
        "equipment_id": "eq_2",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/incline_dumbbell_press.mp4",
        "image_url": "incline_dumbbell_press.png",
        "safety_tips": "凳子调至 30-45 度，哑铃下落至胸部上侧"
    },
    {
        "action_id": "act_089",
        "name": "下斜哑铃卧推",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌下束"],
        "difficulty_level": "中级",
        "equipment_id": "eq_2",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/decline_dumbbell_press.mp4",
        "image_url": "decline_dumbbell_press.png",
        "safety_tips": "注意固定双脚，避免滑落"
    },
    {
        "action_id": "act_090",
        "name": "哑铃仰卧飞鸟",
        "action_category": "main_strength",
        "target_muscles": ["胸大肌"],
        "difficulty_level": "中级",
        "equipment_id": "eq_2",
        "estimated_seconds": 3,
        "video_demo_url": "/videos/strength/dumbbell_fly.mp4",
        "image_url": "dumbbell_fly.png",
        "safety_tips": "手臂微屈，感受胸肌拉伸和收缩"
    },
    
    # ==================== 拉伸动作 (cooldown) - 10 个 ====================
    {
        "action_id": "act_091",
        "name": "股四头肌拉伸",
        "action_category": "cooldown",
        "target_muscles": ["股四头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/quad_stretch.mp4",
        "image_url": "quad_stretch.png",
        "safety_tips": "站立或侧卧，手拉脚踝至臀部，保持 30 秒"
    },
    {
        "action_id": "act_092",
        "name": "腘绳肌拉伸",
        "action_category": "cooldown",
        "target_muscles": ["腘绳肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/hamstring_stretch.mp4",
        "image_url": "hamstring_stretch.png",
        "safety_tips": "坐姿或站姿，腿伸直，身体前倾感受大腿后侧拉伸"
    },
    {
        "action_id": "act_093",
        "name": "臀肌拉伸",
        "action_category": "cooldown",
        "target_muscles": ["臀大肌", "梨状肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/glute_stretch.mp4",
        "image_url": "glute_stretch.png",
        "safety_tips": "仰卧，一腿跨于另一腿上，双手抱膝拉向胸部"
    },
    {
        "action_id": "act_094",
        "name": "胸部拉伸",
        "action_category": "cooldown",
        "target_muscles": ["胸大肌", "三角肌前束"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/chest_stretch.mp4",
        "image_url": "chest_stretch.png",
        "safety_tips": "手臂扶墙，身体缓慢转离，感受胸部拉伸"
    },
    {
        "action_id": "act_095",
        "name": "背部拉伸",
        "action_category": "cooldown",
        "target_muscles": ["背阔肌", "斜方肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/back_stretch.mp4",
        "image_url": "back_stretch.png",
        "safety_tips": "坐姿或站姿，双手交叉前伸，感受背部拉伸"
    },
    {
        "action_id": "act_096",
        "name": "肩部拉伸",
        "action_category": "cooldown",
        "target_muscles": ["三角肌", "肩袖肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/shoulder_stretch.mp4",
        "image_url": "shoulder_stretch.png",
        "safety_tips": "手臂横过胸前，另一手辅助拉伸"
    },
    {
        "action_id": "act_097",
        "name": "肱三头肌拉伸",
        "action_category": "cooldown",
        "target_muscles": ["肱三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/tricep_stretch.mp4",
        "image_url": "tricep_stretch.png",
        "safety_tips": "手臂举过头顶弯曲，另一手轻压手肘"
    },
    {
        "action_id": "act_098",
        "name": "肱二头肌拉伸",
        "action_category": "cooldown",
        "target_muscles": ["肱二头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/bicep_stretch.mp4",
        "image_url": "bicep_stretch.png",
        "safety_tips": "手臂向后伸展，手掌贴墙，身体转离"
    },
    {
        "action_id": "act_099",
        "name": "小腿拉伸",
        "action_category": "cooldown",
        "target_muscles": ["小腿三头肌"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 30,
        "video_demo_url": "/videos/cooldown/calf_stretch.mp4",
        "image_url": "calf_stretch.png",
        "safety_tips": "弓箭步，后腿伸直，脚跟踩实地面"
    },
    {
        "action_id": "act_100",
        "name": "全身放松拉伸",
        "action_category": "cooldown",
        "target_muscles": ["全身肌群"],
        "difficulty_level": "初级",
        "equipment_id": "eq_19",
        "estimated_seconds": 60,
        "video_demo_url": "/videos/cooldown/full_body_stretch.mp4",
        "image_url": "full_body_stretch.png",
        "safety_tips": "配合深呼吸，从头部到脚部依次放松各肌群"
    }
]


def seed_actions():
    """
    初始化训练动作数据
    对应《任务书》技术指标：动作推荐库规模不少于 100 个标准动作
    """
    db = SessionLocal()
    
    try:
        # 1. 检查是否已存在数据
        existing_count = db.query(TrainingAction).count()
        if existing_count > 0:
            print(f"⚠️  数据库中已有{existing_count}条动作数据")
            print("如需重新初始化，请先清空 training_action 表")
            return
        
        # 2. 插入预置数据
        for action_data in ACTIONS_DATA:
            action = TrainingAction(
                action_id=action_data["action_id"],
                name=action_data["name"],
                action_category=action_data["action_category"],
                target_muscles=json.dumps(action_data["target_muscles"], ensure_ascii=False),
                difficulty_level=action_data["difficulty_level"],
                equipment_id=action_data["equipment_id"],
                estimated_seconds=action_data["estimated_seconds"],
                video_demo_url=action_data["video_demo_url"],
                image_url=action_data.get("image_url"),  # ✅ 新增字段
                safety_tips=action_data["safety_tips"]
            )
            db.add(action)
        
        db.commit()
        
        # 3. 验证插入结果
        final_count = db.query(TrainingAction).count()
        print(f"✅ 动作数据初始化完成")
        print(f"📊 共导入 {final_count} 条动作记录")
        print(f"📋 动作分类统计:")
        
        # 统计各类动作数量
        categories = {}
        for action in ACTIONS_DATA:
            cat = action["action_category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            cat_name = {
                "warmup": "热身激活",
                "main_cardio": "正式训练 - 有氧",
                "main_strength": "正式训练 - 力量",
                "cooldown": "拉伸放松"
            }.get(cat, cat)
            print(f"   - {cat_name}: {count} 个")
        
        # 统计难度分布
        difficulties = {}
        for action in ACTIONS_DATA:
            level = action["difficulty_level"]
            difficulties[level] = difficulties.get(level, 0) + 1
        
        print(f"📋 动作难度统计:")
        for level, count in difficulties.items():
            print(f"   - {level}: {count} 个")
        
        # 统计器材关联
        equipment_actions = {}
        for action in ACTIONS_DATA:
            eq_id = action["equipment_id"]
            equipment_actions[eq_id] = equipment_actions.get(eq_id, 0) + 1
        
        print(f"📋 器材关联统计 (前 10):")
        sorted_eq = sorted(equipment_actions.items(), key=lambda x: x[1], reverse=True)[:10]
        for eq_id, count in sorted_eq:
            print(f"   - {eq_id}: {count} 个动作")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败：{e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  训练动作数据初始化脚本")
    print("  对应《需求规格说明书》表 2-4 TrainingAction 业务对象")
    print("  对应《任务书》技术指标：动作库规模≥100 个")
    print("=" * 60)
    seed_actions()
    print("=" * 60)