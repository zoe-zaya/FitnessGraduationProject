<template>
    <view class="container">
      <!-- Logo 区域 -->
      <view class="logo-section">
        <image src="@/static/logo.png" class="logo" mode="aspectFit" />
        <text class="title">TFit</text>
        <text class="subtitle">能够识别健身器材的健身APP</text>
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
          <view class="input-item input-with-margin">
            <img src="@/static/password2.png" class="icon"/>
            <input
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              class="input"
              :class="{ 'input-focus': focusedInput === 'password' }"
              @focus="onInputFocus('password')"
              @blur="onInputBlur"
            />
            <view class="eye-icon" @click="toggleShowPassword">
              <uni-icons :type="showPassword ? 'eye' : 'eye-filled'" size="20" color="#8E8E93"></uni-icons>
            </view>
          </view>
        </view>
        
        <view class="forget-password" @click="navigateToForget">
          忘记密码？
        </view>
        
        <button class="login-btn" @click="handleLogin" :loading="loading" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        
        <view class="register-link" @click="navigateToRegister">
          还没有账号？
          <text class="link-text">创建账号</text>
        </view>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const userStore = useUserStore()
const loading = ref(false)
const focusedInput = ref(null)
const showPassword = ref(false)

const formData = ref({
    phone: '',
    password: ''
})

const toggleShowPassword = () => {
    showPassword.value = !showPassword.value
}
  
  const onInputFocus = (inputName) => {
    focusedInput.value = inputName
  }
  
  const onInputBlur = () => {
    focusedInput.value = null
  }
  
  /**
   * 处理登录
   * 对应《需求规格说明书》3.2 节登录用例
   */
  const handleLogin = async () => {
    // 1. 验证输入（对应扩展事件流 2a, 2b）
    if (!formData.value.phone || formData.value.phone.length !== 11) {
      uni.showToast({ title: '请输入正确的手机号', icon: 'none', duration: 2000 })
      return
    }
    if (!formData.value.password) {
      uni.showToast({ title: '请输入密码', icon: 'none', duration: 2000 })
      return
    }
    
    loading.value = true
    
    try {
      // 2. 调用登录 API
      const res = await request.post(API.LOGIN, {
        phone: formData.value.phone,
        password: formData.value.password
      })
      
      // 3. 保存登录信息
      userStore.setLoginInfo(res.access_token, res.user_info)
      
      uni.showToast({ title: '登录成功', icon: 'success', duration: 1500 })
      
      // 4. 检查用户基本信息是否完整
      await checkProfileCompleteAndRedirect()
      
    } catch (error) {
      console.error('登录失败:', error)
      uni.showToast({ title: error.response.data.detail || '登录失败，请稍后重试', icon: 'none', duration: 2000 })
    } finally {
      loading.value = false
    }
  }
  
  const checkProfileCompleteAndRedirect = async () => {
    try{
      // 调用资料完整性检查接口
      const checkRes = await request.get(API.CHECK_PROFILE_COMPLETE)
      
      console.log('资料完整性检查结果:', checkRes)
      
      // 5. 根据完整性决定跳转页面
      if (checkRes.is_complete) {
        // 资料完整：跳转首页（用户管理模块阶段跳转个人中心）
        console.log('资料完整，跳转首页')
        setTimeout(() => {
          // 用户管理模块开发阶段，先跳转个人中心页面
          uni.reLaunch({ url: '/pages/profile/profile' })
          // 完整系统阶段改为：uni.reLaunch({ url: '/pages/index/index' })
        }, 1000)
      } else {
        // 资料不完整：跳转编辑个人资料
        // console.log('资料不完整，缺失字段:', checkRes.missing_fields)
        uni.showToast({ 
          title: '请先完善个人资料和身体数据', 
          icon: 'none', 
          duration: 1000 
        })
        setTimeout(() => {
          uni.redirectTo({ url: '/pages/profile/edit-profile-login' })
        }, 1500)
      }
    }catch(error){
      console.error('检查资料完整性失败:', error)
      uni.showToast({ 
          title: '检查资料完整性失败', 
          icon: 'none', 
          duration: 1000 
        })
      // 如果检查失败，默认跳转登陆页面
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/login/login' })
      }, 1000)
    }
  }
  const navigateToRegister = () => {
    uni.navigateTo({ url: '/pages/register/register' })
  }
  
  const navigateToForget = () => {
    uni.navigateTo({ url: '/pages/forget-password/step1' })
  }
  </script>
  
  <style lang="scss" scoped>
  @import '../../uni.scss';

  .container {
    min-height: 100vh;
    background: url('@/static/background.png') no-repeat center center / cover;
    padding: $size-4 $size-6 $size-6;
    font-family: Manrope;
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
          padding-top: $size-4;
          padding-bottom: $size-4;
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

        .eye-icon {
          position: absolute;
          right: $size-3;
          top: 50%;
          transform: translateY(-50%);
          padding: 10rpx;
        }
      }
    }

    .forget-password {
      text-align: right;
      font-size: $size-3;
      color: $color-primary;
      font-weight: 700;
      line-height: $size-4;
      margin-bottom: $size-3;
      font-family: Manrope;
    }

    .login-btn {
      width: 100%;
      height: $size-12;
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
        opacity: 0.6;
      }
    }

    .register-link {
      text-align: center;
      font-size: $size-3;
      color: $color-secondory;
      margin-top: $size-3;

      .link-text {
        color: $color-primary;
        font-weight: 700;
        font-family: Manrope;
      }
    }
  }
  </style>