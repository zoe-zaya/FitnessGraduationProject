# 训练执行页面计时与完成训练功能实施计划

## 需求概述

在 `training-execution.vue` 页面实现：

1. 点击"开始训练"按钮后开始计时，同时"结束训练"按钮被激活
2. 点击"结束训练"按钮后，将实际练习时长写入数据库并返回计划详情页面
3. 同一个训练计划一天只能做一次，开始/结束训练时都需要确认弹窗

## 现状分析

### 已有功能

* 计时器逻辑已实现（`elapsedSeconds`、`startTimer`、`pauseTimer`、`stopTimer`）

* 底部栏有"开始训练/暂停/继续"按钮和"完成训练"按钮（仅所有动作完成后显示）

* `TrainingSchedule` 模型已有 `COMPLETED` 状态枚举

### 需要修复/新增

* **后端缺失**：没有"完成训练"API 端点，前端错误调用了 `postponeSchedule` 端点

* **数据库缺失**：`TrainingSchedule` 表没有 `actual_duration_seconds` 字段

* **前端缺失**：没有"结束训练"按钮的激活逻辑，没有确认弹窗，没有保存时长到数据库

***

## 实施步骤

### 第一步：后端 — 数据库模型修改

**文件**: `02_Backend/app/models/plan.py`

在 `TrainingSchedule` 模型中新增字段：

```python
actual_duration_seconds = Column(Integer, nullable=True, comment="实际训练时长（秒）")
```

### 第二步：后端 — Schema 新增

**文件**: `02_Backend/app/schemas/plan.py`

1. 新增请求模型 `ScheduleCompleteRequest`：

```python
class ScheduleCompleteRequest(BaseModel):
    """完成训练日程请求模型"""
    actual_duration_seconds: int = Field(..., ge=0, description="实际训练时长（秒）")
```

1. 新增响应模型 `ScheduleCompleteResponse`：

```python
class ScheduleCompleteResponse(BaseModel):
    """完成训练响应模型"""
    message: str
    actual_duration_seconds: int
```

1. 更新 `TrainingScheduleResponse`，新增 `actual_duration_seconds` 字段

### 第三步：后端 — 新增 API 端点

**文件**: `02_Backend/app/api/plan_v2.py`

新增 `POST /api/plan/v2/completeSchedule/{plan_id}/{schedule_id}` 端点：

* 验证日程归属当前用户

* 验证日程状态不是 REST

* 验证日程状态不是已完成（防止重复完成）

* 将日程状态更新为 `COMPLETED`

* 将 `actual_duration_seconds` 写入数据库

* 返回完成响应

### 第四步：后端 — 数据库迁移

运行数据库迁移，为 `training_schedule` 表新增 `actual_duration_seconds` 列。

### 第五步：前端 — 常量配置更新

**文件**: `03_Frontend/my-fitness-app/src/utils/constants.js`

在 `API_V2` 中新增：

```javascript
SCHEDULE_COMPLETE: '/api/plan/v2/completeSchedule'
```

### 第六步：前端 — 训练执行页面改造

**文件**: `03_Frontend/my-fitness-app/src/pages/plan/training-execution.vue`

#### 6.1 修改底部栏按钮布局

将原来的"开始训练/暂停/继续" + "完成训练"（条件显示）改为：

* **"开始训练"按钮**：训练未开始时显示

* **"暂停"按钮** + **"结束训练"按钮**：训练进行中时显示

* **"继续"按钮** + **"结束训练"按钮**：训练暂停时显示

即：训练开始后，"结束训练"按钮始终可见且激活。

#### 6.2 修改 `toggleTraining` 函数

在首次点击"开始训练"时，弹出确认弹窗：

```
标题：确认开始训练
内容：确定要开始本次训练吗？同一训练计划每天只能训练一次。
```

确认后才启动计时器。

#### 6.3 修改 `finishTraining` 函数

* 弹出确认弹窗：

  ```
  标题：确认结束训练
  内容：确定要结束本次训练吗？结束后将保存训练记录。
  ```

* 确认后调用新的 `SCHEDULE_COMPLETE` API，传入 `actual_duration_seconds: elapsedSeconds.value`

* 成功后显示 Toast 提示，延迟返回计划详情页

#### 6.4 删除 `allSessionsCompleted` 条件

"结束训练"按钮不再依赖所有动作完成，只要训练已开始就可以结束。

### 第七步：前端 — 计划详情页面适配

**文件**: `03_Frontend/my-fitness-app/src/pages/plan/plan-detail.vue`

修改 `showStartBtn` 计算属性，增加对日程状态的判断：

* 如果当天日程状态为 `COMPLETED`，则不显示"开始训练"按钮

* 可选：显示"今日已完成训练"的提示信息

***

## 修改文件清单

| 文件                                                                 | 修改类型 | 说明                                               |
| ------------------------------------------------------------------ | ---- | ------------------------------------------------ |
| `02_Backend/app/models/plan.py`                                    | 修改   | TrainingSchedule 新增 actual\_duration\_seconds 字段 |
| `02_Backend/app/schemas/plan.py`                                   | 修改   | 新增请求/响应模型，更新 Schedule 响应模型                       |
| `02_Backend/app/api/plan_v2.py`                                    | 修改   | 新增 completeSchedule 端点，更新 import                 |
| `03_Frontend/my-fitness-app/src/utils/constants.js`                | 修改   | API\_V2 新增 SCHEDULE\_COMPLETE                    |
| `03_Frontend/my-fitness-app/src/pages/plan/training-execution.vue` | 修改   | 底部栏改造、确认弹窗、保存时长逻辑                                |
| `03_Frontend/my-fitness-app/src/pages/plan/plan-detail.vue`        | 修改   | 已完成日程不显示开始训练按钮                                   |

