<template>
    <view class="container">
      <view class="header">
        <text class="title">注册账号</text>
        <text class="subtitle">创建您的健身账户</text>
      </view>
      
      <view class="form-section">
        <view class="input-item">
          <text class="label">手机号</text>
          <input 
            v-model="formData.phone" 
            type="number" 
            placeholder="请输入 11 位手机号"
            class="input"
            maxlength="11"
          />
        </view>
        
        <view class="input-item">
          <text class="label">密码</text>
          <input 
            v-model="formData.password" 
            type="password" 
            placeholder="8 位以上，含大小写数字符号"
            class="input"
          />
          <text class="tip">需包含大小写字母、数字和特殊符号!@#$%^&*()_+-=</text>
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
        
        <view class="agreement">
          <view class="switch-wrapper">
            <switch 
              :checked="agreed" 
              @change="onAgreeChange"
              color="#007AFF"
              class="agreement-switch"
            />
          </view>
          <text class="agreement-text">
            我已阅读并同意
            <text class="link">《用户协议》</text>
            <text>和</text>
            <text class="link">《隐私政策》</text>
          </text>
        </view>
        
        <button class="register-btn" @click="handleRegister" :loading="loading">
          注册
        </button>
      </view>
      
      <view class="login-link" @click="navigateToLogin">
        已有账号？
        <text>立即登录</text>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import request from '@/utils/request'
  import { API, PASSWORD_REGEX } from '@/utils/constants'
  
  const loading = ref(false)
  const agreed = ref(false)
  
  const formData = ref({
    phone: '',
    password: '',
    confirmPassword: ''
  })
  
  /**
   * 处理注册
   * 对应《需求规格说明书》3.2 节注册用例
   */
  const handleRegister = async () => {
    // 1. 验证协议（对应扩展事件流）
    console.log('agreed.value', agreed.value)
    if (!agreed.value) {
      uni.showToast({ title: '请先同意用户协议', icon: 'none', duration: 2000 })
      return
    }
    
    // 2. 验证手机号
    if (!formData.value.phone || formData.value.phone.length !== 11) {
      uni.showToast({ title: '请输入正确的手机号', icon: 'none', duration: 2000 })
      return
    }
    
    // 3. 密码复杂度校验（对应扩展事件流 4a）
    if (!PASSWORD_REGEX.test(formData.value.password)) {
      uni.showToast({ 
        title: '密码需 8 位以上，含大小写字母、数字和特殊符号', 
        icon: 'none',
        duration: 3000
      })
      return
    }
    
    // 4. 确认密码校验（对应扩展事件流 4b）
    if (formData.value.password !== formData.value.confirmPassword) {
      uni.showToast({ title: '两次密码不一致', icon: 'none', duration: 2000 })
      return
    }
    
    loading.value = true
    
    try {
      // 5. 调用注册 API
      await request.post(API.REGISTER, {
        phone: formData.value.phone,
        password: formData.value.password,
        confirm_password: formData.value.confirmPassword
      })
      
      uni.showToast({ title: '注册成功', icon: 'success', duration: 1500 })
      
      // 6. 返回登录页（对应用例步骤 6）
      setTimeout(() => {
        uni.navigateBack()
      }, 1000)
      
    } catch (error) {
      console.error('注册失败:', error)
      // 检查错误类型并显示相应提示
      if (error.response && error.response.data && error.response.data.detail) {
        const errorMessage = error.response.data.detail;
        if (errorMessage.includes('该手机号已注册')) {
          uni.showToast({ 
            title: '该手机号已注册，请直接登录', 
            icon: 'none', 
            duration: 2000 
          });
        }
      } else {
        uni.showToast({ 
          title: '网络错误，请稍后重试', 
          icon: 'none', 
          duration: 2000 
        });
      }
    } finally {
      loading.value = false
    }
  }
  
  const onAgreeChange = (e) => {
    // switch 返回布尔值，直接赋值
    agreed.value = e.detail.value
  }

  const navigateToLogin = () => {
    uni.navigateBack()
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
    
    .agreement {
      display: flex;
      align-items: center;
      font-size: $font-xs;
      color: $fitness-text-light;
      margin-bottom: 40rpx;
      
      .switch-wrapper {
        display: flex;
        align-items: center;
        weight:0px;
        
        .agreement-switch {
          transform: scale(0.5);
          transform-origin: center left;
        }
      }
      
      .agreement-text {
        flex: 1;
        line-height: 1.5;
        
        .link {
          color: $uni-primary;
          margin: 0 5rpx;
        }
      }
    }
    
    .register-btn {
      width: 100%;
      height: 90rpx;
      background: $fitness-primary;
      color: #FFFFFF;
      font-size: $font-lg;
      border-radius: $radius-xl;
      border: none;
    }
  }
  
  .login-link {
    text-align: center;
    font-size: $font-md;
    color: $fitness-text-light;
    margin-top: 40rpx;
    
    text {
      color: $uni-primary;
    }
  }
  </style>