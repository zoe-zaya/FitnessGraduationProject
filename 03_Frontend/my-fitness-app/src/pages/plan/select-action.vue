<template>
    <view class="container">
        <view class="header">
            <view class="header-top">
                <text class="back-btn" @click="goBack">←</text>
                <text class="header-title">{{ mode === 'replace' ? '替换动作' : '添加动作' }}</text>
            </view>
        </view>

        <view class="search-bar">
            <view class="search-input-wrapper">
                <text class="search-icon">🔍</text>
                <input
                    v-model="searchKeyword"
                    type="text"
                    placeholder="搜索动作名称或肌群"
                    class="search-input"
                    @confirm="searchActions"
                />
            </view>
            <view class="search-btn" @click="searchActions">
                <text class="btn-text">搜索</text>
            </view>
        </view>

        <view class="filter-bar">
            <view class="filter-item">
                <text class="filter-label">难度：</text>
                <picker
                    @change="onDifficultyChange"
                    :value="difficultyIndex"
                    :range="difficultyOptions"
                    range-key="label"
                    class="filter-picker"
                >
                    <text class="filter-text">{{ difficultyOptions[difficultyIndex]?.label }}</text>
                </picker>
            </view>
        </view>

        <view class="session-info-card">
            <text class="info-title">📍 添加到</text>
            <text class="info-value">{{ getSessionName(sessionType) }}</text>
        </view>

        <view class="content">
            <view class="action-list" v-if="actionList.length > 0">
                <view
                    class="action-card"
                    v-for="(action, index) in actionList"
                    :key="action.action_id"
                    @click="selectAction(action)"
                >
                    <view class="action-header">
                        <text class="action-name">{{ action.name }}</text>
                        <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                            {{ action.difficulty_level }}
                        </text>
                    </view>

                    <view class="action-category">
                        <text class="category-label">📊 类别：</text>
                        <text class="category-value">{{ getCategoryName(action.action_category) }}</text>
                    </view>

                    <view class="action-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
                        <text class="muscles-label">🎯 目标肌群：</text>
                        <view class="muscles-tags">
                            <text
                                class="muscle-tag"
                                v-for="(muscle, mIndex) in action.target_muscles.slice(0, 3)"
                                :key="mIndex"
                            >
                                {{ muscle }}
                            </text>
                            <text class="muscle-tag more" v-if="action.target_muscles.length > 3">
                                +{{ action.target_muscles.length - 3 }}
                            </text>
                        </view>
                    </view>

                    <view class="action-equipment" v-if="action.equipment_name">
                        <text class="equipment-label">🏋️ 器材：</text>
                        <text class="equipment-value">{{ action.equipment_name }}</text>
                    </view>

                    <view class="action-footer">
                        <text class="action-duration">⏱️ {{ formatDuration(action.estimated_seconds) }}</text>
                        <view class="select-btn">
                            <text class="btn-icon">{{ mode === 'replace' ? '🔄' : '+' }}</text>
                            <text class="btn-text">{{ mode === 'replace' ? '替换' : '添加' }}</text>
                        </view>
                    </view>
                </view>
            </view>

            <view class="empty-state" v-else-if="hasSearched">
                <image src="/static/empty-search.png" class="empty-image" mode="aspectFit" />
                <text class="empty-text">未找到匹配的动作</text>
                <text class="empty-subtext">请尝试其他关键词或筛选条件</text>
            </view>

            <view class="default-tip" v-else>
                <image src="/static/search-guide.png" class="tip-image" mode="aspectFit" />
                <text class="tip-text">输入关键词搜索动作</text>
                <text class="tip-subtext">如"深蹲"、"卧推"、"胸大肌"等</text>
            </view>
        </view>

        <view class="loading-mask" v-if="loading">
            <text class="loading-text">加载中...</text>
        </view>
    </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API_V2, SESSION_TYPE_MAP, DIFFICULTY_MAP, ACTION_CATEGORY_MAP, DEFAULT_SETS, DEFAULT_REPS, DEFAULT_REST_SECONDS, DEFAULT_DURATION_MINUTES } from '@/utils/constants'

const planId = ref('')
const sessionId = ref('')
const sessionType = ref('')
const actionItemId = ref('')
const mode = ref('add')

const searchKeyword = ref('')
const difficultyIndex = ref(0)
const difficultyOptions = ref([
    { label: '全部难度', value: '' },
    { label: '初级', value: '初级' },
    { label: '中级', value: '中级' },
    { label: '高级', value: '高级' }
])

const actionList = ref([])
const loading = ref(false)
const hasSearched = ref(false)

onLoad((options) => {
    planId.value = options.plan_id || ''
    sessionId.value = options.session_id || ''
    sessionType.value = options.session_type || ''
    actionItemId.value = options.action_id || ''
    mode.value = options.mode || 'add'
})

const searchActions = async () => {
    loading.value = true
    hasSearched.value = true

    try {
        const params = {}

        if (searchKeyword.value.trim()) {
            params.keyword = searchKeyword.value.trim()
        }

        if (difficultyIndex.value > 0) {
            params.difficulty_level = difficultyOptions.value[difficultyIndex.value].value
        }

        params.action_category = getCategoryForSession(sessionType.value)

        const res = await request.get('/api/action/query', { params })

        if (difficultyIndex.value > 0) {
            const selectedDifficulty = difficultyOptions.value[difficultyIndex.value]?.value
            actionList.value = (res || []).filter(action => action.difficulty_level === selectedDifficulty)
        } else {
            actionList.value = res || []
        }

    } catch (error) {
        console.error('搜索失败:', error)
        actionList.value = []
    } finally {
        loading.value = false
    }
}

const onDifficultyChange = (e) => {
    difficultyIndex.value = e.detail.value
    searchActions()
}

const getCategoryForSession = (type) => {
    switch (type) {
        case 'warmup':
            return 'warmup'
        case 'main':
            return 'main_strength'
        case 'cooldown':
            return 'cooldown'
        default:
            return ''
    }
}

const getSessionName = (type) => {
    return SESSION_TYPE_MAP[type]?.label || type
}

const getCategoryName = (category) => {
    return ACTION_CATEGORY_MAP[category] || category
}

const getDifficultyColor = (level) => {
    return DIFFICULTY_MAP[level]?.color || '#999999'
}

const formatDuration = (seconds) => {
    if (!seconds) return '0 秒'
    if (seconds < 60) return `${seconds}秒`
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return secs > 0 ? `${mins}分${secs}秒` : `${mins}分钟`
}

const selectAction = async (action) => {
    if (mode.value === 'replace') {
        await replaceAction(action)
    } else {
        await addAction(action)
    }
}

const addAction = async (action) => {
    try {
        const addData = {
            session_id: sessionId.value,
            action_id: action.action_id,
            sets: action.action_category === 'main_strength' ? DEFAULT_SETS : undefined,
            reps_per_set: action.action_category === 'main_strength' ? DEFAULT_REPS : undefined,
            rest_seconds_default: action.action_category === 'main_strength' ? DEFAULT_REST_SECONDS : undefined,
            duration_minutes: action.action_category === 'main_cardio' ? DEFAULT_DURATION_MINUTES : undefined
        }

        await request.post(`${API_V2.PLAN_ADD_ACTION}/${planId.value}`, addData)

        uni.showToast({
            title: `"${action.name}"已添加`,
            icon: 'success',
            duration: 1500
        })

        setTimeout(() => {
            uni.navigateBack()
        }, 1000)

    } catch (error) {
        console.error('添加失败:', error)

        if (error.code === 400 && error.detail?.includes('器材')) {
            uni.showToast({
                title: '该动作所需器材您当前健身房未配备',
                icon: 'none',
                duration: 2000
            })
        } else {
            uni.showToast({
                title: error.detail || '添加失败',
                icon: 'none',
                duration: 2000
            })
        }
    }
}

const replaceAction = async (action) => {
    try {
        const replaceData = {
            new_action_id: action.action_id,
            keep_params: true
        }

        await request.post(`${API_V2.PLAN_REPLACE_ACTION}/${planId.value}/${actionItemId.value}`, replaceData)

        uni.showToast({
            title: `"${action.name}"已替换`,
            icon: 'success',
            duration: 1500
        })

        setTimeout(() => {
            uni.navigateBack()
        }, 1000)

    } catch (error) {
        console.error('替换失败:', error)

        if (error.code === 400 && error.detail?.includes('器材')) {
            uni.showToast({
                title: '该动作所需器材您当前健身房未配备',
                icon: 'none',
                duration: 2000
            })
        } else {
            uni.showToast({
                title: error.detail || '替换失败',
                icon: 'none',
                duration: 2000
            })
        }
    }
}

const goBack = () => {
    uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.container {
    min-height: 100vh;
    background: #F5F5F5;
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

.search-bar {
    display: flex;
    align-items: center;
    padding: 24rpx 30rpx;
    background: #FFFFFF;
    gap: 16rpx;

    .search-input-wrapper {
        flex: 1;
        display: flex;
        align-items: center;
        background: #F5F5F5;
        border-radius: 32rpx;
        padding: 0 24rpx;

        .search-icon {
            font-size: 32rpx;
            margin-right: 12rpx;
        }

        .search-input {
            flex: 1;
            height: 72rpx;
            font-size: 28rpx;
        }
    }

    .search-btn {
        padding: 0 32rpx;
        height: 72rpx;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 36rpx;
        display: flex;
        align-items: center;
        justify-content: center;

        .btn-text {
            font-size: 28rpx;
            color: #FFFFFF;
            font-weight: 600;
        }
    }
}

.filter-bar {
    display: flex;
    align-items: center;
    padding: 20rpx 30rpx;
    background: #FFFFFF;
    border-bottom: 1rpx solid #E5E5E5;
    gap: 24rpx;

    .filter-item {
        display: flex;
        align-items: center;

        .filter-label {
            font-size: 26rpx;
            color: #666666;
            margin-right: 12rpx;
        }

        .filter-picker {
            .filter-text {
                font-size: 26rpx;
                color: #667eea;
                font-weight: 500;
            }
        }
    }
}

.session-info-card {
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
    margin: 30rpx 40rpx;
    border-radius: 20rpx;
    padding: 24rpx 32rpx;
    display: flex;
    align-items: center;
    border-left: 6rpx solid #1976D2;

    .info-title {
        font-size: 26rpx;
        color: #1565C0;
        margin-right: 12rpx;
    }

    .info-value {
        font-size: 28rpx;
        color: #1976D2;
        font-weight: 600;
    }
}

.content {
    padding: 0 30rpx 30rpx;
}

.action-list {
    .action-card {
        background: #FFFFFF;
        border-radius: 20rpx;
        padding: 28rpx;
        margin-bottom: 20rpx;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);

        .action-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16rpx;

            .action-name {
                font-size: 30rpx;
                font-weight: 600;
                color: #333333;
                flex: 1;
            }

            .action-difficulty {
                font-size: 22rpx;
                padding: 6rpx 16rpx;
                border-radius: 12rpx;
                color: #FFFFFF;
                margin-left: 16rpx;
            }
        }

        .action-category {
            display: flex;
            margin-bottom: 12rpx;

            .category-label {
                font-size: 24rpx;
                color: #666666;
                margin-right: 8rpx;
            }

            .category-value {
                font-size: 24rpx;
                color: #333333;
                font-weight: 500;
            }
        }

        .action-muscles {
            margin-bottom: 12rpx;

            .muscles-label {
                display: block;
                font-size: 24rpx;
                color: #666666;
                margin-bottom: 8rpx;
            }

            .muscles-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 10rpx;

                .muscle-tag {
                    background: #F5F5F5;
                    color: #333333;
                    font-size: 22rpx;
                    padding: 6rpx 16rpx;
                    border-radius: 12rpx;

                    &.more {
                        background: #E0E0E0;
                        color: #666666;
                    }
                }
            }
        }

        .action-equipment {
            display: flex;
            margin-bottom: 16rpx;

            .equipment-label {
                font-size: 24rpx;
                color: #666666;
                margin-right: 8rpx;
            }

            .equipment-value {
                font-size: 24rpx;
                color: #333333;
                font-weight: 500;
            }
        }

        .action-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;

            .action-duration {
                font-size: 24rpx;
                color: #999999;
            }

            .select-btn {
                display: flex;
                align-items: center;
                padding: 12rpx 28rpx;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 24rpx;

                .btn-icon {
                    font-size: 28rpx;
                    color: #FFFFFF;
                    margin-right: 6rpx;
                }

                .btn-text {
                    font-size: 24rpx;
                    color: #FFFFFF;
                    font-weight: 600;
                }
            }
        }
    }
}

.empty-state, .default-tip {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100rpx 40rpx;
    text-align: center;

    .empty-image, .tip-image {
        width: 280rpx;
        height: 280rpx;
        margin-bottom: 40rpx;
    }

    .empty-text, .tip-text {
        font-size: 30rpx;
        color: #333333;
        font-weight: 600;
        margin-bottom: 16rpx;
    }

    .empty-subtext, .tip-subtext {
        font-size: 26rpx;
        color: #666666;
    }
}

.loading-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;

    .loading-text {
        font-size: 28rpx;
        color: #666666;
    }
}
</style>
