<template>
    <view class="container">
        <view class="header">
            <view class="header-content">
                <view class="plan-title-row">
                    <text class="plan-name">{{ planInfo.plan_name }}</text>
                    <view class="plan-type-badge" :class="planInfo.plan_type?.toLowerCase()">
                        {{ planInfo.plan_type === 'FAT_LOSS' ? '减脂' : '增肌' }}
                    </view>
                </view>
                <view class="plan-meta">
                    <view class="meta-item">
                        <text class="meta-icon">📋</text>
                        <text class="meta-text" v-if="planInfo.scheme_type">{{ getSchemeName(planInfo.scheme_type) }}</text>
                        <text class="meta-text" v-else>全身训练</text>
                    </view>
                    <view class="meta-item">
                        <text class="meta-icon">📅</text>
                        <text class="meta-text">{{ planInfo.cycle_rule }}</text>
                    </view>
                </view>
            </view>
            <view class="header-actions">
                <view class="action-btn schedule" @click="viewSchedule">
                    <text class="btn-icon">📅</text>
                    <text class="btn-text">日程</text>
                </view>
                <view class="action-btn execute" @click="startExecution">
                    <text class="btn-icon">▶️</text>
                    <text class="btn-text">执行</text>
                </view>
            </view>
        </view>

        <view class="content">
            <view class="sessions-section">
                <view
                    class="session-card"
                    v-for="(session, index) in planInfo.sessions"
                    :key="session.session_id"
                >
                    <view class="session-header" :style="{ borderLeftColor: SESSION_TYPE_MAP[session.session_type]?.color }">
                        <view class="session-info">
                            <text class="session-icon">{{ SESSION_TYPE_MAP[session.session_type]?.icon }}</text>
                            <view class="session-details">
                                <text class="session-name">{{ SESSION_TYPE_MAP[session.session_type]?.label }}</text>
                                <text class="session-duration">⏱️ 约{{ session.estimated_duration_minutes }}分钟</text>
                            </view>
                        </view>
                        <text class="session-order">{{ session.sequence_order }}/3</text>
                    </view>

                    <view class="target-muscles" v-if="session.target_muscles && session.target_muscles.length > 0">
                        <text class="muscles-label">🎯 目标肌群：</text>
                        <view class="muscles-tags">
                            <text class="muscle-tag" v-for="(muscle, mIndex) in session.target_muscles" :key="mIndex">
                                {{ muscle }}
                            </text>
                        </view>
                    </view>

                    <view class="action-list">
                        <view
                            class="action-item"
                            v-for="(action, aIndex) in session.action_items"
                            :key="action.item_id"
                            @click="viewActionDetail(action)"
                        >
                            <view class="action-main">
                                <view class="action-info">
                                    <text class="action-name">{{ action.action_name }}</text>
                                    <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                                        {{ action.difficulty_level }}
                                    </text>
                                </view>

                                <view class="action-params" v-if="action.sets">
                                    <text class="param-item">📊 {{ action.sets }}组 × {{ action.reps_per_set }}次</text>
                                    <text class="param-item">⏸️ 休息{{ action.rest_seconds_default }}秒</text>
                                </view>

                                <view class="action-params" v-else-if="action.duration_minutes">
                                    <text class="param-item">⏱️ {{ action.duration_minutes }}分钟</text>
                                </view>

                                <view class="weight-display" v-if="action.weight_records && action.weight_records.length > 0">
                                    <text class="weight-label">重量记录：</text>
                                    <text class="weight-values">{{ action.weight_records.join('kg, ') }}kg</text>
                                </view>
                            </view>

                            <view class="action-operations">
                                <view class="op-btn replace" @click.stop="replaceAction(action, session)">
                                    <text class="op-icon">🔄</text>
                                </view>
                                <view class="op-btn delete" @click.stop="confirmDeleteAction(action)">
                                    <text class="op-icon">🗑️</text>
                                </view>
                            </view>
                        </view>

                        <view class="add-action-btn" @click="addActionToSession(session)">
                            <text class="btn-icon">+</text>
                            <text class="btn-text">添加动作</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>

        <view class="bottom-bar">
            <button class="btn archive-btn" @click="archivePlan" v-if="planInfo.status === 'ACTIVE'">
                <text>归档计划</text>
            </button>
            <button class="btn edit-btn" @click="editPlan">
                <text>编辑计划</text>
            </button>
        </view>
    </view>
</template>

<script setup>
import { ref } from 'vue'
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
    sessions: []
})

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
    return DIFFICULTY_MAP[level]?.color || '#999999'
}

const viewSchedule = () => {
    uni.navigateTo({ url: `/pages/plan/weekly-schedule?plan_id=${planId.value}` })
}

const startExecution = () => {
    const mainSession = planInfo.value.sessions?.find(s => s.session_type === 'main')
    if (mainSession && mainSession.session_id) {
        uni.navigateTo({
            url: `/pages/plan/training-execution?plan_id=${planId.value}&session_id=${mainSession.session_id}`
        })
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

const archivePlan = () => {
    uni.showModal({
        title: '归档计划',
        content: '确定要归档此计划吗？归档后可以在"已归档"中查看。',
        success: async (res) => {
            if (res.confirm) {
                try {
                    await request.put(`${API_V2.PLAN_UPDATE}/${planId.value}`, { status: 'ARCHIVED' })
                    uni.showToast({ title: '归档成功', icon: 'success' })
                    setTimeout(() => {
                        uni.navigateBack()
                    }, 1000)
                } catch (error) {
                    console.error('归档失败:', error)
                    uni.showToast({ title: '归档失败', icon: 'none' })
                }
            }
        }
    })
}

const editPlan = () => {
    uni.navigateTo({ url: `/pages/plan/plan-edit?plan_id=${planId.value}` })
}
</script>

<style lang="scss" scoped>
.container {
    min-height: 100vh;
    background: #F5F5F5;
    padding-bottom: 140rpx;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40rpx;

    .header-content {
        margin-bottom: 30rpx;

        .plan-title-row {
            display: flex;
            align-items: center;
            margin-bottom: 16rpx;

            .plan-name {
                font-size: 40rpx;
                font-weight: bold;
                color: #FFFFFF;
                margin-right: 16rpx;
            }

            .plan-type-badge {
                font-size: 22rpx;
                padding: 6rpx 16rpx;
                border-radius: 12rpx;
                color: #FFFFFF;

                &.fat_loss {
                    background: rgba(255, 107, 107, 0.8);
                }

                &.muscle_gain {
                    background: rgba(255, 255, 255, 0.2);
                }
            }
        }

        .plan-meta {
            display: flex;
            gap: 24rpx;

            .meta-item {
                display: flex;
                align-items: center;

                .meta-icon {
                    font-size: 28rpx;
                    margin-right: 8rpx;
                }

                .meta-text {
                    font-size: 26rpx;
                    color: rgba(255, 255, 255, 0.9);
                }
            }
        }
    }

    .header-actions {
        display: flex;
        gap: 16rpx;

        .action-btn {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20rpx;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 20rpx;

            .btn-icon {
                font-size: 28rpx;
                margin-right: 8rpx;
            }

            .btn-text {
                font-size: 26rpx;
                color: #FFFFFF;
            }

            &.execute {
                background: #FFFFFF;

                .btn-icon, .btn-text {
                    color: #667eea;
                }
            }
        }
    }
}

.content {
    padding: 30rpx 40rpx;
}

.sessions-section {
    .session-card {
        background: #FFFFFF;
        border-radius: 24rpx;
        padding: 32rpx;
        margin-bottom: 24rpx;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);

        .session-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24rpx;
            padding-left: 20rpx;
            border-left: 6rpx solid #007AFF;

            .session-info {
                display: flex;
                align-items: center;

                .session-icon {
                    font-size: 40rpx;
                    margin-right: 16rpx;
                }

                .session-details {
                    .session-name {
                        display: block;
                        font-size: 30rpx;
                        font-weight: bold;
                        color: #333333;
                        margin-bottom: 4rpx;
                    }

                    .session-duration {
                        display: block;
                        font-size: 24rpx;
                        color: #666666;
                    }
                }
            }

            .session-order {
                font-size: 24rpx;
                color: #999999;
                font-weight: bold;
            }
        }

        .target-muscles {
            margin-bottom: 24rpx;

            .muscles-label {
                display: block;
                font-size: 26rpx;
                color: #666666;
                margin-bottom: 12rpx;
            }

            .muscles-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 12rpx;

                .muscle-tag {
                    background: #F5F5F5;
                    color: #333333;
                    font-size: 24rpx;
                    padding: 8rpx 20rpx;
                    border-radius: 16rpx;
                }
            }
        }

        .action-list {
            .action-item {
                background: #F9F9F9;
                border-radius: 16rpx;
                padding: 24rpx;
                margin-bottom: 16rpx;
                display: flex;
                justify-content: space-between;

                .action-main {
                    flex: 1;

                    .action-info {
                        display: flex;
                        align-items: center;
                        margin-bottom: 12rpx;

                        .action-name {
                            font-size: 28rpx;
                            font-weight: 600;
                            color: #333333;
                            margin-right: 16rpx;
                        }

                        .action-difficulty {
                            font-size: 22rpx;
                            padding: 6rpx 16rpx;
                            border-radius: 12rpx;
                            color: #FFFFFF;
                        }
                    }

                    .action-params {
                        display: flex;
                        gap: 24rpx;
                        margin-bottom: 8rpx;

                        .param-item {
                            font-size: 24rpx;
                            color: #666666;
                        }
                    }

                    .weight-display {
                        .weight-label {
                            font-size: 24rpx;
                            color: #999999;
                        }

                        .weight-values {
                            font-size: 24rpx;
                            color: #34C759;
                        }
                    }
                }

                .action-operations {
                    display: flex;
                    gap: 12rpx;
                    align-items: flex-start;

                    .op-btn {
                        width: 56rpx;
                        height: 56rpx;
                        border-radius: 28rpx;
                        display: flex;
                        justify-content: center;
                        align-items: center;

                        &.replace {
                            background: #E3F2FD;
                        }

                        &.delete {
                            background: #FFEBEE;
                        }

                        .op-icon {
                            font-size: 26rpx;
                        }
                    }
                }
            }

            .add-action-btn {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 24rpx;
                background: #F5F5F5;
                border-radius: 16rpx;
                border: 2rpx dashed #CCCCCC;

                .btn-icon {
                    font-size: 32rpx;
                    color: #667eea;
                    margin-right: 8rpx;
                }

                .btn-text {
                    font-size: 26rpx;
                    color: #667eea;
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
    gap: 20rpx;
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

        &.archive-btn {
            background: #F5F5F5;
            color: #666666;
        }

        &.edit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #FFFFFF;
        }
    }
}
</style>
