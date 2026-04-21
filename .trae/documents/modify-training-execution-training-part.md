# 修改 training-execution.vue：接收 training_part 参数，只显示对应 training_part 的 sessions

## 当前状态分析

training-execution.vue 中已有以下实现（来自之前的修改）：
- `trainingPart` ref 变量已定义（第 141 行）
- `allSessions` ref 变量已定义（第 142 行）
- `onLoad` 已接收 `training_part` URL 参数（第 161 行）
- `loadPlanDetail` 中已根据 `trainingPart` 过滤 sessions（第 202-204 行）
- plan-detail.vue 的 `startExecution` 函数已传递 `training_part` 参数

## 需要优化的问题

### 1. 页面标题应根据 training_part 动态显示
当前页面标题固定为"训练执行"（第 6 行），当只执行某一天的 training_part 时，应显示更具体的标题（如"推日训练"），让用户清楚当前训练的是哪天内容。

### 2. session-tabs 中应按 SESSION_ORDER 排序
过滤后的 sessions 应按照 WARMUP → MAIN → COOLDOWN 的顺序排列，确保训练流程正确（先热身、再正式、后拉伸）。

### 3. 当 training_part 为空时的兼容性
当前实现中，如果 `training_part` 为空字符串，`sessions` 会显示所有 sessions，这是正确的 fallback 行为，无需修改。

### 4. sessionId 定位逻辑需适配过滤后的 sessions
当前 `loadPlanDetail` 中通过 `sessionId` 查找初始激活的 session index（第 206-210 行），这个逻辑在过滤后仍然正确，因为 `findIndex` 是在过滤后的 `sessions` 中查找。无需修改。

## 实施步骤

### 步骤 1：修改页面标题
在 `onLoad` 中，根据 `training_part` 参数动态设置页面标题：
- 如果有 training_part（如"推"），标题设为"推日训练"
- 如果没有 training_part，标题保持"训练执行"

使用 `uni.setNavigationBarTitle` API 动态修改标题。

### 步骤 2：对过滤后的 sessions 按 SESSION_ORDER 排序
在 `loadPlanDetail` 中，对过滤后的 sessions 按 session_type 排序（WARMUP → MAIN → COOLDOWN），确保训练阶段顺序正确。

### 步骤 3：验证整体逻辑
确认以下场景表现正确：
- 有 training_part 时：只显示对应 part 的 sessions，标题显示具体训练日
- 无 training_part 时：显示所有 sessions（兼容旧入口），标题为"训练执行"
- sessionId 定位在过滤后的 sessions 中正确工作

## 涉及文件

- `src/pages/plan/training-execution.vue` — 修改 onLoad 添加动态标题 + loadPlanDetail 添加排序逻辑
