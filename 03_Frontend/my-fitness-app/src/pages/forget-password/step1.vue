<template>
  <view class="container">
    <!-- 表单区域 -->
    <view class="form-section">
      <view class="input-wrapper">
        <!-- 手机号输入 -->
        <view class="text">手机号</view>
        <view class="input-item">
          <img src="@/static/phone2.png" class="icon"/>
          <input 
            v-model="formData.phone" 
            type="number" 
            placeholder="请输入手机号"
            class="input"
            maxlength="11"
          />
        </view>
        
        <!-- 验证码输入 -->
        <view class="text">验证码</view>
        <view class="input-item input-with-border">
          <view class="code-input-wrapper">
            <img src="@/static/verify-code.png" class="icon"/>
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
  background: url('@/static/background2.png') no-repeat center center / cover;
  padding: 60rpx $size-5 $size-5;
}

.form-section {
  background: rgba(252, 249, 248, 0.7);
  border-radius: $radius-l;
  padding: $size-8;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
  .shadow-\[0_8px_24px_rgba\(160\2c 62\2c 64\2c 0\.06\)\] {
    --tw-shadow: 0 8px 24px rgba(160,62,64,0.06);
    --tw-shadow-colored: 0 8px 24px var(--tw-shadow-color);
    box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
  }

  .input-wrapper {
    .text{
      font-weight: 700;
      font-size: 0.75rem;
      line-height: 1rem;
      font-family: Manrope;
      display: block;
      margin-left: 0.25rem;
      color: rgb(86 66 65 / var(--tw-text-opacity, 1));
    }
  }
  
  .input-item {
    position: relative;
    margin-bottom: 30rpx;
    --tw-space-y-reverse: 0;
    margin-top: calc(0.5rem * calc(1 - var(--tw-space-y-reverse)));
    margin-bottom: calc(0.5rem * var(--tw-space-y-reverse));
    align-items: center;
    display: flex;
    position: relative;
    
    .icon{
      margin-left: 36rpx;
      padding-bottom: 2$size-1;
      align-items: center;
      position: absolute;
      width:$size-4;
    }
    
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
      transition-property: all;
      transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
      transition-duration: 150ms;
      --tw-ring-color: rgb(220 192 191 / 0.2);
      --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
      --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(1px + var(--tw-ring-offset-width)) var(--tw-ring-color);
      box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
      --tw-text-opacity: 1;
      color: rgb(27 28 28 / var(--tw-text-opacity, 1));
      padding-right: $size-4;
      padding-left: $size-12;
      padding-top: $size-4;
      padding-bottom: $size-4;
      --tw-bg-opacity: 1;
      background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
      border-style: none;
      border-radius: $size-4;
      width: 100%;
      margin-bottom: $size-4;
      font-size: $font-lg;
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
      height: 100rpx;
      background: $uni-primary;
      color: #FFFFFF;
      font-size: $font-sm;
      border-radius: $size-4;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 500;
      margin-bottom: $size-4;

      
      &[disabled] {
        opacity: 0.6;
      }
    }
  }
  
  .tip-text {
    font-size: $font-sm;
    color: rgb(86, 66, 65, var(--tw-text-opacity, 1));    text-align: center;
    margin: $spacing-lg 0;
    font-weight: 550;
    font-family: Manrope;
  }
  
  .next-btn {
    width: 100%;
    height: $size-11;
    background: $button-bg2;
    color: #FFFFFF;
    font-size: $font-lg;
    border-radius: $radius-xl;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-family: Manrope;
    
    &[disabled] {
      opacity: 0.6;
    }
  }
}

.back-login {
  text-align: center;
  font-size: $font-md;
  color: rgb(160 62 64 / var(--tw-text-opacity, 1));
  margin-top: $spacing-lg;
  font-weight: 700;
  font-family: Manrope;
}
</style>