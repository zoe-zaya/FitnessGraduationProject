<!--个人中心页面：管理身体数据，个人资料，账号与安全，退出登录-->
<template>
    <view class="container">
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <image 
          :src="userInfo.avatar_url || '/static/default-avatar.png'" 
          class="avatar" 
          mode="aspectFill"
        />
        <view class="user-info">
          <view class="user-base-info">
            <text class="name">{{ userInfo.name || '未设置昵称' }}</text>
          </view>
          <!--<text class="phone">{{ userInfo.phone || '未绑定手机号' }}</text>-->
          <view class="tags" v-if="userInfo.fitness_goal">
            <text class="tag" v-if="userInfo.gender" :class="{'male': userInfo.gender === 'male', 'female': userInfo.gender === 'female'}">
              {{ userInfo.gender === 'male' ? '♂' : '♀' }}
            </text>
            <text class="tag">{{ userInfo.fitness_goal }}</text>
            <text class="tag">{{ userInfo.experience_level }}</text>
          </view>
        </view>
      </view>
      
      <!-- 功能菜单 -->
      <view class="menu-section">
        <view class="menu-group">
          <text class="group-title">健康管理</text>
          
          <view class="menu-item" @click="navigateToBodyData">
            <view class="menu-left">
              <text class="menu-icon">📊</text>
              <text class="menu-label">身体数据</text>
            </view>
            <view class="menu-right">
              <text class="menu-value">{{ bmi ? 'BMI: ' + bmi : '未设置' }}</text>
              <text class="arrow">></text>
            </view>
          </view>
          
          <view class="menu-item" @click="navigateToProfile">
            <view class="menu-left">
              <text class="menu-icon">👤</text>
              <text class="menu-label">个人资料</text>
            </view>
            <view class="menu-right">
              <text class="arrow">></text>
            </view>
          </view>
        </view>
        
        <view class="menu-group">
          <text class="group-title">账号安全</text>
          
          <view class="menu-item" @click="navigateToSecurity">
            <view class="menu-left">
              <text class="menu-icon">🔒</text>
              <text class="menu-label">账号与安全</text>
            </view>
            <view class="menu-right">
              <text class="arrow">></text>
            </view>
          </view>
        </view>
        
        <view class="menu-group">
          <view class="menu-item logout" @click="handleLogout">
            <view class="menu-left">
              <text class="menu-icon">🚪</text>
              <text class="menu-label">退出登录</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { onShow, onLoad } from '@dcloudio/uni-app' 
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const userStore = useUserStore()
  const userInfo = computed(() => userStore.userInfo)
  const bmi = computed(() => userStore.bmi)
  
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
  
  const navigateToBodyData = () => {
    uni.navigateTo({ url: '/pages/profile/body-data' })
  }
  
  const navigateToProfile = () => {
    uni.navigateTo({ url: '/pages/profile/edit-profile' })
  }
  
  const navigateToSecurity = () => {
    uni.navigateTo({ url: '/pages/profile/security' })
  }
  
  const handleLogout = () => {
    uni.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          userStore.logout()
          uni.reLaunch({ url: '/pages/login/login' })
        }
      }
    })
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: $fitness-bg;
    padding-bottom: 40rpx;
  }
  
  .user-card {
    background: $fitness-primary;
    padding: 60rpx 40rpx 40rpx;
    display: flex;
    align-items: center;
    
    .avatar {
      width: 120rpx;
      height: 120rpx;
      border-radius: 60rpx;
      border: 4rpx solid #FFFFFF;
      margin-right: 30rpx;
    }
    
    .user-info {
      flex: 1;
      
      .user-base-info {
        display: flex;
        align-items: center;
        margin-bottom: 10rpx;
        
        .name {
          font-size: $font-xl;
          font-weight: bold;
          color: #FFFFFF;
        }
        
        .gender-icon {
          display: inline-block;
          width: 40rpx;
          height: 40rpx;
          line-height: 40rpx;
          text-align: center;
          background: rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          font-size: $font-sm;
          color: #FFFFFF;
          margin-left: 20rpx;
          
          &.male {
            background: rgba(64, 158, 255, 0.3); /* 蓝色背景表示男性 */
          }
          
          &.female {
            background: rgba(255, 107, 141, 0.3); /* 粉色背景表示女性 */
          }
        }
      }
      
      .name {
        display: block;
        font-size: $font-xl;
        font-weight: bold;
        color: #FFFFFF;
      }
      
      .phone {
        display: block;
        font-size: $font-xs;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 15rpx;
      }
      
      .tags {
        display: flex;
        
        .tag {
          background: rgba(255, 255, 255, 0.2);
          color: #FFFFFF;
          font-size: $font-xs;
          padding: 6rpx 16rpx;
          border-radius: 20rpx;
          margin-right: 15rpx;
        }
      }
    }
  }
  
  .menu-section {
    margin-top: 30rpx;
    
    .menu-group {
      background: #FFFFFF;
      margin-bottom: 30rpx;
      
      .group-title {
        display: block;
        font-size: $font-xs;
        color: $fitness-text-gray;
        padding: 20rpx 30rpx 10rpx;
      }
      
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
            font-size: 36rpx;
            margin-right: 20rpx;
          }
          
          .menu-label {
            font-size: $font-md;
            color: $fitness-text;
          }
        }
        
        .menu-right {
          display: flex;
          align-items: center;
          
          .menu-value {
            font-size: $font-sm;
            color: $fitness-text-gray;
            margin-right: 15rpx;
          }
          
          .arrow {
            font-size: $font-sm;
            color: $fitness-placeholder;
          }
        }
        
        &.logout {
          .menu-label {
            color: $uni-error;
          }
        }
      }
    }
  }
  </style>