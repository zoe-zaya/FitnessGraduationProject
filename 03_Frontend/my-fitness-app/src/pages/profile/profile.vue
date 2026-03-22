<!--个人中心页面：管理身体数据，个人资料，账号与安全-->
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
          <text class="name">{{ userInfo.name || '未设置昵称' }}</text>
          <!--<text class="phone">{{ userInfo.phone ? maskPhone(userInfo.phone) : '未绑定手机号' }}</text>-->
          <view class="tags">
            <text class="tag" v-if="userInfo.gender" :class="{'male': userInfo.gender === 'male', 'female': userInfo.gender === 'female'}">
              {{ userInfo.gender === 'male' ? '♂' : '♀' }}
            </text>
            <text class="tag" v-if="userInfo.age"> {{ userInfo.age }}岁</text>
            <text class="tag" v-if="userInfo.fitness_goal">{{ userInfo.fitness_goal }}</text>
            <text class="tag" v-if="userInfo.experience_level">{{ userInfo.experience_level }}</text>
          </view>
        </view>
      </view>
      
      <!-- 功能菜单 -->
      <view class="menu-section">
        <view class="menu-group">
          <view class="menu-item border-bottom" @click="navigateToBodyData">
            <view class="menu-left">
              <text class="menu-icon">📊</text>
              <text class="menu-label">身体数据</text>
            </view>
            <view class="menu-right">
              <text class="menu-value">{{ bmi ? 'BMI: ' + bmi : '未设置' }}</text>
              <text class="arrow">›</text>
            </view>
          </view>
          
          <view class="menu-item" @click="navigateToProfile">
            <view class="menu-left">
              <text class="menu-icon">👤</text>
              <text class="menu-label">个人资料</text>
            </view>
            <view class="menu-right">
              <text class="arrow">›</text>
            </view>
          </view>
        </view>
        
        <view class="menu-group">
          <view class="menu-item" @click="navigateToSecurity">
            <view class="menu-left">
              <text class="menu-icon">🔒</text>
              <text class="menu-label">账号与安全</text>
            </view>
            <view class="menu-right">
              <text class="arrow">›</text>
            </view>
          </view>
        </view>
        
        <view class="menu-group">
          <view class="menu-item destructive" @click="handleLogout">
            <view class="menu-left">
              <text class="menu-icon logout-icon">🚪</text>
              <text class="menu-label logout-label">退出登录</text>
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
   * 对手机号进行脱敏处理
   */
  const maskPhone = (phone) => {
    return phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2");
  }
  
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
      confirmColor: '#FF3B30', // iOS删除按钮颜色
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
    background-color: $fitness-secondary;
    padding-bottom: 40rpx;
  }
  
  .user-card {
    background: $fitness-primary;
    padding: 60rpx 40rpx 40rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
    
    .avatar {
      width: 120rpx;
      height: 120rpx;
      border-radius: $radius-xl;
      margin-right: 30rpx;
    }
    
    .user-info {
      flex: 1;
      
      .name {
        display: block;
        font-size: $font-xl;
        font-weight: 600;
        color: $fitness-text;
        margin-bottom: 8rpx;
      }
      
      .phone {
        display: block;
        font-size: $font-md;
        color: $fitness-text-light;
        margin-bottom: 20rpx;
      }
      
      .tags {
        display: flex;
        
        .tag {
          background: $fitness-secondary;
          color: $fitness-text;
          font-size: $font-sm;
          padding: 10rpx 20rpx;
          border-radius: $radius-lg;
          margin-right: 15rpx;
        }
        
        .male {
          color: #1E90FF;
        }
        
        .female {
          color: #FF69B4;
        }
      }
    }
  }
  
  .menu-section {
    margin-top: $spacing-lg;
    padding: 0 $spacing-lg;
    
    .menu-group {
      background: $fitness-primary;
      border-radius: $radius-lg;
      overflow: hidden;
      margin-bottom: $spacing-lg;
      box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .menu-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 36rpx $spacing-lg;
      position: relative;
      background: $fitness-primary;
      
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
      
      &.destructive {
        .menu-icon, .menu-label {
          color: $uni-error;
        }
      }
      
      .menu-left {
        display: flex;
        align-items: center;
      }
      
      .menu-icon {
        font-size: $font-lg;
        margin-right: 20rpx;
        width: 40rpx;
        text-align: center;
      }
      
      .logout-icon {
        color: $uni-error;
      }
      
      .menu-label {
        font-size: $font-md;
        color: $fitness-text;
      }
      
      .logout-label {
        color: $uni-error;
      }
      
      .menu-value {
        font-size: $font-sm;
        color: $fitness-text-light;
        margin-right: 10rpx;
      }
      
      .arrow {
        font-size: $font-xl;
        color: $fitness-text-light;
        font-weight: bold;
      }
    }
  }
  </style>