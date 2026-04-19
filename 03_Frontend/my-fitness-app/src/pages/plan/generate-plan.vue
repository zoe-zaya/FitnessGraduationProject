<template>
    <view class="container">
        <view class="header">
            <text class="header-title">生成训练计划</text>
        </view>

        <view class="content">
            <view class="step-section">
                <view class="step-indicator">
                    <view class="step-dot" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">1</view>
                    <view class="step-line" :class="{ active: currentStep > 1 }"></view>
                    <view class="step-dot" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">2</view>
                    <view class="step-line" :class="{ active: currentStep > 2 }"></view>
                    <view class="step-dot" :class="{ active: currentStep >= 3 }">3</view>
                </view>
                <view class="step-labels">
                    <text class="step-label" :class="{ active: currentStep >= 1 }">选择类型</text>
                    <text class="step-label" :class="{ active: currentStep >= 2 }">选择方案</text>
                    <text class="step-label" :class="{ active: currentStep >= 3 }">选择健身房</text>
                </view>
            </view>

            <view class="form-section">
                <view class="step-content" v-show="currentStep === 1">
                    <view class="section-title">
                        <text class="title-icon">🎯</text>
                        <text class="title-text">请选择您的健身目标</text>
                    </view>

                    <view class="plan-type-cards">
                        <view
                            class="plan-type-card"
                            :class="{ selected: selectedPlanType === 'FAT_LOSS' }"
                            @click="selectPlanType('FAT_LOSS')"
                        >
                            <view class="card-icon">🔥</view>
                            <view class="card-content">
                                <text class="card-title">减脂计划</text>
                                <text class="card-desc">有氧+力量组合，高效燃脂</text>
                            </view>
                            <view class="card-check" v-if="selectedPlanType === 'FAT_LOSS'">✓</view>
                        </view>

                        <view
                            class="plan-type-card"
                            :class="{ selected: selectedPlanType === 'MUSCLE_GAIN' }"
                            @click="selectPlanType('MUSCLE_GAIN')"
                        >
                            <view class="card-icon">💪</view>
                            <view class="card-content">
                                <text class="card-title">增肌计划</text>
                                <text class="card-desc">力量训练为主，肌肉增长</text>
                            </view>
                            <view class="card-check" v-if="selectedPlanType === 'MUSCLE_GAIN'">✓</view>
                        </view>
                    </view>
                </view>

                <view class="step-content" v-show="currentStep === 2 && selectedPlanType === 'MUSCLE_GAIN'">
                    <view class="section-title">
                        <text class="title-icon">📋</text>
                        <text class="title-text">请选择分化方案</text>
                    </view>

                    <view class="scheme-cards">
                        <view
                            class="scheme-card"
                            v-for="scheme in SCHEME_TYPES"
                            :key="scheme.value"
                            :class="{ selected: selectedSchemeType === scheme.value }"
                            @click="selectSchemeType(scheme.value)"
                        >
                            <view class="scheme-header">
                                <text class="scheme-name">{{ scheme.label }}</text>
                                <view class="scheme-check" v-if="selectedSchemeType === scheme.value">✓</view>
                            </view>
                            <text class="scheme-desc">{{ scheme.description }}</text>
                        </view>
                    </view>
                </view>

                <view class="step-content" v-show="currentStep === 2 && selectedPlanType === 'FAT_LOSS'">
                    <view class="section-title">
                        <text class="title-icon">🏃</text>
                        <text class="title-text">减脂计划说明</text>
                    </view>

                    <view class="info-card">
                        <view class="info-row">
                            <text class="info-icon">🔥</text>
                            <text class="info-text">热身激活 → 力量训练 → 有氧训练 → 拉伸放松</text>
                        </view>
                        <view class="info-row">
                            <text class="info-icon">⏱️</text>
                            <text class="info-text">每次训练约 45-60 分钟</text>
                        </view>
                        <view class="info-row">
                            <text class="info-icon">📅</text>
                            <text class="info-text">练 3 休 1 循环</text>
                        </view>
                        <view class="info-row">
                            <text class="info-icon">🏋️</text>
                            <text class="info-text">4 个力量动作 + 30 分钟有氧</text>
                        </view>
                    </view>
                </view>

                <view class="step-content" v-show="currentStep === 3">
                    <view class="section-title">
                        <text class="title-icon">🏢</text>
                        <text class="title-text">请选择健身房</text>
                    </view>

                    <view class="gym-list" v-if="gymList.length > 0">
                        <view
                            class="gym-card"
                            v-for="(gym, index) in gymList"
                            :key="gym.inventory_id"
                            :class="{ selected: selectedGymIndex === index }"
                            @click="selectGym(index)"
                        >
                            <view class="gym-info">
                                <text class="gym-name">{{ gym.location_tag }}</text>
                                <text class="gym-equipment">器材数量: {{ gym.equipment_count || 0 }}</text>
                            </view>
                            <view class="gym-check" v-if="selectedGymIndex === index">✓</view>
                        </view>
                    </view>

                    <view class="empty-gym" v-else>
                        <text class="empty-text">暂无可用健身房</text>
                        <text class="empty-tip">请先添加健身房和器材</text>
                    </view>
                </view>
            </view>

            <view class="action-section">
                <button class="btn prev-btn" v-if="currentStep > 1" @click="prevStep">
                    <text>上一步</text>
                </button>
                <button
                    class="btn next-btn"
                    v-if="currentStep < 3"
                    @click="nextStep"
                    :disabled="!canNext"
                >
                    <text>下一步</text>
                </button>
                <button
                    class="btn generate-btn"
                    v-if="currentStep === 3"
                    @click="generatePlan"
                    :loading="loading"
                    :disabled="!canGenerate || loading"
                >
                    <text>{{ loading ? '生成中...' : '生成计划' }}</text>
                </button>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import { API_V2, PLAN_TYPES, SCHEME_TYPES } from '@/utils/constants'

const userStore = useUserStore()
const loading = ref(false)
const currentStep = ref(1)

const selectedPlanType = ref('')
const selectedSchemeType = ref('')
const selectedGymIndex = ref(-1)
const gymList = ref([])

onShow(async () => {
    await loadGymList()
})

const canNext = computed(() => {
    if (currentStep.value === 1 && selectedPlanType.value) return true
    if (currentStep.value === 2) {
        if (selectedPlanType.value === 'MUSCLE_GAIN') {
            return !!selectedSchemeType.value
        }
        return true
    }
    return false
})

const canGenerate = computed(() => {
    return selectedGymIndex.value >= 0
})

const selectPlanType = (type) => {
    selectedPlanType.value = type
    if (type === 'FAT_LOSS') {
        currentStep.value = 2
    }
}

const selectSchemeType = (type) => {
    selectedSchemeType.value = type
}

const selectGym = (index) => {
    selectedGymIndex.value = index
}

const loadGymList = async () => {
    try {
        const res = await request.get(API_V2.PLAN_LIST)
        const gymRes = await request.get('/api/equipment/getAllGym')
        gymList.value = gymRes || []

        if (gymList.value.length > 0) {
            const inventoryRes = await request.get('/api/equipment/getAllGym')
            gymList.value = inventoryRes.map(gym => ({
                ...gym,
                equipment_count: gym.equipment_count || 0
            }))
        }
    } catch (error) {
        console.error('加载健身房列表失败:', error)
    }
}

const nextStep = () => {
    if (currentStep.value === 1 && selectedPlanType.value === 'MUSCLE_GAIN') {
        currentStep.value = 2
    } else if (currentStep.value === 1 && selectedPlanType.value === 'FAT_LOSS') {
        currentStep.value = 3
    } else if (currentStep.value === 2) {
        currentStep.value = 3
    }
}

const prevStep = () => {
    if (currentStep.value > 1) {
        currentStep.value--
    }
}

const generatePlan = async () => {
    if (!canGenerate.value) {
        uni.showToast({ title: '请选择健身房', icon: 'none' })
        return
    }

    loading.value = true

    try {
        const selectedGym = gymList.value[selectedGymIndex.value]
        const requestData = {
            inventory_id: selectedGym.inventory_id,
            plan_type: selectedPlanType.value
        }

        if (selectedPlanType.value === 'MUSCLE_GAIN') {
            requestData.scheme_type = selectedSchemeType.value
        }

        const res = await request.post(API_V2.PLAN_GENERATE, requestData)

        uni.showToast({ title: '生成成功', icon: 'success' })

        setTimeout(() => {
            uni.redirectTo({ url: `/pages/plan/plan-detail?plan_id=${res.plan_id}` })
        }, 1000)

    } catch (error) {
        console.error('生成失败:', error)
        uni.showToast({
            title: error.detail || error.message || '生成失败',
            icon: 'none',
            duration: 3000
        })
    } finally {
        loading.value = false
    }
}
</script>

<style lang="scss" scoped>
.container {
    min-height: 100vh;
    background: #F5F5F5;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40rpx 40rpx 60rpx;

    .header-title {
        font-size: 40rpx;
        font-weight: bold;
        color: #FFFFFF;
    }
}

.content {
    margin-top: -30rpx;
    background: #FFFFFF;
    border-radius: 32rpx 32rpx 0 0;
    min-height: calc(100vh - 200rpx);
    padding: 40rpx 40rpx 120rpx;
}

.step-section {
    margin-bottom: 50rpx;
}

.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20rpx;

    .step-dot {
        width: 48rpx;
        height: 48rpx;
        border-radius: 50%;
        background: #E0E0E0;
        color: #999999;
        font-size: 24rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        transition: all 0.3s;

        &.active {
            background: #667eea;
            color: #FFFFFF;
        }

        &.completed {
            background: #34C759;
            color: #FFFFFF;
        }
    }

    .step-line {
        width: 100rpx;
        height: 4rpx;
        background: #E0E0E0;
        margin: 0 10rpx;
        transition: all 0.3s;

        &.active {
            background: #667eea;
        }
    }
}

.step-labels {
    display: flex;
    justify-content: space-between;
    padding: 0 30rpx;

    .step-label {
        font-size: 24rpx;
        color: #999999;
        flex: 1;
        text-align: center;

        &.active {
            color: #667eea;
            font-weight: 600;
        }
    }
}

.form-section {
    flex: 1;
}

.section-title {
    display: flex;
    align-items: center;
    margin-bottom: 40rpx;

    .title-icon {
        font-size: 40rpx;
        margin-right: 16rpx;
    }

    .title-text {
        font-size: 32rpx;
        font-weight: bold;
        color: #333333;
    }
}

.plan-type-cards {
    display: flex;
    flex-direction: column;
    gap: 24rpx;

    .plan-type-card {
        display: flex;
        align-items: center;
        padding: 32rpx;
        background: #F8F8F8;
        border-radius: 24rpx;
        border: 4rpx solid transparent;
        transition: all 0.3s;

        &.selected {
            background: #F0EEFF;
            border-color: #667eea;
        }

        .card-icon {
            font-size: 56rpx;
            margin-right: 24rpx;
        }

        .card-content {
            flex: 1;

            .card-title {
                display: block;
                font-size: 32rpx;
                font-weight: bold;
                color: #333333;
                margin-bottom: 8rpx;
            }

            .card-desc {
                display: block;
                font-size: 26rpx;
                color: #666666;
            }
        }

        .card-check {
            width: 48rpx;
            height: 48rpx;
            border-radius: 50%;
            background: #667eea;
            color: #FFFFFF;
            font-size: 28rpx;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
    }
}

.scheme-cards {
    display: flex;
    flex-direction: column;
    gap: 20rpx;

    .scheme-card {
        padding: 28rpx 32rpx;
        background: #F8F8F8;
        border-radius: 20rpx;
        border: 4rpx solid transparent;
        transition: all 0.3s;

        &.selected {
            background: #F0EEFF;
            border-color: #667eea;
        }

        .scheme-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12rpx;

            .scheme-name {
                font-size: 30rpx;
                font-weight: bold;
                color: #333333;
            }

            .scheme-check {
                width: 40rpx;
                height: 40rpx;
                border-radius: 50%;
                background: #667eea;
                color: #FFFFFF;
                font-size: 24rpx;
                display: flex;
                align-items: center;
                justify-content: center;
            }
        }

        .scheme-desc {
            font-size: 26rpx;
            color: #666666;
        }
    }
}

.info-card {
    background: #F8F8F8;
    border-radius: 24rpx;
    padding: 32rpx;

    .info-row {
        display: flex;
        align-items: center;
        margin-bottom: 20rpx;

        &:last-child {
            margin-bottom: 0;
        }

        .info-icon {
            font-size: 32rpx;
            margin-right: 16rpx;
        }

        .info-text {
            font-size: 28rpx;
            color: #333333;
        }
    }
}

.gym-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;

    .gym-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 28rpx 32rpx;
        background: #F8F8F8;
        border-radius: 20rpx;
        border: 4rpx solid transparent;
        transition: all 0.3s;

        &.selected {
            background: #F0EEFF;
            border-color: #667eea;
        }

        .gym-info {
            .gym-name {
                display: block;
                font-size: 30rpx;
                font-weight: bold;
                color: #333333;
                margin-bottom: 8rpx;
            }

            .gym-equipment {
                font-size: 26rpx;
                color: #666666;
            }
        }

        .gym-check {
            width: 48rpx;
            height: 48rpx;
            border-radius: 50%;
            background: #667eea;
            color: #FFFFFF;
            font-size: 28rpx;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
    }
}

.empty-gym {
    text-align: center;
    padding: 60rpx 0;

    .empty-text {
        display: block;
        font-size: 30rpx;
        color: #666666;
        margin-bottom: 16rpx;
    }

    .empty-tip {
        display: block;
        font-size: 26rpx;
        color: #999999;
    }
}

.action-section {
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
        height: 96rpx;
        border-radius: 48rpx;
        border: none;
        font-size: 30rpx;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;

        &.prev-btn {
            background: #F5F5F5;
            color: #666666;
        }

        &.next-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #FFFFFF;
            opacity: 0.5;

            &:not([disabled]) {
                opacity: 1;
            }
        }

        &.generate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #FFFFFF;

            &[disabled] {
                opacity: 0.5;
            }
        }
    }
}
</style>
