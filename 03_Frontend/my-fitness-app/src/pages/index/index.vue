<template>
  <view class="container">
    <!-- 快捷操作 -->
    <view class="quick-actions">
      <view class="action-card" @click="navigateToactions">
        <text class="action-icon">🏋️</text>
        <text class="action-title">动作库</text>
        <text class="action-desc">看看有哪些动作可以练习吧</text>
      </view>
    </view>

    <!-- 今日训练安排 -->
    <view class="today-plan-section">
      <text class="section-title">今日训练安排</text>
      <view class="plan-list">
        <view class="plan-item">
          <view class="plan-time">08:00</view>
          <view class="plan-content">
            <text class="plan-name">晨间热身</text>
            <text class="plan-duration">15分钟</text>
          </view>
        </view>
        <view class="plan-item">
          <view class="plan-time">09:00</view>
          <view class="plan-content">
            <text class="plan-name">力量训练 - 胸部</text>
            <text class="plan-duration">45分钟</text>
          </view>
        </view>
        <view class="plan-item">
          <view class="plan-time">10:30</view>
          <view class="plan-content">
            <text class="plan-name">有氧运动</text>
            <text class="plan-duration">30分钟</text>
          </view>
        </view>
        <view class="plan-item">
          <view class="plan-time">14:00</view>
          <view class="plan-content">
            <text class="plan-name">拉伸放松</text>
            <text class="plan-duration">15分钟</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

const navigateToactions = () => {
  uni.navigateTo({
    url: `/pages/action/action-library`
  })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background-color: #FFFFFF;
  padding: 32rpx;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.quick-actions {
  display: flex;
  gap: 24rpx;
  margin-bottom: 48rpx;

  .action-card {
    flex: 1;
    background: rgba(252, 249, 248, 1);
    border-radius: 32rpx;
    padding: 48rpx 40rpx;
    text-align: center;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
    border: 2rpx solid #efefef;
    transition: all 0.2s ease;

    &:active {
      transform: scale(0.96);
      box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.08);
    }

    .action-icon {
      display: block;
      font-size: 80rpx;
      margin-bottom: 24rpx;
    }

    .action-title {
      display: block;
      font-size: 32rpx;
      font-weight: 700;
      color: #1B1C1C;
      margin-bottom: 16rpx;
      line-height: 1.2;
    }

    .action-desc {
      display: block;
      font-size: 24rpx;
      color: #8E8E93;
      line-height: 1.4;
      font-weight: 525;
    }
  }
}

.today-plan-section {
  background: rgba(252, 249, 248, 0.7);
  border-radius: 32rpx;
  padding: 48rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
  border: 2rpx solid #efefef;

  .section-title {
    display: block;
    font-size: 40rpx;
    font-weight: 700;
    color: #a03e40;
    margin-bottom: 40rpx;
    line-height: 1.3;
  }

  .plan-list {
    .plan-item {
      display: flex;
      align-items: center;
      padding: 32rpx 0;
      border-bottom: 2rpx solid rgba(0, 0, 0, 0.05);
      transition: all 0.15s ease;

      &:active {
        background: rgba(252, 249, 248, 0.5);
        padding-left: 16rpx;
        padding-right: 16rpx;
        border-radius: 16rpx;
      }

      &:last-child {
        border-bottom: none;
      }

      .plan-time {
        font-size: 28rpx;
        font-weight: 700;
        color: #a03e40;
        width: 120rpx;
        flex-shrink: 0;
        line-height: 1.4;
      }

      .plan-content {
        flex: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .plan-name {
          font-size: 28rpx;
          color: #1B1C1C;
          font-weight: 600;
          line-height: 1.4;
        }

        .plan-duration {
          font-size: 24rpx;
          color: #564241;
          font-weight: 525;
          line-height: 1.4;
        }
      }
    }
  }
}
</style>