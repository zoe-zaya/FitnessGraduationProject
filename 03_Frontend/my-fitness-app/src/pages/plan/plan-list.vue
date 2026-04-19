<template>
    <view class="container">
        <view class="header">
            <text class="title">我的训练计划</text>
            <view class="generate-btn" @click="navigateToGenerate">
                <text class="btn-icon">+</text>
                <text class="btn-text">生成计划</text>
            </view>
        </view>

        <view class="tab-bar">
            <view
                class="tab-item"
                :class="{ active: currentTab === 'ACTIVE' }"
                @click="switchTab('ACTIVE')"
            >
                <text class="tab-text">进行中</text>
            </view>
            <view
                class="tab-item"
                :class="{ active: currentTab === 'ARCHIVED' }"
                @click="switchTab('ARCHIVED')"
            >
                <text class="tab-text">已归档</text>
            </view>
        </view>

        <view class="plan-list" v-if="filteredPlanList.length > 0">
            <view
                class="plan-card"
                v-for="(plan, index) in filteredPlanList"
                :key="plan.plan_id"
                @click="viewPlanDetail(plan)"
            >
                <view class="plan-header">
                    <view class="plan-title-row">
                        <text class="plan-name">{{ plan.plan_name }}</text>
                        <view class="plan-type-badge" :class="plan.plan_type.toLowerCase()">
                            {{ plan.plan_type === 'FAT_LOSS' ? '减脂' : '增肌' }}
                        </view>
                    </view>
                    <view class="plan-status" :class="plan.status.toLowerCase()">
                        {{ plan.status === 'ACTIVE' ? '进行中' : '已归档' }}
                    </view>
                </view>

                <view class="plan-meta">
                    <view class="meta-item" v-if="plan.scheme_type">
                        <text class="meta-icon">📋</text>
                        <text class="meta-text">{{ getSchemeName(plan.scheme_type) }}</text>
                    </view>
                    <view class="meta-item">
                        <text class="meta-icon">📅</text>
                        <text class="meta-text">{{ plan.cycle_rule }}</text>
                    </view>
                    <view class="meta-item">
                        <text class="meta-icon">🏢</text>
                        <text class="meta-text">{{ plan.inventory_name }}</text>
                    </view>
                </view>

                <view class="plan-footer">
                    <text class="create-time">创建于 {{ formatDate(plan.create_time) }}</text>
                    <view class="action-buttons">
                        <view class="action-btn schedule" @click.stop="viewSchedule(plan)">
                            <text class="btn-icon">📅</text>
                        </view>
                        <view class="action-btn edit" @click.stop="editPlan(plan)">
                            <text class="btn-icon">✏️</text>
                        </view>
                        <view class="action-btn delete" @click.stop="confirmDelete(plan)">
                            <text class="btn-icon">🗑️</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>

        <view class="empty-state" v-else>
            <image src="/static/empty-plan.png" class="empty-image" mode="aspectFit" />
            <text class="empty-text">暂无{{ currentTab === 'ACTIVE' ? '进行中' : '已归档' }}的训练计划</text>
            <text class="empty-subtext" v-if="currentTab === 'ACTIVE'">点击下方按钮生成您的第一个训练计划</text>
            <button class="generate-plan-btn" @click="navigateToGenerate" v-if="currentTab === 'ACTIVE'">
                生成训练计划
            </button>
        </view>
    </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SCHEME_TYPES } from '@/utils/constants'

const planList = ref([])
const currentTab = ref('ACTIVE')
const loading = ref(false)

onShow(async () => {
    await loadPlanList()
})

const filteredPlanList = computed(() => {
    return planList.value.filter(plan => plan.status === currentTab.value)
})

const loadPlanList = async () => {
    loading.value = true
    try {
        const res = await request.get(API_V2.PLAN_LIST)
        planList.value = res || []
    } catch (error) {
        console.error('加载计划列表失败:', error)
        uni.showToast({ title: '加载失败', icon: 'none' })
    } finally {
        loading.value = false
    }
}

const switchTab = (tab) => {
    currentTab.value = tab
}

const getSchemeName = (schemeType) => {
    const scheme = SCHEME_TYPES.find(s => s.value === schemeType)
    return scheme ? scheme.label.split('（')[0] : schemeType
}

const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const navigateToGenerate = () => {
    uni.navigateTo({ url: '/pages/plan/generate-plan' })
}

const viewPlanDetail = (plan) => {
    uni.navigateTo({ url: `/pages/plan/plan-detail?plan_id=${plan.plan_id}` })
}

const viewSchedule = (plan) => {
    uni.navigateTo({ url: `/pages/plan/weekly-schedule?plan_id=${plan.plan_id}` })
}

const editPlan = (plan) => {
    uni.navigateTo({ url: `/pages/plan/plan-edit?plan_id=${plan.plan_id}` })
}

const confirmDelete = (plan) => {
    uni.showModal({
        title: '提示',
        content: `确定要删除"${plan.plan_name}"吗？删除后无法恢复。`,
        success: async (res) => {
            if (res.confirm) {
                await deletePlan(plan.plan_id)
            }
        }
    })
}

const deletePlan = async (planId) => {
    try {
        await request.delete(`${API_V2.PLAN_DELETE}/${planId}`)
        uni.showToast({ title: '删除成功', icon: 'success' })
        await loadPlanList()
    } catch (error) {
        console.error('删除失败:', error)
        uni.showToast({ title: '删除失败', icon: 'none' })
    }
}
</script>

<style lang="scss" scoped>
.container {
    min-height: 100vh;
    background: #F5F5F5;
    padding: 0 0 40rpx;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx 40rpx;
    background: #FFFFFF;
    border-bottom: 1rpx solid #E5E5E5;

    .title {
        font-size: 36rpx;
        font-weight: bold;
        color: #333333;
    }

    .generate-btn {
        display: flex;
        align-items: center;
        padding: 12rpx 24rpx;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 32rpx;

        .btn-icon {
            font-size: 32rpx;
            color: #FFFFFF;
            margin-right: 8rpx;
        }

        .btn-text {
            font-size: 26rpx;
            color: #FFFFFF;
        }
    }
}

.tab-bar {
    display: flex;
    background: #FFFFFF;
    padding: 0 40rpx;

    .tab-item {
        flex: 1;
        padding: 24rpx 0;
        text-align: center;
        border-bottom: 4rpx solid transparent;
        transition: all 0.3s;

        &.active {
            border-bottom-color: #667eea;

            .tab-text {
                color: #667eea;
                font-weight: 600;
            }
        }

        .tab-text {
            font-size: 28rpx;
            color: #666666;
        }
    }
}

.plan-list {
    padding: 30rpx 40rpx;

    .plan-card {
        background: #FFFFFF;
        border-radius: 24rpx;
        padding: 32rpx;
        margin-bottom: 24rpx;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);

        .plan-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 24rpx;

            .plan-title-row {
                display: flex;
                align-items: center;
                flex: 1;

                .plan-name {
                    font-size: 32rpx;
                    font-weight: bold;
                    color: #333333;
                    margin-right: 16rpx;
                }

                .plan-type-badge {
                    font-size: 22rpx;
                    padding: 6rpx 16rpx;
                    border-radius: 12rpx;
                    color: #FFFFFF;

                    &.fat_loss {
                        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
                    }

                    &.muscle_gain {
                        background: linear-gradient(135deg, #667eea, #764ba2);
                    }
                }
            }

            .plan-status {
                font-size: 24rpx;
                padding: 8rpx 20rpx;
                border-radius: 20rpx;

                &.active {
                    background: #E8F5E9;
                    color: #34C759;
                }

                &.archived {
                    background: #F5F5F5;
                    color: #999999;
                }
            }
        }

        .plan-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 20rpx;
            margin-bottom: 24rpx;

            .meta-item {
                display: flex;
                align-items: center;

                .meta-icon {
                    font-size: 28rpx;
                    margin-right: 8rpx;
                }

                .meta-text {
                    font-size: 26rpx;
                    color: #666666;
                }
            }
        }

        .plan-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 24rpx;
            border-top: 1rpx solid #F5F5F5;

            .create-time {
                font-size: 24rpx;
                color: #999999;
            }

            .action-buttons {
                display: flex;
                gap: 16rpx;

                .action-btn {
                    width: 60rpx;
                    height: 60rpx;
                    border-radius: 30rpx;
                    display: flex;
                    justify-content: center;
                    align-items: center;

                    &.schedule {
                        background: #E3F2FD;
                    }

                    &.edit {
                        background: #FFF3E0;
                    }

                    &.delete {
                        background: #FFEBEE;
                    }

                    .btn-icon {
                        font-size: 28rpx;
                    }
                }
            }
        }
    }
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100rpx 40rpx;

    .empty-image {
        width: 300rpx;
        height: 300rpx;
        margin-bottom: 40rpx;
    }

    .empty-text {
        font-size: 32rpx;
        color: #333333;
        font-weight: 600;
        margin-bottom: 16rpx;
    }

    .empty-subtext {
        font-size: 28rpx;
        color: #666666;
        margin-bottom: 40rpx;
    }

    .generate-plan-btn {
        width: 300rpx;
        height: 88rpx;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #FFFFFF;
        font-size: 30rpx;
        font-weight: 600;
        border-radius: 44rpx;
        border: none;
    }
}
</style>
