<template>
  <view class="container">
    <!-- 当前账号信息 -->
    <view class="account-info">
      <text class="info-label">当前手机号</text>
      <div class="line"> </div>
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
  background: url('@/static/background.png') no-repeat center center / cover;
  padding: 0;
}

.account-info {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0 0 $size-5 $size-5;
  margin-bottom: $size-5;
  padding: $size-4 $size-6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1rpx 10rpx rgba(0, 0, 0, 0.15); // iOS风格阴影
  
  .info-label {
    font-size: $size-4;
    color: $color-label;
    //font-weight: 450;
  }
  
  .info-value {
    font-size: $size-4;
    font-weight: 700;
    //color: $color-label;
    color: $color-primary;
  }
  .line{
      --tw-bg-opacity: 1;
      background-color: $color-line;
      flex: 1 1 0%;
      height: 1px;
      margin-left: $size-4;
      margin-right: $size-4;
  }
}

.menu-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: $size-5;
  margin: 0 $size-6;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
  
  .menu-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $size-3 $size-4;
    position: relative;
    border-bottom: 4rpx solid rgba(160, 62, 64, 0.1);
    
    &:last-child {
      border-bottom: none;
      
      &::after {
        display: none;
      }
    }
    
    &.border-bottom::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: $size-1;
      right: $size-1;
      height: 1rpx;
      transform: scaleY(0.5);
    }
    
    .menu-left {
      display: flex;
      align-items: center;
      
      .menu-icon {
        font-size: $size-6;
        margin-right: $size-3;
        width: $size-6;
        text-align: center;
      }
      
      .menu-label {
        font-size: $size-4;
        color: $color-input;
      }
    }
    
    .menu-right {
      .arrow {
        font-size: $size-5;
        color: $color-secondory;
        font-weight: bold;
        display: flex;
        align-items: center;
        padding-bottom: $size-1;
      }
    }
  }
}
</style>