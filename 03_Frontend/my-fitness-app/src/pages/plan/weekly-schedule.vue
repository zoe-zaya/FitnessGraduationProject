<template>
    <view class="container">
        <view class="header">
            <text class="header-title">7天训练日程</text>
            <text class="header-subtitle">从今天开始的训练安排</text>
        </view>

        <view class="schedule-content">
            <view class="week-nav">
                <view class="week-label">
                    <text class="week-icon">📅</text>
                    <text class="week-text">{{ getWeekRange() }}</text>
                </view>
            </view>

            <view class="schedule-list">
                <view
                    class="schedule-card"
                    v-for="(item, index) in scheduleList"
                    :key="item.schedule_id || index"
                    :class="{ 'today': isToday(item.scheduled_date), 'rest': item.status === 'REST', 'completed': item.status === 'COMPLETED' }"
                >
                    <view class="date-section">
                        <text class="date-day">{{ getDayOfWeek(item.scheduled_date) }}</text>
                        <text class="date-num">{{ formatDateNum(item.scheduled_date) }}</text>
                        <view class="today-badge" v-if="isToday(item.scheduled_date)">今天</view>
                    </view>

                    <view class="schedule-divider"></view>

                    <view class="schedule-info">
                        <view class="status-badge" :class="item.status.toLowerCase()">
                            {{ getStatusLabel(item.status) }}
                        </view>

                        <view class="session-info" v-if="item.session_type">
                            <text class="session-type">{{ getSessionLabel(item.session_type) }}</text>
                            <text class="session-part" v-if="item.training_part">{{ getPartLabel(item.training_part) }}</text>
                            <text class="session-target" v-if="item.target_muscles">{{ item.target_muscles.join('、') }}</text>
                        </view>

                        <view class="rest-info" v-else-if="item.status === 'REST'">
                            <text class="rest-text">休息日</text>
                        </view>
                    </view>

                    <view class="schedule-actions">
                        <view
                            class="action-btn postpone"
                            v-if="(item.status === 'PLANNED' || item.status === 'POSTPONED') && item.can_postpone"
                            @click="showPostponeOptions(item)"
                        >
                            <text class="btn-icon">⏰</text>
                            <text class="btn-text">延后</text>
                        </view>
                        <view
                            class="action-btn start"
                            v-if="item.status === 'PLANNED'"
                            @click="startTraining(item)"
                        >
                            <text class="btn-icon">▶️</text>
                            <text class="btn-text">开始</text>
                        </view>
                        <view
                            class="action-btn view"
                            v-if="item.status === 'COMPLETED'"
                            @click="viewRecord(item)"
                        >
                            <text class="btn-icon">📋</text>
                            <text class="btn-text">查看</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>

        <RestCountdown
            :visible="showRestModal"
            :initialSeconds="60"
            @update:visible="showRestModal = $event"
            @complete="onRestComplete"
            @skip="onRestSkip"
        />
    </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SESSION_TYPE_MAP, SCHEDULE_STATUS } from '@/utils/constants'
import RestCountdown from '@/components/RestCountdown.vue'

const planId = ref('')
const scheduleList = ref([])
const showRestModal = ref(false)

onLoad((options) => {
    planId.value = options.plan_id || ''
})

onMounted(async () => {
    await loadSchedule()
})

const loadSchedule = async () => {
    try {
        const res = await request.get(`${API_V2.SCHEDULE_LIST}/${planId.value}`)
        scheduleList.value = res || []
    } catch (error) {
        console.error('加载日程失败:', error)
        uni.showToast({ title: '加载失败', icon: 'none' })
    }
}

const getWeekRange = () => {
    if (scheduleList.value.length === 0) return ''
    const first = new Date(scheduleList.value[0].scheduled_date)
    const last = new Date(scheduleList.value[scheduleList.value.length - 1].scheduled_date)
    return `${formatDateShort(first)} ~ ${formatDateShort(last)}`
}

const isToday = (dateStr) => {
    const today = new Date()
    const date = new Date(dateStr)
    return date.toDateString() === today.toDateString()
}

const getDayOfWeek = (dateStr) => {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const date = new Date(dateStr)
    return days[date.getDay()]
}

const formatDateNum = (dateStr) => {
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}月${date.getDate()}日`
}

const formatDateShort = (date) => {
    return `${date.getMonth() + 1}/${date.getDate()}`
}

const getStatusLabel = (status) => {
    return SCHEDULE_STATUS[status]?.label || status
}

const getSessionLabel = (sessionType) => {
    return SESSION_TYPE_MAP[sessionType]?.label || sessionType
}

const PART_LABEL_MAP = {
    '推': '推日 · 胸肩三头',
    '腿': '腿日 · 臀腿',
    '拉': '拉日 · 背二头'
}

const getPartLabel = (part) => PART_LABEL_MAP[part] || part

const showPostponeOptions = (item) => {
    const maxDays = 3 - (item.postpone_count || 0)
    const options = []
    for (let i = 1; i <= maxDays; i++) {
        options.push(`延后${i}天`)
    }
    if (options.length === 0) return

    uni.showActionSheet({
        itemList: options,
        success: async (res) => {
            const days = res.tapIndex + 1
            await postponeSchedule(item, days)
        }
    })
}

const postponeSchedule = async (item, days) => {
    try {
        await request.post(`${API_V2.SCHEDULE_POSTPONE}/${planId.value}/${item.schedule_id}`, { days })
        uni.showToast({ title: `已延后${days}天`, icon: 'success' })
        await loadSchedule()
    } catch (error) {
        console.error('延后失败:', error)
        uni.showToast({ title: error.detail || '延后失败', icon: 'none' })
    }
}

const startTraining = (item) => {
    uni.navigateTo({
        url: `/pages/plan/training-execution?plan_id=${planId.value}&schedule_id=${item.schedule_id}&session_id=${item.session_id}`
    })
}

const viewRecord = (item) => {
    uni.navigateTo({
        url: `/pages/plan/training-record?schedule_id=${item.schedule_id}`
    })
}

const onRestComplete = () => {
    showRestModal.value = false
}

const onRestSkip = () => {
    showRestModal.value = false
}
</script>

<style lang="scss" scoped>
.container {
    min-height: 100vh;
    background: #F5F5F5;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40rpx 40rpx 80rpx;

    .header-title {
        display: block;
        font-size: 40rpx;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 8rpx;
    }

    .header-subtitle {
        display: block;
        font-size: 26rpx;
        color: rgba(255, 255, 255, 0.8);
    }
}

.schedule-content {
    margin-top: -40rpx;
    padding: 0 30rpx 40rpx;
}

.week-nav {
    background: #FFFFFF;
    border-radius: 20rpx;
    padding: 24rpx 32rpx;
    margin-bottom: 30rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);

    .week-label {
        display: flex;
        align-items: center;

        .week-icon {
            font-size: 32rpx;
            margin-right: 12rpx;
        }

        .week-text {
            font-size: 28rpx;
            color: #333333;
            font-weight: 500;
        }
    }
}

.schedule-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
}

.schedule-card {
    background: #FFFFFF;
    border-radius: 24rpx;
    padding: 28rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
    position: relative;
    overflow: hidden;

    &.today {
        border: 2rpx solid #667eea;
    }

    &.rest {
        background: #F8F8F8;
    }

    &.completed {
        opacity: 0.8;
    }

    .date-section {
        width: 120rpx;
        text-align: center;
        position: relative;

        .date-day {
            display: block;
            font-size: 24rpx;
            color: #666666;
            margin-bottom: 8rpx;
        }

        .date-num {
            display: block;
            font-size: 28rpx;
            color: #333333;
            font-weight: bold;
        }

        .today-badge {
            position: absolute;
            top: -10rpx;
            right: 10rpx;
            background: #667eea;
            color: #FFFFFF;
            font-size: 18rpx;
            padding: 4rpx 12rpx;
            border-radius: 10rpx;
        }
    }

    .schedule-divider {
        width: 2rpx;
        height: 80rpx;
        background: #E5E5E5;
        margin: 0 24rpx;
    }

    .schedule-info {
        flex: 1;

        .status-badge {
            display: inline-block;
            font-size: 22rpx;
            padding: 6rpx 16rpx;
            border-radius: 12rpx;
            margin-bottom: 12rpx;

            &.planned {
                background: #E3F2FD;
                color: #1976D2;
            }

            &.completed {
                background: #E8F5E9;
                color: #34C759;
            }

            &.postponed {
                background: #FFF3E0;
                color: #FF9800;
            }

            &.rest {
                background: #F5F5F5;
                color: #999999;
            }
        }

        .session-info {
            .session-type {
                display: block;
                font-size: 28rpx;
                color: #333333;
                font-weight: 600;
                margin-bottom: 4rpx;
            }

            .session-part {
                display: block;
                font-size: 24rpx;
                color: #667eea;
                font-weight: 600;
                margin-bottom: 4rpx;
            }

            .session-target {
                display: block;
                font-size: 24rpx;
                color: #666666;
            }
        }

        .rest-info {
            .rest-text {
                font-size: 28rpx;
                color: #999999;
            }
        }
    }

    .schedule-actions {
        display: flex;
        gap: 12rpx;

        .action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16rpx 20rpx;
            border-radius: 16rpx;
            min-width: 80rpx;

            .btn-icon {
                font-size: 28rpx;
                margin-bottom: 4rpx;
            }

            .btn-text {
                font-size: 22rpx;
            }

            &.postpone {
                background: #FFF3E0;

                .btn-text {
                    color: #FF9800;
                }
            }

            &.start {
                background: linear-gradient(135deg, #667eea, #764ba2);

                .btn-text {
                    color: #FFFFFF;
                }
            }

            &.view {
                background: #E3F2FD;

                .btn-text {
                    color: #1976D2;
                }
            }
        }
    }
}
</style>
