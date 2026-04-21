<template>
    <view class="container">
        <view class="header">
            <text class="header-title"> </text>
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
                        <text class="title-text">请选择您的健身目标</text>
                    </view>

                    <view class="plan-type-cards">
                        <view
                            class="plan-type-card"
                            :class="{ selected: selectedPlanType === 'FAT_LOSS' }"
                            @click="selectPlanType('FAT_LOSS')"
                        >
                            <view class="card-icon-wrap">
                                <image src="@/static/fatLoss.png" class="card-icon-img" mode="aspectFit" />
                            </view>
                            <view class="card-content">
                                <text class="card-title">减脂计划</text>
                                <text class="card-desc">有氧+力量组合，高效燃脂</text>
                            </view>
                            <view class="card-check" v-if="selectedPlanType === 'FAT_LOSS'">
                                <image src="@/static/check.png" class="check-icon" mode="aspectFit" />
                            </view>
                        </view>

                        <view
                            class="plan-type-card"
                            :class="{ selected: selectedPlanType === 'MUSCLE_GAIN' }"
                            @click="selectPlanType('MUSCLE_GAIN')"
                        >
                            <view class="card-icon-wrap">
                                <image src="@/static/muscle.png" class="card-icon-img" mode="aspectFit" />
                            </view>
                            <view class="card-content">
                                <text class="card-title">增肌计划</text>
                                <text class="card-desc">力量训练为主，肌肉增长</text>
                            </view>
                            <view class="card-check" v-if="selectedPlanType === 'MUSCLE_GAIN'">
                                <image src="@/static/check.png" class="check-icon" mode="aspectFit" />
                            </view>
                        </view>
                    </view>
                </view>

                <view class="step-content" v-show="currentStep === 2 && selectedPlanType === 'MUSCLE_GAIN'">
                    <view class="section-title">
                        <uni-icons type="list" size="22" color="#a03e40"></uni-icons>
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
                                <view class="scheme-check" v-if="selectedSchemeType === scheme.value">
                                    <image src="@/static/check.png" class="check-icon-sm" mode="aspectFit" />
                                </view>
                            </view>
                            <text class="scheme-desc">{{ scheme.description }}</text>
                        </view>
                    </view>
                </view>

                <view class="step-content" v-show="currentStep === 2 && selectedPlanType === 'FAT_LOSS'">
                    <view class="section-title">
                        <uni-icons type="staff" size="22" color="#a03e40"></uni-icons>
                        <text class="title-text">减脂计划说明</text>
                    </view>

                    <view class="info-card">
                        <view class="info-row">
                            <uni-icons type="fire" size="20" color="#d8696a"></uni-icons>
                            <text class="info-text">热身激活 → 力量训练 → 有氧训练 → 拉伸放松</text>
                        </view>
                        <view class="info-row">
                            <uni-icons type="clock" size="20" color="#d8696a"></uni-icons>
                            <text class="info-text">每次训练约 45-60 分钟</text>
                        </view>
                        <view class="info-row">
                            <uni-icons type="calendar" size="20" color="#d8696a"></uni-icons>
                            <text class="info-text">连练3天休息1天循环</text>
                        </view>
                        <view class="info-row">
                            <uni-icons type="flag" size="20" color="#d8696a"></uni-icons>
                            <text class="info-text">第1天：胸·肩·三头 + 30分钟有氧</text>
                        </view>
                        <view class="info-row">
                            <uni-icons type="flag" size="20" color="#d8696a"></uni-icons>
                            <text class="info-text">第2天：臀·腿 + 30分钟有氧</text>
                        </view>
                        <view class="info-row">
                            <uni-icons type="flag" size="20" color="#d8696a"></uni-icons>
                            <text class="info-text">第3天：背·二头 + 30分钟有氧</text>
                        </view>
                        <view class="info-row">
                            <uni-icons type="flag" size="20" color="#d8696a"></uni-icons>
                            <text class="info-text">每天4个力量动作 + 30分钟有氧</text>
                        </view>
                    </view>
                </view>

                <view class="step-content" v-show="currentStep === 3">
                    <view class="section-title">
                        <uni-icons type="home" size="22" color="#a03e40"></uni-icons>
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
                            <view class="gym-check" v-if="selectedGymIndex === index">
                                <image src="@/static/check.png" class="check-icon" mode="aspectFit" />
                            </view>
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
                    上一步
                </button>
                <button
                    class="btn next-btn"
                    v-if="currentStep < 3"
                    @click="nextStep"
                    :disabled="!canNext"
                >
                    下一步
                </button>
                <button
                    class="btn generate-btn"
                    v-if="currentStep === 3"
                    @click="generatePlan"
                    :loading="loading"
                    :disabled="!canGenerate || loading"
                >
                    {{ loading ? '生成中...' : '生成计划' }}
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
            title: error.message || '生成失败',
            icon: 'none',
            duration: 3000
        })
    } finally {
        loading.value = false
    }
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
    min-height: 100vh;
    background: $fitness-secondary;
    font-family: Manrope;
}

.header {
    background: $color-primary;
    padding: $size-5 $size-5 $size-8;

    .header-title {
        font-size: $size-5;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.3;
    }
}

.content {
    margin-top: -$size-3;
    background: $fitness-primary;
    border-radius: $size-4 $size-4 0 0;
    min-height: calc(100vh - 200rpx);
    padding: $size-5 $size-5 140rpx;
}

.step-section {
    margin-bottom: $size-7;
}

.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $size-3;

    .step-dot {
        width: $size-6;
        height: $size-6;
        border-radius: 50%;
        background: $fitness-border;
        color: $color-secondory;
        font-size: $size-3;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        transition: all 0.3s;

        &.active {
            background: $button-bg2;
            color: #FFFFFF;
        }

        &.completed {
            background: $color-primary;
            color: #FFFFFF;
        }
    }

    .step-line {
        width: 100rpx;
        height: 4rpx;
        background: $fitness-border;
        margin: 0 $size-2;
        transition: all 0.3s;

        &.active {
            background: $button-bg2;
        }
    }
}

.step-labels {
    display: flex;
    justify-content: space-between;
    padding: 0 $size-4;

    .step-label {
        font-size: $size-3;
        color: $color-secondory;
        flex: 1;
        text-align: center;

        &.active {
            color: $color-primary;
            font-weight: 700;
        }
    }
}

.form-section {
    flex: 1;
}

.section-title {
    display: flex;
    align-items: center;
    margin-bottom: $size-5;

    .title-text {
        font-size: $size-4;
        font-weight: 700;
        color: $color-input;
        margin-left: $size-2;
    }
}

.plan-type-cards {
    display: flex;
    flex-direction: column;
    gap: $size-3;

    .plan-type-card {
        display: flex;
        align-items: center;
        padding: $size-4;
        background: $glass-bg1;
        border-radius: $size-4;
        border: 2px solid rgba(160, 62, 64, 0.1);
        box-shadow: 0 2rpx 10rpx $border-shadow;
        transition: all 0.3s;

        &.selected {
            background: $color-primary-light;
            border-color: $color-primary;
        }

        .card-icon-wrap {
            width: $size-10;
            height: $size-10;
            border-radius: $size-4;
            background: rgba(216, 105, 106, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: $size-3;

            .card-icon-img {
                width: 48rpx;
                height: 48rpx;
            }
        }

        .card-content {
            flex: 1;

            .card-title {
                display: block;
                font-size: $size-4;
                font-weight: 700;
                color: $color-input;
                margin-bottom: $size-1;
            }

            .card-desc {
                display: block;
                font-size: $size-3;
                color: $color-secondory;
            }
        }

        .card-check {
            width: $size-6;
            height: $size-6;
            border-radius: 50%;
            background: $button-bg2;
            display: flex;
            align-items: center;
            justify-content: center;

            .check-icon {
                width: 28rpx;
                height: 28rpx;
            }
        }
    }
}

.scheme-cards {
    display: flex;
    flex-direction: column;
    gap: $size-3;

    .scheme-card {
        padding: $size-4;
        background: $glass-bg1;
        border-radius: $size-4;
        border: 2px solid rgba(160, 62, 64, 0.1);
        box-shadow: 0 2rpx 10rpx $border-shadow;
        transition: all 0.3s;

        &.selected {
            background: $color-primary-light;
            border-color: $color-primary;
        }

        .scheme-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: $size-2;

            .scheme-name {
                font-size: $size-4;
                font-weight: 700;
                color: $color-input;
            }

            .scheme-check {
                width: $size-5;
                height: $size-5;
                border-radius: 50%;
                background: $button-bg2;
                display: flex;
                align-items: center;
                justify-content: center;

                .check-icon-sm {
                    width: 24rpx;
                    height: 24rpx;
                }
            }
        }

        .scheme-desc {
            font-size: $size-3;
            color: $color-secondory;
        }
    }
}

.info-card {
    background: $glass-bg1;
    border-radius: $size-4;
    padding: $size-4;
    box-shadow: 0 2rpx 10rpx $border-shadow;

    .info-row {
        display: flex;
        align-items: center;
        margin-bottom: $size-3;

        &:last-child {
            margin-bottom: 0;
        }

        .info-text {
            font-size: $size-3;
            color: $color-label;
            margin-left: $size-2;
        }
    }
}

.gym-list {
    display: flex;
    flex-direction: column;
    gap: $size-3;

    .gym-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: $size-4;
        background: $glass-bg1;
        border-radius: $size-4;
        border: 2px solid rgba(160, 62, 64, 0.1);
        box-shadow: 0 2rpx 10rpx $border-shadow;
        transition: all 0.3s;

        &.selected {
            background: $color-primary-light;
            border-color: $color-primary;
        }

        .gym-info {
            .gym-name {
                display: block;
                font-size: $size-4;
                font-weight: 700;
                color: $color-input;
                margin-bottom: $size-1;
            }

            .gym-equipment {
                font-size: $size-3;
                color: $color-secondory;
            }
        }

        .gym-check {
            width: $size-6;
            height: $size-6;
            border-radius: 50%;
            background: $button-bg2;
            display: flex;
            align-items: center;
            justify-content: center;

            .check-icon {
                width: 28rpx;
                height: 28rpx;
            }
        }
    }
}

.empty-gym {
    text-align: center;
    padding: $size-8 0;

    .empty-text {
        display: block;
        font-size: $size-4;
        color: $color-label;
        margin-bottom: $size-2;
    }

    .empty-tip {
        display: block;
        font-size: $size-3;
        color: $color-secondory;
    }
}

.action-section {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    gap: $size-3;
    padding: $size-3 $size-5;
    padding-bottom: calc(#{$size-3} + env(safe-area-inset-bottom));
    background: $fitness-primary;
    border-top: 1px solid $fitness-border;

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

        &.prev-btn {
            background: $fitness-secondary;
            color: $color-label;
        }

        &.next-btn {
            background: $button-bg2;
            color: #FFFFFF;
            opacity: 0.6;

            &:not([disabled]) {
                opacity: 1;
            }
        }

        &.generate-btn {
            background: $button-bg2;
            color: #FFFFFF;

            &[disabled] {
                opacity: 0.6;
            }
        }
    }
}
</style>
