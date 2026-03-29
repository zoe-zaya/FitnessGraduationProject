<template>
    <view class="container">
      <!-- 表单区域 -->
      <view class="form-section">
        <view class="input-wrapper">
          <!-- 旧密码 -->
          <view class="text">当前密码</view>
          <view class="input-item">
            <img src="@/static/password2.png" class="icon"/>
            <input 
              v-model="formData.oldPassword" 
              type="password" 
              placeholder="请输入当前密码"
              class="input"
              :class="{ 'input-focus': focusedInput === 'oldPassword' }"
              @focus="onInputFocus('oldPassword')"
              @blur="onInputBlur"
            />
          </view>
        
          <!-- 新密码 -->
          <view class="text">新密码</view>
          <view class="input-item">
            <img src="@/static/password2.png" class="icon"/>
            <input 
              v-model="formData.newPassword" 
              type="password" 
              placeholder="请输入新密码"
              class="input"
              :class="{ 'input-focus': focusedInput === 'newPassword' }"
              @focus="onInputFocus('newPassword')"
              @blur="onInputBlur"
            />
          </view>
        
          <!-- 确认新密码 -->
          <view class="text">确认新密码</view>
          <view class="input-item">
            <img src="@/static/password2.png" class="icon"/>
            <input 
              v-model="formData.confirmPassword" 
              type="password" 
              placeholder="请再次输入新密码"
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

      <!-- 提交按钮 -->
      <button class="submit-btn" @click="handleSubmit" :loading="loading">
          确认修改
      </button>

      <view class="forget-password" @click="navigateToForget">
        忘记密码？
      </view>
    </view>
  </view>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import request from '@/utils/request'
  import { API, PASSWORD_REGEX } from '@/utils/constants'
  import { useUserStore } from '@/store/user'
  
  const loading = ref(false)
  const focusedInput = ref(null)
  
  const formData = ref({
    oldPassword: '',
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
   * 修改登录密码
   * 对应《需求规格说明书》3.2 节编辑账号与安全用例步骤 5-6
   */
  const handleSubmit = async () => {
    // 1. 验证旧密码不为空（对应扩展事件流 6a）
    if (!formData.value.oldPassword) {
      uni.showToast({ title: '请输入当前密码', icon: 'none', duration: 2000 })
      return
    }
    
    // 2. 验证新密码复杂度（对应扩展事件流 6a）
    if (!PASSWORD_REGEX.test(formData.value.newPassword)) {
      uni.showToast({ 
        title: '密码需 8 位以上，含大小写字母、数字和特殊符号', 
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    // 3. 验证确认密码（对应扩展事件流 6b）
    if (formData.value.newPassword !== formData.value.confirmPassword) {
      uni.showToast({ 
        title: '两次输入的密码不一致', 
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    // 4. 验证新旧密码是否相同
    if (formData.value.oldPassword === formData.value.newPassword) {
      uni.showToast({ 
        title: '新密码不能与当前密码相同', 
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    loading.value = true
    
    try {
      // 5. 调用修改密码 API
      await request.put(API.USER_SECURITY_PASSWORD, {
        old_password: formData.value.oldPassword,
        new_password: formData.value.newPassword,
        confirm_password: formData.value.confirmPassword
      })
      
      // 6. 修改成功提示
      uni.showToast({ title: '密码修改成功', icon: 'success', duration: 1500 })
      const userStore = useUserStore()
      userStore.logout()
      uni.redirectTo({ url: '/pages/login/login' })
      
    } catch (error) {
      console.error('修改失败:', error)
      // 错误信息已在 request 拦截器中处理
    } finally {
      loading.value = false
    }
  }
  const navigateToForget = () => {
    uni.navigateTo({ url: '/pages/forget-password/step1' })
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: url('@/static/background.png') no-repeat center center / cover;
    padding: $size-8 $size-6 $size-6;
  }
  
  .form-section {
    background: rgba(252, 249, 248, 0.7);
    border-radius: $size-4;
    padding: $size-8;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);

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

  .forget-password {
      text-align: right;
      font-size: $size-3;
      color: $color-primary;
      font-weight: 600;
      margin-top: $size-3;
    }
  </style>