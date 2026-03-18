<!--编辑个人资料：头像、昵称、生日-->
<template>
    <view class="container">
      <!-- 头像上传 -->
      <view class="avatar-section" @click="chooseAvatar">
        <image 
          :src="formData.avatar_url || '/static/default-avatar.png'" 
          class="avatar" 
          mode="aspectFill"
        />
        <view class="avatar-tip">点击更换头像</view>
      </view>
      
      <view class="form-section">
        <view class="input-item">
          <text class="label">昵称</text>
          <input 
            v-model="formData.name" 
            type="text" 
            placeholder="请输入昵称"
            class="input"
            maxlength="20"
          />
        </view>
        
        <view class="input-item">
          <text class="label">生日</text>
          <picker 
            mode="date" 
            :value="formData.birthday" 
            @change="onBirthdayChange"
          >
            <view class="picker">
              {{ formData.birthday || '请选择' }}
            </view>
          </picker>
        </view>
        <!--
        <view class="age-display" v-if="calculatedAge">
          <text class="age-label">自动计算年龄：</text>
          <text class="age-value">{{ calculatedAge }} 岁</text>
        </view>
        
        -->
        
        <button class="submit-btn" @click="handleSubmit" :loading="loading">
          保存
        </button>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { onShow, onLoad } from '@dcloudio/uni-app' 
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  import dayjs from 'dayjs'
  
  const userStore = useUserStore()
  const loading = ref(false)
  
  const formData = ref({
    name: '',
    avatar_url: '',
    birthday: '' // 格式：YYYY-MM-DD
  })
  
  /**
   * 计算年龄（对应《需求规格说明书》2.2.1 业务规则）
   * 生日更新后自动重新计算年龄并写入数据库中
   */
  const calculatedAge = computed(() => {
    if (!formData.value.birthday) return null
    const birth = dayjs(formData.value.birthday)
    const now = dayjs()
    let age = now.year() - birth.year()
    if (now.month() < birth.month() || 
        (now.month() === birth.month() && now.date() < birth.date())) {
      age--
    }
    return age > 0 ? age : 0
  })
  
  /**
   * 页面显示时加载用户数据
   * Uni-app 页面生命周期钩子
  */
  onShow(() => {
    const info = userStore.userInfo
    formData.value = {
      name: info.name || '',
      avatar_url: info.avatar_url || '',
      birthday: info.birthday || ''
    }
  })
  
  /**
   * 选择头像（对应用例步骤 3-6）
   */
  const chooseAvatar = () => {
    uni.showActionSheet({
      itemList: ['拍照', '从相册选择'],
      success: (res) => {
        if (res.tapIndex === 0) {
          // 拍照
          uni.chooseImage({
            count: 1,
            sourceType: ['camera'],
            success: (imageRes) => {
              formData.value.avatar_url = imageRes.tempFilePaths[0]
              // 实际项目中需上传至服务器
            }
          })
        } else {
          // 相册
          uni.chooseImage({
            count: 1,
            sourceType: ['album'],
            success: (imageRes) => {
              formData.value.avatar_url = imageRes.tempFilePaths[0]
            }
          })
        }
      }
    })
  }
  
  const onBirthdayChange = (e) => {
    formData.value.birthday = e.detail.value // 格式：YYYY-MM-DD
  }
  
  /**
   * 提交个人资料
   * 对应《需求规格说明书》3.2 节编辑个人资料用例
   */
  const handleSubmit = async () => {
    if (!formData.value.name) {
      uni.showToast({ title: '请输入昵称', icon: 'error', duration: 2000 })
      return
    }
    if (!formData.value.avatar_url) {
      uni.showToast({ title: '请上传头像', icon: 'error', duration: 2000 })
      return
    }
    if (!formData.value.birthday) {
      uni.showToast({ title: '请选择生日', icon: 'error', duration: 2000 })
      return
    }
    
    loading.value = true
    
    try {
      console.log('formData.value:', formData.value)

      const res = await request.put(API.USER_PROFILE, formData.value)
      console.log('res:',res)
      userStore.updateUserInfo(res)
      
      uni.showToast({ title: '保存成功', icon: 'success', duration: 1500 })
      
      // 获取页面栈，判断上一个页面是否为注册页面
      const pages = getCurrentPages();
      const prevPage = pages[pages.length - 2]; // 上一个页面
      console.log(pages)
      
      // 如果上一个页面是登录页面，则跳转到身体数据页面
      setTimeout(() => {
          uni.redirectTo({ url: '/pages/profile/body-data' })
      }, 1500)
      
    } catch (error) {
      console.error('保存失败:', error)
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
  
  .avatar-section {
    text-align: center;
    margin-bottom: 60rpx;
    
    .avatar {
      width: 200rpx;
      height: 200rpx;
      border-radius: 100rpx;
      border: 4rpx solid $uni-primary;
      margin-bottom: 20rpx;
    }
    
    .avatar-tip {
      font-size: $font-xs;
      color: $uni-primary;
    }
  }
  
  .form-section {
    .input-item {
      background: #FFFFFF;
      border-radius: $radius-md;
      padding: 30rpx;
      margin-bottom: 30rpx;
      
      .label {
        display: block;
        font-size: $font-md;
        color: $fitness-text;
        margin-bottom: 15rpx;
      }
      
      .input, .picker {
        width: 100%;
        height: 80rpx;
        background: $fitness-bg;
        border-radius: $radius-sm;
        padding: 0 20rpx;
        font-size: $font-md;
        box-sizing: border-box;
        align-content: center;
      }
    }
    
    .age-display {
      background: #FFFFFF;
      border-radius: $radius-md;
      padding: 30rpx;
      margin-bottom: 40rpx;
      text-align: center;
      
      .age-label {
        font-size: $font-md;
        color: $fitness-text-light;
        margin-right: 20rpx;
      }
      
      .age-value {
        font-size: $font-xl;
        font-weight: bold;
        color: $uni-primary;
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