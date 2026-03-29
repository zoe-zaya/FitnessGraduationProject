<!--个人中心页面：管理身体数据，个人资料，账号与安全-->
<template>
    <view class="container">
      <!-- 用户信息卡片 -->
      <view class="user-card" @click="navigateToProfile">
        <image 
          :src="userInfo.avatar_url || '/static/default-avatar.png'" 
          class="avatar" 
          mode="aspectFill"
        />
        <view class="user-info">
          <view class="name">
            {{ userInfo.name || '未设置昵称' }}
            <text class="gender" v-if="userInfo.gender" :class="{'male': userInfo.gender === 'male', 'female': userInfo.gender === 'female'}">
              {{ userInfo.gender === 'male' ? '♂' : '♀' }}
            </text>
          </view>
          <!--<text class="phone">{{ userInfo.phone ? maskPhone(userInfo.phone) : '未绑定手机号' }}</text>-->
          <view class="tags">
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
              <img src="@/static/body-data.png" class="menu-icon"/>
              <text class="menu-label">身体数据</text>
            </view>
            <view class="menu-right">
              <text class="menu-value">{{ bmi ? 'BMI: ' + bmi : '未设置' }}</text>
              <text class="arrow">›</text>
            </view>
          </view>
          
          <view class="menu-item" @click="navigateToProfile">
            <view class="menu-left">
              <img src="@/static/profile-info.png" class="menu-icon"/>
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
              <img src="@/static/setting.png" class="menu-icon"/>
              <text class="menu-label">账号与安全</text>
            </view>
            <view class="menu-right">
              <text class="arrow">›</text>
            </view>
          </view>
        </view>
        
        <view class="menu-group destructive">
          <view class="menu-item destructive" @click="handleLogout">
            <view class="menu-left">
              <img src="@/static/logout.png" class="menu-icon"/>
              <text class="menu-label logout-label">退出登录</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, Static } from 'vue'
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
    background: url('@/static/background4.png') no-repeat center center / cover;
    //padding-bottom: $size-1;
    font-family: Manrope;
  }
  
  .user-card {
    background: rgba(252, 249, 248, 0.5);
    padding: $size-8 $size-5;
    border-radius: 0 0 $size-5 $size-5;
    display: flex;
    align-items: center;
    box-shadow: 0 1rpx 10rpx rgba(0, 0, 0, 0.12);

    .avatar {
      width: 180rpx;
      height: 180rpx;
      border-radius: 100rpx;
      border: 4rpx solid #ffffff;
      margin-right: 30rpx;
      box-shadow: 0 10px 30px -12px rgba(0, 0, 0, 0.2);;
    }
    
    .user-info {
      flex: 1;
      
      .name {
        display: flex;
        font-size: $size-6;
        font-weight: 700;
        border: 4rpx solid #ffffff;
        color: $color-input;
        margin-bottom: $size-1;
        align-items: center;

        .gender{
          font-size: $size-5;
          margin-left: $size-2;
          font-weight: 800;
        }
        .male {
          color: #1E90FF;
        }
        
        .female {
          color: #FF69B4;
        }
      }
      
      .tags {
        display: flex;
        
        .tag {
          background: $color-primary-light;
          color: $color-tag;
          font-size: $size-3;
          font-weight: 600;
          padding: $size-1 $size-2;
          border-radius: $size-5;
          border: 2px solid rgba(160, 62, 64, 0.1);
          margin-right: 15rpx;
        }
      }
    }
  }
  
  .menu-section {
    margin-top: $size-5;
    padding: 0 $size-6;
    
    .menu-group {
      background: $fitness-primary; //白色
      border-radius: $size-4;
      overflow: hidden; //隐藏溢出部分，保持圆角效果
      margin-bottom: $size-4;
      //border: 1px solid rgba(160, 62, 64, 0.12);
      box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
      
      &:last-child {
        margin-bottom: 0;
      }
      &.destructive {
        background: rgba(255, 255, 255, 0.2);
        border: 1.5px solid rgba(255, 59, 48, 0.3);
        //border: 1.5px solid rgba(160, 62, 64, 0.3);
      }
    }
    
    .menu-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $size-3 $size-4;
      position: relative;
      border: none;
      border-bottom: 1px solid rgba(160, 62, 64, 0.1);
      
      &.border-bottom::after {//最后一项的底部边框
        content: '';
        position: absolute;
        bottom: 0;
        left: $size-5;
        right: $size-5;
        height: 1rpx;
        background: rgba(160, 62, 64, 0.1);
        transform: scaleY(0.5);
      }
      
      &.destructive {
        justify-content: center;
        align-items: center;
        .menu-icon, .menu-label {
          //color: $uni-primary;
          font-weight: 500;
          color: #cf0e00;
          margin-right: $size-1;
          //color: $color-primary;
        }
      }
      
      .menu-left {
        display: flex;
        align-items: center;
      }
      
      .menu-icon {
        font-size: $size-5;
        margin-right: $size-4;
        width: $size-6;
      }
      
      .logout-icon {
        color: $uni-error;
      }
      
      .menu-label {
        font-size: $size-4;
        //color: $fitness-text;
        color: $color-input;
      }
      
      .logout-label {
        color: $uni-error;
      }
      
      .menu-right {
        display: flex;
        align-items: center;
      }

      .menu-value {
        font-size: $size-3;
        color: $color-secondory;
        margin-right: 10rpx;
      }
      
      .arrow {
        font-size: $size-5;
        color: $color-secondory;
        padding-bottom: $size-1;
      }
    }
  }
  </style>