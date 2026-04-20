<template>
    <view class="container">
        <view class="header">
            <view class="plan-title-row">
                <text class="plan-name">{{ planInfo.plan_name }}</text>
                <view class="plan-type-badge" :class="planInfo.plan_type?.toLowerCase()">
                    {{ planInfo.plan_type === 'FAT_LOSS' ? '减脂' : '增肌' }}
                </view>
            </view>

            <view class="week-strip">
                <view
                    class="day-cell"
                    v-for="(day, index) in weekDays"
                    :key="index"
                    :class="{ today: day.isToday, rest: day.isRest, selected: selectedDayIndex === index }"
                    @click="selectDay(index)"
                >
                    <text class="day-weekday">{{ day.weekday }}</text>
                    <text class="day-date">{{ day.dateNum }}</text>
                    <view class="day-status" :class="day.isRest ? 'rest' : 'train'">
                        <text class="status-text">{{ day.isRest ? '休' : '练' }}</text>
                    </view>
                    <view class="today-dot" v-if="day.isToday"></view>
                </view>
            </view>
        </view>

        <view class="content">
            <view class="today-card" v-if="todaySession">
                <view class="today-header">
                    <view class="today-header-left">
                        <view class="part-badge" :class="todaySession.training_part" v-if="todaySession.training_part">
                            {{ getPartLabel(todaySession.training_part) }}
                        </view>
                        <text class="today-muscles">{{ todayMusclesDesc }}</text>
                    </view>
                    <view class="postpone-btn" v-if="canPostpone" @click="showPostponeOptions">
                        <uni-icons type="redo" size="16" color="#a03e40"></uni-icons>
                        <text class="postpone-text">延后</text>
                    </view>
                </view>

                <view class="session-list">
                    <view
                        class="session-item"
                        v-for="session in todaySessions"
                        :key="session.session_id"
                    >
                        <view class="session-type-bar" :style="{ backgroundColor: getSessionColor(session.session_type) }"></view>
                        <view class="session-body">
                            <view class="session-top">
                                <text class="session-name">{{ SESSION_TYPE_MAP[session.session_type]?.label }}</text>
                                <text class="session-duration">约{{ session.estimated_duration_minutes }}分钟</text>
                            </view>
                            <view class="action-list">
                                <view
                                    class="action-row"
                                    v-for="action in session.action_items"
                                    :key="action.item_id"
                                    @click="viewActionDetail(action)"
                                >
                                    <view class="action-left">
                                        <text class="action-name">{{ action.action_name }}</text>
                                        <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                                            {{ action.difficulty_level }}
                                        </text>
                                    </view>
                                    <view class="action-right">
                                        <text class="action-param" v-if="action.sets">{{ action.sets }}×{{ action.reps_per_set }}</text>
                                        <text class="action-param" v-else-if="action.duration_minutes">{{ action.duration_minutes }}分钟</text>
                                    </view>
                                </view>
                            </view>
                        </view>
                    </view>
                </view>
            </view>

            <view class="rest-card" v-else>
                <text class="rest-title">今天是休息日</text>
                <text class="rest-sub">好好休息，为下次训练蓄力</text>
            </view>
        </view>

        <view class="bottom-bar">
            <button class="btn edit-btn" @click="editPlan">编辑计划</button>
            <button class="btn start-btn" @click="startExecution">开始训练</button>
        </view>
    </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SESSION_TYPE_MAP, DIFFICULTY_MAP, SCHEME_TYPES } from '@/utils/constants'

const planId = ref('')
const planInfo = ref({
    plan_name: '',
    plan_type: '',
    scheme_type: '',
    cycle_rule: '',
    status: '',
    sessions: [],
    weekly_schedule: []
})

const selectedDayIndex = ref(-1)

const SESSION_COLORS = {
    WARMUP: '#FF9500',
    MAIN: '#a03e40',
    COOLDOWN: '#24a978'
}

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

const getPartLabel = (part) => PART_LABEL_MAP[part] || part
const getSessionColor = (type) => SESSION_COLORS[type] || '#a03e40'

const weekDays = computed(() => {
    const schedule = planInfo.value.weekly_schedule || []
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    const today = new Date()

    return schedule.map((item, index) => {
        const date = new Date(item.scheduled_date)
        const isToday = date.toDateString() === today.toDateString()
        const isRest = item.status === 'REST'

        if (isToday && selectedDayIndex.value === -1) {
            selectedDayIndex.value = index
        }

        return {
            weekday: '周' + weekdays[date.getDay()],
            dateNum: date.getDate(),
            isToday,
            isRest,
            schedule: item
        }
    })
})

const currentSchedule = computed(() => {
    const idx = selectedDayIndex.value >= 0 ? selectedDayIndex.value : 0
    const schedule = planInfo.value.weekly_schedule || []
    return schedule[idx] || null
})

const todaySession = computed(() => {
    if (!currentSchedule.value || currentSchedule.value.status === 'REST') return null
    return currentSchedule.value
})

const todayTrainingPart = computed(() => {
    return currentSchedule.value?.training_part || null
})

const todaySessions = computed(() => {
    const part = todayTrainingPart.value
    if (!part) return []
    const sessions = planInfo.value.sessions || []
    return sessions.filter(s => s.training_part === part)
})

const todayMusclesDesc = computed(() => {
    const part = todayTrainingPart.value
    if (!part) return ''
    return PART_MUSCLES_DESC[part] || currentSchedule.value?.target_muscles?.join(' · ') || ''
})

const selectDay = (index) => {
    selectedDayIndex.value = index
}

onLoad((options) => {
    planId.value = options.plan_id || ''
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

const getSchemeName = (schemeType) => {
    const scheme = SCHEME_TYPES.find(s => s.value === schemeType)
    return scheme ? scheme.label.split('（')[0] : schemeType
}

const getDifficultyColor = (level) => {
    return DIFFICULTY_MAP[level]?.color || '#8E8E93'
}

const startExecution = () => {
    const part = todayTrainingPart.value
    const sessions = planInfo.value.sessions || []
    const mainSession = sessions.find(s => s.session_type === 'MAIN' && s.training_part === part)
    if (mainSession && mainSession.session_id) {
        uni.navigateTo({
            url: `/pages/plan/training-execution?plan_id=${planId.value}&session_id=${mainSession.session_id}`
        })
    } else {
        const fallback = sessions.find(s => s.session_type === 'MAIN')
        if (fallback && fallback.session_id) {
            uni.navigateTo({
                url: `/pages/plan/training-execution?plan_id=${planId.value}&session_id=${fallback.session_id}`
            })
        }
    }
}

const viewActionDetail = (action) => {
    uni.navigateTo({ url: `/pages/action/action-detail?action_id=${action.action_id}` })
}

const replaceAction = (action, session) => {
    uni.navigateTo({
        url: `/pages/plan/select-action?session_id=${session.session_id}&plan_id=${planId.value}&session_type=${session.session_type}&action_id=${action.item_id}&mode=replace`
    })
}

const addActionToSession = (session) => {
    uni.navigateTo({
        url: `/pages/plan/select-action?session_id=${session.session_id}&plan_id=${planId.value}&session_type=${session.session_type}&mode=add`
    })
}

const confirmDeleteAction = (action) => {
    uni.showModal({
        title: '提示',
        content: `确定要删除"${action.action_name}"吗？`,
        success: async (res) => {
            if (res.confirm) {
                await deleteActionItem(action.item_id)
            }
        }
    })
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

const editPlan = () => {
    uni.navigateTo({ url: `/pages/plan/plan-edit?plan_id=${planId.value}` })
}

const canPostpone = computed(() => {
    const schedule = currentSchedule.value
    if (!schedule) return false
    if (schedule.status === 'REST' || schedule.status === 'COMPLETED') return false
    return schedule.can_postpone === true
})

const showPostponeOptions = () => {
    const schedule = currentSchedule.value
    if (!schedule) return

    const maxDays = 3 - (schedule.postpone_count || 0)
    const options = []
    for (let i = 1; i <= maxDays; i++) {
        options.push(`延后${i}天`)
    }

    uni.showActionSheet({
        itemList: options,
        success: async (res) => {
            const days = res.tapIndex + 1
            await postponeSchedule(schedule.schedule_id, days)
        }
    })
}

const postponeSchedule = async (scheduleId, days) => {
    try {
        await request.post(`${API_V2.SCHEDULE_POSTPONE}/${planId.value}/${scheduleId}`, { days })
        uni.showToast({ title: '已延后', icon: 'success' })
        await loadPlanDetail()
    } catch (error) {
        console.error('延后失败:', error)
        uni.showToast({ title: '延后失败', icon: 'none' })
    }
}
</script>

<style lang="scss" scoped>
@import '../../uni.scss';

.container {
    min-height: 100vh;
    background: $fitness-secondary;
    padding-bottom: 140rpx;
    font-family: Manrope;
}

.header {
    background: linear-gradient(135deg, #a03e40 0%, #c05557 100%);
    padding: $size-5 $size-5 $size-6;

    .plan-title-row {
        display: flex;
        align-items: center;
        margin-bottom: $size-4;

        .plan-name {
            font-size: $size-5;
            font-weight: 700;
            color: #FFFFFF;
            margin-right: $size-2;
        }

        .plan-type-badge {
            font-size: $size-3;
            padding: $size-1 $size-2;
            border-radius: $size-2;
            color: #FFFFFF;

            &.fat_loss {
                background: rgba(255, 255, 255, 0.25);
            }

            &.muscle_gain {
                background: rgba(255, 255, 255, 0.15);
            }
        }
    }

    .week-strip {
        display: flex;
        background: transparent;
        border-radius: $size-4;
        //padding: $size-2;

        .day-cell {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: $size-2 0;
            border-radius: $size-3;
            transition: all 0.2s;

            &.selected {
                background: rgba(255, 255, 255, 0.3);
            }

            &.today {
                .today-dot {
                    width: 8rpx;
                    height: 8rpx;
                    border-radius: 50%;
                    background: #FFFFFF;
                    margin-top: 6rpx;
                }
            }

            &.rest {
                .day-weekday, .day-date {
                    opacity: 0.5;
                }
            }

            .day-weekday {
                font-size: 20rpx;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 4rpx;
            }

            .day-date {
                font-size: $size-3;
                font-weight: 700;
                color: #FFFFFF;
                margin-bottom: $size-1;
            }

            .day-status {
                //width: 36rpx;
                //height: 36rpx;
                //border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;

                .status-text {
                    font-size: 18rpx;
                    font-weight: 700;
                    color: #FFFFFF;
                }
            }
        }
    }
}

.content {
    padding: $size-4 $size-5;
}

.today-card {
    background: $glass-bg1;
    border-radius: $size-5;
    overflow: hidden;
    box-shadow: 0 4rpx 20rpx $border-shadow;

    .today-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: $size-4 $size-5;
        border-bottom: 1rpx solid $fitness-border;

        .today-header-left {
            display: flex;
            align-items: center;
            gap: $size-3;
        }

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

        .today-muscles {
            font-size: $size-3;
            color: $color-secondory;
        }

        .postpone-btn {
            display: flex;
            align-items: center;
            gap: 6rpx;
            padding: $size-1 $size-3;
            border-radius: $size-6;
            background: rgba(160, 62, 64, 0.08);

            .postpone-text {
                font-size: $size-3;
                color: $color-primary;
                font-weight: 700;
            }
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

                .action-list {
                    .action-row {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        padding: $size-2 $size-3;
                        background: #FFFFFF;
                        border-radius: $size-3;
                        margin-bottom: $size-2;
                        border: 1rpx solid $fitness-border;

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

                        .action-right {
                            display: flex;
                            align-items: center;
                            gap: $size-2;

                            .action-param {
                                font-size: $size-3;
                                color: $color-secondory;
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
                                        width: 28rpx;
                                        height: 28rpx;
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

.bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    gap: $size-3;
    padding: $size-3 $size-5;
    padding-bottom: calc(#{$size-3} + env(safe-area-inset-bottom));
    background: #FFFFFF;
    border-top: 1rpx solid $fitness-border;
    box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);

    .btn {
        flex: 1;
        height: $size-12;
        border-radius: $size-6;
        border: none;
        font-size: $size-4;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Manrope;

        &.edit-btn {
            background: $fitness-secondary;
            color: $color-label;
        }

        &.start-btn {
            background: $button-bg2;
            color: #FFFFFF;
        }
    }
}

.rest-card {
    background: $glass-bg1;
    border-radius: $size-5;
    padding: $size-10 $size-5;
    text-align: center;
    box-shadow: 0 4rpx 20rpx $border-shadow;

    .rest-title {
        display: block;
        font-size: $size-5;
        font-weight: 700;
        color: $color-input;
        margin-bottom: $size-2;
    }

    .rest-sub {
        display: block;
        font-size: $size-3;
        color: $color-secondory;
    }
}
</style>
