<template>
    <view class="container">
        <view class="header">
            <view class="header-top">
                <text class="back-btn" @click="goBack">←</text>
                <text class="header-title">编辑计划</text>
            </view>
        </view>

        <view class="content">
            <view class="plan-info-section">
                <view class="section-card">
                    <text class="section-title">📋 计划信息</text>

                    <view class="form-item">
                        <text class="form-label">计划名称</text>
                        <input
                            v-model="planInfo.plan_name"
                            type="text"
                            placeholder="请输入计划名称"
                            class="form-input"
                            maxlength="50"
                        />
                    </view>
                </view>
            </view>

            <view class="sessions-section">
                <view
                    class="session-card"
                    v-for="(session, sIndex) in planInfo.sessions"
                    :key="session.session_id"
                >
                    <view class="session-header" :style="{ borderLeftColor: SESSION_TYPE_MAP[session.session_type]?.color }">
                        <view class="session-info">
                            <text class="session-icon">{{ SESSION_TYPE_MAP[session.session_type]?.icon }}</text>
                            <text class="session-name">{{ SESSION_TYPE_MAP[session.session_type]?.label }}</text>
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
                        >
                            <view class="action-header">
                                <text class="action-name">{{ action.action_name }}</text>
                                <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                                    {{ action.difficulty_level }}
                                </text>
                            </view>

                            <view class="action-params" v-if="action.sets">
                                <view class="param-row">
                                    <text class="param-label">组数：</text>
                                    <input
                                        v-model="action.sets"
                                        type="number"
                                        class="param-input"
                                        @blur="updateActionItem(action)"
                                        min="1"
                                        max="6"
                                    />
                                </view>
                                <view class="param-row">
                                    <text class="param-label">次数/组：</text>
                                    <input
                                        v-model="action.reps_per_set"
                                        type="number"
                                        class="param-input"
                                        @blur="updateActionItem(action)"
                                        min="5"
                                        max="20"
                                    />
                                </view>
                                <view class="param-row">
                                    <text class="param-label">休息（秒）：</text>
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

                            <view class="action-params" v-else-if="action.duration_minutes">
                                <view class="param-row">
                                    <text class="param-label">时长（分钟）：</text>
                                    <input
                                        v-model="action.duration_minutes"
                                        type="number"
                                        class="param-input"
                                        @blur="updateActionItem(action)"
                                        min="1"
                                    />
                                </view>
                            </view>

                            <view class="action-footer">
                                <view class="action-btn replace" @click="replaceAction(action, session)">
                                    <text class="btn-icon">🔄</text>
                                </view>
                                <view class="action-btn delete" @click="confirmDeleteAction(action)">
                                    <text class="btn-icon">🗑️</text>
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
            <button class="btn cancel-btn" @click="goBack">
                <text>取消</text>
            </button>
            <button class="btn save-btn" @click="saveChanges" :loading="saving">
                <text>{{ saving ? '保存中...' : '保存修改' }}</text>
            </button>
        </view>
    </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SESSION_TYPE_MAP, DIFFICULTY_MAP } from '@/utils/constants'

const planId = ref('')
const saving = ref(false)
const planInfo = ref({
    plan_name: '',
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

const getDifficultyColor = (level) => {
    return DIFFICULTY_MAP[level]?.color || '#999999'
}

const updateActionItem = async (action) => {
    try {
        const updateData = {}

        if (action.sets !== undefined) {
            updateData.sets = parseInt(action.sets) || 4
            updateData.reps_per_set = parseInt(action.reps_per_set) || 12
            updateData.rest_seconds_default = parseInt(action.rest_seconds_default) || 60
        } else if (action.duration_minutes !== undefined) {
            updateData.duration_minutes = parseInt(action.duration_minutes) || 30
        }

        await request.put(`${API_V2.PLAN_UPDATE_ACTION}/${planId.value}/${action.item_id}`, updateData)
    } catch (error) {
        console.error('更新失败:', error)
        uni.showToast({ title: '更新失败', icon: 'none' })
    }
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
.container {
    min-height: 100vh;
    background: #F5F5F5;
    padding-bottom: 140rpx;
}

.header {
    background: #FFFFFF;
    padding: 40rpx;

    .header-top {
        display: flex;
        align-items: center;

        .back-btn {
            font-size: 40rpx;
            color: #333333;
            margin-right: 20rpx;
        }

        .header-title {
            font-size: 36rpx;
            font-weight: bold;
            color: #333333;
        }
    }
}

.content {
    padding: 30rpx 40rpx;
}

.plan-info-section {
    margin-bottom: 30rpx;

    .section-card {
        background: #FFFFFF;
        border-radius: 24rpx;
        padding: 32rpx;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);

        .section-title {
            display: block;
            font-size: 30rpx;
            font-weight: bold;
            color: #333333;
            margin-bottom: 24rpx;
        }

        .form-item {
            .form-label {
                display: block;
                font-size: 28rpx;
                font-weight: 600;
                color: #333333;
                margin-bottom: 12rpx;
            }

            .form-input {
                width: 100%;
                height: 88rpx;
                background: #F5F5F5;
                border-radius: 16rpx;
                padding: 0 30rpx;
                font-size: 28rpx;
                box-sizing: border-box;
            }
        }
    }
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
                    margin-right: 12rpx;
                }

                .session-name {
                    font-size: 30rpx;
                    font-weight: bold;
                    color: #333333;
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

                .action-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 16rpx;

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
                    margin-bottom: 16rpx;

                    .param-row {
                        display: flex;
                        align-items: center;
                        margin-bottom: 12rpx;

                        &:last-child {
                            margin-bottom: 0;
                        }

                        .param-label {
                            font-size: 24rpx;
                            color: #666666;
                            width: 140rpx;
                        }

                        .param-input {
                            flex: 1;
                            height: 64rpx;
                            background: #FFFFFF;
                            border: 1rpx solid #E5E5E5;
                            border-radius: 12rpx;
                            padding: 0 20rpx;
                            font-size: 24rpx;
                            text-align: center;
                        }
                    }
                }

                .action-footer {
                    display: flex;
                    gap: 12rpx;

                    .action-btn {
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

                        .btn-icon {
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

        &.cancel-btn {
            background: #F5F5F5;
            color: #666666;
        }

        &.save-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #FFFFFF;
        }
    }
}
</style>
