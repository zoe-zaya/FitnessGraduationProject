# 修改 plan-edit.vue：接收 training_part 参数，只显示对应 training_part 的 sessions

## 当前状态分析

plan-edit.vue 中已有以下实现（来自之前的修改）：
- `trainingPart` ref 变量已定义（第 164 行）
- `onLoad` 已接收 `training_part` URL 参数（第 197 行）
- `groupedSessions` 计算属性已根据 `trainingPart` 过滤 sessions（第 175-177 行）
- plan-detail.vue 的 `editPlan` 函数已传递 `training_part` 参数（第 296 行）

## 需要优化的问题

### 1. 页面标题应根据 training_part 动态显示
当前页面标题固定为"编辑计划"，当只编辑某一天的 training_part 时，应显示更具体的标题（如"编辑推日计划"），让用户清楚知道正在编辑哪天的内容。

### 2. 当 training_part 为空时的兼容性
当前实现中，如果 `training_part` 为空字符串，`groupedSessions` 会显示所有 sessions，这是正确的 fallback 行为，无需修改。

### 3. 从 select-action 页面返回后的数据刷新
`addActionToSession` 和 `replaceAction` 使用 `uni.navigateTo` 跳转到 select-action 页面，返回时会触发 `onShow` 重新加载数据。`trainingPart` ref 的值在页面生命周期内保持不变，所以过滤逻辑在返回后仍然生效。无需修改。

## 实施步骤

### 步骤 1：修改页面导航栏标题
在 `onLoad` 中，根据 `training_part` 参数动态设置页面标题：
- 如果有 training_part（如"推"），标题设为"编辑推日计划"
- 如果没有 training_part，标题保持"编辑计划"

使用 `uni.setNavigationBarTitle` API 动态修改标题。

### 步骤 2：验证过滤逻辑的正确性
确认 `groupedSessions` 在以下场景中表现正确：
- 有 training_part 时：只显示对应 part 的 sessions
- 无 training_part 时：显示所有 sessions（兼容旧入口）

## 涉及文件

- `src/pages/plan/plan-edit.vue` — 修改 onLoad 添加动态标题逻辑
