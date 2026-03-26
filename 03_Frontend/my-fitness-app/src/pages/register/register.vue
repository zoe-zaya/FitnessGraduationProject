<template>
    <view class="container">
      <!-- Logo 区域 -->
      <view class="logo-section">
        <text class="title">TFit</text>
        <text class="subtitle">能够识别健身器材并生成训练计划的健身APP</text>
      </view>

      <!-- 表单区域 -->
      <view class="form-section">
        <view class="input-wrapper">
          <view class="input-item">
            <input 
              v-model="formData.phone" 
              type="number" 
              placeholder="请输入手机号"
              class="input"
              maxlength="11"
            />
          </view>

          <view class="input-item input-with-margin">
            <input 
              v-model="formData.password" 
              type="password" 
              placeholder="8位以上包含数字大小写字母和特殊符号"
              class="input"
            />
            <uni-icons type="eye-filled" size="20" color="#8E8E93"></uni-icons>
          </view>

          <view class="input-item input-with-margin">
            <input 
              v-model="formData.confirmPassword" 
              type="password" 
              placeholder="至少 8 个字符"
              class="input"
            />
            <uni-icons type="eye-filled" size="20" color="#8E8E93"></uni-icons>
          </view>
        </view>

        <view class="checkbox-section">
          <checkbox-group @change="checkboxChange">
            <label>
              <checkbox value="agree" :checked="isAgree"/>
              我已阅读并同意《用户协议》和《隐私政策》
            </label>
          </checkbox-group>
        </view>

        <button class="register-btn" @click="handleRegister" :loading="loading" :disabled="!isAgree || loading">
          注册
        </button>

        <view class="login-link">
          已有账号？
          <text class="link-text" @click="navigateToLogin">立即登录</text>
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
const isAgree = ref(false)

const formData = ref({
  phone: '',
  password: '',
  confirmPassword: ''
})

const checkboxChange = (e) => {
  isAgree.value = e.detail.value.includes('agree')
}

const handleRegister = async () => {
  // 验证输入
  if (!formData.value.phone || formData.value.phone.length !== 11) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none', duration: 2000 })
    return
  }
  if (!formData.value.password || !/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(formData.value.password)) {
    uni.showToast({ title: '密码不符合要求', icon: 'none', duration: 2000 })
    return
  }
  if (formData.value.password !== formData.value.confirmPassword) {
    uni.showToast({ title: '两次输入的密码不一致', icon: 'none', duration: 2000 })
    return
  }

  loading.value = true

  try {
    const res = await request.post(API.REGISTER, {
      phone: formData.value.phone,
      password: formData.value.password
    })

    userStore.setLoginInfo(res.access_token, res.user_info)

    uni.showToast({ title: '注册成功', icon: 'success', duration: 1500 })

    setTimeout(() => {
      uni.reLaunch({ url: '/pages/login/login' })
    }, 1000)
  } catch (error) {
    console.error('注册失败:', error)
    uni.showToast({ title: error.response.data.detail || '注册失败，请稍后重试', icon: 'none', duration: 2000 })
  } finally {
    loading.value = false
  }
}

const navigateToLogin = () => {
  uni.navigateTo({ url: '/pages/login/login' })
}
</script>

<style lang="scss" scoped>
@import '../../uni.scss';

.container {
  min-height: 100vh;
  background: url('@/static/background.png') no-repeat center center / cover;
  padding: 80rpx 40rpx 40rpx;
}

.logo-section {
  text-align: center;
  margin-bottom: 40rpx;

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
  background: #FFFFFF;
  border-radius: $radius-lg;
  padding: 40rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);

  .input-wrapper {
    .input-item {
      position: relative;
      margin-bottom: 30rpx;

      .input {
        width: 100%;
        height: 80rpx;
        font-size: $font-md;
        color: $fitness-text;
        padding: 0 30rpx;
        box-sizing: border-box;
        border: none;
        border-bottom: 1rpx solid $fitness-border;
      }

      uni-icons {
        position: absolute;
        right: 20rpx;
        top: 50%;
        transform: translateY(-50%);
      }
    }
  }

  .checkbox-section {
    margin-bottom: 30rpx;
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

  .login-link {
    text-align: center;
    font-size: $font-md;
    color: $fitness-text-light;
    margin-top: 30rpx;

    .link-text {
      color: $uni-primary;
      font-weight: 500;
    }
  }
}
</style>