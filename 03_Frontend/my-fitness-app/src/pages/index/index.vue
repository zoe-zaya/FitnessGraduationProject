<template>
  <view class="container">
    <view class="welcome-section">
      <view class="greeting">
        <text class="greeting-text">欢迎回来</text>
        <text class="username">{{ userInfo.name || '用户' }}</text>
      </view>
      <view class="today-stats">
        <view class="stat-item">
          <text class="stat-number">0</text>
          <text class="stat-label">今日运动</text>
        </view>
        <view class="stat-item">
          <text class="stat-number">7</text>
          <text class="stat-label">连续打卡</text>
        </view>
        <view class="stat-item">
          <text class="stat-number">2.5</text>
          <text class="stat-label">本月小时</text>
        </view>
      </view>
    </view>
    
    <view class="quick-actions">
      <view class="action-card" @click="startExercise">
        <text class="action-icon">💪</text>
        <text class="action-title">开始训练</text>
        <text class="action-desc">开始今天的锻炼计划</text>
      </view>
      
      <view class="action-card" @click="recordExercise">
        <text class="action-icon">📷</text>
        <text class="action-title">动作识别</text>
        <text class="action-desc">拍照识别健身动作</text>
      </view>
    </view>
    
    <view class="recent-section">
      <text class="section-title">最近训练</text>
      <view class="no-data">
        <text class="no-data-text">暂无训练记录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

const startExercise = () => {
  uni.showToast({
    title: '功能即将开放',
    icon: 'none'
  })
}

const recordExercise = () => {
  uni.showToast({
    title: '功能即将开放',
    icon: 'none'
  })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background-color: rgba(252, 249, 248, 0.5);
;
  padding: $size-5 $size-5 0;
}

.welcome-section {
  background: $fitness-primary;
  border-radius: $size-5;
  padding: $size-5;
  margin-bottom: $size-5;
  box-shadow: 0 1rpx 0 0 rgba(0, 0, 0, 0.12); // iOS风格阴影
  
  .greeting {
    margin-bottom: $size-5;
    
    .greeting-text {
      display: block;
      font-size: $size-6;
      color: $color-label;
      margin-bottom: 10rpx;
    }
    
    .username {
      display: block;
      font-size: $font-xxl;
      font-weight: 700;
      color: $fitness-text;
    }
  }
  
  .today-stats {
    display: flex;
    justify-content: space-between;
    
    .stat-item {
      text-align: center;
      flex: 1;
      
      .stat-number {
        display: block;
        font-size: $font-xxl;
        font-weight: 700;
        color: $fitness-text;
        margin-bottom: 10rpx;
      }
      
      .stat-label {
        display: block;
        font-size: $size-3;
        color: $color-label;
      }
    }
  }
}

.quick-actions {
  display: flex;
  gap: $size-5;
  margin-bottom: $size-5;
  
  .action-card {
    flex: 1;
    background: $fitness-primary;
    border-radius: $size-5;
    padding: $size-5 20rpx;
    text-align: center;
    box-shadow: 0 1rpx 0 0 rgba(0, 0, 0, 0.12); // iOS风格阴影
    
    .action-icon {
      display: block;
      font-size: $font-xxl;
      margin-bottom: 20rpx;
    }
    
    .action-title {
      display: block;
      font-size: $size-5;
      font-weight: 600;
      color: $fitness-text;
      margin-bottom: 10rpx;
    }
    
    .action-desc {
      display: block;
      font-size: $size-3;
      color: $color-label;
    }
  }
}

.recent-section {
  background: $fitness-primary;
  border-radius: $size-5;
  padding: $size-5;
  box-shadow: 0 1rpx 0 0 rgba(0, 0, 0, 0.12); // iOS风格阴影
  
  .section-title {
    display: block;
    font-size: $size-5;
    font-weight: 600;
    color: $fitness-text;
    margin-bottom: 30rpx;
  }
  
  .no-data {
    text-align: center;
    padding: 60rpx 0;
    
    .no-data-text {
      font-size: $size-4;
      color: $color-label;
    }
  }
}
</style>