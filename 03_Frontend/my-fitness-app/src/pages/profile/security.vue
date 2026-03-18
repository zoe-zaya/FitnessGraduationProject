<template>
    <view class="container">
      <view class="section">
        <text class="section-title">修改手机号</text>
        
        <view class="input-item">
          <text class="label">当前手机号</text>
          <input 
            v-model="formData.oldPhone" 
            type="number" 
            placeholder="请输入当前手机号"
            class="input"
            maxlength="11"
          />
        </view>
        
        <view class="input-item">
          <text class="label">新手机号</text>
          <input 
            v-model="formData.newPhone" 
            type="number" 
            placeholder="请输入新手机号"
            class="input"
            maxlength="11"
          />
        </view>
        
        <button class="submit-btn" @click="handleUpdatePhone" :loading="loading">
          修改手机号
        </button>
      </view>
      
      <view class="section">
        <text class="section-title">修改密码</text>
        
        <view class="input-item">
          <text class="label">当前密码</text>
          <input 
            v-model="passwordForm.oldPassword" 
            type="password" 
            placeholder="请输入当前密码"
            class="input"
          />
        </view>
        
        <view class="input-item">
          <text class="label">新密码</text>
          <input 
            v-model="passwordForm.newPassword" 
            type="password" 
            placeholder="8 位以上，含大小写数字符号"
            class="input"
          />
        </view>
        
        <view class="input-item">
          <text class="label">确认新密码</text>
          <input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入新密码"
            class="input"
          />
        </view>
        
        <button class="submit-btn" @click="handleUpdatePassword" :loading="loading">
          修改密码
        </button>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API, PASSWORD_REGEX } from '@/utils/constants'
  
  const userStore = useUserStore()
  const loading = ref(false)
  
  const formData = ref({
    oldPhone: '',
    newPhone: ''
  })
  
  const passwordForm = ref({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  
  const handleUpdatePhone = async () => {
    if (!formData.value.oldPhone || formData.value.oldPhone.length !== 11) {
      uni.showToast({ title: '请输入正确的当前手机号', icon: 'none' })
      return
    }
    
    if (!formData.value.newPhone || formData.value.newPhone.length !== 11) {
      uni.showToast({ title: '请输入正确的新手机号', icon: 'none' })
      return
    }
    
    loading.value = true
    
    try {
      await request.put(API.USER_SECURITY, {
        type: 'phone',
        old_value: formData.value.oldPhone,
        new_value: formData.value.newPhone
      })
      
      uni.showToast({ title: '手机号修改成功', icon: 'success' })
    } catch (error) {
      console.error('修改失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  const handleUpdatePassword = async () => {
    // 密码复杂度校验
    if (!PASSWORD_REGEX.test(passwordForm.value.newPassword)) {
      uni.showToast({ 
        title: '密码需 8 位以上，含大小写字母、数字和特殊符号', 
        icon: 'none' 
      })
      return
    }
    
    // 确认密码校验
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
      uni.showToast({ title: '两次密码不一致', icon: 'none' })
      return
    }
    
    loading.value = true
    
    try {
      await request.put(API.USER_SECURITY, {
        type: 'password',
        old_value: passwordForm.value.oldPassword,
        new_value: passwordForm.value.newPassword,
        confirm_value: passwordForm.value.confirmPassword
      })
      
      uni.showToast({ title: '密码修改成功', icon: 'success' })
    } catch (error) {
      console.error('修改失败:', error)
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
  
  .section {
    background: #FFFFFF;
    border-radius: $radius-md;
    padding: 30rpx;
    margin-bottom: 40rpx;
    
    .section-title {
      display: block;
      font-size: $font-lg;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 30rpx;
    }
    
    .input-item {
      margin-bottom: 30rpx;
      
      .label {
        display: block;
        font-size: $font-md;
        color: $fitness-text-light;
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
    }
    
    .submit-btn {
      width: 100%;
      height: 90rpx;
      background: $fitness-primary;
      color: #FFFFFF;
      font-size: $font-lg;
      border-radius: $radius-xl;
      border: none;
    }
  }
  </style>