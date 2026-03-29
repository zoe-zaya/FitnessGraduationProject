<template>
    <view class="container">
      <!-- 表单区域 -->
      <view class="form-section">
        <!-- 旧密码 -->
        <view class="input-item">
          <text class="label">当前密码</text>
          <input 
            v-model="formData.oldPassword" 
            type="password" 
            placeholder="请输入当前密码"
            class="input"
          />
        </view>
        
        <!-- 新密码 -->
        <view class="input-item">
          <text class="label">新密码</text>
          <input 
            v-model="formData.newPassword" 
            type="password" 
            placeholder="8 位以上，含大小写数字符号"
            class="input"
          />
        </view>
        
        <!-- 确认新密码 -->
        <view class="input-item">
          <text class="label">确认新密码</text>
          <input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="请再次输入新密码"
            class="input"
          />
        </view>
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
        
        <!-- 提交按钮 -->
        <button class="submit-btn" @click="handleSubmit" :loading="loading">
          确认修改
        </button>

        <view class="forget-password" @click="navigateToForget">
          忘记密码？
        </view>
      </view>
      
      <!-- 安全提示 -->
      <!--<view class="security-notice">
        <text class="notice-title">💡 密码安全建议</text>
        <text class="notice-content">
          1. 不要使用生日、手机号等易猜信息\n
          2. 定期更换密码，建议每 3 个月一次\n
          3. 不要与其他网站使用相同密码\n
          4. 密码修改后需使用新密码登录
        </text>
      </view>-->
    </view>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import request from '@/utils/request'
  import { API, PASSWORD_REGEX } from '@/utils/constants'
  import { useUserStore } from '@/store/user'
  
  const loading = ref(false)
  
  const formData = ref({
    oldPassword: '',
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
        duration: 3000
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
      uni.showModal({
        title: '提示',
        content: '密码修改成功，请使用新密码重新登录',
        showCancel: false,
        success: () => {
          // 退出登录，返回登录页面
          const userStore = useUserStore()
          userStore.logout()
          uni.redirectTo({ url: '/pages/login/login' })
        }
      })
      
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
    background: $fitness-primary;
    padding: 20rpx;
  }
  
  .form-section {
    background: #FFFFFF;
    padding: 30rpx;
    margin-bottom: 30rpx;
    
    .input-item {
      margin-bottom: 20rpx;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      border-radius: $radius-lg;
      border: 3.2rpx solid $fitness-border;

      
      &:last-child {
        margin-bottom: 0;
      }
      
      .label {
        width:25%;
        font-size: $font-md;
        color: $fitness-text;
        margin-left: 15rpx;
      }
      
      .input {
        width: 70%;
        height: 90rpx;
        background: $fitness-primary;
        border-radius: $radius-sm;
        padding: 0 30rpx;
        font-size: $font-md;
        box-sizing: border-box;
      }
    }
    .tip {
        display: block;
        font-size: $font-xs;
        color: $fitness-text-gray;
        margin-left: 10rpx;
      }
    
    .password-strength {
      display: flex;
      align-items: center;
      margin-top: 10rpx;
      padding: 10rpx;
      background: $fitness-primary;
      border-radius: $radius-sm;
      
      .strength-label {
        width: auto;
        font-size: $font-xs;
        color: $fitness-text-gray;
        margin-right: 10rpx;
      }
      
      .strength-value {
        width: auto;
        font-size: $font-xs;
        font-weight: bold;
        padding: 4rpx $size-2;
        border-radius: $radius-sm;
        
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
      height: $size-11;
      background: $uni-primary;
      color: #FFFFFF;
      font-size: $font-lg;
      border-radius: $radius-lg;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      margin-top: $size-5;
      
      &[disabled] {
        opacity: 0.6;
      }
    }
  }

  .forget-password {
      text-align: right;
      font-size: $font-xs;
      color: $uni-primary;
      margin-top: $size-5;
    }
  
  .security-notice {
    background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
    border-radius: $radius-md;
    padding: 30rpx;
    
    .notice-title {
      display: block;
      font-size: $font-md;
      font-weight: bold;
      color: #2E7D32;
      margin-bottom: 10rpx;
    }
    
    .notice-content {
      display: block;
      font-size: $font-xs;
      color: #388E3C;
      line-height: 2;
      white-space: pre-line;
    }
  }
  </style>