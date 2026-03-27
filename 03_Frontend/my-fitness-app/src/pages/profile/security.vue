<template>
  <view class="container">
    <!-- 当前账号信息 -->
    <view class="account-info">
      <text class="info-label">当前手机号</text>
      <text class="info-value">{{ maskedCurrentPhone }}</text>
    </view>
    
    <!-- 功能菜单 -->
    <view class="menu-section">
      <!-- 修改手机号 -->
      <view class="menu-item border-bottom" @click="navigateToUpdatePhone">
        <view class="menu-left">
          <img src="@/static/phone.png" class="menu-icon"/>
          <text class="menu-label">修改手机号</text>
        </view>
        <view class="menu-right">
          <text class="arrow">›</text>
        </view>
      </view>
      
      <!-- 修改登录密码 -->
      <view class="menu-item" @click="navigateToUpdatePassword">
        <view class="menu-left">
          <img src="@/static/password.png" class="menu-icon"/>
          <text class="menu-label">修改登录密码</text>
        </view>
        <view class="menu-right">
          <text class="arrow">›</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import { API } from '@/utils/constants'

const userStore = useUserStore()
const currentUserPhone = computed(() => userStore.userInfo.phone || '未绑定')
const maskedCurrentPhone = computed(() => {
  if (!userStore.userInfo.phone) {
    return '未绑定'
  }
  // 隐藏手机号中间4位数字
  const phone = userStore.userInfo.phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
})

/**
 * 页面显示时刷新用户信息
 */
onShow(async () => {
  if (userStore.isLogin) {
    try {
      const res = await request.get(API.USER_ME)
      userStore.updateUserInfo(res)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
})

/**
 * 跳转至修改手机号页面
 */
const navigateToUpdatePhone = () => {
  uni.navigateTo({ url: '/pages/profile/update-phone' })
}

/**
 * 跳转至修改登录密码页面
 */
const navigateToUpdatePassword = () => {
  uni.navigateTo({ url: '/pages/profile/update-password' })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background-color: $fitness-primary;
  padding: 0;
}

.account-info {
  background: $fitness-primary;
  border-radius: $radius-lg;
  padding: 20rpx;
  margin: 0 $spacing-lg;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
  
  .info-label {
    font-size: $font-md;
    color: $fitness-text-light;
  }
  
  .info-value {
    font-size: $font-lg;
    font-weight: 600;
    color: $fitness-text;
  }
}

.menu-section {
  background: $fitness-primary;
  border-radius: $radius-lg;
  margin: 0 $spacing-lg $spacing-lg;
  box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
  
  .menu-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 36rpx $spacing-lg;
    position: relative;
    
    &.border-bottom::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: $spacing-lg;
      right: $spacing-lg;
      height: 1rpx;
      background: $fitness-border;
      transform: scaleY(0.5);
    }
    
    .menu-left {
      display: flex;
      align-items: center;
      
      .menu-icon {
        font-size: $font-xl;
        margin-right: 20rpx;
        width: $size-6;
        text-align: center;
      }
      
      .menu-label {
        font-size: $font-md;
        color: $fitness-text;
      }
    }
    
    .menu-right {
      .arrow {
        font-size: $font-xl;
        color: $fitness-text-light;
        font-weight: bold;
      }
    }
  }
}
</style>