<template>
    <view class="container">
      <view class="header">
        <text class="title">重置密码</text>
        <text class="subtitle">设置新的登录密码</text>
      </view>
      
      <view class="form-section">
        <view class="input-item">
          <text class="label">新密码</text>
          <input 
            v-model="formData.newPassword" 
            type="password" 
            placeholder="8 位以上，含大小写数字符号"
            class="input"
          />
        </view>
        
        <view class="input-item">
          <text class="label">确认密码</text>
          <input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            class="input"
          />
        </view>
        
        <button class="submit-btn" @click="handleSubmit" :loading="loading">
          确认重置
        </button>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { onLoad } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API, PASSWORD_REGEX } from '@/utils/constants'
  
  const loading = ref(false)
  const phone = ref('')
  
  const formData = ref({
    newPassword: '',
    confirmPassword: ''
  })
  
  onLoad((options) => {
    phone.value = options.phone || ''
  })
  
  const handleSubmit = async () => {
    // 密码复杂度校验
    if (!PASSWORD_REGEX.test(formData.value.newPassword)) {
      uni.showToast({ 
        title: '密码需 8 位以上，含大小写字母、数字和特殊符号', 
        icon: 'none' 
      })
      return
    }
    
    // 确认密码校验
    if (formData.value.newPassword !== formData.value.confirmPassword) {
      uni.showToast({ title: '两次密码不一致', icon: 'none' })
      return
    }
    
    loading.value = true
    
    try {
      // 开发环境直接返回
      uni.showToast({ title: '密码重置成功', icon: 'success' })
      setTimeout(() => {
        uni.navigateBack({ delta: 2 })
      }, 1000)
    } catch (error) {
      console.error('重置失败:', error)
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: $fitness-bg;
    padding: 60rpx 40rpx;
  }
  
  .header {
    text-align: center;
    margin-bottom: 60rpx;
    
    .title {
      display: block;
      font-size: $font-xxl;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 10rpx;
    }
    
    .subtitle {
      display: block;
      font-size: $font-sm;
      color: $fitness-text-gray;
    }
  }
  
  .form-section {
    .input-item {
      margin-bottom: 40rpx;
      
      .label {
        display: block;
        font-size: $font-md;
        color: $fitness-text-light;
        margin-bottom: 15rpx;
      }
      
      .input {
        width: 100%;
        height: 90rpx;
        background: #FFFFFF;
        border: 1rpx solid $fitness-border;
        border-radius: $radius-md;
        padding: 0 30rpx;
        font-size: $font-md;
        box-sizing: border-box;
      }
    }
    
    .submit-btn {
      width: 100%;
      height: 90rpx;
      background: $fitness-primary;
      color: #FFFFFF;
      font-size: $font-lg;
      border-radius: $radius-xl;
      border: none;
    }
  }
  </style>