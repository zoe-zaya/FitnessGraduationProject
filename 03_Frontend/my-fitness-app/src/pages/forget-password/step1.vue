<template>
  <view class="container">
    <!-- 表单区域 -->
    <view class="form-section">
      <view class="input-wrapper">
        <!-- 手机号输入 -->
        <view class="input-item">
          <input 
            v-model="formData.phone" 
            type="number" 
            placeholder="请输入手机号"
            class="input"
            maxlength="11"
          />
        </view>
        
        <!-- 验证码输入 -->
        <view class="input-item input-with-border">
          <view class="code-input-wrapper">
            <input 
              v-model="formData.code" 
              type="number" 
              placeholder="请输入 6 位验证码"
              class="input"
              maxlength="6"
            />
            <button 
              class="code-btn" 
              @click="sendCode" 
              :disabled="countdown > 0 || !formData.phone"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </button>
          </view>
        </view>
      </view>
      
      <!-- 提示信息 -->
      <view class="tip-text">
        验证码将发送至您的手机号上
      </view>
      
      <!-- 下一步按钮 -->
      <button class="next-btn" @click="handleNext" :loading="loading" :disabled="loading">
        {{ loading ? '验证中...' : '下一步' }}
      </button>
    </view>
    
    <!-- 返回登录 -->
    <view class="back-login" @click="backToLogin">
      返回登录
    </view>
  </view>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'  // ✅ 修复：添加 onUnmounted 导入
import request from '@/utils/request'
import { API, PHONE_REGEX, CONFIG } from '@/utils/constants'

const loading = ref(false)
const countdown = ref(0)
let countdownTimer = null

const formData = ref({
  phone: '',
  code: ''
})

/**
 * 发送验证码
 */
const sendCode = async () => {
  // 1. 验证手机号格式
  if (!formData.value.phone) {
    uni.showToast({ title: '请输入手机号', icon: 'none', duration: 2000 })
    return
  }
  
  if (!PHONE_REGEX.test(formData.value.phone)) {
    uni.showToast({ 
      title: '请输入有效的手机号', 
      icon: 'none', 
      duration: 2000 
    })
    return
  }
  
  try {
    // 2. 调用发送验证码 API
    await request.post(API.SEND_CODE, {
      phone: formData.value.phone,
      type: 'reset_password'
    })
    
    uni.showToast({ title: '验证码已发送', icon: 'success', duration: 1500 })
    
    // 3. 开始倒计时
    startCountdown()
    
  } catch (error) {
    console.error('发送验证码失败:', error)
  }
}

/**
 * 验证码倒计时
 */
const startCountdown = () => {
  countdown.value = CONFIG.CODE_COUNTDOWN_SECONDS
  
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
  
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

/**
 * 验证手机号和验证码
 */
const handleNext = async () => {
  // 1. 验证手机号
  if (!formData.value.phone || !PHONE_REGEX.test(formData.value.phone)) {
    uni.showToast({ 
      title: '请输入正确的 11 位手机号', 
      icon: 'none', 
      duration: 2000 
    })
    return
  }
  
  // 2. 验证验证码
  if (!formData.value.code || formData.value.code.length !== 6) {
    uni.showToast({ 
      title: '请输入 6 位验证码', 
      icon: 'none', 
      duration: 2000 
    })
    return
  }
  
  loading.value = true
  
  try {
    // 3. 调用验证验证码 API
    await request.post(API.VERIFY_CODE, {
      phone: formData.value.phone,
      code: formData.value.code,
      type: 'reset_password'
    })
    
    // 4. 验证成功，跳转至重置密码页面
    uni.navigateTo({ 
      url: `/pages/forget-password/step2?phone=${formData.value.phone}` 
    })
    
  } catch (error) {
    console.error('验证失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 返回登录页面
 */
const backToLogin = () => {
  //uni.navigateBack({ delta: 1 })
  uni.redirectTo({ url: '/pages/login/login' })
}

/**
 * 页面卸载时清除定时器
 * 防止页面关闭后定时器仍在运行导致内存泄漏
 */
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background-color: $fitness-primary;
  padding: 60rpx 40rpx 40rpx;
}

.form-section {
  .input-wrapper {
    background: $fitness-primary;
    border-radius: $radius-lg;
    border: 3.5rpx solid $fitness-border;
    box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
    overflow: hidden;
  }
  
  .input-item {
    position: relative;
    padding: 0 $spacing-lg;
    
    &:not(:last-child)::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: $spacing-lg;
      right: $spacing-lg;
      height: 1rpx;
      background: $fitness-border;
      transform: scaleY(0.5);
    }
    
    .input {
      width: 100%;
      height: 96rpx;
      font-size: $font-md;
      color: $fitness-text;
      padding: 0;
      box-sizing: border-box;
      border: none;
      border-bottom: 1rpx solid $fitness-border;
    }
  }
  
  .code-input-wrapper {
    display: flex;
    align-items: center;
    
    .input {
      flex: 1;
      margin-right: $spacing-md;
    }
    
    .code-btn {
      width: 170rpx;
      height: 80rpx;
      background: $uni-primary;
      color: #FFFFFF;
      font-size: $font-sm;
      border-radius: $radius-md;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 500;
      
      &[disabled] {
        opacity: 0.5;
      }
    }
  }
  
  .tip-text {
    font-size: $font-sm;
    color: $fitness-text-light;
    text-align: center;
    margin: $spacing-lg 0;
  }
  
  .next-btn {
    width: 100%;
    height: 88rpx;
    background: $uni-primary;
    color: #FFFFFF;
    font-size: $font-lg;
    border-radius: $radius-lg;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    
    &[disabled] {
      opacity: 0.6;
    }
  }
}

.back-login {
  text-align: center;
  font-size: $font-md;
  color: $uni-primary;
  margin-top: $spacing-lg;
}
</style>