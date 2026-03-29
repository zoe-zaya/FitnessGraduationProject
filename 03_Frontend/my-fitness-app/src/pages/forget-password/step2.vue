<template>
  <view class="container">
    <!-- 表单区域 -->
    <view class="form-section">
      <view class="input-wrapper">
        <!-- 新密码输入 -->
        <view class="text">新密码</view>
        <view class="input-item">
          <img src="@/static/password2.png" class="icon"/>
          <input 
            v-model="formData.newPassword" 
            type="password" 
            placeholder="请输入新密码"
            class="input"
            :class="{ 'input-focus': focusedInput === 'password' }"
            @focus="onInputFocus('password')"
            @blur="onInputBlur"
          />
        </view>
        
        <!-- 确认密码输入 -->
        <view class="text">确认密码</view>
        <view class="input-item input-with-border">
          <img src="@/static/password2.png" class="icon"/>
          <input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            class="input"
            :class="{ 'input-focus': focusedInput === 'confirmPassword' }"
            @focus="onInputFocus('confirmPassword')"
            @blur="onInputBlur"
          />
          <uni-icons type="eye-filled" size="20" color="#8E8E93"></uni-icons>
        </view>
      </view>
      
      <view class="password-tip">
          <img src="@/static/exclamation-icon.png" class="icon"/>
          <text class="info">密码长度应大于8位，需包含大小写字母、数字和特殊符号。</text>
      </view>
      <view class="password-tip">
          <img src="@/static/exclamation-icon.png" class="icon"/>
          <text class="info">特殊符号是!@#$%^&*()_+-=。</text>
      </view> 

      <view class="password-info">       
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
const focusedInput = ref(null)

const formData = ref({
  newPassword: '',
  confirmPassword: ''
})

const onInputFocus = (inputName) => {
  focusedInput.value = inputName
}
  
const onInputBlur = () => {
  focusedInput.value = null
}

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
    background: url('@/static/background.png') no-repeat center center / cover;
    padding: $size-8 $size-6 $size-6;
    font-family: Manrope;
}

.form-section {
    background: rgba(252, 249, 248, 0.7);
    border-radius: $size-4;
    padding: $size-8;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
    .shadow-\[0_8px_24px_rgba\(160\2c 62\2c 64\2c 0\.06\)\] {
      --tw-shadow: 0 8px 24px rgba(160,62,64,0.06);
      --tw-shadow-colored: 0 8px 24px var(--tw-shadow-color);
      box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
    }

    .input-wrapper {
      .text{
          font-weight: 700;
          font-size: $size-3;
          line-height: $size-5;
          display: block;
          margin-left: $size-1;
          color: $color-label;
      }
  
      .input-item {
          position: relative;
          margin-bottom: $size-3;
          margin-top: $size-2;
          margin-bottom: 0;
          align-items: center;
          display: flex;
          position: relative;

          .icon{
              margin-left: $size-5;
              padding-bottom: $size-4;
              align-items: center;
              position: absolute;
              width: $size-4;
          }
    
          &:not(:last-child)::after {
              content: '';
              position: absolute;
              bottom: 0;
              left: $size-4;
              right: $size-4;
              height: 1rpx;
              background: #ffffff;
              transform: scaleY(0.5);
          }
    
          .input {
              transition-property: all;
              transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
              transition-duration: 150ms;
              color: $color-input;
              padding-right: $size-4;
              padding-left: $size-12;
              padding-top: $size-3;
              padding-bottom: $size-3;
              background-color: $fitness-primary;
              border-style: none;
              border-radius: $size-4;
              border: 2px solid rgba(160, 62, 64, 0.1);
              width: 100%;
              margin-bottom: $size-4;
              font-size: $size-4;
          }
          .input-focus {
              border: 2px solid rgba(160, 62, 64, 0.4);
          }
          uni-icons {
              position: absolute;
              right: $size-3;
              top: 50%;
              transform: translateY(-50%);
          }
      }
    }
  
  .password-info {
    padding: 0 $size-2;
    margin-bottom: $size-4;
    
    .tip {
      display: block;
      font-size: $size-3;
      color: $color-label;
      margin-bottom: $size-3;
    }
    
    .password-strength {
      display: flex;
      align-items: center;
      
      .strength-label {
        font-size: $size-3;
        color: $color-label;
        margin-right: $size-2;
      }
      
      .strength-value {
        font-size: $size-3;
        font-weight: 600;
        padding: $size-1 $size-4;
        border-radius: $size-2;
        
        &.strength-weak {
          color: $uni-error;
          background: $uni-error-bg;
        }
        
        &.strength-medium {
          color: $uni-warning;
          background: $uni-warning-bg;
        }
        
        &.strength-strong {
          color: $uni-success;
          background: $uni-success-bg;
        }
      }
    }
  }

  .password-tip {
    display: flex;
    margin-bottom: $size-2;

    .icon{
      margin-left: $size-1;
      padding-bottom: $size-3;
      padding-right: $size-3;
      align-items: center;
      width: $size-5;
    }
    .info{
      color: $color-label;
      font-size: $size-3;
      line-height: $size-4;
      font-weight: 525;
    }    
  }
  
  .submit-btn {
    width: 100%;
    height: $size-12;
    background: $uni-primary;
    color: #FFFFFF;
    font-size: $size-4;
    border-radius: $size-6;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    
    &[disabled] {
      opacity: 0.6;
    }
  }
}
</style>