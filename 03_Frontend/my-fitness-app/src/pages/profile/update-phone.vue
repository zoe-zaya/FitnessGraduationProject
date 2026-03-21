<template>
    <view class="container">
      <!-- 当前手机号提示 -->
      <view class="current-phone-tip">
        <text class="tip-label">当前手机号</text>
        <text class="tip-value">{{ maskedCurrentPhone }}</text>
      </view>
      
      <!-- 表单区域 -->
      <view class="form-section">
        <!-- 旧手机号 -->
        <view class="input-item">
          <text class="label">当前手机号</text>
          <input 
            v-model="formData.oldPhone" 
            type="number" 
            placeholder="请输入当前手机号"
            class="input"
            maxlength="11"
          />
          <text class="tip">用于验证身份</text>
        </view>
        
        <!-- 新手机号 -->
        <view class="input-item">
          <text class="label">新手机号</text>
          <input 
            v-model="formData.newPhone" 
            type="number" 
            placeholder="请输入新手机号"
            class="input"
            maxlength="11"
          />
          <text class="tip">新手机号将用于登录和接收通知</text>
        </view>
        
        <!-- 确认新手机号 -->
        <!--<view class="input-item">
          <text class="label">确认新手机号</text>
          <input 
            v-model="formData.confirmPhone" 
            type="number" 
            placeholder="请再次输入新手机号"
            class="input"
            maxlength="11"
          />
        </view>->
        
        <!-- 提交按钮 -->
        <button class="submit-btn" @click="handleSubmit" :loading="loading">
          确认修改
        </button>
      </view>
      
      <!-- 安全提示 -->
      <!--<view class="security-notice">
        <text class="notice-title">⚠️ 注意事项</text>
        <text class="notice-content">
          1. 修改成功后，请使用新手机号登录\
          2. 请确保新手机号未被其他账号注册\
          3. 修改后原手机号将解除绑定
        </text>
      </view>-->
    </view>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import { onShow } from '@dcloudio/uni-app'
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API, PHONE_REGEX } from '@/utils/constants'
  
  const userStore = useUserStore()
  const loading = ref(false)
  
  const currentPhone = computed(() => userStore.userInfo.phone || '未绑定')
  const maskedCurrentPhone = computed(() => {
  if (!userStore.userInfo.phone) {
    return '未绑定'
  }
  // 隐藏手机号中间4位数字
  const phone = userStore.userInfo.phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
})
  const formData = ref({
    oldPhone: '',
    newPhone: ''
    //confirmPhone: ''
  })
  
  /*onShow(() => {
    // 预填充当前手机号
    formData.value.oldPhone = userStore.userInfo.phone || ''
  })*/
  
  /**
   * 修改手机号
   * 对应《需求规格说明书》3.2 节编辑账号与安全用例步骤 3-4
   */
  const handleSubmit = async () => {
    // 1. 验证旧手机号（对应扩展事件流 4a）
    if (!formData.value.oldPhone) {
      uni.showToast({ title: '请输入当前手机号', icon: 'none', duration: 2000 })
      return
    }
    
    if (formData.value.oldPhone !== userStore.userInfo.phone) {
      uni.showToast({ 
        title: '输入的当前手机号不正确', 
        icon: 'none', 
        duration: 2000 
      })
      return
    }
    
    // 2. 验证新手机号格式（对应扩展事件流 4b）
    if (!formData.value.newPhone || !PHONE_REGEX.test(formData.value.newPhone)) {
      uni.showToast({ 
        title: '请输入有效的手机号', 
        icon: 'none', 
        duration: 2000 
      })
      return
    }
    
    // 3. 验证两次输入的新手机号是否一致
    /*if (formData.value.newPhone !== formData.value.confirmPhone) {
      uni.showToast({ 
        title: '两次输入的新手机号不一致', 
        icon: 'none', 
        duration: 2000 
      })
      return
    }*/
    
    // 4. 验证新旧手机号是否相同
    if (formData.value.oldPhone === formData.value.newPhone) {
      uni.showToast({ 
        title: '新手机号不能与当前手机号相同', 
        icon: 'none', 
        duration: 2000 
      })
      return
    }
    
    loading.value = true
    
    try {
      // 5. 调用修改手机号 API
      await request.put(API.USER_SECURITY_PHONE, {
        old_phone: formData.value.oldPhone,
        new_phone: formData.value.newPhone
      })
      
      // 6. 更新本地存储的用户信息
      userStore.updateUserInfo({ phone: formData.value.newPhone })
      
      uni.showToast({ title: '手机号修改成功', icon: 'success', duration: 1500 })
      
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/login/login' })
      }, 1000)
      
    } catch (error) {
      console.error('修改失败:', error)
      // 错误信息已在 request 拦截器中处理
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: $fitness-bg;
    padding: 40rpx;
  }
  
  .current-phone-tip {
    background: #FFFFFF;
    border-radius: $radius-md;
    padding: 30rpx;
    margin-bottom: 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .tip-label {
      font-size: $font-md;
      color: $fitness-text-light;
    }
    
    .tip-value {
      font-size: $font-lg;
      font-weight: bold;
      color: $uni-primary;
    }
  }
  
  .form-section {
    background: #FFFFFF;
    border-radius: $radius-md;
    padding: 30rpx;
    margin-bottom: 30rpx;
    
    .input-item {
      margin-bottom: 30rpx;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .label {
        display: block;
        font-size: $font-md;
        color: $fitness-text;
        margin-bottom: 15rpx;
      }
      
      .input {
        width: 100%;
        height: 90rpx;
        background: $fitness-bg;
        border: 1rpx solid $fitness-border;
        border-radius: $radius-sm;
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
    
    .submit-btn {
      width: 100%;
      height: 90rpx;
      background: $fitness-primary;
      color: #FFFFFF;
      font-size: $font-lg;
      border-radius: $radius-xl;
      border: none;
      margin-top: 40rpx;
    }
  }
  
  .security-notice {
    background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
    border-radius: $radius-md;
    padding: 30rpx;
    
    .notice-title {
      display: block;
      font-size: $font-md;
      font-weight: bold;
      color: #E65100;
      margin-bottom: 10rpx;
    }
    
    .notice-content {
      display: block;
      font-size: $font-xs;
      color: #EF6C00;
      line-height: 2;
      white-space: pre-line;
    }
  }
  </style>