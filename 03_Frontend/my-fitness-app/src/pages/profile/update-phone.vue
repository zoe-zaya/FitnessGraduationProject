<template>
    <view class="container">
      <!-- 当前手机号提示 -->
      <view class="current-phone-tip">
        <text class="tip-label">当前手机号</text>
        <text class="tip-value">{{ maskedCurrentPhone }}</text>
      </view>
      
      <!-- 表单区域 -->
      <view class="form-section">
        <view class="input-wrapper">
          <!-- 旧手机号 -->
          <view class="input-item">
            <input 
              v-model="formData.oldPhone" 
              type="number" 
              placeholder="请输入当前手机号"
              class="input"
              maxlength="11"
            />
          </view>
          
          <!-- 新手机号 -->
          <view class="input-item input-with-border">
            <input 
              v-model="formData.newPhone" 
              type="number" 
              placeholder="请输入新手机号"
              class="input"
              maxlength="11"
            />
          </view>
        </view>
        
        <!-- 提交按钮 -->
        <button class="submit-btn" @click="handleSubmit" :loading="loading" :disabled="loading">
          {{ loading ? '修改中...' : '确认修改' }}
        </button>
      </view>
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
    background-color: $fitness-primary;
    padding: 0rpx $size-5 0;
  }
  
  .current-phone-tip {
    background: $fitness-primary;
    border-radius: $radius-lg;
    padding: 20rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    //box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
    
    .tip-label {
      font-size: $font-md;
      color: $fitness-text-light;
    }
    
    .tip-value {
      font-size: $font-md;
      font-weight: 600;
      color: $uni-primary;
    }
  }
  
  .form-section {
    .input-wrapper {
      background: $fitness-primary;
      border-radius: $radius-lg;
      border: 3.5rpx solid $fitness-border;
      //box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
      overflow: hidden;
    }
    
    .input-item {
      position: relative;
      
      &:not(:last-child)::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: $size-5;
        right: $size-5;
        height: 1rpx;
        background: #FFFFFF;
        transform: scaleY(0.5);
      }
      
      .input {
        width: 100%;
        height: $size-12;
        font-size: $font-md;
        color: $fitness-text;
        padding: 0 $size-5;
        box-sizing: border-box;
        border: none;
        border-bottom: 1rpx solid $fitness-border;
      }
    }
    
    .phone-info {
      background: $fitness-primary;
      border-radius: $radius-lg;
      padding: $size-5;
      margin: $size-5 0;
      box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
      
      .tip {
        display: block;
        font-size: $font-sm;
        color: $fitness-text-light;
        margin-bottom: $size-4;
        
        &:last-child {
          margin-bottom: 0;
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
  </style>