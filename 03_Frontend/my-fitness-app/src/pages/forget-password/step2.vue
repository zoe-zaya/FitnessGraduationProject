<template>
  <view class="container">
    <!-- 表单区域 -->
    <view class="form-section">
      <view class="input-wrapper">
        <!-- 新密码输入 -->
        <view class="input-item">
          <input 
            v-model="formData.newPassword" 
            type="password" 
            placeholder="8 位以上，含大小写数字符号"
            class="input"
          />
        </view>
        
        <!-- 确认密码输入 -->
        <view class="input-item input-with-border">
          <input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            class="input"
          />
        </view>
      </view>
      
      <view class="password-info">
        <text class="tip">需包含大小写字母、数字和特殊符号</text>
        
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
      </view>
      
      <!-- 确认按钮 -->
      <button class="submit-btn" @click="handleSubmit" :loading="loading" :disabled="loading">
        {{ loading ? '重置中...' : '确认重置' }}
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
  background-color: $fitness-secondary;
  padding: 60rpx 40rpx 40rpx;
}

.form-section {
  .input-wrapper {
    background: $fitness-primary;
    border-radius: $radius-lg;
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
    }
  }
  
  .password-info {
    background: $fitness-primary;
    border-radius: $radius-lg;
    padding: $spacing-lg;
    margin: $spacing-lg 0;
    box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
    
    .tip {
      display: block;
      font-size: $font-sm;
      color: $fitness-text-light;
      margin-bottom: $spacing-md;
    }
    
    .password-strength {
      display: flex;
      align-items: center;
      padding: 16rpx;
      background: $fitness-secondary;
      border-radius: $radius-md;
      
      .strength-label {
        font-size: $font-sm;
        color: $fitness-text-light;
        margin-right: 10rpx;
      }
      
      .strength-value {
        font-size: $font-sm;
        font-weight: 600;
        padding: 8rpx 16rpx;
        border-radius: $radius-md;
        
        &.strength-weak {
          color: $uni-error;
          background: rgba(255, 59, 48, 0.1);
        }
        
        &.strength-medium {
          color: $uni-warning;
          background: rgba(255, 149, 0, 0.1);
        }
        
        &.strength-strong {
          color: $uni-success;
          background: rgba(52, 199, 89, 0.1);
        }
      }
    }
  }
  
  .submit-btn {
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
</style>