<template>
    <view class="container">
        <view class="loading-wrapper" v-if="loading">
            <view class="loading-spinner"></view>
            <text class="loading-text">加载中...</text>
        </view>

        <template v-else>
            <view class="plan-list" v-if="planList.length > 0">
                <view
                    class="plan-card"
                    v-for="plan in planList"
                    :key="plan.plan_id"
                    @click="viewPlanDetail(plan)"
                >
                    <view class="plan-header">
                        <view class="plan-title-row">
                            <text class="plan-name">{{ plan.plan_name }}</text>
                            <view class="plan-type-badge" :class="plan.plan_type.toLowerCase()">
                                {{ getPlanTypeLabel(plan.plan_type) }}
                            </view>
                        </view>
                        <view class="plan-status" :class="plan.status.toLowerCase()">
                            {{ getStatusLabel(plan.status) }}
                        </view>
                    </view>

                    <view class="plan-info-tags">
                        <view class="info-tag" v-if="plan.scheme_type">
                            <uni-icons type="bars" size="14" color="#d8696a"></uni-icons>
                            <text class="tag-text" :class="getDifficultyClass(plan.scheme_type)">{{ getDifficultyLabel(plan.scheme_type) }}</text>
                        </view>
                        <view class="info-tag" v-else>
                            <uni-icons type="fire" size="14" color="#d8696a"></uni-icons>
                            <text class="tag-text">有氧+力量</text>
                        </view>
                        <view class="info-tag" v-if="plan.cycle_rule">
                            <uni-icons type="reload" size="14" color="#8E8E93"></uni-icons>
                            <text class="tag-text">{{ plan.cycle_rule }}</text>
                        </view>
                        <view class="info-tag">
                            <uni-icons type="home" size="14" color="#8E8E93"></uni-icons>
                            <text class="tag-text">{{ plan.inventory_name }}</text>
                        </view>
                    </view>

                    <view class="plan-footer">
                        <text class="create-time">创建于 {{ formatDate(plan.create_time) }}</text>
                        <view class="action-buttons">
                            <view class="action-btn edit" @click.stop="editPlan(plan)">
                                <image src="@/static/edit.png" class="action-icon" mode="aspectFit" />
                            </view>
                            <view class="action-btn delete" @click.stop="confirmDelete(plan)">
                                <image src="@/static/delete.png" class="action-icon" mode="aspectFit" />
                            </view>
                        </view>
                    </view>
                </view>
            </view>

            <view class="empty-state" v-else>
                <image src="/static/empty-data.png" class="empty-image" mode="aspectFit" />
                <text class="empty-text">暂无训练计划</text>
                <text class="empty-subtext">点击右下角按钮生成您的第一个训练计划</text>
            </view>
        </template>

        <view class="fab-btn" @click="navigateToGenerate">
            <image src="/static/add.png" class="fab-icon" mode="aspectFit" />
        </view>

        <CustomModal
            :show="deleteModalShow"
            title="删除计划"
            :content="deleteModalContent"
            confirmText="删除"
            cancelText="取消"
            confirmColor="#db0f00"
            @confirm="handleDeleteConfirm"
            @cancel="handleDeleteCancel"
        />
    </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SCHEME_TYPES } from '@/utils/constants'
import CustomModal from '@/components/CustomModal.vue'

const planList = ref([])
const loading = ref(false)
const deleteModalShow = ref(false)
const deleteModalContent = ref('')
const pendingDeletePlanId = ref('')

const DIFFICULTY_MAP = {
    'ONE_SPLIT': { label: '初级', class: 'difficulty-beginner' },
    'TWO_SPLIT': { label: '中级', class: 'difficulty-intermediate' },
    'THREE_SPLIT': { label: '中高级', class: 'difficulty-advanced' },
    'FOUR_SPLIT': { label: '高级', class: 'difficulty-expert' }
}

onShow(async () => {
    await loadPlanList()
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

const getPlanTypeLabel = (planType) => {
    return planType === 'FAT_LOSS' ? '减脂' : '增肌'
}

const getStatusLabel = (status) => {
    const map = {
        'ACTIVE': '进行中',
        'active': '进行中',
        'ARCHIVED': '已归档',
        'archived': '已归档'
    }
    return map[status] || status
}

const getDifficultyLabel = (schemeType) => {
    const diff = DIFFICULTY_MAP[schemeType]
    if (diff) return diff.label
    const scheme = SCHEME_TYPES.find(s => s.value === schemeType)
    return scheme ? scheme.label.split('（')[0] : schemeType
}

const getDifficultyClass = (schemeType) => {
    const diff = DIFFICULTY_MAP[schemeType]
    return diff ? diff.class : ''
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

const editPlan = (plan) => {
    uni.navigateTo({ url: `/pages/plan/plan-edit?plan_id=${plan.plan_id}` })
}

const confirmDelete = (plan) => {
    pendingDeletePlanId.value = plan.plan_id
    deleteModalContent.value = `确定要删除"${plan.plan_name}"吗？删除后无法恢复。`
    deleteModalShow.value = true
}

const handleDeleteConfirm = async () => {
    deleteModalShow.value = false
    if (pendingDeletePlanId.value) {
        await deletePlan(pendingDeletePlanId.value)
        pendingDeletePlanId.value = ''
    }
}

const handleDeleteCancel = () => {
    deleteModalShow.value = false
    pendingDeletePlanId.value = ''
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
@import '@/uni.scss';

.container {
    min-height: 100vh;
    background-color: $fitness-secondary;
    padding: 0 0 $size-5;
    font-family: Manrope;
}

.loading-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 200rpx 0;

    .loading-spinner {
        width: $size-8;
        height: $size-8;
        border: 6rpx solid $fitness-border;
        border-top-color: $color-primary;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    .loading-text {
        margin-top: $size-3;
        font-size: $size-3;
        color: $color-secondory;
        font-weight: 525;
    }
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.plan-list {
    padding: $size-3 $size-5;

    .plan-card {
        background: $glass-bg1;
        border-radius: $size-4;
        padding: $size-4;
        margin-bottom: $size-3;
        box-shadow: 0 2rpx 10rpx $border-shadow;
        border: 2rpx solid $fitness-border;
        transition: all 0.2s ease;

        &:active {
            transform: scale(0.98);
            box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.08);
        }

        .plan-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: $size-3;

            .plan-title-row {
                display: flex;
                align-items: center;
                flex: 1;
                margin-right: $size-2;

                .plan-name {
                    font-size: $size-4;
                    font-weight: 700;
                    color: $color-input;
                    margin-right: $size-2;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    max-width: 360rpx;
                    line-height: 1.2;
                }

                .plan-type-badge {
                    font-size: $size-3;
                    padding: $size-1 $size-2;
                    border-radius: $size-2;
                    color: $fitness-primary;
                    font-weight: 700;
                    flex-shrink: 0;

                    &.fat_loss {
                        background: rgba(160, 62, 64, 0.12);
                        color: $color-primary;
                    }

                    &.muscle_gain {
                        background: $color-primary-light;
                        color: $color-primary;
                    }
                }
            }

            .plan-status {
                font-size: $size-3;
                padding: $size-1 $size-3;
                border-radius: $size-3;
                font-weight: 700;
                flex-shrink: 0;

                &.active {
                    background: $uni-success-bg;
                    color: $uni-success;
                }

                &.archived {
                    background: $fitness-secondary;
                    color: $color-secondory;
                }
            }
        }

        .plan-info-tags {
            display: flex;
            flex-wrap: wrap;
            gap: $size-2;
            margin-bottom: $size-3;
            padding: $size-3;
            background: $fitness-secondary;
            border-radius: $size-4;

            .info-tag {
                display: flex;
                align-items: center;
                gap: $size-1;
                padding: $size-1 $size-2;
                background: $fitness-primary;
                border-radius: $size-2;
                border: 1rpx solid $fitness-border;

                .tag-text {
                    font-size: $size-3;
                    color: $color-input;
                    font-weight: 700;
                    line-height: 1.4;

                    &.difficulty-beginner {
                        color: $uni-success;
                    }

                    &.difficulty-intermediate {
                        color: $uni-warning;
                    }

                    &.difficulty-advanced {
                        color: $color-primary;
                    }

                    &.difficulty-expert {
                        color: $uni-error;
                    }
                }
            }
        }

        .plan-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: $size-3;
            border-top: 1rpx solid $fitness-border;

            .create-time {
                font-size: $size-3;
                color: $color-secondory;
                font-weight: 525;
            }

            .action-buttons {
                display: flex;
                gap: $size-3;

                .action-btn {
                    width: $size-7;
                    height: $size-7;
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    transition: all 0.15s ease;

                    &:active {
                        transform: scale(0.9);
                    }

                    &.edit {
                        background: $uni-warning-bg;

                        .action-icon {
                            width: 36rpx;
                            height: 36rpx;
                        }
                    }

                    &.delete {
                        background: $uni-error-bg;

                        .action-icon {
                            width: 36rpx;
                            height: 36rpx;
                        }
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
    padding: 160rpx $size-5 100rpx;

    .empty-image {
        width: 300rpx;
        height: 300rpx;
        margin-bottom: $size-5;
    }

    .empty-text {
        font-size: $size-4;
        color: $color-input;
        font-weight: 700;
        margin-bottom: $size-2;
        line-height: 1.3;
    }

    .empty-subtext {
        font-size: $size-3;
        color: $color-secondory;
        font-weight: 525;
        line-height: 1.4;
    }
}

.fab-btn {
    position: fixed;
    right: $size-5;
    bottom: 120rpx;
    width: $size-12;
    height: $size-12;
    border-radius: 50%;
    background: $button-bg2;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 8rpx 24rpx rgba(216, 105, 106, 0.4);
    z-index: 200;
    transition: all 0.2s ease;

    &:active {
        transform: scale(0.9);
        box-shadow: 0 4rpx 12rpx rgba(216, 105, 106, 0.3);
    }

    .fab-icon {
        width: $size-6;
        height: $size-6;
    }
}
</style>
