<template>
    <view class="container">
        <view class="header">
            <view class="header-top">
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
                    <image class="tab-icon" :src="SESSION_TYPE_MAP[session.session_type]?.icon" mode="aspectFit"></image>
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
            <template v-if="!isStarted">
                <button class="btn action-btn" @click="startTraining">
                    <text>开始训练</text>
                </button>
            </template>
            <template v-else>
                <button class="btn action-btn" @click="togglePauseResume">
                    <text>{{ isTraining ? '暂停' : '继续' }}</text>
                </button>
                <button class="btn finish-btn" @click="finishTraining">
                    <text>结束训练</text>
                </button>
            </template>
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

const PART_LABEL_MAP = {
    '推': '推日',
    '腿': '腿日',
    '拉': '拉日'
}

const SESSION_ORDER = ['WARMUP', 'MAIN', 'COOLDOWN']

const planId = ref('')
const scheduleId = ref('')
const sessionId = ref('')
const trainingPart = ref('')
const allSessions = ref([])
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
    trainingPart.value = options.training_part ? decodeURIComponent(options.training_part) : ''

    if (trainingPart.value) {
        const label = PART_LABEL_MAP[trainingPart.value] || trainingPart.value
        uni.setNavigationBarTitle({ title: `${label}训练` })
    }
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

const loadPlanDetail = async () => {
    try {
        const res = await request.get(`${API_V2.PLAN_DETAIL}/${planId.value}`)
        allSessions.value = res.sessions || []

        sessions.value = trainingPart.value
            ? allSessions.value.filter(s => s.training_part === trainingPart.value)
                .sort((a, b) => SESSION_ORDER.indexOf(a.session_type) - SESSION_ORDER.indexOf(b.session_type))
            : allSessions.value

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

const startTraining = () => {
    uni.showModal({
        title: '确认开始训练',
        content: '确定要开始本次训练吗？同一训练计划每天只能训练一次。',
        success: (res) => {
            if (res.confirm) {
                startTimer()
                isStarted.value = true
                isTraining.value = true
            }
        }
    })
}

const togglePauseResume = () => {
    if (isTraining.value) {
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

const finishTraining = () => {
    pauseTimer()

    uni.showModal({
        title: '确认结束训练',
        content: '确定要结束本次训练吗？结束后将保存训练记录。',
        success: async (res) => {
            if (res.confirm) {
                stopTimer()
                try {
                    await request.post(`${API_V2.SCHEDULE_COMPLETE}/${planId.value}/${scheduleId.value}`, {
                        actual_duration_seconds: elapsedSeconds.value
                    })
                    uni.showToast({ title: '训练已完成', icon: 'success' })
                    setTimeout(() => {
                        uni.navigateBack()
                    }, 1500)
                } catch (error) {
                    console.error('完成训练失败:', error)
                    uni.showToast({ title: '操作失败', icon: 'none' })
                    resumeTimer()
                    isTraining.value = true
                }
            } else {
                resumeTimer()
                isTraining.value = true
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
    background: $fitness-secondary;
    padding-bottom: 200rpx;
    font-family: Manrope;
}

.header {
    background: linear-gradient(135deg, #a03e40 0%, #c05557 100%);
    padding: $size-5 $size-5 $size-4;

    .header-top {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: $size-4;

        .header-time {
            font-size: $size-6;
            color: #FFFFFF;
            font-weight: 700;
            font-family: Manrope;
        }
    }

    .session-tabs {
        display: flex;
        gap: $size-2;

        .session-tab {
            flex: 1;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            padding: $size-2;
            background: rgba(255, 255, 255, 0.2);
            border-radius: $size-2;
            transition: all 0.3s;

            &.active {
                background: rgba(255, 255, 255, 0.7);
                flex-direction: row;

                .tab-icon, .tab-label {
                    color: $color-primary;
                }
            }

            .tab-icon {
                width: $size-5;
                height: $size-5;
                margin-bottom: $size-1;
            }

            .tab-label {
                font-size: $size-3;
                font-weight: 700;
                color: rgba(255, 255, 255, 0.9);
            }
        }
    }
}

.content {
    padding: $size-4 $size-5;
}

.current-session {
    .session-header {
        margin-bottom: $size-4;

        .session-name {
            display: block;
            font-size: $size-4;
            font-weight: 700;
            color: $color-input;
            margin-bottom: $size-1;
        }

        .session-info {
            display: block;
            font-size: $size-3;
            color: $color-secondory;
        }
    }
}

.action-list {
    display: flex;
    flex-direction: column;
    gap: $size-3;

    .action-card {
        background: $glass-bg1;
        border-radius: $size-4;
        padding: $size-4;
        box-shadow: 0 2rpx 10rpx $border-shadow;
        border: 2rpx solid $fitness-border;
        transition: all 0.3s;

        &.active {
            border: 2rpx solid $color-primary;
        }

        &.completed {
            opacity: 0.7;

            .action-name {
                text-decoration: line-through;
            }
        }

        .action-main {
            margin-bottom: $size-3;

            .action-info {
                display: flex;
                align-items: center;
                margin-bottom: $size-2;

                .action-name {
                    font-size: $size-4;
                    font-weight: 700;
                    color: $color-input;
                    margin-right: $size-2;
                }

                .action-difficulty {
                    font-size: $size-3;
                    padding: $size-1 $size-2;
                    border-radius: $size-1;
                    color: #FFFFFF;
                }
            }

            .action-params {
                display: flex;
                align-items: center;
                gap: $size-2;

                .param-item {
                    display: flex;
                    align-items: baseline;

                    .param-value {
                        font-size: $size-4;
                        font-weight: 700;
                        color: $color-input;
                    }

                    .param-label {
                        font-size: $size-3;
                        color: $color-label;
                        margin-left: $size-1;
                    }
                }

                .param-divider {
                    font-size: $size-3;
                    color: $color-secondory;
                }
            }
        }

        .action-progress {
            display: flex;
            gap: $size-2;
            flex-wrap: wrap;

            .set-indicator {
                width: $size-8;
                height: $size-8;
                border-radius: 50%;
                background: $fitness-secondary;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;

                .set-num {
                    font-size: $size-3;
                    font-weight: 700;
                    color: $color-label;
                }

                &.current {
                    background: $button-bg2;

                    .set-num {
                        color: #FFFFFF;
                    }
                }

                &.completed {
                    background: $uni-success;

                    .set-num {
                        color: #FFFFFF;
                    }
                }
            }
        }

        .weight-section {
            margin-top: $size-3;
            padding-top: $size-3;
            border-top: 2rpx solid $fitness-border;

            .weight-label {
                display: block;
                font-size: $size-3;
                font-weight: 700;
                color: $color-label;
                margin-bottom: $size-2;
            }

            .weight-inputs {
                display: flex;
                gap: $size-2;

                .weight-input {
                    flex: 1;
                    height: $size-9;
                    background: $fitness-primary;
                    border-radius: $size-2;
                    border: 2rpx solid rgba(160, 62, 64, 0.1);
                    padding: 0 $size-2;
                    font-size: $size-3;
                    font-family: Manrope;
                    color: $color-input;
                    text-align: center;
                }
            }
        }
    }
}

.empty-actions {
    text-align: center;
    padding: $size-8 0;

    .empty-text {
        font-size: $size-4;
        color: $color-secondory;
    }
}

.bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    gap: $size-2;
    padding: $size-3 $size-5;
    padding-bottom: calc(#{$size-3} + env(safe-area-inset-bottom));
    background: $fitness-primary;
    border-top: 2rpx solid $fitness-border;
    box-shadow: 0 -2rpx 10rpx $border-shadow;

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

        &.action-btn {
            background: $button-bg2;
            color: #FFFFFF;
        }

        &.finish-btn {
            background: $uni-success;
            color: #FFFFFF;
        }
    }
}
</style>
