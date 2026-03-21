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
      <view class="menu-item" @click="navigateToUpdatePhone">
        <view class="menu-left">
          <text class="menu-icon">📱</text>
          <text class="menu-label">修改手机号</text>
        </view>
        <view class="menu-right">
          <text class="arrow">></text>
        </view>
      </view>
      
      <!-- 修改登录密码 -->
      <view class="menu-item" @click="navigateToUpdatePassword">
        <view class="menu-left">
          <text class="menu-icon">🔐</text>
          <text class="menu-label">修改登录密码</text>
        </view>
        <view class="menu-right">
          <text class="arrow">></text>
        </view>
      </view>
    </view>
    
    <!-- 安全提示 -->
    <!--<view class="security-tip">
      <text class="tip-title">💡 安全提示</text>
      <text class="tip-content">
        为了您的账号安全，建议定期更换密码，不要使用过于简单的密码
      </text>
    </view>-->
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
  background: $fitness-bg;
  padding: 40rpx;
}

.account-info {
  background: #FFFFFF;
  border-radius: $radius-md;
  padding: 30rpx;
  margin-bottom: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .info-label {
    font-size: $font-md;
    color: $fitness-text-light;
  }
  
  .info-value {
    font-size: $font-lg;
    font-weight: bold;
    color: $fitness-text;
  }
}

.menu-section {
  background: #FFFFFF;
  border-radius: $radius-md;
  margin-bottom: 30rpx;
  
  .menu-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx;
    border-bottom: 1rpx solid $fitness-bg;
    
    &:last-child {
      border-bottom: none;
    }
    
    .menu-left {
      display: flex;
      align-items: center;
      
      .menu-icon {
        font-size: 40rpx;
        margin-right: 20rpx;
      }
      
      .menu-label {
        font-size: $font-md;
        color: $fitness-text;
      }
    }
    
    .menu-right {
      .arrow {
        font-size: $font-sm;
        color: $fitness-placeholder;
      }
    }
  }
}

.security-tip {
  background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
  border-radius: $radius-md;
  padding: 30rpx;
  
  .tip-title {
    display: block;
    font-size: $font-md;
    font-weight: bold;
    color: #1565C0;
    margin-bottom: 10rpx;
  }
  
  .tip-content {
    display: block;
    font-size: $font-xs;
    color: #1976D2;
    line-height: 1.6;
  }
}
</style>