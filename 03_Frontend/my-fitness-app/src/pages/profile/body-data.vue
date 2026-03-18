<!--编辑身体数据-->
<template>
    <view class="container">
      <view class="form-section">
        <view class="input-item">
          <text class="label">年龄</text>
          <input 
            :value="calculatedAge" 
            type="number" 
            placeholder="根据生日自动计算"
            class="input"
            disabled
          />
          <text class="tip">根据生日自动计算，不可手动调整</text>
        </view>
        
        <view class="input-item">
          <text class="label">性别</text>
          <picker 
            :range="GENDERS" 
            range-key="label"
            @change="onGenderChange"
          >
            <view class="picker">
              {{ formData.gender ? GENDERS.find(g => g.value === formData.gender)?.label : '请选择' }}
            </view>
          </picker>
        </view>
        
        <view class="input-item">
          <text class="label">身高 (cm)</text>
          <input 
            v-model="formData.height" 
            type="digit" 
            placeholder="厘米"
            class="input"
          />
        </view>
        
        <view class="input-item">
          <text class="label">体重 (kg)</text>
          <input 
            v-model="formData.weight" 
            type="digit" 
            placeholder="千克"
            class="input"
          />
        </view>
        
        <view class="input-item">
          <text class="label">健身目标</text>
          <picker 
            :range="FITNESS_GOALS" 
            range-key="label"
            @change="onGoalChange"
          >
            <view class="picker">
              {{ formData.fitness_goal ? FITNESS_GOALS.find(g => g.value === formData.fitness_goal)?.label : '请选择' }}
            </view>
          </picker>
        </view>
        
        <view class="input-item">
          <text class="label">经验水平</text>
          <picker 
            :range="EXPERIENCE_LEVELS" 
            range-key="label"
            @change="onLevelChange"
          >
            <view class="picker">
              {{ formData.experience_level ? EXPERIENCE_LEVELS.find(l => l.value === formData.experience_level)?.label : '请选择' }}
            </view>
          </picker>
        </view>
        
        <!-- BMI 展示 -->
        <view class="bmi-card" v-if="bmi">
          <text class="bmi-label">您的 BMI 指数</text>
          <text class="bmi-value">{{ bmi }}</text>
          <text class="bmi-status" :class="bmiStatusClass">{{ bmiStatus }}</text>
        </view>
        
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
  import { API, GENDERS, FITNESS_GOALS, EXPERIENCE_LEVELS } from '@/utils/constants'
  
  const userStore = useUserStore()
  const loading = ref(false)
  
  // 表单数据
  const formData = ref({
    gender: '',
    height: '',
    weight: '',
    fitness_goal: '',
    experience_level: ''
  })
  
  // 计算年龄
  const calculatedAge = computed(() => {
    if (!userStore.userInfo || !userStore.userInfo.birthday) {
      return '';
    }
    
    const birthday = new Date(userStore.userInfo.birthday);
    const today = new Date();
    let age = today.getFullYear() - birthday.getFullYear();
    const monthDiff = today.getMonth() - birthday.getMonth();
    
    // 如果还没过生日，则减一岁
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthday.getDate())) {
      age--;
    }
    
    return age;
  });
  
  // BMI 计算
  const bmi = computed(() => {
    if (formData.value.height && formData.value.weight) {
      const h = formData.value.height / 100
      return (formData.value.weight / (h * h)).toFixed(2)
    }
    return null
  })
  
  const bmiStatus = computed(() => {
    if (!bmi.value) return ''
    const val = parseFloat(bmi.value)
    if (val < 18.5) return '偏瘦'
    if (val < 24) return '正常'
    if (val < 28) return '偏胖'
    return '肥胖'
  })
  
  const bmiStatusClass = computed(() => {
    if (bmiStatus.value === '正常') return 'status-normal'
    if (bmiStatus.value === '偏瘦') return 'status-warning'
    return 'status-danger'
  })
  
  /**
   * 页面显示时加载用户数据
   */
  onShow(() => {
    const info = userStore.userInfo
    formData.value = {
      // 年龄不再从用户信息中获取，而是动态计算
      gender: info.gender || '',
      height: info.height || '',
      weight: info.weight || '',
      fitness_goal: info.fitness_goal || '',
      experience_level: info.experience_level || ''
    }
  })
  
  // 选择器事件
  const onGenderChange = (e) => {
    formData.value.gender = GENDERS[e.detail.value].value
  }
  
  const onGoalChange = (e) => {
    formData.value.fitness_goal = FITNESS_GOALS[e.detail.value].value
  }
  
  const onLevelChange = (e) => {
    formData.value.experience_level = EXPERIENCE_LEVELS[e.detail.value].value
  }
  
  /**
   * 提交身体数据
   * 对应《需求规格说明书》3.2 节编辑身体数据用例
   */
  const handleSubmit = async () => {
    // 验证必填项
    if (!formData.value.height || !formData.value.weight) {
      uni.showToast({ title: '请填写身高和体重', icon: 'error', duration: 2000 })
      return
    }
    // 验证必填项
    if (!formData.value.gender) {
      uni.showToast({ title: '请选择性别', icon: 'error', duration: 2000 })
      return
    }
    if (!formData.value.fitness_goal) {
      uni.showToast({ title: '请选择健身目标', icon: 'error', duration: 2000 })
      return
    }
    if (!formData.value.experience_level) {
      uni.showToast({ title: '请选择健身经验', icon: 'error', duration: 2000 })
      return
    }
    loading.value = true
    
    try {
      // 准备提交的数据，不包括年龄
      const submitData = {
        gender: formData.value.gender,
        height: formData.value.height,
        weight: formData.value.weight,
        fitness_goal: formData.value.fitness_goal,
        experience_level: formData.value.experience_level
      };
      
      // 调用 API
      const res = await request.put(API.USER_BODY_DATA, submitData)
      
      // 更新本地状态
      userStore.updateUserInfo(res)
      
      uni.showToast({ title: '保存成功', icon: 'success', duration: 1500 })
      
      // 获取页面栈，判断上一个页面是否为注册页面
      const pages = getCurrentPages();
      const prevPage = pages[pages.length - 2]; // 上一个页面
      
      setTimeout(() => {
          uni.reLaunch({ url: '/pages/profile/profile' })
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
      
      .tip {
        display: block;
        font-size: $font-xs;
        color: $fitness-text-gray;
        margin-top: 10rpx;
      }
    }
    
    .bmi-card {
      background: $fitness-primary;
      border-radius: $radius-md;
      padding: 40rpx;
      text-align: center;
      margin-bottom: 40rpx;
      
      .bmi-label {
        display: block;
        font-size: $font-xs;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 10rpx;
      }
      
      .bmi-value {
        display: block;
        font-size: 72rpx;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 15rpx;
      }
      
      .bmi-status {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        color: #FFFFFF;
        font-size: $font-xs;
        padding: 8rpx 30rpx;
        border-radius: 20rpx;
        
        &.status-normal {
          background: $uni-success;
        }
        
        &.status-warning {
          background: $uni-warning;
        }
        
        &.status-danger {
          background: $uni-error;
        }
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