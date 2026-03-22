<template>
    <view class="container">
      <!--<view class="header">
        <text class="title">注册账号</text>
        <text class="subtitle">创建您的健身账户</text>
      </view>-->
      
      <view class="form-section">
        <view class="input-wrapper">
          <view class="input-item">
            <input 
              v-model="formData.phone" 
              type="number" 
              placeholder="请输入 11 位手机号"
              class="input"
              maxlength="11"
            />
          </view>
          
          <view class="input-item input-with-border">
            <input 
              v-model="formData.password" 
              type="password" 
              placeholder="8 位以上，含大小写数字符号"
              class="input"
            />
          </view>
          
          <view class="input-item">
            <input 
              v-model="formData.confirmPassword" 
              type="password" 
              placeholder="请再次输入密码"
              class="input"
            />
          </view>
        </view>
        
        <view class="password-tip">
          <text>密码需包含大小写字母、数字和特殊符号!@#$%^&*()_+-=</text>
        </view>
        
        <view class="agreement-section">
          <!-- 使用自定义图标代替checkbox -->
          <view class="agreement-item" @click="toggleAgreement">
            <view class="custom-checkbox" :class="{ checked: agreed }">
              <text v-if="agreed" class="checkmark">✓</text>
            </view>
            <text class="agreement-text">
              我已阅读并同意
              <text class="link" @click.stop="showAgreement('user')">《用户协议》</text>
              <text>和</text>
              <text class="link" @click.stop="showAgreement('privacy')">《隐私政策》</text>
            </text>
          </view>
        </view>
        
        <button 
          class="register-btn" 
          :disabled="!isFormValid"
          @click="handleRegister" 
        >
        注册
        </button>
      </view>
      
      <view class="login-link" @click="navigateToLogin">
        已有账号？
        <text class="link-text">立即登录</text>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import request from '@/utils/request'
  import { API, PASSWORD_REGEX, PHONE_REGEX } from '@/utils/constants'
  
  //const loading = ref(false)
  const agreed = ref(false)
  
  const formData = ref({
    phone: '',
    password: '',
    confirmPassword: ''
  })
  
  // 计算属性，判断表单是否有效
  const isFormValid = computed(() => {
    return formData.value.phone.length === 11 &&
           PASSWORD_REGEX.test(formData.value.password) &&
           formData.value.password === formData.value.confirmPassword &&
           agreed.value;
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
    if (!PHONE_REGEX.test(formData.value.phone)) {
      uni.showToast({ 
        title: '请输入有效的手机号', 
        icon: 'none',
        duration: 3000
      })
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
    
    //loading.value = true
    
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
        navigateToLogin()
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
      //loading.value = false
      agreed.value = false; // 注册完成后重置协议同意状态
      uni.reLaunch({ url: '/pages/register/register' });
    }
  }
  
  // 切换协议同意状态
  const toggleAgreement = () => {
    agreed.value = !agreed.value;
  }

  const showAgreement = (type) => {
    // 这里可以实现显示协议内容的逻辑
    console.log(`显示${type === 'user' ? '用户协议' : '隐私政策'}`)
    // 可以通过模态框或跳转页面展示协议内容
  }

  const navigateToLogin = () => {
    uni.reLaunch({ url: '/pages/login/login' })
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background-color: $fitness-secondary;
    padding: 60rpx 40rpx 40rpx;
  }
  
  .header {
    text-align: center;
    margin-bottom: 60rpx;
    
    .title {
      display: block;
      font-size: $font-xxl;
      font-weight: 700;
      color: $fitness-text;
      margin-bottom: 10rpx;
    }
    
    .subtitle {
      display: block;
      font-size: $font-md;
      color: $fitness-text-light;
    }
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
        padding: 0 $spacing-lg;
        box-sizing: border-box;
      }
    }
    
    .password-tip {
      font-size: $font-sm;
      color: $fitness-text-light;
      margin: $spacing-md 0 $spacing-lg;
      padding: 0 $spacing-xs;
    }
    
    .agreement-section {
      margin-bottom: $spacing-lg;
      
      .agreement-item {
        display: flex;
        align-items: center;
        padding: $spacing-md 0;
        
        .custom-checkbox {
          width: 40rpx;
          height: 40rpx;
          border: 2rpx solid $fitness-border;
          border-radius: $radius-sm;
          margin-right: $spacing-md;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          background: $fitness-primary;
          transition: background-color 0.3s;
          
          &.checked {
            background: $uni-primary;
            border-color: $uni-primary;
          }
          
          .checkmark {
            color: white;
            font-size: $font-md;
            line-height: 1;
            font-weight: bold;
          }
        }
        
        .agreement-text {
          flex: 1;
          font-size: $font-md;
          color: $fitness-text-light;
          line-height: 1.5;
          
          .link {
            color: $uni-primary;
            font-weight: 500;
          }
        }
      }
    }
    
    .register-btn {
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
  
  .login-link {
    text-align: center;
    font-size: $font-md;
    color: $fitness-text-light;
    margin-top: $spacing-lg;
    
    .link-text {
      color: $uni-primary;
      font-weight: 500;
    }
  }
  </style>