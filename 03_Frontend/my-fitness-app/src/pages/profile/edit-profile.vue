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
      <view class="input-wrapper">
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
        
        <view class="input-item input-with-border">
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
      </view>
      
      <view class="age-display" v-if="calculatedAge">
        <text class="age-label">自动计算年龄：</text>
        <text class="age-value">{{ calculatedAge }} 岁</text>
      </view>
      
      <button class="submit-btn" @click="handleSubmit" :loading="loading" :disabled="loading">
        {{ loading ? '保存中...' : '保存' }}
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
/**
 * 页面显示时刷新用户信息
 */
 onShow(async () => {
  if (userStore.isLogin) {
    try {
      const res = await request.get(API.USER_ME)
      //console.log('当前用信息:', res)
      userStore.updateUserInfo(res)
      const info = userStore.userInfo
      //console.log('userStore中的用户信息:', info)
      formData.value = {
        name: info.name || '',
        avatar_url: info.avatar_url || '',
        birthday: info.birthday || ''
      }
      console.log('formData中的用户信息:', formData.value)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
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

//检查资料完整性
const checkProfileCompleteAndRedirect = async () => {
  try{
    // 调用资料完整性检查接口
    const checkRes = await request.get(API.CHECK_PROFILE_COMPLETE)
    
    console.log('资料完整性检查结果:', checkRes)
    
    // 资料完整
    if (checkRes.is_complete) {
      await onShow() // 刷新用户信息
      /*setTimeout(() => {
        uni.reLaunch({ url: '/pages/profile/edit-profile' })
      }, 1000)*/
    } else {
      // 资料不完整
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/profile/body-data' })
      }, 1500)
    }
  }catch(error){
    console.error('检查资料完整性失败:', error)
    uni.showToast({ 
        title: '检查资料完整性失败', 
        icon: 'none', 
        duration: 2000 
      })
  }
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
    
    // 保存成功后检查资料完整性并跳转
    await checkProfileCompleteAndRedirect()
    
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
  background: $fitness-primary;
  padding: $size-5;
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
    border-radius: $radius-lg;
    padding: 30rpx;
    margin-bottom: 30rpx;
    border: 3.5rpx solid $fitness-border;

    
    .label {
      display: block;
      font-size: $font-md;
      color: $fitness-text;
      margin-bottom: 15rpx;
    }
    
    .input, .picker {
      width: 100%;
      height: $size-10;
      background: $fitness-secondary;
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
    padding: 10rpx;
    margin-bottom: 10rpx;
    text-align: center;
    
    .age-label {
      font-size: $font-md;
      color: $fitness-text-light;
      margin-right: 10rpx;
    }
    
    .age-value {
      font-size: $font-md;
      font-weight: bold;
      color: $fitness-text-light;
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
    margin-top: $spacing-lg;
    
    &[disabled] {
      opacity: 0.6;
    }
  }
}
</style>