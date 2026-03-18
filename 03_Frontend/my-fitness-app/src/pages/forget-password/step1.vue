<template>
  <view class="container">
    <view class="header">
      <text class="title">忘记密码</text>
      <text class="subtitle">验证手机号重置密码</text>
    </view>
    
    <view class="form-section">
      <view class="input-item">
        <text class="label">手机号</text>
        <input 
          v-model="formData.phone" 
          type="number" 
          placeholder="请输入注册手机号"
          class="input"
          maxlength="11"
        />
      </view>
      
      <view class="input-item">
        <text class="label">验证码</text>
        <view class="code-input-wrapper">
          <input 
            v-model="formData.code" 
            type="number" 
            placeholder="请输入验证码"
            class="input"
            maxlength="6"
          />
          <button 
            class="code-btn" 
            @click="sendCode" 
            :disabled="countdown > 0"
          >
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </view>
      </view>
      
      <button class="next-btn" @click="handleNext" :loading="loading">
        下一步
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import request from '@/utils/request'

const loading = ref(false)
const countdown = ref(0)

const formData = ref({
  phone: '',
  code: ''
})

const sendCode = async () => {
  if (!formData.value.phone || formData.value.phone.length !== 11) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  
  // 开发环境模拟发送验证码
  uni.showToast({ title: '验证码已发送：123456', icon: 'success' })
  
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const handleNext = async () => {
  if (!formData.value.phone || formData.value.phone.length !== 11) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  
  if (!formData.value.code || formData.value.code.length !== 6) {
    uni.showToast({ title: '请输入 6 位验证码', icon: 'none' })
    return
  }
  
  loading.value = true
  
  try {
    // 开发环境直接跳转
    uni.navigateTo({ 
      url: `/pages/forget-password/step2?phone=${formData.value.phone}` 
    })
  } catch (error) {
    console.error('验证失败:', error)
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
  
  .code-input-wrapper {
    display: flex;
    align-items: center;
    
    .input {
      flex: 1;
      margin-right: 20rpx;
    }
    
    .code-btn {
      width: 200rpx;
      height: 90rpx;
      background: $uni-primary;
      color: #FFFFFF;
      font-size: $font-xs;
      border-radius: $radius-md;
      border: none;
      
      &[disabled] {
        background: #CCCCCC;
      }
    }
  }
  
  .next-btn {
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