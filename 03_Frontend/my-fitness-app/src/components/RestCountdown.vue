<template>
    <view class="rest-modal" v-if="visible">
        <view class="modal-overlay" @click="skipRest"></view>
        <view class="modal-content">
            <view class="modal-header">
                <text class="rest-title">⏱️ 休息时间</text>
                <text class="rest-subtitle">组间休息</text>
            </view>

            <view class="countdown-display">
                <text class="countdown-time">{{ formatTime(remainingSeconds) }}</text>
                <text class="countdown-label">剩余时间</text>
            </view>

            <view class="progress-bar">
                <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
            </view>

            <view class="rest-settings">
                <text class="settings-label">调整休息时长</text>
                <view class="time-buttons">
                    <view
                        class="time-btn"
                        :class="{ active: selectedRestTime === 30 }"
                        @click="setRestTime(30)"
                    >
                        30秒
                    </view>
                    <view
                        class="time-btn"
                        :class="{ active: selectedRestTime === 60 }"
                        @click="setRestTime(60)"
                    >
                        60秒
                    </view>
                    <view
                        class="time-btn"
                        :class="{ active: selectedRestTime === 90 }"
                        @click="setRestTime(90)"
                    >
                        90秒
                    </view>
                    <view
                        class="time-btn"
                        :class="{ active: selectedRestTime === 120 }"
                        @click="setRestTime(120)"
                    >
                        2分钟
                    </view>
                </view>
            </view>

            <view class="modal-actions">
                <button class="btn skip-btn" @click="skipRest">
                    <text>跳过休息</text>
                </button>
                <button class="btn confirm-btn" @click="confirmRest">
                    <text>确认完成</text>
                </button>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { DEFAULT_REST_SECONDS, MIN_REST_SECONDS, MAX_REST_SECONDS } from '@/utils/constants'

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    initialSeconds: {
        type: Number,
        default: DEFAULT_REST_SECONDS
    }
})

const emit = defineEmits(['update:visible', 'complete', 'skip'])

const remainingSeconds = ref(DEFAULT_REST_SECONDS)
const selectedRestTime = ref(DEFAULT_REST_SECONDS)
let timer = null

const progressPercent = computed(() => {
    return ((selectedRestTime.value - remainingSeconds.value) / selectedRestTime.value) * 100
})

watch(() => props.visible, (newVal) => {
    if (newVal) {
        startTimer()
    } else {
        stopTimer()
    }
})

watch(() => props.initialSeconds, (newVal) => {
    remainingSeconds.value = newVal
    selectedRestTime.value = newVal
})

const startTimer = () => {
    remainingSeconds.value = selectedRestTime.value
    stopTimer()
    timer = setInterval(() => {
        if (remainingSeconds.value > 0) {
            remainingSeconds.value--
        } else {
            stopTimer()
            playSound()
            emit('complete')
        }
    }, 1000)
}

const stopTimer = () => {
    if (timer) {
        clearInterval(timer)
        timer = null
    }
}

const setRestTime = (seconds) => {
    if (seconds < MIN_REST_SECONDS || seconds > MAX_REST_SECONDS) return
    selectedRestTime.value = seconds
    remainingSeconds.value = seconds
    startTimer()
}

const skipRest = () => {
    stopTimer()
    emit('skip')
    emit('update:visible', false)
}

const confirmRest = () => {
    stopTimer()
    emit('complete')
    emit('update:visible', false)
}

const playSound = () => {
    const audioContext = uni.createInnerAudioContext()
    audioContext.src = '/static/audio/beep.mp3'
    audioContext.play()
    setTimeout(() => {
        audioContext.destroy()
    }, 1000)
}

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    if (mins > 0) {
        return `${mins}:${String(secs).padStart(2, '0')}`
    }
    return `${secs}`
}
</script>

<style lang="scss" scoped>
.rest-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;

    .modal-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
    }

    .modal-content {
        position: relative;
        width: 600rpx;
        background: #FFFFFF;
        border-radius: 32rpx;
        padding: 48rpx 40rpx;
        box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
    }

    .modal-header {
        text-align: center;
        margin-bottom: 40rpx;

        .rest-title {
            display: block;
            font-size: 40rpx;
            font-weight: bold;
            color: #333333;
            margin-bottom: 8rpx;
        }

        .rest-subtitle {
            display: block;
            font-size: 26rpx;
            color: #999999;
        }
    }

    .countdown-display {
        text-align: center;
        margin-bottom: 32rpx;

        .countdown-time {
            display: block;
            font-size: 120rpx;
            font-weight: bold;
            color: #667eea;
            font-family: 'DIN Alternate', -apple-system;
            line-height: 1;
            margin-bottom: 16rpx;
        }

        .countdown-label {
            display: block;
            font-size: 28rpx;
            color: #666666;
        }
    }

    .progress-bar {
        height: 12rpx;
        background: #E0E0E0;
        border-radius: 6rpx;
        margin-bottom: 40rpx;
        overflow: hidden;

        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 6rpx;
            transition: width 0.3s ease;
        }
    }

    .rest-settings {
        margin-bottom: 40rpx;

        .settings-label {
            display: block;
            font-size: 26rpx;
            color: #666666;
            margin-bottom: 20rpx;
            text-align: center;
        }

        .time-buttons {
            display: flex;
            gap: 16rpx;
            justify-content: center;

            .time-btn {
                padding: 16rpx 24rpx;
                background: #F5F5F5;
                border-radius: 16rpx;
                font-size: 26rpx;
                color: #666666;
                transition: all 0.3s;

                &.active {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: #FFFFFF;
                }
            }
        }
    }

    .modal-actions {
        display: flex;
        gap: 20rpx;

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

            &.skip-btn {
                background: #F5F5F5;
                color: #666666;
            }

            &.confirm-btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: #FFFFFF;
            }
        }
    }
}
</style>
