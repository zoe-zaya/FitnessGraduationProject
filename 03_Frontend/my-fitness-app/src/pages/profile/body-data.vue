<!--编辑身体数据-->
<template>
    <view class="container">
      <view class="form-section">
        <view class="input-wrapper">
          <view class="input-item">
            <text class="input-label">年龄</text>
            <input 
              :value="calculatedAge" 
              type="number" 
              placeholder="根据生日自动计算"
              class="input"
              disabled
            />
          </view>
          
          <view class="input-item input-with-border">
            <text class="input-label">性别</text>
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
          
          <view class="input-item input-with-border">
            <text class="input-label">身高 (cm)</text>
            <input 
              v-model="formData.height" 
              type="digit" 
              placeholder="厘米"
              class="input"
            />
          </view>
          
          <view class="input-item input-with-border">
            <text class="input-label">体重 (kg)</text>
            <input 
              v-model="formData.weight" 
              type="digit" 
              placeholder="千克"
              class="input"
            />
          </view>
          
          <view class="input-item input-with-border">
            <text class="input-label">健身目标</text>
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
          
          <view class="input-item input-with-border">
            <text class="input-label">经验水平</text>
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
        </view>
        
        <view class="input-wrapper" v-if="bmi">
          <view class="bmi-card">
            <text class="bmi-label">您的 BMI 指数</text>
            <text class="bmi-value">{{ bmi }}</text>
            <text class="bmi-status" :class="bmiStatusClass">{{ bmiStatus }}</text>
          </view>
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
    background-color: $fitness-primary;
    padding: 40rpx 40rpx 0;
  }
  
  .form-section {
    .input-wrapper {
      background: $fitness-primary;
      border-radius: $radius-lg;
      border: 3.5rpx solid $fitness-border;
      box-shadow: 0 1rpx 0 0 $divider-ios; // iOS风格阴影
      overflow: hidden;
      margin-bottom: $spacing-xl;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .input-item {
      position: relative;
      padding: 0 $spacing-lg;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border: none;
      border-bottom: 1rpx solid $fitness-border;
      
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
      
      .input-label {
        font-size: $font-sm;
        color: $fitness-text-light;
        flex: 1;
        margin: 26rpx 30rpx 26rpx 0;
      }
      
      .input, .picker {
        flex: 2;
        height: 80rpx;
        font-size: $font-md;
        color: $fitness-text;
        padding: 0;
        box-sizing: border-box;
        align-content: center;
        text-align: right;
      }
    }
    
    .bmi-card {
      background: #382626;
      border-radius: $radius-lg;
      padding: 40rpx;
      text-align: center;
      margin: $spacing-lg;
      box-shadow: 0 4rpx 10rpx rgba(3, 7, 11, 0.2);
      
      .bmi-label {
        display: block;
        font-size: $font-sm;
        color: rgba(243, 243, 243, 0.8);
        margin-bottom: 10rpx;
      }
      
      .bmi-value {
        display: block;
        font-size: 72rpx;
        font-weight: 700;
        color: rgb(243, 243, 243);
        margin-bottom: 15rpx;
      }
      
      .bmi-status {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        color: #FFFFFF;
        font-size: $font-sm;
        padding: 10rpx 30rpx;
        border-radius: $radius-lg;
        
        &.status-normal {
          background: rgba(95, 205, 123, 0.9);
        }
        
        &.status-warning {
          background: rgba(255, 149, 0, 0.9);
        }
        
        &.status-danger {
          background: rgb(245 44 33 / 90%);
        }
      }
    }
    
    .submit-btn {
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
      margin-top: $spacing-xl;
      
      &[disabled] {
        opacity: 0.6;
      }
    }
  }
  </style>