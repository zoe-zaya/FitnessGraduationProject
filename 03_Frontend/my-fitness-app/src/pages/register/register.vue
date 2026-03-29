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
            :class="{ 'input-focus': focusedInput === 'phone' }"
            @focus="onInputFocus('phone')"
            @blur="onInputBlur"
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
            :class="{ 'input-focus': focusedInput === 'password' }"
            @focus="onInputFocus('password')"
            @blur="onInputBlur"
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
            :class="{ 'input-focus': focusedInput === 'confirmPassword' }"
            @focus="onInputFocus('confirmPassword')"
            @blur="onInputBlur"

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
            <text v-if="agreed" class="checkmark">√</text>
          </view>
          <text class="agreement-text">
            我已阅读并同意
            <text class="link" @click.stop="showAgreement('user')">用户协议 </text>
            <text>和</text>
            <text class="link" @click.stop="showAgreement('privacy')"> 隐私政策</text>
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

      <view class="login-link" @click="navigateToLogin">
      已有账号？
      <text class="link-text">立即登录</text>
    </view>
    </view>    
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import request from '@/utils/request'
import { API, PASSWORD_REGEX, PHONE_REGEX } from '@/utils/constants'

//const loading = ref(false)
const agreed = ref(false)
const focusedInput = ref(null)

const formData = ref({
  phone: '',
  password: '',
  confirmPassword: ''
})

const onInputFocus = (inputName) => {
    focusedInput.value = inputName
}
  
const onInputBlur = () => {
  focusedInput.value = null
}

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
    padding: $size-3 $size-6 $size-6;
}

.logo-section {
    text-align: center;
    margin-bottom: $size-5;

    .logo {
        width: 220rpx;
        height: 220rpx;
    }

    .title {
        display: block;
        font-size: $size-8;
        font-weight: 700;
        color: $color-primary;      
        margin-bottom: 10rpx;
    }

    .subtitle {
        display: block;
        font-size: $size-3;
        color: $color-secondory;
    }
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
      
            .icon{
                margin-left: $size-5;
                padding-bottom: $size-4;
                align-items: center;
                position: absolute;
                width: $size-4;
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
              border: 2px solid rgba(160, 62, 64, 0.2);
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
  
  .agreement-section {
    margin-bottom: $size-3;
    .agreement-item {
      display: flex;
      align-items: center;
      
      .custom-checkbox {
        width: $size-5;
        height: $size-5;
        border: 2px solid rgba(160, 62, 64, 0.1);
        border-radius: $size-2;
        margin-right: $size-3;
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
          font-size: $size-3;
          line-height: 1;
          font-weight: bold;
        }
      }
      
      .agreement-text {
        --tw-text-opacity: 1;
        color: $color-label;
        line-height: 1;
        font-size: $size-3;

        .link {
          color: $color-primary;
          font-weight:700;
        }
      }
    }
  }
  
  .register-btn {
    width: 100%;
    height: $size-11;
    background: $button-bg2;
    color: #FFFFFF;
    font-size: $size-4;
    border-radius: $size-6;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    
    &[disabled] {
      opacity: 6;
    }
  }
}

.login-link {
  text-align: center;
  font-size: $size-3;
  color: $color-secondory;
  margin-top: $size-4;
  
  .link-text {
    color: $color-primary;
    font-weight: 700;
    font-family: Manrope;
  }
}
</style>