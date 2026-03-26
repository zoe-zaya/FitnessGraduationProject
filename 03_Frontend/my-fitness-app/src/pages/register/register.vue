<template>
  <view class="container">
    <!-- Logo 区域 -->
    <view class="logo-section">
        <text class="title">TFit</text>
        <text class="subtitle">能够识别健身器材并生成健身计划的健身APP</text>
    </view>
      
    <!-- 表单区域 -->
    <view class="form-section">
      <view class="input-wrapper">
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

        <view class="text">密码</view>
        <view class="input-item input-with-border">
          <img src="@/static/password2.png" class="icon"/>
          <input 
            v-model="formData.password" 
            type="password" 
            placeholder="输入 8 位以上的密码"
            class="input"
          />
        </view>

        <view class="text">确认密码</view>
        <view class="input-item">
          <img src="@/static/password2.png" class="icon"/>
          <input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            class="input"
          />
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
    background: url('@/static/background.png') no-repeat center center / cover;
    padding: 48rpx 48rpx 48rpx;
  }

  .logo-section {
    text-align: center;
    margin-bottom: 40rpx;

    .logo {
      width: 220rpx;
      height: 220rpx;
    }

    .title {
      display: block;
      font-size: $font-xxxl;
      font-weight: 700;
      color: rgb(160 62 64 / var(--tw-text-opacity, 1));      margin-bottom: 10rpx;
    }

    .subtitle {
      display: block;
      font-size: $font-md;
      color: $fitness-text-light;
    }
  }

.form-section {
  background: rgba(252, 249, 248, 0.7);
  border-radius: $radius-l;
  padding: 64rpx;
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
  
    .input-item {
      position: relative;
      margin-bottom: 30rpx;
      --tw-space-y-reverse: 0;
      margin-top: calc(0.5rem * calc(1 - var(--tw-space-y-reverse)));
      margin-bottom: calc(0.5rem * var(--tw-space-y-reverse));
      align-items: center;
      display: flex;
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
      
      .icon{
        margin-left: 36rpx;
        padding-bottom: 28rpx;
        align-items: center;
        position: absolute;
        width:32rpx;
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
        padding-right: 32rpx;
        padding-left: 96rpx;
        padding-top: 32rpx;
        padding-bottom: 32rpx;
        --tw-bg-opacity: 1;
        background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
        border-style: none;
        border-radius: 32rpx;
        width: 100%;
        margin-bottom: 32rpx;
        font-size: $font-lg;
      }
    }
  }
  .password-tip {
    display: flex;
    margin-bottom: 10rpx;

    .icon{
      margin-left: 6rpx;
      padding-bottom: 28rpx;
      padding-right: 14rpx;
      align-items: center;
      width:34rpx;
    }
    .info{
      color: rgb(86 66 65 / var(--tw-text-opacity, 1));
      font-size: $font-md;
      line-height: 32rpx;
      font-weight: 525
    }    
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
          background: $button-bg2;
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
        --tw-text-opacity: 1;
        color: rgb(86 66 65 / var(--tw-text-opacity, 1));
        line-height: 1.625;
        font-size: 24rpx;
        font-weight: 600;

        .link {
          color: rgb(160 62 64 / var(--tw-text-opacity, 1));
          font-weight:6500;
        }
      }
    }
  }
  
  .register-btn {
    width: 100%;
    height: 88rpx;
    background: $button-bg2;
    color: #FFFFFF;
    font-size: $font-lg;
    border-radius: $radius-xl;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    
    &[disabled] {
      opacity: 1;
    }
  }
}

.login-link {
  text-align: center;
  font-size: $font-md;
  color: $fitness-text-light;
  margin-top: 30rpx;
  
  .link-text {
    color: rgb(160 62 64 / var(--tw-text-opacity, 1));
    font-weight: 700;
    font-family: Manrope;
  }
}
</style>