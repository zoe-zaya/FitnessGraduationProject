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
                    <view class="plan-left">
                        <view class="plan-name-row">
                            <text class="plan-name">{{ plan.plan_name }}</text>
                        </view>
                        <view class="plan-meta">
                            <view class="meta-item">
                                <text class="meta-label">目标</text>
                                <text class="meta-value" :class="plan.plan_type.toLowerCase()">{{ getPlanTypeLabel(plan.plan_type) }}</text>
                            </view>
                            <view class="meta-divider"></view>
                            <view class="meta-item">
                                <text class="meta-label">健身房</text>
                                <text class="meta-value">{{ plan.inventory_name }}</text>
                            </view>
                        </view>
                    </view>
                    <view class="plan-right">
                        <view class="action-btn edit" @click.stop="openRenameDialog(plan)">
                            <image src="@/static/edit.png" class="action-icon" mode="aspectFit" />
                        </view>
                        <view class="action-btn delete" @click.stop="confirmDelete(plan)">
                            <image src="@/static/delete.png" class="action-icon" mode="aspectFit" />
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

        <view class="dialog-mask" v-if="renameDialogShow" @click="closeRenameDialog">
            <view class="dialog-content" @click.stop>
                <text class="dialog-title">修改计划名称</text>
                <view class="form-item">
                    <text class="form-label">计划名称</text>
                    <textarea
                        v-model="renameForm.plan_name"
                        placeholder="请输入新的计划名称"
                        class="form-input"
                        maxlength="20"
                    />
                </view>
                <view class="dialog-buttons">
                    <button class="btn-cancel" @click="closeRenameDialog">取消</button>
                    <button class="btn-confirm" @click="handleRename" :loading="renameLoading">确认</button>
                </view>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2 } from '@/utils/constants'
import CustomModal from '@/components/CustomModal.vue'

const planList = ref([])
const loading = ref(false)
const deleteModalShow = ref(false)
const deleteModalContent = ref('')
const pendingDeletePlanId = ref('')
const renameDialogShow = ref(false)
const renameLoading = ref(false)
const renameForm = ref({
    plan_id: '',
    plan_name: ''
})

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

const navigateToGenerate = () => {
    uni.navigateTo({ url: '/pages/plan/generate-plan' })
}

const viewPlanDetail = (plan) => {
    uni.navigateTo({ url: `/pages/plan/plan-detail?plan_id=${plan.plan_id}` })
}

const openRenameDialog = (plan) => {
    renameForm.value = {
        plan_id: plan.plan_id,
        plan_name: plan.plan_name
    }
    renameDialogShow.value = true
}

const closeRenameDialog = () => {
    renameDialogShow.value = false
    renameForm.value = {
        plan_id: '',
        plan_name: ''
    }
}

const handleRename = async () => {
    if (!renameForm.value.plan_name || renameForm.value.plan_name.trim().length === 0) {
        uni.showToast({ title: '请输入计划名称', icon: 'none' })
        return
    }
    renameLoading.value = true
    try {
        await request.put(`${API_V2.PLAN_UPDATE}/${renameForm.value.plan_id}`, {
            plan_name: renameForm.value.plan_name.trim()
        })
        uni.showToast({ title: '修改成功', icon: 'success' })
        closeRenameDialog()
        await loadPlanList()
    } catch (error) {
        console.error('修改名称失败:', error)
        uni.showToast({ title: '修改失败', icon: 'none' })
    } finally {
        renameLoading.value = false
    }
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
    background-color: #ffffff;
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
        padding: $size-4 $size-4 $size-4 $size-5;
        margin-bottom: $size-3;
        box-shadow: 0 2rpx 10rpx $border-shadow;
        border: 2rpx solid $fitness-border;
        display: flex;
        align-items: center;
        transition: all 0.2s ease;

        &:active {
            transform: scale(0.98);
            box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.08);
        }

        .plan-left {
            flex: 1;
            min-width: 0;
            margin-right: $size-3;

            .plan-name-row {
                margin-bottom: $size-2;

                .plan-name {
                    font-size: $size-4;
                    font-weight: 700;
                    color: $uni-primary;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    line-height: 1.3;
                }
            }

            .plan-meta {
                display: flex;
                align-items: center;

                .meta-item {
                    display: flex;
                    align-items: center;
                    gap: 6rpx;

                    .meta-label {
                        font-size: 22rpx;
                        color: $color-secondory;
                        font-weight: 525;
                    }

                    .meta-value {
                        font-size: 22rpx;
                        color: $color-input;
                        font-weight: 700;

                        &.fat_loss {
                            color: $color-input;
                        }

                        &.muscle_gain {
                            color: $color-input;
                        }
                    }
                }

                .meta-divider {
                    width: 2rpx;
                    height: 20rpx;
                    background: $fitness-border;
                    margin: 0 $size-2;
                }
            }
        }

        .plan-right {
            display: flex;
            align-items: center;
            gap: $size-2;
            flex-shrink: 0;

            .action-btn {
                width: 64rpx;
                height: 64rpx;
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                transition: all 0.15s ease;

                &:active {
                    transform: scale(0.85);
                }

                &.edit {
                    background: $fitness-secondary;

                    .action-icon {
                        width: 32rpx;
                        height: 32rpx;
                    }
                }

                &.delete {
                    background: $fitness-secondary;

                    .action-icon {
                        width: 32rpx;
                        height: 32rpx;
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

.dialog-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: end;
    z-index: 999;

    .dialog-content {
        background: $fitness-primary;
        border-radius: $size-4 $size-4 0 0;
        padding: $size-5;
        width: stretch;
        box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.15);

        .dialog-title {
            display: block;
            font-size: $size-5;
            font-weight: 700;
            text-align: center;
            margin-bottom: $size-4;
            color: $color-input;
        }

        .form-item {
            margin-bottom: $size-4;

            .form-label {
                font-weight: 700;
                font-size: 24rpx;
                display: block;
                margin-left: $size-1;
                color: $color-secondory;
                margin-bottom: $size-2;
            }

            .form-input {
                width: 100%;
                background: $fitness-secondary;
                border: 2rpx solid $fitness-border;
                border-radius: $size-4;
                padding: 20rpx 30rpx;
                font-size: $size-4;
                font-family: Manrope;
                color: $color-input;
                box-sizing: border-box;
                height: 96rpx;
            }
        }

        .dialog-buttons {
            display: flex;
            gap: $size-3;
            margin-top: $size-5;

            .btn-cancel, .btn-confirm {
                flex: 1;
                height: 96rpx;
                border-radius: $size-4;
                font-size: $size-5;
                font-weight: 700;
                display: flex;
                align-content: center;
                align-items: center;
                justify-content: center;
                border: none;
            }

            .btn-cancel {
                background: transparent;
                color: $color-primary;
                border: 2rpx solid $color-primary;
            }

            .btn-cancel:after {
                border: none;
            }

            .btn-confirm {
                background: $button-bg2;
                color: $fitness-primary;
            }
        }
    }
}
</style>
