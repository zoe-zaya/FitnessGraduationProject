# 添加动作弹窗功能实现计划

## 需求概述

在编辑计划页面点击某一阶段的"添加动作"按钮时，弹出底部抽屉式弹窗，弹窗中推荐的动作需满足：

1. 和该阶段的目标肌群相似
2. 可替换动作需要用到的器材是健身房里有的
3. 动作类别符合该阶段类型

点击推荐动作即可添加到该阶段。

## 现状分析

* **当前添加动作方式**：点击"+ 添加动作"按钮 → `addActionToSession()` → 跳转到独立的 `select-action.vue` 页面

* **现有替换弹窗**：`plan-edit.vue` 中已有一个底部抽屉式替换动作弹窗（第131-228行模板，第732-1088行样式），可作为参考

* **后端现有 API**：

  * `GET /api/action/query`：按类别/肌群查询动作，但不过滤用户健身房器材

  * `GET /api/action/replace-recommend/{action_id}`：替换推荐，基于原动作的肌群+器材过滤，但需要原动作 ID

  * 缺少一个**基于阶段信息推荐可添加动作**的 API

## 实现步骤

### 步骤 1：后端 - 新增"添加动作推荐"API

**文件**：`02_Backend/app/api/action.py`

新增 API 端点 `GET /api/action/add-recommend/{session_id}`，逻辑如下：

1. 接收参数：`session_id`（必填）、`plan_id`（必填，Query 参数）
2. 查询 `PlanSession` 获取阶段的 `target_muscles`、`session_type`、`plan_id`
3. 通过 `TrainingPlan.inventory_id` 查询用户健身房的所有器材 ID 集合
4. 根据 `session_type` 映射 `action_category`：

   * WARMUP → warmup

   * MAIN → main\_strength（同时包含 main\_cardio）

   * COOLDOWN → cooldown
5. 查询 `TrainingAction` 表，筛选条件：

   * `action_category` 符合阶段类型

   * `equipment_id` 在用户健身房器材集合中，或 `equipment_id == 'none'`

   * 排除该阶段已有的动作（通过 `SessionActionItem` 查询已添加的 `action_id` 列表）
6. 计算每个候选动作与阶段目标肌群的相似度（Jaccard 系数）
7. 按相似度降序排序返回

**响应模型**：复用 `ReplaceRecommendResponse`（包含 `muscle_similarity` 字段），或新建 `AddRecommendResponse`

**文件**：`02_Backend/app/schemas/action.py`

新增 `AddRecommendResponse` 模型（与 `ReplaceRecommendResponse` 结构一致，可考虑复用）

### 步骤 2：前端 - 在 plan-edit.vue 中添加"添加动作"弹窗

**文件**：`03_Frontend/my-fitness-app/src/pages/plan/plan-edit.vue`

#### 2.1 模板部分

在替换弹窗之后，新增"添加动作"底部抽屉弹窗，结构参考替换弹窗：

```
add-dialog-mask
  ├── add-dialog-content
  │   ├── add-dialog-handle（拖拽条）
  │   ├── add-dialog-header（标题"添加动作" + 关闭按钮）
  │   ├── session-info-card（显示当前阶段信息：阶段名称 + 目标肌群标签）
  │   ├── add-dialog-body
  │   │   ├── recommend-header（"推荐动作" + 可选数量）
  │   │   ├── add-loading（加载状态）
  │   │   ├── recommend-list（推荐动作列表，scroll-view）
  │   │   │   └── recommend-item（动作名称 + 肌群相似度 + 难度 + 器材 + 目标肌群标签）
  │   │   └── recommend-empty（无推荐时的空状态）
```

#### 2.2 脚本部分

新增状态变量：

* `showAddDialog`：控制弹窗显示

* `currentAddSession`：当前要添加动作的阶段

* `addRecommendList`：推荐动作列表

* `addLoading`：加载状态

新增方法：

* `openAddDialog(session)`：打开弹窗，记录当前阶段，调用 `loadAddRecommendations`

* `loadAddRecommendations(session)`：调用新 API `GET /api/action/add-recommend/{session_id}?plan_id=xxx`，获取推荐列表

* `closeAddDialog()`：关闭弹窗，清空状态

* `confirmAddAction(action)`：点击推荐动作，调用 `POST /api/plan/v2/addAction/{plan_id}` 添加动作，成功后关闭弹窗并刷新计划详情

修改方法：

* `addActionToSession(session)`：从 `uni.navigateTo` 改为调用 `openAddDialog(session)`

#### 2.3 样式部分

复用替换弹窗的样式模式（`.replace-dialog-*`），新增 `.add-dialog-*` 样式类。两者结构高度相似，主要区别：

* 弹窗标题为"添加动作"

* 顶部显示阶段信息卡片（阶段名称 + 目标肌群），而非原动作卡片

* 推荐项点击后执行添加操作而非替换

### 步骤 3：前端 - 更新 API 常量

**文件**：`03_Frontend/my-fitness-app/src/utils/constants.js`

在 `API` 对象中新增：

```javascript
ACTION_ADD_RECOMMEND: '/api/action/add-recommend'
```

### 步骤 4：验证与测试

1. 后端：启动服务，调用新 API 验证返回数据正确性
2. 前端：在编辑计划页面点击"添加动作"按钮，验证弹窗弹出、推荐动作加载、点击添加功能正常
3. 验证三个筛选条件：肌群相似、器材可用、类别匹配

## 涉及文件清单

| 文件                                                        | 操作 | 说明                                            |
| --------------------------------------------------------- | -- | --------------------------------------------- |
| `02_Backend/app/api/action.py`                            | 修改 | 新增 `add-recommend` API 端点                     |
| `02_Backend/app/schemas/action.py`                        | 修改 | 新增 `AddRecommendResponse` 模型                  |
| `03_Frontend/my-fitness-app/src/pages/plan/plan-edit.vue` | 修改 | 新增添加动作弹窗（模板+脚本+样式），修改 `addActionToSession` 方法 |
| `03_Frontend/my-fitness-app/src/utils/constants.js`       | 修改 | 新增 `ACTION_ADD_RECOMMEND` 常量                  |

