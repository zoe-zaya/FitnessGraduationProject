<template>
    <view class="container">
      <!-- Logo 区域 -->
      <view class="logo-section">
        <image src="@/static/logo.png" class="logo" mode="aspectFit" />
        <!--
        <text class="title">健身管理系统</text>
        <text class="subtitle">智能识别 · 科学训练</text>
        -->
      </view>
      
      <!-- 表单区域 -->
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
          
          <view class="input-item input-with-margin">
            <input 
              v-model="formData.password" 
              type="password" 
              placeholder="请输入密码"
              class="input"
            />
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
          <text class="link-text">立即注册</text>
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
    background: $fitness-primary;
    padding: 80rpx 40rpx 40rpx;
  }
  
  .logo-section {
    text-align: center;
    margin-bottom: 40rpx;
    
    .logo {
      width: 400rpx;
      height: 400rpx;
      margin-bottom: 0rpx;
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
    .input-wrapper {
      background: $fitness-primary;
      border-radius: $radius-lg;
      border: 3.5rpx solid $fitness-border;
      padding: 0 $spacing-lg;
      margin-bottom: $spacing-lg;
      box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
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
      
      &.input-with-margin {
        margin-top: 0;
      }
      
      .input {
        width: 100%;
        height: 96rpx;
        font-size: $font-md;
        color: $fitness-text;
        padding: 0 $spacing-md;
        box-sizing: border-box;
        border: none;
        border-bottom: 1rpx solid $fitness-border;
      }
    }
    
    .forget-password {
      text-align: right;
      font-size: $font-md;
      color: $uni-primary;
      margin-bottom: $spacing-lg;
      padding-right: $spacing-xs;
    }
    
    .login-btn {
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
    
    .register-link {
      text-align: center;
      font-size: $font-md;
      color: $fitness-text-light;
      margin-top: $spacing-lg;
      
      .link-text {
        color: $uni-primary;
        font-weight: 500;
      }
    }
  }
  </style>