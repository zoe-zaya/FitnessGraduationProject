# 训练计划模块重构计划（V2.1）

## 一、需求分析总结

根据接口设计文档（V2.1）和需求分析文档（V2.1）：

### 1.1 核心业务对象
| 对象 | 说明 |
|------|------|
| TrainingPlan | 训练计划，含 plan_type、scheme_type、cycle_rule |
| PlanSession | 计划阶段，含热身/正式/拉伸三阶段 |
| SessionActionItem | 阶段动作项，含重量记录、休息时长（默认60s） |
| TrainingSchedule | 训练日程，支持延后1-3天 |

### 1.2 API 端点（共11个）
| # | 接口 | 路径 | 方法 |
|---|------|------|------|
| 1 | 生成训练计划 | `/generate` | POST |
| 2 | 获取计划列表 | `/getAllPlan` | GET |
| 3 | 获取计划详情 | `/getPlan/{plan_id}` | GET |
| 4 | 获取7天日程 | `/schedule/{plan_id}` | GET |
| 5 | 更新计划信息 | `/updatePlan/{plan_id}` | PUT |
| 6 | 删除训练计划 | `/deletePlan/{plan_id}` | DELETE |
| 7 | 添加动作项 | `/addAction/{plan_id}` | POST |
| 8 | 修改动作项 | `/updateAction/{plan_id}/{item_id}` | PUT |
| 9 | 删除动作项 | `/deleteAction/{plan_id}/{item_id}` | DELETE |
| 10 | 替换动作项 | `/replaceAction/{plan_id}/{item_id}` | POST |
| 11 | 延后训练 | `/postponeSchedule/{plan_id}/{schedule_id}` | POST |

### 1.3 关键业务规则
- **休息时长**：默认60秒，范围30-300秒
- **延后限制**：最多延后3天
- **器材约束**：所有动作必须符合用户器材清单
- **分化方案**：ONE_SPLIT/TWO_SPLIT/THREE_SPLIT/FOUR_SPLIT

---

## 二、现有代码分析

### 2.1 已实现组件 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `app/models/plan.py` | ✅ 完整 | 包含 TrainingPlan、PlanSession、SessionActionItem、TrainingSchedule |
| `app/schemas/plan.py` | ✅ 完整 | 包含所有请求/响应模型 |
| `app/api/plan_v2.py` | ✅ 完整 | 包含全部11个API端点 |
| `app/services/plan_generator_v2.py` | ✅ 完整 | 实现减脂/增肌计划生成逻辑 |

### 2.2 发现的问题 ❌

| # | 问题 | 位置 | 说明 |
|---|------|------|------|
| 1 | **器材约束验证缺失** | `replaceAction` 端点 | 新动作未验证是否在用户器材清单中 |
| 2 | **replaceAction 缺少器材检查** | plan_v2.py L469-477 | 添加动作时验证了器材，但替换时未验证 |

---

## 三、重构任务清单

### Task 1: 修复 replaceAction 端点的器材约束验证
**问题**：`replaceAction` 端点未验证新动作所需的器材是否在用户器材清单中

**修复位置**：`app/api/plan_v2.py` L447-505

**修复内容**：
在替换动作前，添加与 `addAction` 相同的器材可用性检查逻辑

```python
# 检查器材可用性（新增）
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
```

### Task 2: 验证编译无错误
**操作**：运行后端服务，检查是否有导入错误或语法错误

### Task 3: 代码审查确认
**检查项**：
- [ ] rest_seconds_default 默认值为 60
- [ ] postpone_count 最大值为 3
- [ ] 所有枚举值与文档一致
- [ ] 7天日程生成逻辑正确

---

## 四、执行步骤

1. **修复 replaceAction 端点** - 添加器材约束验证
2. **运行后端验证** - python -m uvicorn app.main:app --reload
3. **检查诊断信息** - 确认无编译错误

---

## 五、预计工作量

- 修改代码：1处（约20行）
- 验证测试：约15分钟
