<template>
  <view class="container">
    <!-- 头部 -->
    <!--<view class="header">
      <text class="title">重置密码</text>
      <text class="subtitle">设置新的登录密码</text>
    </view>-->
    
    <!-- 表单区域 -->
    <view class="form-section">
      <!-- 新密码输入 -->
      <view class="input-item">
        <text class="label">新密码</text>
        <input 
          v-model="formData.newPassword" 
          type="password" 
          placeholder="8 位以上，含大小写数字符号"
          class="input"
        />
        <text class="tip">需包含大小写字母、数字和特殊符号</text>
      </view>
      
      <!-- 确认密码输入 -->
      <view class="input-item">
        <text class="label">确认密码</text>
        <input 
          v-model="formData.confirmPassword" 
          type="password" 
          placeholder="请再次输入密码"
          class="input"
        />
      </view>
      
      <!-- 密码强度提示 -->
      <view class="password-strength" v-if="formData.newPassword">
        <text class="strength-label">密码强度：</text>
        <text 
          class="strength-value" 
          :class="passwordStrengthClass"
        >
          {{ passwordStrengthText }}
        </text>
      </view>
      
      <!-- 确认按钮 -->
      <button class="submit-btn" @click="handleSubmit" :loading="loading">
        确认重置
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API, PASSWORD_REGEX } from '@/utils/constants'

const loading = ref(false)
const phone = ref('')

const formData = ref({
  newPassword: '',
  confirmPassword: ''
})

/**
 * 计算密码强度
 */
const passwordStrength = computed(() => {
  const pwd = formData.value.newPassword
  if (!pwd) return 0
  
  let strength = 0
  if (pwd.length >= 8) strength++
  if (/[a-z]/.test(pwd)) strength++
  if (/[A-Z]/.test(pwd)) strength++
  if (/\d/.test(pwd)) strength++
  if (/[!@#$%^&*()_+=-]/.test(pwd)) strength++
  
  return strength
})

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 2) return 'strength-weak'
  if (strength <= 4) return 'strength-medium'
  return 'strength-strong'
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 2) return '弱'
  if (strength <= 4) return '中'
  return '强'
})

/**
 * 页面加载时获取手机号参数
 */
onLoad((options) => {
  phone.value = options.phone || ''
})

/**
 * 重置密码
 * 对应《需求规格说明书》3.2 节忘记密码用例步骤 5-6
 */
const handleSubmit = async () => {
  // 1. 验证新密码复杂度（对应扩展事件流 6a）
  if (!PASSWORD_REGEX.test(formData.value.newPassword)) {
    uni.showToast({ 
      title: '密码需 8 位以上，含大小写字母、数字和特殊符号', 
      icon: 'none',
      duration: 3000
    })
    return
  }
  
  // 2. 验证确认密码（对应扩展事件流 6b）
  if (formData.value.newPassword !== formData.value.confirmPassword) {
    uni.showToast({ 
      title: '两次输入的密码不一致', 
      icon: 'none',
      duration: 2000
    })
    return
  }
  
  loading.value = true
  
  try {
    // 3. 调用重置密码 API
    await request.post(API.RESET_PASSWORD, {
      phone: phone.value,
      new_password: formData.value.newPassword,
      confirm_password: formData.value.confirmPassword
    })
    
    // 4. 重置密码成功，返回登录页面
    uni.showToast({ title: '密码重置成功', icon: 'success', duration: 1500 })
    
    setTimeout(() => {
      // 返回登录页面（delta=2 表示返回两层）
      //uni.navigateBack({ delta: 2 })
      uni.redirectTo({ url: '/pages/login/login' })
    }, 1000)
    
  } catch (error) {
    console.error('重置失败:', error)
    // 对应《需求规格说明书》：重置密码失败则保持在原页面并提示
    uni.showToast({ 
      title: '重置密码失败，请重试', 
      icon: 'none',
      duration: 2000
    })
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
  margin-bottom: 80rpx;
  
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
    position: relative;
    
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
    
    .tip {
      display: block;
      font-size: $font-xs;
      color: $fitness-text-gray;
      margin-top: 10rpx;
    }
  }
  
  .password-strength {
    display: flex;
    align-items: center;
    margin-bottom: 40rpx;
    padding: 20rpx;
    background: #FFFFFF;
    border-radius: $radius-sm;
    
    .strength-label {
      font-size: $font-xs;
      color: $fitness-text-gray;
      margin-right: 10rpx;
    }
    
    .strength-value {
      font-size: $font-xs;
      font-weight: bold;
      padding: 4rpx 16rpx;
      border-radius: 20rpx;
      
      &.strength-weak {
        color: $uni-error;
        background: rgba(255, 68, 68, 0.1);
      }
      
      &.strength-medium {
        color: $uni-warning;
        background: rgba(255, 159, 0, 0.1);
      }
      
      &.strength-strong {
        color: $uni-success;
        background: rgba(24, 179, 123, 0.1);
      }
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