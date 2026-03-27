<!--编辑个人资料：头像、昵称、生日-->
<template>
    <view class="container">
      <!--进度条-->
      <view class="step-indicator">
        <view class="label">
            <img src="@/static/num1-icon.png" class="icon"/>
            <text class="text">个人资料</text>
        </view>
        <div class="line"> </div>
        <view class="label">
            <img src="@/static/num2-icon.png" class="icon" />
            <text class="text">身体数据</text>
        </view>
      </view>
      <!-- 头像上传 -->
      <view class="avatar-section" @click="chooseAvatar">
        <image 
          :src="formData.avatar_url || '/static/default-avatar.png'" 
          class="avatar" 
          mode="aspectFill"
        />
        <view class="avatar-tip">点击更换头像</view>
      </view>
      
      <!--表单-->
      <view class="form-section">
        <view class="input-wrapper">
          <view class="input-item">
            <text class="label">昵称</text>
            <input 
              v-model="formData.name" 
              type="text" 
              placeholder="请输入昵称"
              class="input"
              :class="{ 'input-focus': focusedInput === 'name' }"
              @focus="onInputFocus('name')"
              @blur="onInputBlur"
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
  const focusedInput = ref(null)

  const formData = ref({
    name: '',
    avatar_url: '',
    birthday: '' // 格式：YYYY-MM-DD
  })
  
  const onInputFocus = (inputName) => {
    focusedInput.value = inputName
  }
  
  const onInputBlur = () => {
    focusedInput.value = null
  }

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
          uni.redirectTo({ url: '/pages/profile/body-data-login' })
        }, 1500)
      }
    }catch(error){
      console.error('检查资料完整性失败:', error)
      uni.showToast({ 
          title: '检查资料完整性失败', 
          icon: 'none', 
          duration: 1500 
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
    background: url('@/static/background3.png') no-repeat center center / cover;
    padding: $size-6;
    font-family: Manrope;
  }
  
  .step-indicator{
    padding-left: $size-2;
    padding-right: $size-2;
    justify-content: space-between;
    align-items: center;
    object-position: center;
    display: flex;
    margin-bottom: $size-5;

    .label{
        gap: $size-3;
        align-items: center;
        display: flex;
        .icon{
            width: 20px;
            height:20px;
        }
        .text{
            color: $color-label;
            font-weight: 700;
            font-size: $size-4;
            line-height: $size-6;
        }
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
  .avatar-section {
    text-align: center;
    //justify-content: center;
    margin-bottom: $size-6;
    //position: relative;
    
    .avatar {
      --tw-shadow: 0 10px 30px -12px rgba(0, 0, 0, 0.2);
      --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color);
      box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
      width: 352rpx;
      height: 352rpx;
      border-radius: 999rpx;
      box-sizing: border-box;
      border-style: solid;
      border-color: #ffffff;    
      margin-bottom: $size-2;
    }
    
    .avatar-tip {
      //font-size: $size-3;
      font-size: 28rpx;
      color: $color-primary;
      font-weight: 550;
      font-family: Manrope;
    }
  }
  
  .form-section {
  .input-item {
    background: $glass-bg1;
    border-radius: $size-4;
    padding: $size-5;
    margin-bottom: $size-3;
    box-shadow: 0 2rpx 10rpx $border-shadow;
    .shadow-\[0_8px_24px_rgba\(160\2c 62\2c 64\2c 0\.06\)\] {
      --tw-shadow: 0 8px 24px rgba(160, 62, 64, 0.2);
      --tw-shadow-colored: 0 8px 24px var(--tw-shadow-color);
      box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
    }
    
    .label {
      display: block;
      font-weight: 700;
      font-size: 28rpx;
      line-height: $size-3;
      color: $color-label;
      margin-bottom: $size-2;
      font-family: Manrope;
    }
    
    .input, .picker {
        transition-property: all;
        transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
        transition-duration: 150ms;
        color: $color-input;
        padding: $size-2 $size-4;
        background-color: $fitness-primary;
        border-style: none;
        border-radius: $size-4;
        border: 2px solid rgba(160, 62, 64, 0.1);
        width: auto;
        font-size: $size-4;
    }
    .input-focus {
        border: 2px solid rgba(160, 62, 64, 0.4);
    }
  }
  
  .age-display {
    border-radius: $size-3;
    margin-bottom: $size-2;
    text-align: center;
    
    .age-label {
      font-size: $size-3;
      color: $color-secondory;
      margin-right: $size-1;
    }
    
    .age-value {
      font-size: $size-3;
      font-weight: bold;
      color: $color-secondory;
    }
  }
  
  .submit-btn {
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
}
</style>