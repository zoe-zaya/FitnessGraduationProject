<template>
    <view class="container">
        <view class="content">
            <view class="sessions-section">
                <view
                    class="part-card"
                    v-for="group in groupedSessions"
                    :key="group.training_part"
                >
                    <view class="part-header">
                        <view class="part-badge" :class="group.training_part">
                            {{ getPartLabel(group.training_part) }}
                        </view>
                        <text class="part-muscles">{{ getPartMusclesDesc(group.training_part) }}</text>
                    </view>

                    <view class="session-list">
                        <view
                            class="session-item"
                            v-for="session in group.sessions"
                            :key="session.session_id"
                        >
                            <view class="session-type-bar" :style="{ backgroundColor: getSessionColor(session.session_type) }"></view>
                            <view class="session-body">
                                <view class="session-top">
                                    <text class="session-name">{{ SESSION_TYPE_MAP[session.session_type]?.label }}</text>
                                    <text class="session-duration">约{{ session.estimated_duration_minutes }}分钟</text>
                                </view>

                                <view class="target-muscles" v-if="session.target_muscles && session.target_muscles.length > 0">
                                    <view class="muscles-tags">
                                        <text class="muscle-tag" v-for="(muscle, mIndex) in session.target_muscles" :key="mIndex">
                                            {{ muscle }}
                                        </text>
                                    </view>
                                </view>

                                <view class="action-list">
                                    <view
                                        class="action-row"
                                        v-for="action in session.action_items"
                                        :key="action.item_id"
                                    >
                                        <view class="action-top">
                                            <view class="action-left">
                                                <text class="action-name">{{ action.action_name }}</text>
                                                <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                                                    {{ action.difficulty_level }}
                                                </text>
                                            </view>
                                            <view class="action-ops">
                                                <view class="op-icon replace" @click="replaceAction(action, session)">
                                                    <image class="op-img" src="/static/replace.png" mode="aspectFit"></image>
                                                </view>
                                                <view class="op-icon delete" @click="confirmDeleteAction(action)">
                                                    <image class="op-img" src="/static/delete.png" mode="aspectFit"></image>
                                                </view>
                                            </view>
                                        </view>

                                        <view class="action-params" v-if="action.sets !== undefined && action.sets !== null">
                                            <view class="param-item">
                                                <text class="param-label">组数</text>
                                                <input
                                                    v-model="action.sets"
                                                    type="number"
                                                    class="param-input"
                                                    @blur="updateActionItem(action)"
                                                    min="1"
                                                    max="6"
                                                />
                                            </view>
                                            <view class="param-item">
                                                <text class="param-label">次数</text>
                                                <input
                                                    v-model="action.reps_per_set"
                                                    type="number"
                                                    class="param-input"
                                                    @blur="updateActionItem(action)"
                                                    min="5"
                                                    max="20"
                                                />
                                            </view>
                                            <view class="param-item">
                                                <text class="param-label">休息(秒)</text>
                                                <input
                                                    v-model="action.rest_seconds_default"
                                                    type="number"
                                                    class="param-input"
                                                    @blur="updateActionItem(action)"
                                                    min="30"
                                                    max="300"
                                                />
                                            </view>
                                        </view>

                                        <view class="action-params" v-else-if="action.duration_minutes !== undefined && action.duration_minutes !== null">
                                            <view class="param-item">
                                                <text class="param-label">时长(分钟)</text>
                                                <input
                                                    v-model="action.duration_minutes"
                                                    type="number"
                                                    class="param-input"
                                                    @blur="updateActionItem(action)"
                                                    min="1"
                                                />
                                            </view>
                                        </view>
                                    </view>

                                    <view class="add-action" @click="addActionToSession(session)">
                                        <text class="add-text">+ 添加动作</text>
                                    </view>
                                </view>
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </view>

        <view class="bottom-bar">
            <button class="btn cancel-btn" @click="goBack">
                <text>取消</text>
            </button>
            <button class="btn save-btn" @click="saveChanges" :loading="saving">
                <text>{{ saving ? '保存中...' : '保存修改' }}</text>
            </button>
        </view>

        <view class="replace-dialog-mask" :class="{ 'mask-visible': showReplaceDialog }" @click="closeReplaceDialog">
            <view class="replace-dialog-content" :class="{ 'dialog-visible': showReplaceDialog }" @click.stop>
                <view class="replace-dialog-handle"></view>

                <view class="replace-dialog-header">
                    <view class="header-left">
                        <image src="/static/replace.png" class="header-icon" mode="aspectFit" />
                        <text class="replace-dialog-title">替换动作</text>
                    </view>
                    <view class="replace-dialog-close" @click="closeReplaceDialog">
                        <text class="close-icon">✕</text>
                    </view>
                </view>

                <view class="original-action-card" v-if="currentReplaceAction">
                    <view class="original-card-inner">
                        <view class="original-indicator">
                            <text class="indicator-text">原动作</text>
                        </view>
                        <view class="original-main">
                            <view class="original-top">
                                <text class="original-name">{{ currentReplaceAction.action_name }}</text>
                                <text class="original-difficulty" :style="{ backgroundColor: getDifficultyColor(currentReplaceAction.difficulty_level) }">
                                    {{ currentReplaceAction.difficulty_level }}
                                </text>
                            </view>
                            <view class="original-muscles" v-if="currentReplaceAction.target_muscles && currentReplaceAction.target_muscles.length > 0">
                                <text class="original-muscle-tag" v-for="(muscle, mIndex) in currentReplaceAction.target_muscles" :key="mIndex">
                                    {{ muscle }}
                                </text>
                            </view>
                        </view>
                    </view>
                </view>

                <view class="replace-dialog-body">
                    <view class="recommend-header">
                        <text class="recommend-label">推荐替换</text>
                        <text class="recommend-count" v-if="!replaceLoading && replaceRecommendList.length > 0">
                            {{ replaceRecommendList.length }} 个可选
                        </text>
                    </view>

                    <view class="replace-loading" v-if="replaceLoading">
                        <view class="loading-spinner"></view>
                        <text class="loading-text">正在匹配相似动作...</text>
                    </view>

                    <scroll-view class="recommend-list" scroll-y v-else-if="replaceRecommendList.length > 0">
                        <view
                            class="recommend-item"
                            v-for="(action, index) in replaceRecommendList"
                            :key="action.action_id"
                            @click="confirmReplaceAction(action)"
                            hover-class="recommend-item-active"
                        >
                            <view class="recommend-item-main">
                                <view class="recommend-item-top">
                                    <view class="recommend-item-name-row">
                                        <text class="recommend-action-name">{{ action.name }}</text>
                                        <view class="similarity-badge">
                                            <text class="similarity-text" :style="{ color: getSimilarityColor(action.muscle_similarity) }">{{ getSimilarityLabel(action.muscle_similarity) }}</text>
                                        </view>
                                    </view>
                                    <view class="recommend-item-meta">
                                        <text class="recommend-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                                            {{ action.difficulty_level }}
                                        </text>
                                        <text class="recommend-equipment-text" v-if="action.equipment_name">使用{{ action.equipment_name }}</text>
                                    </view>
                                </view>

                                <view class="recommend-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
                                    <text class="recommend-muscle-tag" v-for="(muscle, mIndex) in action.target_muscles.slice(0, 4)" :key="mIndex">
                                        {{ muscle }}
                                    </text>
                                    <text class="recommend-muscle-tag more" v-if="action.target_muscles.length > 4">
                                        +{{ action.target_muscles.length - 4 }}
                                    </text>
                                </view>
                            </view>

                            <view class="recommend-item-action">
                                <text class="action-icon">›</text>
                            </view>
                        </view>
                    </scroll-view>

                    <view class="recommend-empty" v-else>
                        <view class="empty-icon-wrap">
                            <text class="empty-icon">🔍</text>
                        </view>
                        <text class="empty-text">暂无可替换动作</text>
                        <text class="empty-subtext">没有找到肌群相似且器材可用的动作</text>
                    </view>
                </view>
            </view>
        </view>

        <view class="add-dialog-mask" :class="{ 'mask-visible': showAddDialog }" @click="closeAddDialog">
            <view class="add-dialog-content" :class="{ 'dialog-visible': showAddDialog }" @click.stop>
                <view class="add-dialog-handle"></view>

                <view class="add-dialog-header">
                    <view class="header-left">
                        <image src="/static/add.png" class="header-icon" mode="aspectFit" />
                        <text class="add-dialog-title">添加动作</text>
                    </view>
                    <view class="add-dialog-close" @click="closeAddDialog">
                        <text class="close-icon">✕</text>
                    </view>
                </view>

                <view class="session-info-card" v-if="currentAddSession">
                    <view class="session-card-inner">
                        <view class="session-indicator">
                            <text class="indicator-text">{{ SESSION_TYPE_MAP[currentAddSession.session_type]?.label }}</text>
                        </view>
                        <view class="session-main">
                            <view class="session-target-muscles" v-if="currentAddSession.target_muscles && currentAddSession.target_muscles.length > 0">
                                <text class="session-muscle-tag" v-for="(muscle, mIndex) in currentAddSession.target_muscles" :key="mIndex">
                                    {{ muscle }}
                                </text>
                            </view>
                        </view>
                    </view>
                </view>

                <view class="add-dialog-body">
                    <view class="recommend-header">
                        <text class="recommend-label">推荐动作</text>
                        <text class="recommend-count" v-if="!addLoading && addRecommendList.length > 0">
                            {{ addRecommendList.length }} 个可选
                        </text>
                    </view>

                    <view class="add-loading" v-if="addLoading">
                        <view class="loading-spinner"></view>
                        <text class="loading-text">正在匹配推荐动作...</text>
                    </view>

                    <scroll-view class="recommend-list" scroll-y v-else-if="addRecommendList.length > 0">
                        <view
                            class="recommend-item"
                            v-for="(action, index) in addRecommendList"
                            :key="action.action_id"
                            @click="confirmAddAction(action)"
                            hover-class="recommend-item-active"
                        >
                            <view class="recommend-item-main">
                                <view class="recommend-item-top">
                                    <view class="recommend-item-name-row">
                                        <text class="recommend-action-name">{{ action.name }}</text>
                                        <view class="similarity-badge">
                                            <text class="similarity-text" :style="{ color: getSimilarityColor(action.muscle_similarity) }">{{ getSimilarityLabel(action.muscle_similarity) }}</text>
                                        </view>
                                    </view>
                                    <view class="recommend-item-meta">
                                        <text class="recommend-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                                            {{ action.difficulty_level }}
                                        </text>
                                        <text class="recommend-equipment-text" v-if="action.equipment_name">使用{{ action.equipment_name }}</text>
                                    </view>
                                </view>

                                <view class="recommend-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
                                    <text class="recommend-muscle-tag" v-for="(muscle, mIndex) in action.target_muscles.slice(0, 4)" :key="mIndex">
                                        {{ muscle }}
                                    </text>
                                    <text class="recommend-muscle-tag more" v-if="action.target_muscles.length > 4">
                                        +{{ action.target_muscles.length - 4 }}
                                    </text>
                                </view>
                            </view>

                            <view class="recommend-item-action">
                                <text class="action-add-icon">+</text>
                            </view>
                        </view>
                    </scroll-view>

                    <view class="recommend-empty" v-else>
                        <view class="empty-icon-wrap">
                            <text class="empty-icon">🔍</text>
                        </view>
                        <text class="empty-text">暂无推荐动作</text>
                        <text class="empty-subtext">没有找到肌群相似且器材可用的动作</text>
                    </view>
                </view>
            </view>
        </view>

        <view class="delete-dialog-mask" :class="{ 'mask-visible': showDeleteDialog }" @click="closeDeleteDialog">
            <view class="delete-dialog-content" :class="{ 'dialog-visible': showDeleteDialog }" @click.stop>
                <text class="delete-dialog-title">删除动作</text>
                <text class="delete-dialog-desc">确定要删除"{{ currentDeleteAction?.action_name }}"吗？删除后将无法恢复。</text>
                <view class="delete-dialog-actions">
                    <view class="delete-dialog-btn cancel" @click="closeDeleteDialog">
                        <text class="delete-btn-text cancel-text">取消</text>
                    </view>
                    <view class="delete-dialog-btn confirm" @click="executeDeleteAction">
                        <text class="delete-btn-text confirm-text">删除</text>
                    </view>
                </view>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SESSION_TYPE_MAP, DIFFICULTY_MAP, ACTION_CATEGORY_MAP, API, DEFAULT_SETS, DEFAULT_REPS, DEFAULT_REST_SECONDS, DEFAULT_DURATION_MINUTES } from '@/utils/constants'

const PART_LABEL_MAP = {
    '推': '推日',
    '腿': '腿日',
    '拉': '拉日'
}

const PART_MUSCLES_DESC = {
    '推': '胸 · 肩 · 三头',
    '腿': '臀 · 腿',
    '拉': '背 · 二头'
}

const SESSION_COLORS = {
    WARMUP: '#FF9500',
    MAIN: '#a03e40',
    COOLDOWN: '#24a978'
}

const SESSION_ORDER = ['WARMUP', 'MAIN', 'COOLDOWN']

const getPartLabel = (part) => PART_LABEL_MAP[part] || part
const getPartMusclesDesc = (part) => PART_MUSCLES_DESC[part] || ''
const getSessionColor = (type) => SESSION_COLORS[type] || '#a03e40'

const planId = ref('')
const trainingPart = ref('')
const saving = ref(false)
const planInfo = ref({
    plan_name: '',
    sessions: []
})

const showReplaceDialog = ref(false)
const currentReplaceAction = ref(null)
const currentReplaceSession = ref(null)
const replaceRecommendList = ref([])
const replaceLoading = ref(false)

const showAddDialog = ref(false)
const currentAddSession = ref(null)
const addRecommendList = ref([])
const addLoading = ref(false)

const showDeleteDialog = ref(false)
const currentDeleteAction = ref(null)

const groupedSessions = computed(() => {
    const sessions = planInfo.value.sessions || []
    const groupMap = new Map()

    const filteredSessions = trainingPart.value
        ? sessions.filter(s => s.training_part === trainingPart.value)
        : sessions

    filteredSessions.forEach(session => {
        const part = session.training_part || '其他'
        if (!groupMap.has(part)) {
            groupMap.set(part, [])
        }
        groupMap.get(part).push(session)
    })

    return Array.from(groupMap.entries()).map(([training_part, sessions]) => ({
        training_part,
        sessions: sessions.sort((a, b) => {
            return SESSION_ORDER.indexOf(a.session_type) - SESSION_ORDER.indexOf(b.session_type)
        })
    }))
})

onLoad((options) => {
    planId.value = options.plan_id || ''
    trainingPart.value = options.training_part ? decodeURIComponent(options.training_part) : ''

    if (trainingPart.value) {
        const label = PART_LABEL_MAP[trainingPart.value] || trainingPart.value
        uni.setNavigationBarTitle({ title: `编辑${label}计划` })
    }
})

onShow(async () => {
    if (planId.value) {
        await loadPlanDetail()
    }
})

const loadPlanDetail = async () => {
    try {
        const res = await request.get(`${API_V2.PLAN_DETAIL}/${planId.value}`)
        planInfo.value = res
    } catch (error) {
        console.error('加载失败:', error)
        uni.showToast({ title: '加载失败', icon: 'none' })
    }
}

const getDifficultyColor = (level) => {
    return DIFFICULTY_MAP[level]?.color || '#8E8E93'
}

const updateActionItem = async (action) => {
    try {
        const updateData = {}

        if (action.sets != null) {
            updateData.sets = parseInt(action.sets) || 4
            updateData.reps_per_set = parseInt(action.reps_per_set) || 12
            updateData.rest_seconds_default = parseInt(action.rest_seconds_default) || 60
        } else if (action.duration_minutes != null) {
            updateData.duration_minutes = parseInt(action.duration_minutes) || 30
        }

        await request.put(`${API_V2.PLAN_UPDATE_ACTION}/${planId.value}/${action.item_id}`, updateData)
    } catch (error) {
        console.error('更新失败:', error)
        uni.showToast({ title: '更新失败', icon: 'none' })
    }
}

const replaceAction = async (action, session) => {
    currentReplaceAction.value = action
    currentReplaceSession.value = session
    showReplaceDialog.value = true
    await loadReplaceRecommendations(action)
}

const loadReplaceRecommendations = async (action) => {
    replaceLoading.value = true
    try {
        const res = await request.get(`${API.ACTION_REPLACE_RECOMMEND}/${action.action_id}`, {
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

const closeReplaceDialog = () => {
    showReplaceDialog.value = false
    currentReplaceAction.value = null
    currentReplaceSession.value = null
    replaceRecommendList.value = []
}

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

const getSimilarityLabel = (similarity) => {
    if (similarity >= 0.8) return '高度相似'
    if (similarity >= 0.5) return '较为相似'
    if (similarity > 0) return '部分相似'
    return '不同肌群'
}

const getSimilarityColor = (similarity) => {
    if (similarity >= 0.8) return '#ff6b8f'
    if (similarity >= 0.5) return '#e6ac00'
    if (similarity > 0) return '#52c41a'
    return '#878787'
}

const addActionToSession = (session) => {
    currentAddSession.value = session
    showAddDialog.value = true
    loadAddRecommendations(session)
}

const loadAddRecommendations = async (session) => {
    addLoading.value = true
    try {
        const res = await request.get(`${API.ACTION_ADD_RECOMMEND}/${session.session_id}`, {
            params: { plan_id: planId.value }
        })
        addRecommendList.value = res || []
    } catch (error) {
        console.error('加载推荐动作失败:', error)
        addRecommendList.value = []
    } finally {
        addLoading.value = false
    }
}

const closeAddDialog = () => {
    showAddDialog.value = false
    currentAddSession.value = null
    addRecommendList.value = []
}

const confirmAddAction = async (action) => {
    try {
        const addData = {
            session_id: currentAddSession.value.session_id,
            action_id: action.action_id,
            sets: action.action_category === 'main_strength' ? DEFAULT_SETS : undefined,
            reps_per_set: action.action_category === 'main_strength' ? DEFAULT_REPS : undefined,
            rest_seconds_default: action.action_category === 'main_strength' ? DEFAULT_REST_SECONDS : undefined,
            duration_minutes: action.action_category === 'main_cardio' ? DEFAULT_DURATION_MINUTES : undefined
        }

        await request.post(`${API_V2.PLAN_ADD_ACTION}/${planId.value}`, addData)

        uni.showToast({ title: `"${action.name}"已添加`, icon: 'success' })
        showAddDialog.value = false
        await loadPlanDetail()
    } catch (error) {
        if (error.code === 400 && error.detail?.includes('器材')) {
            uni.showToast({ title: '该动作所需器材您当前健身房未配备', icon: 'none' })
        } else {
            uni.showToast({ title: error.detail || '添加失败', icon: 'none' })
        }
    }
}

const confirmDeleteAction = (action) => {
    currentDeleteAction.value = action
    showDeleteDialog.value = true
}

const closeDeleteDialog = () => {
    showDeleteDialog.value = false
    currentDeleteAction.value = null
}

const executeDeleteAction = async () => {
    if (!currentDeleteAction.value) return
    const itemId = currentDeleteAction.value.item_id
    showDeleteDialog.value = false
    await deleteActionItem(itemId)
    currentDeleteAction.value = null
}

const deleteActionItem = async (itemId) => {
    try {
        await request.delete(`${API_V2.PLAN_DELETE_ACTION}/${planId.value}/${itemId}`)
        uni.showToast({ title: '删除成功', icon: 'success' })
        await loadPlanDetail()
    } catch (error) {
        console.error('删除失败:', error)
        uni.showToast({ title: '删除失败', icon: 'none' })
    }
}

const saveChanges = async () => {
    saving.value = true
    try {
        await request.put(`${API_V2.PLAN_UPDATE}/${planId.value}`, {
            plan_name: planInfo.value.plan_name
        })
        uni.showToast({ title: '保存成功', icon: 'success' })
        setTimeout(() => {
            uni.navigateBack()
        }, 1000)
    } catch (error) {
        console.error('保存失败:', error)
        uni.showToast({ title: '保存失败', icon: 'none' })
    } finally {
        saving.value = false
    }
}

const goBack = () => {
    uni.showModal({
        title: '提示',
        content: '确定要放弃修改吗？',
        success: (res) => {
            if (res.confirm) {
                uni.navigateBack()
            }
        }
    })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
    min-height: 100vh;
    background: #FFFFFF;
    padding-bottom: 140rpx;
    font-family: Manrope;
}

.content {
    padding: $size-4 $size-5;
}

.sessions-section {
    .part-card {
        background: $glass-bg1;
        border-radius: $size-5;
        overflow: hidden;
        margin-bottom: $size-4;
        box-shadow: 0 4rpx 20rpx $border-shadow;

        .part-header {
            display: flex;
            align-items: center;
            gap: $size-3;
            padding: $size-4 $size-5;
            border-bottom: 1rpx solid $fitness-border;

            .part-badge {
                font-size: $size-4;
                font-weight: 700;
                padding: $size-1 $size-3;
                border-radius: $size-2;
                color: #FFFFFF;

                &.推 {
                    background: #e74c3c;
                }

                &.腿 {
                    background: #3498db;
                }

                &.拉 {
                    background: #2ecc71;
                }
            }

            .part-muscles {
                font-size: $size-3;
                color: $color-secondory;
            }
        }

        .session-list {
            .session-item {
                display: flex;
                border-bottom: 1rpx solid $fitness-border;

                &:last-child {
                    border-bottom: none;
                }

                .session-type-bar {
                    width: 8rpx;
                    flex-shrink: 0;
                }

                .session-body {
                    flex: 1;
                    padding: $size-3 $size-4;

                    .session-top {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-bottom: $size-3;

                        .session-name {
                            font-size: $size-3;
                            font-weight: 700;
                            color: $color-input;
                        }

                        .session-duration {
                            font-size: $size-3;
                            color: $color-secondory;
                        }
                    }

                    .target-muscles {
                        margin-bottom: $size-3;

                        .muscles-tags {
                            display: flex;
                            flex-wrap: wrap;
                            gap: $size-2;

                            .muscle-tag {
                                background: $color-primary-light;
                                color: $color-tag;
                                font-size: $size-3;
                                padding: $size-1 $size-3;
                                border-radius: $size-2;
                                font-weight: 500;
                            }
                        }
                    }

                    .action-list {
                        .action-row {
                            display: flex;
                            flex-direction: column;
                            padding: $size-3;
                            background: #FFFFFF;
                            border-radius: $size-3;
                            margin-bottom: $size-2;
                            border: 1rpx solid $fitness-border;

                            .action-top {
                                display: flex;
                                align-items: center;
                                justify-content: space-between;
                                margin-bottom: $size-2;

                                .action-left {
                                    display: flex;
                                    align-items: center;
                                    gap: $size-2;

                                    .action-name {
                                        font-size: $size-3;
                                        font-weight: 700;
                                        color: $color-input;
                                    }

                                    .action-difficulty {
                                        font-size: 20rpx;
                                        padding: 2rpx $size-2;
                                        border-radius: $size-1;
                                        color: #FFFFFF;
                                        font-weight: 500;
                                    }
                                }

                                .action-ops {
                                    display: flex;
                                    gap: $size-1;

                                    .op-icon {
                                        width: 48rpx;
                                        height: 48rpx;
                                        border-radius: $size-2;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        background: $fitness-secondary;

                                        .op-img {
                                            width: 32rpx;
                                            height: 32rpx;
                                        }
                                    }
                                }
                            }

                            .action-params {
                                display: flex;
                                flex-direction: row;
                                gap: $size-2;

                                .param-item {
                                    display: flex;
                                    flex-direction: row;
                                    align-items: center;
                                    gap: $size-1;

                                    .param-label {
                                        font-size: 20rpx;
                                        color: $color-secondory;
                                    }

                                    .param-input {
                                        width: 72rpx;
                                        height: $size-7;
                                        background: $fitness-secondary;
                                        border: 2rpx solid rgba(160, 62, 64, 0.1);
                                        border-radius: $size-1;
                                        padding: 0 $size-1;
                                        font-size: 22rpx;
                                        font-family: Manrope;
                                        color: $color-input;
                                        text-align: center;

                                        &:focus {
                                            border-color: rgba(160, 62, 64, 0.4);
                                        }
                                    }
                                }
                            }
                        }

                        .add-action {
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            gap: $size-1;
                            padding: $size-2;
                            border: 2rpx dashed rgba(160, 62, 64, 0.3);
                            border-radius: $size-3;

                            .add-text {
                                font-size: $size-3;
                                color: $color-primary;
                                font-weight: 700;
                            }
                        }
                    }
                }
            }
        }
    }
}

.bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    gap: $size-3;
    padding: $size-3 $size-5;
    padding-bottom: calc(#{$size-3} + env(safe-area-inset-bottom));
    background: $fitness-primary;
    border-top: 1rpx solid $fitness-border;
    box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);

    .btn {
        flex: 1;
        height: $size-12;
        border-radius: $size-6;
        border: none;
        font-size: $size-4;
        font-weight: 700;
        font-family: Manrope;
        display: flex;
        align-items: center;
        justify-content: center;

        &.cancel-btn {
            background: $fitness-secondary;
            color: $color-label;
        }

        &.save-btn {
            background: $button-bg2;
            color: #FFFFFF;
        }
    }
}

.replace-dialog-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0);
    z-index: 1000;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    pointer-events: none;
    transition: background 0.3s ease;

    &.mask-visible {
        background: rgba(0, 0, 0, 0.45);
        pointer-events: auto;
    }

    .replace-dialog-content {
        width: 100%;
        max-height: 85vh;
        background: #FFFFFF;
        border-radius: 32rpx 32rpx 0 0;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transform: translateY(100%);
        transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1);

        &.dialog-visible {
            transform: translateY(0);
        }

        .replace-dialog-handle {
            width: 72rpx;
            height: 8rpx;
            background: #D1D1D6;
            border-radius: 4rpx;
            margin: $size-2 auto 0;
        }

        .replace-dialog-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: $size-4 $size-5 $size-3;

            .header-left {
                display: flex;
                align-items: center;
                gap: $size-2;

                .header-icon {
                    width: 36rpx;
                    height: 36rpx;
                }

                .replace-dialog-title {
                    font-size: $size-5;
                    font-weight: 700;
                    color: $color-input;
                }
            }

            .replace-dialog-close {
                width: 56rpx;
                height: 56rpx;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                background: $fitness-secondary;

                .close-icon {
                    font-size: $size-4;
                    color: $color-secondory;
                    line-height: 1;
                }
            }
        }

        .original-action-card {
            margin: 0 $size-5;
            background: linear-gradient(135deg, rgba(160, 62, 64, 0.06), rgba(160, 62, 64, 0.02));
            border-radius: $size-4;
            border: 1rpx solid rgba(160, 62, 64, 0.12);
            overflow: hidden;

            .original-card-inner {
                display: flex;
                padding: $size-3 $size-4;

                .original-indicator {
                    writing-mode: vertical-lr;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: $size-3;
                    padding: $size-2 0;
                    border-right: 1rpx solid rgba(160, 62, 64, 0.15);

                    .indicator-text {
                        font-size: 20rpx;
                        color: $color-primary;
                        font-weight: 700;
                        letter-spacing: 4rpx;
                    }
                }

                .original-main {
                    flex: 1;

                    .original-top {
                        display: flex;
                        align-items: center;
                        gap: $size-2;
                        margin-bottom: $size-2;

                        .original-name {
                            font-size: $size-4;
                            font-weight: 700;
                            color: $color-input;
                        }

                        .original-difficulty {
                            font-size: 20rpx;
                            padding: 2rpx $size-2;
                            border-radius: $size-1;
                            color: #FFFFFF;
                            font-weight: 500;
                        }
                    }

                    .original-muscles {
                        display: flex;
                        flex-wrap: wrap;
                        gap: $size-1;

                        .original-muscle-tag {
                            background: #FFFFFF;
                            color: $color-tag;
                            font-size: 22rpx;
                            padding: 4rpx $size-2;
                            border-radius: $size-1;
                            font-weight: 500;
                            border: 1rpx solid rgba(160, 62, 64, 0.1);
                        }
                    }
                }
            }
        }

        .replace-dialog-body {
            flex: 1;
            padding: $size-3 $size-5 $size-5;
            overflow: hidden;
            display: flex;
            flex-direction: column;

            .recommend-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: $size-3;

                .recommend-label {
                    font-size: $size-4;
                    font-weight: 700;
                    color: $color-input;
                }

                .recommend-count {
                    font-size: $size-3;
                    color: $color-secondory;
                    font-weight: 500;
                }
            }

            .replace-loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: $size-12 0;
                gap: $size-3;

                .loading-spinner {
                    width: 48rpx;
                    height: 48rpx;
                    border: 4rpx solid $fitness-secondary;
                    border-top-color: $color-primary;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }

                .loading-text {
                    font-size: $size-3;
                    color: $color-secondory;
                }
            }

            .recommend-list {
                flex: 1;
                max-height: 50vh;

                .recommend-item {
                    display: flex;
                    align-items: center;
                    background: #FFFFFF;
                    border: 1rpx solid $fitness-border;
                    border-radius: $size-4;
                    padding: $size-3 $size-2 $size-3 $size-4;
                    margin-bottom: $size-2;
                    transition: all 0.15s ease;

                    &.recommend-item-active {
                        background: rgba(160, 62, 64, 0.04);
                        border-color: rgba(160, 62, 64, 0.15);
                        transform: scale(0.98);
                    }

                    .recommend-item-main {
                        flex: 1;
                        min-width: 0;

                        .recommend-item-top {
                            margin-bottom: $size-2;

                            .recommend-item-name-row {
                                display: flex;
                                align-items: center;
                                margin-bottom: $size-1;

                                .recommend-action-name {
                                    font-size: $size-4;
                                    font-weight: 700;
                                    color: $color-input;
                                    flex: 1;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                    white-space: nowrap;
                                    margin-right: $size-2;
                                }

                                .similarity-badge {
                                    padding: 2rpx $size-2;
                                    border-radius: 8rpx;
                                    flex-shrink: 0;

                                    .similarity-text {
                                        font-size: 20rpx;
                                        color: #FFFFFF;
                                        font-weight: 600;
                                    }
                                }
                            }

                            .recommend-item-meta {
                                display: flex;
                                align-items: center;
                                gap: $size-2;

                                .recommend-difficulty {
                                    font-size: 20rpx;
                                    padding: 2rpx $size-2;
                                    border-radius: $size-1;
                                    color: #FFFFFF;
                                    font-weight: 500;
                                }

                                .recommend-equipment-text {
                                    font-size: 22rpx;
                                    color: $color-secondory;
                                }
                            }
                        }

                        .recommend-muscles {
                            display: flex;
                            flex-wrap: wrap;
                            gap: $size-1;

                            .recommend-muscle-tag {
                                background: $fitness-secondary;
                                color: $color-tag;
                                font-size: 20rpx;
                                padding: 2rpx $size-2;
                                border-radius: $size-1;
                                font-weight: 500;

                                &.more {
                                    background: $fitness-secondary;
                                    color: $color-secondory;
                                }
                            }
                        }
                    }

                    .recommend-item-action {
                        margin-left: $size-2;
                        flex-shrink: 0;
                        width: 48rpx;
                        height: 48rpx;
                        display: flex;
                        align-items: center;
                        justify-content: center;

                        .action-icon {
                            font-size: $size-7;
                            color: $color-secondory;
                            font-weight: 300;
                            line-height: 1;
                        }
                    }
                }
            }

            .recommend-empty {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: $size-12 0;

                .empty-icon-wrap {
                    width: 120rpx;
                    height: 120rpx;
                    border-radius: 50%;
                    background: $fitness-secondary;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: $size-4;

                    .empty-icon {
                        font-size: 56rpx;
                    }
                }

                .empty-text {
                    font-size: $size-4;
                    color: $color-input;
                    font-weight: 600;
                    margin-bottom: $size-2;
                }

                .empty-subtext {
                    font-size: $size-3;
                    color: $color-secondory;
                    text-align: center;
                    line-height: 1.5;
                }
            }
        }
    }
}

.add-dialog-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0);
    z-index: 1000;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    pointer-events: none;
    transition: background 0.3s ease;

    &.mask-visible {
        background: rgba(0, 0, 0, 0.45);
        pointer-events: auto;
    }

    .add-dialog-content {
        width: 100%;
        max-height: 85vh;
        background: #FFFFFF;
        border-radius: 32rpx 32rpx 0 0;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transform: translateY(100%);
        transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1);

        &.dialog-visible {
            transform: translateY(0);
        }

        .add-dialog-handle {
            width: 72rpx;
            height: 8rpx;
            background: #D1D1D6;
            border-radius: 4rpx;
            margin: $size-2 auto 0;
        }

        .add-dialog-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: $size-4 $size-5 $size-3;

            .header-left {
                display: flex;
                align-items: center;
                gap: $size-2;

                .header-icon {
                    width: 36rpx;
                    height: 36rpx;
                }

                .add-dialog-title {
                    font-size: $size-5;
                    font-weight: 700;
                    color: $color-input;
                }
            }

            .add-dialog-close {
                width: 56rpx;
                height: 56rpx;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                background: $fitness-secondary;

                .close-icon {
                    font-size: $size-4;
                    color: $color-secondory;
                    line-height: 1;
                }
            }
        }

        .session-info-card {
            margin: 0 $size-5;
            background: linear-gradient(135deg, rgba(160, 62, 64, 0.06), rgba(160, 62, 64, 0.02));
            border-radius: $size-4;
            border: 1rpx solid rgba(160, 62, 64, 0.12);
            overflow: hidden;

            .session-card-inner {
                display: flex;
                padding: $size-3 $size-4;

                .session-indicator {
                    writing-mode: vertical-lr;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: $size-3;
                    padding: $size-2 0;
                    border-right: 1rpx solid rgba(160, 62, 64, 0.15);

                    .indicator-text {
                        font-size: 20rpx;
                        color: $color-primary;
                        font-weight: 700;
                        letter-spacing: 4rpx;
                    }
                }

                .session-main {
                    flex: 1;

                    .session-target-muscles {
                        display: flex;
                        flex-wrap: wrap;
                        gap: $size-1;

                        .session-muscle-tag {
                            background: #FFFFFF;
                            color: $color-tag;
                            font-size: 22rpx;
                            padding: 4rpx $size-2;
                            border-radius: $size-1;
                            font-weight: 500;
                            border: 1rpx solid rgba(160, 62, 64, 0.1);
                        }
                    }
                }
            }
        }

        .add-dialog-body {
            flex: 1;
            padding: $size-3 $size-5 $size-5;
            overflow: hidden;
            display: flex;
            flex-direction: column;

            .recommend-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: $size-3;

                .recommend-label {
                    font-size: $size-4;
                    font-weight: 700;
                    color: $color-input;
                }

                .recommend-count {
                    font-size: $size-3;
                    color: $color-secondory;
                    font-weight: 500;
                }
            }

            .add-loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: $size-12 0;
                gap: $size-3;

                .loading-spinner {
                    width: 48rpx;
                    height: 48rpx;
                    border: 4rpx solid $fitness-secondary;
                    border-top-color: $color-primary;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }

                .loading-text {
                    font-size: $size-3;
                    color: $color-secondory;
                }
            }

            .recommend-list {
                flex: 1;
                max-height: 50vh;

                .recommend-item {
                    display: flex;
                    align-items: center;
                    background: #FFFFFF;
                    border: 1rpx solid $fitness-border;
                    border-radius: $size-4;
                    padding: $size-3 $size-2 $size-3 $size-4;
                    margin-bottom: $size-2;
                    transition: all 0.15s ease;

                    &.recommend-item-active {
                        background: rgba(160, 62, 64, 0.04);
                        border-color: rgba(160, 62, 64, 0.15);
                        transform: scale(0.98);
                    }

                    .recommend-item-main {
                        flex: 1;
                        min-width: 0;

                        .recommend-item-top {
                            margin-bottom: $size-2;

                            .recommend-item-name-row {
                                display: flex;
                                align-items: center;
                                margin-bottom: $size-1;

                                .recommend-action-name {
                                    font-size: $size-4;
                                    font-weight: 700;
                                    color: $color-input;
                                    flex: 1;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                    white-space: nowrap;
                                    margin-right: $size-2;
                                }

                                .similarity-badge {
                                    padding: 2rpx $size-2;
                                    border-radius: 8rpx;
                                    flex-shrink: 0;

                                    .similarity-text {
                                        font-size: 20rpx;
                                        color: #FFFFFF;
                                        font-weight: 600;
                                    }
                                }
                            }

                            .recommend-item-meta {
                                display: flex;
                                align-items: center;
                                gap: $size-2;

                                .recommend-difficulty {
                                    font-size: 20rpx;
                                    padding: 2rpx $size-2;
                                    border-radius: $size-1;
                                    color: #FFFFFF;
                                    font-weight: 500;
                                }

                                .recommend-equipment-text {
                                    font-size: 22rpx;
                                    color: $color-secondory;
                                }
                            }
                        }

                        .recommend-muscles {
                            display: flex;
                            flex-wrap: wrap;
                            gap: $size-1;

                            .recommend-muscle-tag {
                                background: $fitness-secondary;
                                color: $color-tag;
                                font-size: 20rpx;
                                padding: 2rpx $size-2;
                                border-radius: $size-1;
                                font-weight: 500;

                                &.more {
                                    background: $fitness-secondary;
                                    color: $color-secondory;
                                }
                            }
                        }
                    }

                    .recommend-item-action {
                        margin-left: $size-2;
                        flex-shrink: 0;
                        width: 48rpx;
                        height: 48rpx;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: $button-bg2;
                        border-radius: 50%;

                        .action-add-icon {
                            font-size: $size-5;
                            color: #FFFFFF;
                            font-weight: 700;
                            line-height: 1;
                        }
                    }
                }
            }

            .recommend-empty {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: $size-12 0;

                .empty-icon-wrap {
                    width: 120rpx;
                    height: 120rpx;
                    border-radius: 50%;
                    background: $fitness-secondary;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: $size-4;

                    .empty-icon {
                        font-size: 56rpx;
                    }
                }

                .empty-text {
                    font-size: $size-4;
                    color: $color-input;
                    font-weight: 600;
                    margin-bottom: $size-2;
                }

                .empty-subtext {
                    font-size: $size-3;
                    color: $color-secondory;
                    text-align: center;
                    line-height: 1.5;
                }
            }
        }
    }
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.delete-dialog-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
    transition: background 0.3s ease;

    &.mask-visible {
        background: rgba(0, 0, 0, 0.45);
        pointer-events: auto;
    }

    .delete-dialog-content {
        width: 560rpx;
        background: #FFFFFF;
        border-radius: $size-4;
        box-shadow: 0 8rpx 40rpx $border-shadow;
        padding: $size-8 $size-8 $size-6;
        display: flex;
        flex-direction: column;
        align-items: center;
        opacity: 0;
        transform: scale(0.85);
        transition: all 0.25s cubic-bezier(0.32, 0.72, 0, 1);

        &.dialog-visible {
            opacity: 1;
            transform: scale(1);
        }

        .delete-dialog-title {
            font-size: $size-4;
            font-weight: 700;
            color: $color-input;
            margin-bottom: $size-2;
        }

        .delete-dialog-desc {
            font-size: $size-3;
            color: $color-secondory;
            text-align: center;
            line-height: 1.5;
            margin-bottom: $size-6;
        }

        .delete-dialog-actions {
            display: flex;
            gap: $size-3;
            width: 100%;

            .delete-dialog-btn {
                flex: 1;
                height: $size-12;
                border-radius: $size-4;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: opacity 0.15s ease;

                &:active {
                    opacity: 0.7;
                }

                &.cancel {
                    background: $fitness-secondary;

                    .cancel-text {
                        font-size: $size-4;
                        font-weight: 700;
                        color: $color-label;
                    }
                }

                &.confirm {
                    background: $button-bg2;

                    .confirm-text {
                        font-size: $size-4;
                        font-weight: 700;
                        color: #FFFFFF;
                    }
                }
            }
        }
    }
}
</style>
