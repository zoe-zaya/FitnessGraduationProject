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
              maxlength="11"
            />
          </view>
          
          <view class="text">密码</view>
          <view class="input-item input-with-margin">
            <img src="@/static/password2.png" class="icon"/>            
            <input 
              v-model="formData.password" 
              type="password" 
              placeholder="请输入密码"
              class="input"
            />
            <uni-icons type="eye-filled" size="20" color="#8E8E93"></uni-icons>
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
  
  const formData = ref({
    phone: '',
    password: ''
  })
  
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
          duration: 2000 
        })
        setTimeout(() => {
          uni.redirectTo({ url: '/pages/profile/edit-profile' })
        }, 1500)
      }
    }catch(error){
      console.error('检查资料完整性失败:', error)
      uni.showToast({ 
          title: '检查资料完整性失败', 
          icon: 'none', 
          duration: 2000 
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
    padding: 80rpx 48rpx 48rpx;
  }

  .logo-section {
    text-align: center;
    margin-bottom: 40rpx;

    .logo {
      width: 200rpx;
      height: 200rpx;
      margin-bottom: 20rpx;
    }

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

        uni-icons {
          position: absolute;
          right: 20rpx;
          top: 50%;
          transform: translateY(-50%);
        }
      }
    }

    .forget-password {
      text-align: right;
      font-size: $font-md;
      color: rgb(160 62 64 / var(--tw-text-opacity, 1));
      font-weight: 700;
      line-height: 32rpx;
      margin-bottom: 30rpx;
      font-family: Manrope;
    }

    .login-btn {
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
        opacity: 0.6;
      }
    }

    .register-link {
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
  }
  </style>