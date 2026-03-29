<template>
    <view class="container">
      <!-- 当前手机号提示 -->
      <view class="current-phone-tip">
        <text class="tip-label">当前手机号</text>
        <div class="line"> </div>
        <text class="tip-value">{{ maskedCurrentPhone }}</text>
      </view>
      
      <!-- 表单区域 -->
      <view class="form-section">
        <view class="input-wrapper">
          <!-- 旧手机号 -->
          <view class="text">当前手机号</view>
          <view class="input-item">
            <img src="@/static/phone2.png" class="icon"/>
            <input 
              v-model="formData.oldPhone" 
              type="number" 
              placeholder="请输入当前手机号"
              class="input"
              maxlength="11"
              :class="{ 'input-focus': focusedInput === 'oldPhone' }"
              @focus="onInputFocus('oldPhone')"
              @blur="onInputBlur"
            />
          </view>
          
          <!-- 新手机号 -->
          <view class="text">新手机号</view>
          <view class="input-item input-with-border">
            <img src="@/static/phone2.png" class="icon"/>
            <input 
              v-model="formData.newPhone" 
              type="number" 
              placeholder="请输入新手机号"
              class="input"
              maxlength="11"
              :class="{ 'input-focus': focusedInput === 'newPhone' }"
              @focus="onInputFocus('newPhone')"
              @blur="onInputBlur"
            />
          </view>
        </view>
      </view>
      <!-- 提交按钮 -->
      <button class="submit-btn" @click="handleSubmit" :loading="loading" :disabled="loading">
          {{ loading ? '修改中...' : '确认修改' }}
      </button>
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
  const focusedInput = ref(null)

const onInputFocus = (inputName) => {
  focusedInput.value = inputName
}
  
const onInputBlur = () => {
  focusedInput.value = null
}

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
    background: url('@/static/background.png') no-repeat center center / cover;
    //padding: 0rpx $size-5 0;
  }
  
  .current-phone-tip {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 0 0 $size-5 $size-5;
    margin-bottom: $size-5;
    padding: $size-4 $size-6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1rpx 10rpx rgba(0, 0, 0, 0.15); // iOS风格阴影
    
    .tip-label {
      font-size: $size-4;
      color: $color-label;
    }
    
    .tip-value {
      font-size: $size-4;
      font-weight: 700;
      //color: $color-label;
      color: $color-primary;
    }
    .line{
      --tw-bg-opacity: 1;
      background-color: $color-line;
      flex: 1 1 0%;
      height: 1px;
      margin-left: $size-4;
      margin-right: $size-4;
    }
  }
  
  .form-section {
    background: rgba(252, 249, 248, 0.7);
    border-radius: $size-4;
    padding: $size-6;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
    margin: 0 $size-6;

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
              border: 2px solid rgba(160, 62, 64, 0.4);
          }
          uni-icons {
              position: absolute;
              right: $size-3;
              top: 50%;
              transform: translateY(-50%);
          }
        }
    }
  }

  .submit-btn {
      width: auto;
      height: $size-12;
      background: $uni-primary;
      color: #FFFFFF;
      font-size: $size-4;
      border-radius: $size-6;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      margin: $size-6;
      
      &[disabled] {
        opacity: 0.6;
      }
    }
  </style>