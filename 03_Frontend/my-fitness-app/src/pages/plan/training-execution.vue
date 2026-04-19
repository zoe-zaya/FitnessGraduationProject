<template>
    <view class="container">
        <view class="header">
            <view class="header-top">
                <text class="back-btn" @click="goBack">←</text>
                <text class="header-title">训练执行</text>
                <text class="header-time">{{ formatElapsedTime(elapsedSeconds) }}</text>
            </view>
            <view class="session-tabs">
                <view
                    class="session-tab"
                    :class="{ active: activeSessionIndex === index }"
                    v-for="(session, index) in sessions"
                    :key="session.session_id"
                    @click="switchSession(index)"
                >
                    <text class="tab-icon">{{ SESSION_TYPE_MAP[session.session_type]?.icon }}</text>
                    <text class="tab-label">{{ SESSION_TYPE_MAP[session.session_type]?.label }}</text>
                </view>
            </view>
        </view>

        <view class="content">
            <view class="current-session" v-if="currentSession">
                <view class="session-header">
                    <text class="session-name">{{ SESSION_TYPE_MAP[currentSession.session_type]?.label }}</text>
                    <text class="session-info">{{ currentSession.target_muscles?.join(', ') }}</text>
                </view>

                <view class="action-list">
                    <view
                        class="action-card"
                        v-for="(item, itemIndex) in currentSession.action_items"
                        :key="item.item_id"
                        :class="{ 'active': currentActionIndex === itemIndex, 'completed': completedActions.has(item.item_id) }"
                        @click="selectAction(itemIndex)"
                    >
                        <view class="action-main">
                            <view class="action-info">
                                <text class="action-name">{{ item.action_name }}</text>
                                <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(item.difficulty_level) }">
                                    {{ item.difficulty_level }}
                                </text>
                            </view>

                            <view class="action-params" v-if="item.sets">
                                <view class="param-item">
                                    <text class="param-value">{{ item.sets }}</text>
                                    <text class="param-label">组</text>
                                </view>
                                <view class="param-divider">×</view>
                                <view class="param-item">
                                    <text class="param-value">{{ item.reps_per_set }}</text>
                                    <text class="param-label">次</text>
                                </view>
                                <view class="param-divider">|</view>
                                <view class="param-item">
                                    <text class="param-value">{{ item.rest_seconds_default }}</text>
                                    <text class="param-label">秒休息</text>
                                </view>
                            </view>

                            <view class="action-params" v-else-if="item.duration_minutes">
                                <view class="param-item">
                                    <text class="param-value">{{ item.duration_minutes }}</text>
                                    <text class="param-label">分钟</text>
                                </view>
                            </view>
                        </view>

                        <view class="action-progress" v-if="item.sets">
                            <view
                                class="set-indicator"
                                v-for="setIndex in item.sets"
                                :key="setIndex"
                                :class="{ 'completed': isSetCompleted(item, setIndex), 'current': currentActionIndex === itemIndex && currentSetIndex === setIndex - 1 }"
                                @click.stop="markSetComplete(item, setIndex)"
                            >
                                <text class="set-num">{{ setIndex }}</text>
                            </view>
                        </view>

                        <view class="weight-section" v-if="item.sets && currentActionIndex === itemIndex">
                            <text class="weight-label">重量记录 (kg)</text>
                            <view class="weight-inputs">
                                <input
                                    class="weight-input"
                                    v-for="(weight, idx) in getWeightRecords(item)"
                                    :key="idx"
                                    type="digit"
                                    :placeholder="`组${idx + 1}`"
                                    v-model="weightRecords[item.item_id][idx]"
                                    @blur="updateWeightRecords(item)"
                                />
                            </view>
                        </view>
                    </view>
                </view>
            </view>

            <view class="empty-actions" v-if="currentSession && currentSession.action_items.length === 0">
                <text class="empty-text">该阶段暂无动作</text>
            </view>
        </view>

        <view class="bottom-bar">
            <button class="btn prev-btn" v-if="hasPrevSession" @click="prevSession">
                <text>上一阶段</text>
            </button>
            <button class="btn action-btn" @click="toggleTraining">
                <text>{{ isTraining ? '暂停' : isStarted ? '继续' : '开始训练' }}</text>
            </button>
            <button class="btn next-btn" v-if="hasNextSession" @click="nextSession">
                <text>下一阶段</text>
            </button>
            <button class="btn finish-btn" v-if="allSessionsCompleted" @click="finishTraining">
                <text>完成训练</text>
            </button>
        </view>

        <RestCountdown
            :visible="showRestModal"
            :initialSeconds="currentRestSeconds"
            @update:visible="showRestModal = $event"
            @complete="onRestComplete"
            @skip="onRestSkip"
        />
    </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SESSION_TYPE_MAP, DIFFICULTY_MAP, DEFAULT_REST_SECONDS } from '@/utils/constants'
import RestCountdown from '@/components/RestCountdown.vue'

const planId = ref('')
const scheduleId = ref('')
const sessionId = ref('')
const sessions = ref([])
const activeSessionIndex = ref(0)
const currentActionIndex = ref(0)
const currentSetIndex = ref(0)
const isStarted = ref(false)
const isTraining = ref(false)
const elapsedSeconds = ref(0)
const showRestModal = ref(false)
const currentRestSeconds = ref(DEFAULT_REST_SECONDS)
const completedActions = ref(new Set())
const weightRecords = ref({})

let timer = null

onLoad((options) => {
    planId.value = options.plan_id || ''
    scheduleId.value = options.schedule_id || ''
    sessionId.value = options.session_id || ''
})

onMounted(async () => {
    await loadPlanDetail()
})

onUnmounted(() => {
    stopTimer()
})

const currentSession = computed(() => {
    return sessions.value[activeSessionIndex.value]
})

const hasPrevSession = computed(() => {
    return activeSessionIndex.value > 0
})

const hasNextSession = computed(() => {
    return activeSessionIndex.value < sessions.value.length - 1
})

const allSessionsCompleted = computed(() => {
    if (sessions.value.length === 0) return false
    for (const session of sessions.value) {
        if (session.action_items.length === 0) continue
        for (const item of session.action_items) {
            if (!completedActions.value.has(item.item_id)) {
                return false
            }
        }
    }
    return true
})

const loadPlanDetail = async () => {
    try {
        const res = await request.get(`${API_V2.PLAN_DETAIL}/${planId.value}`)
        sessions.value = res.sessions || []

        if (sessionId.value) {
            const index = sessions.value.findIndex(s => s.session_id === sessionId.value)
            if (index >= 0) {
                activeSessionIndex.value = index
            }
        }

        sessions.value.forEach(session => {
            session.action_items.forEach(item => {
                if (!weightRecords.value[item.item_id]) {
                    const count = item.sets || 1
                    weightRecords.value[item.item_id] = new Array(count).fill('')
                }
            })
        })
    } catch (error) {
        console.error('加载计划失败:', error)
        uni.showToast({ title: '加载失败', icon: 'none' })
    }
}

const switchSession = (index) => {
    activeSessionIndex.value = index
    currentActionIndex.value = 0
    currentSetIndex.value = 0
}

const prevSession = () => {
    if (hasPrevSession.value) {
        switchSession(activeSessionIndex.value - 1)
    }
}

const nextSession = () => {
    if (hasNextSession.value) {
        switchSession(activeSessionIndex.value + 1)
    }
}

const selectAction = (index) => {
    currentActionIndex.value = index
    currentSetIndex.value = 0
}

const getDifficultyColor = (level) => {
    return DIFFICULTY_MAP[level]?.color || '#999999'
}

const isSetCompleted = (item, setIndex) => {
    const records = weightRecords.value[item.item_id] || []
    return records[setIndex - 1] !== '' && records[setIndex - 1] !== undefined && records[setIndex - 1] !== null
}

const getWeightRecords = (item) => {
    if (!weightRecords.value[item.item_id]) {
        const count = item.sets || 1
        weightRecords.value[item.item_id] = new Array(count).fill('')
    }
    return weightRecords.value[item.item_id]
}

const markSetComplete = async (item, setIndex) => {
    currentSetIndex.value = setIndex - 1

    if (setIndex < item.sets) {
        currentRestSeconds.value = item.rest_seconds_default || DEFAULT_REST_SECONDS
        showRestModal.value = true
    } else {
        completedActions.value.add(item.item_id)
        if (currentActionIndex.value < currentSession.value.action_items.length - 1) {
            currentActionIndex.value++
            currentSetIndex.value = 0
        }
    }

    await updateWeightRecords(item)
}

const updateWeightRecords = async (item) => {
    try {
        const records = weightRecords.value[item.item_id]
            .filter(w => w !== '' && w !== undefined && w !== null)
            .map(w => parseFloat(w))

        if (records.length > 0) {
            await request.put(`${API_V2.PLAN_UPDATE_ACTION}/${planId.value}/${item.item_id}`, {
                weight_records: records
            })
        }
    } catch (error) {
        console.error('更新重量记录失败:', error)
    }
}

const toggleTraining = () => {
    if (!isStarted.value) {
        startTimer()
        isStarted.value = true
        isTraining.value = true
    } else if (isTraining.value) {
        pauseTimer()
        isTraining.value = false
    } else {
        resumeTimer()
        isTraining.value = true
    }
}

const startTimer = () => {
    timer = setInterval(() => {
        elapsedSeconds.value++
    }, 1000)
}

const pauseTimer = () => {
    if (timer) {
        clearInterval(timer)
        timer = null
    }
}

const resumeTimer = () => {
    startTimer()
}

const stopTimer = () => {
    if (timer) {
        clearInterval(timer)
        timer = null
    }
}

const formatElapsedTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    if (hrs > 0) {
        return `${hrs}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
    }
    return `${mins}:${String(secs).padStart(2, '0')}`
}

const onRestComplete = () => {
    showRestModal.value = false
}

const onRestSkip = () => {
    showRestModal.value = false
}

const finishTraining = async () => {
    stopTimer()

    uni.showModal({
        title: '确认完成',
        content: '确定要结束本次训练吗？',
        success: async (res) => {
            if (res.confirm) {
                try {
                    await request.post(`${API_V2.SCHEDULE_POSTPONE}/${planId.value}/${scheduleId.value}`, { completed: true })
                    uni.showToast({ title: '训练已完成', icon: 'success' })
                    setTimeout(() => {
                        uni.navigateBack()
                    }, 1500)
                } catch (error) {
                    console.error('完成训练失败:', error)
                    uni.showToast({ title: '操作失败', icon: 'none' })
                }
            }
        }
    })
}

const goBack = () => {
    if (isStarted.value) {
        uni.showModal({
            title: '提示',
            content: '训练进行中，确定要退出吗？',
            success: (res) => {
                if (res.confirm) {
                    stopTimer()
                    uni.navigateBack()
                }
            }
        })
    } else {
        uni.navigateBack()
    }
}
</script>

<style lang="scss" scoped>
.container {
    min-height: 100vh;
    background: #F5F5F5;
    padding-bottom: 200rpx;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40rpx 40rpx 30rpx;

    .header-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 30rpx;

        .back-btn {
            font-size: 40rpx;
            color: #FFFFFF;
            padding: 10rpx;
        }

        .header-title {
            font-size: 36rpx;
            font-weight: bold;
            color: #FFFFFF;
        }

        .header-time {
            font-size: 32rpx;
            color: #FFFFFF;
            font-family: 'DIN Alternate', -apple-system;
        }
    }

    .session-tabs {
        display: flex;
        gap: 16rpx;

        .session-tab {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16rpx;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 16rpx;
            transition: all 0.3s;

            &.active {
                background: rgba(255, 255, 255, 0.95);

                .tab-icon, .tab-label {
                    color: #667eea;
                }
            }

            .tab-icon {
                font-size: 32rpx;
                margin-bottom: 4rpx;
                color: rgba(255, 255, 255, 0.9);
            }

            .tab-label {
                font-size: 22rpx;
                color: rgba(255, 255, 255, 0.9);
            }
        }
    }
}

.content {
    padding: 30rpx 40rpx;
}

.current-session {
    .session-header {
        margin-bottom: 30rpx;

        .session-name {
            display: block;
            font-size: 32rpx;
            font-weight: bold;
            color: #333333;
            margin-bottom: 8rpx;
        }

        .session-info {
            display: block;
            font-size: 26rpx;
            color: #666666;
        }
    }
}

.action-list {
    display: flex;
    flex-direction: column;
    gap: 24rpx;

    .action-card {
        background: #FFFFFF;
        border-radius: 24rpx;
        padding: 28rpx;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
        transition: all 0.3s;

        &.active {
            border: 2rpx solid #667eea;
        }

        &.completed {
            opacity: 0.7;

            .action-name {
                text-decoration: line-through;
            }
        }

        .action-main {
            margin-bottom: 20rpx;

            .action-info {
                display: flex;
                align-items: center;
                margin-bottom: 16rpx;

                .action-name {
                    font-size: 30rpx;
                    font-weight: bold;
                    color: #333333;
                    margin-right: 16rpx;
                }

                .action-difficulty {
                    font-size: 20rpx;
                    padding: 4rpx 12rpx;
                    border-radius: 8rpx;
                    color: #FFFFFF;
                }
            }

            .action-params {
                display: flex;
                align-items: center;
                gap: 12rpx;

                .param-item {
                    display: flex;
                    align-items: baseline;

                    .param-value {
                        font-size: 32rpx;
                        font-weight: bold;
                        color: #333333;
                    }

                    .param-label {
                        font-size: 22rpx;
                        color: #666666;
                        margin-left: 4rpx;
                    }
                }

                .param-divider {
                    font-size: 24rpx;
                    color: #999999;
                }
            }
        }

        .action-progress {
            display: flex;
            gap: 12rpx;
            flex-wrap: wrap;

            .set-indicator {
                width: 64rpx;
                height: 64rpx;
                border-radius: 50%;
                background: #F5F5F5;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;

                .set-num {
                    font-size: 26rpx;
                    font-weight: bold;
                    color: #666666;
                }

                &.current {
                    background: #667eea;

                    .set-num {
                        color: #FFFFFF;
                    }
                }

                &.completed {
                    background: #34C759;

                    .set-num {
                        color: #FFFFFF;
                    }
                }
            }
        }

        .weight-section {
            margin-top: 20rpx;
            padding-top: 20rpx;
            border-top: 1rpx solid #F0F0F0;

            .weight-label {
                display: block;
                font-size: 24rpx;
                color: #666666;
                margin-bottom: 12rpx;
            }

            .weight-inputs {
                display: flex;
                gap: 12rpx;

                .weight-input {
                    flex: 1;
                    height: 72rpx;
                    background: #F5F5F5;
                    border-radius: 12rpx;
                    padding: 0 16rpx;
                    font-size: 26rpx;
                    text-align: center;
                }
            }
        }
    }
}

.empty-actions {
    text-align: center;
    padding: 60rpx 0;

    .empty-text {
        font-size: 28rpx;
        color: #999999;
    }
}

.bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    gap: 16rpx;
    padding: 24rpx 40rpx;
    padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
    background: #FFFFFF;
    border-top: 1rpx solid #E5E5E5;

    .btn {
        flex: 1;
        height: 88rpx;
        border-radius: 44rpx;
        border: none;
        font-size: 28rpx;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;

        &.prev-btn, &.next-btn {
            background: #F5F5F5;
            color: #666666;
        }

        &.action-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #FFFFFF;
        }

        &.finish-btn {
            background: #34C759;
            color: #FFFFFF;
        }
    }
}
</style>
