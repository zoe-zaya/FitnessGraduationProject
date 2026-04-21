# 替换动作弹窗功能实现计划

## 需求概述

在编辑计划页面点击某一个动作项的替换动作按钮，弹出可替换动作弹窗。弹窗中推荐的动作需满足：

1. 和原动作的目标肌群相似
2. 可替换动作需要用到的器材是健身房里有的
3. 点击想要做的动作即可把原动作替换成新动作

## 现状分析

* **当前实现**：点击替换按钮 → `uni.navigateTo` 跳转到 `select-action.vue` 页面

* **select-action.vue**：是一个独立页面，支持搜索和筛选动作，但不自动推荐相似肌群的动作

* **后端已有 API**：

  * `POST /api/action/query` — 按类别/肌群查询动作，但不筛选健身房器材

  * `POST /api/action/recommend` — 按器材推荐动作，但只接受单个 equipment\_id

  * `POST /api/plan/v2/replaceAction/{plan_id}/{item_id}` — 替换动作（含器材校验）

## 实现方案

### 一、后端：新增替换动作推荐 API

**文件**：`02_Backend/app/api/action.py`

新增接口 `GET /api/action/replace-recommend/{action_id}`，逻辑如下：

1. 根据 `action_id` 查询原动作的 `target_muscles`、`action_category`、`equipment_id`
2. 通过 `plan_id` 查询计划关联的 `inventory_id`，获取用户健身房的所有器材 ID 列表
3. 查询同类别（`action_category`）的所有动作，排除原动作自身
4. 筛选条件：

   * 动作的 `equipment_id` 在用户健身房器材列表中，或 `equipment_id == "none"`（无器材动作）
5. 计算肌群相似度评分：

   * 原动作的 `target_muscles` 与候选动作的 `target_muscles` 的交集比例

   * 相似度 = 交集肌群数 / 原动作肌群数
6. 按相似度降序排列返回

**请求参数**：

* `action_id`（路径参数）：原动作 ID

* `plan_id`（查询参数）：当前计划 ID，用于获取健身房器材

**响应模型**：复用 `ActionInfoResponse`，新增 `muscle_similarity` 字段

**新增 Schema**：`02_Backend/app/schemas/action.py`

* `ReplaceRecommendResponse`：继承 `ActionInfoResponse`，增加 `muscle_similarity: float` 字段

### 二、前端：在 plan-edit.vue 中添加替换动作弹窗

**文件**：`03_Frontend/my-fitness-app/src/pages/plan/plan-edit.vue`

#### 2.1 弹窗 UI 结构

参考 `gym-list.vue` 的 `dialog-mask` + `dialog-content` 底部滑出模式：

```
dialog-mask（半透明遮罩，点击关闭）
  └── dialog-content（底部滑出面板）
        ├── dialog-header（标题"替换动作" + 关闭按钮）
        ├── original-action-info（原动作信息卡片：名称、肌群、难度）
        ├── recommend-list（推荐动作列表，可滚动）
        │     └── recommend-item（每个推荐动作卡片）
        │           ├── 动作名称 + 难度标签
        │           ├── 目标肌群标签
        │           ├── 器材名称
        │           └── 肌群相似度指示
        └── empty-state（无推荐动作时的空状态）
```

#### 2.2 数据与状态

新增响应式变量：

* `showReplaceDialog`：控制弹窗显示/隐藏

* `currentReplaceAction`：当前要替换的原动作对象

* `currentReplaceSession`：当前动作所属的 session

* `replaceRecommendList`：推荐动作列表

* `replaceLoading`：加载状态

#### 2.3 交互流程

1. 点击替换按钮 → 设置 `currentReplaceAction` 和 `currentReplaceSession`，显示弹窗，调用推荐 API
2. API 返回推荐列表 → 渲染到弹窗中
3. 点击某个推荐动作 → 调用 `POST /api/plan/v2/replaceAction/{plan_id}/{item_id}` 替换
4. 替换成功 → 关闭弹窗，刷新计划数据，显示成功提示
5. 点击遮罩或关闭按钮 → 关闭弹窗

#### 2.4 修改 replaceAction 方法

将原来的 `uni.navigateTo` 改为打开弹窗并加载推荐数据：

```javascript
const replaceAction = async (action, session) => {
    currentReplaceAction.value = action
    currentReplaceSession.value = session
    showReplaceDialog.value = true
    await loadReplaceRecommendations(action)
}
```

#### 2.5 新增加载推荐方法

```javascript
const loadReplaceRecommendations = async (action) => {
    replaceLoading.value = true
    try {
        const res = await request.get(`/api/action/replace-recommend/${action.action_id}`, {
            params: { plan_id: planId.value }
        })
        replaceRecommendList.value = res || []
    } catch (error) {
        console.error('加载推荐动作失败:', error)
        replaceRecommendList.value = []
    } finally {
        replaceLoading.value = false
    }
}
```

#### 2.6 新增确认替换方法

```javascript
const confirmReplaceAction = async (newAction) => {
    try {
        await request.post(`${API_V2.PLAN_REPLACE_ACTION}/${planId.value}/${currentReplaceAction.value.item_id}`, {
            new_action_id: newAction.action_id,
            keep_params: true
        })
        uni.showToast({ title: '替换成功', icon: 'success' })
        showReplaceDialog.value = false
        await loadPlanDetail()
    } catch (error) {
        if (error.code === 400 && error.detail?.includes('器材')) {
            uni.showToast({ title: '该动作所需器材您当前健身房未配备', icon: 'none' })
        } else {
            uni.showToast({ title: error.detail || '替换失败', icon: 'none' })
        }
    }
}
```

### 三、前端常量更新

**文件**：`03_Frontend/my-fitness-app/src/utils/constants.js`

在 `API` 对象中新增：

```javascript
ACTION_REPLACE_RECOMMEND: '/api/action/replace-recommend'
```

## 修改文件清单

| 文件                                                        | 修改内容                                                  |
| --------------------------------------------------------- | ----------------------------------------------------- |
| `02_Backend/app/api/action.py`                            | 新增 `GET /api/action/replace-recommend/{action_id}` 接口 |
| `02_Backend/app/schemas/action.py`                        | 新增 `ReplaceRecommendResponse` 模型                      |
| `03_Frontend/my-fitness-app/src/pages/plan/plan-edit.vue` | 添加弹窗 UI、状态变量、交互逻辑                                     |
| `03_Frontend/my-fitness-app/src/utils/constants.js`       | 新增 API 常量                                             |

## 实施步骤

1. **后端**：在 `schemas/action.py` 中新增 `ReplaceRecommendResponse` 响应模型
2. **后端**：在 `api/action.py` 中新增 `GET /api/action/replace-recommend/{action_id}` 接口
3. **前端**：在 `constants.js` 中新增 API 路径常量
4. **前端**：在 `plan-edit.vue` 中添加弹窗相关的响应式状态变量
5. **前端**：在 `plan-edit.vue` 中修改 `replaceAction` 方法，改为打开弹窗
6. **前端**：在 `plan-edit.vue` 中新增 `loadReplaceRecommendations` 和 `confirmReplaceAction` 方法
7. **前端**：在 `plan-edit.vue` 模板中添加替换动作弹窗 UI
8. **前端**：在 `plan-edit.vue` 样式中添加弹窗相关样式
9. **测试验证**：启动前后端，测试完整替换流程

