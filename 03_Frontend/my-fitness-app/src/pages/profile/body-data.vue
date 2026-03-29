<!--编辑身体数据-->
<template>
  <view class="container">
      <!--进度条-->
      <!--
      <view class="step-indicator">
          <view class="label">
              <img src="@/static/num1-icon-gray.png" class="icon"/>
              <text class="text">个人资料</text>
          </view>
          <div class="line"> </div>
          <view class="label">
              <img src="@/static/num2-icon-red.png" class="icon" />
              <text class="text">身体数据</text>
          </view>
      </view>
      -->

      <!--表单-->
      <view class="form-section">
          <view class="input-wrapper">
          <view class="input-item">
              <text class="input-label">年龄</text>
              <input 
              :value="calculatedAge" 
              type="number" 
              placeholder="根据生日自动计算"
              class="input-text"
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
              class="input-text"
              />
          </view>
          
          <view class="input-item input-with-border">
              <text class="input-label">体重 (kg)</text>
              <input 
              v-model="formData.weight" 
              type="digit" 
              placeholder="千克"
              class="input-text"
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
      </view>
      
      <view class="input-wrapper" v-if="bmi">
          <view class="bmi-card">
              <text class="bmi-label">
                BMI 指数
              </text>
              <view class="bmi-value">{{ bmi }}
                <text class="bmi-status" :class="bmiStatusClass">{{ bmiStatus }}</text>
              </view>
          </view>
      </view>

      <button class="submit-btn" @click="handleSubmit" :loading="loading" :disabled="loading">
          {{ loading ? '保存中...' : '保存' }}
      </button>
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
  background: url('@/static/background2.png') no-repeat center center / cover;
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

.form-section {
  .input-wrapper {
      background:rgba(255, 255, 255, 0.9);
      //background: #ffffff;
      border-radius: $size-6;
      box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
      .shadow-\[0_8px_24px_rgba\(160\2c 62\2c 64\2c 0\.06\)\] {
          --tw-shadow: 0 8px 24px rgba(160, 62, 64, 0.12);
          --tw-shadow-colored: 0 8px 24px var(--tw-shadow-color);
          box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
      }      
      overflow: hidden;
      margin-bottom: $size-6;
    
      &:last-child {
          margin-bottom: 0;
      }
  }
  
  .input-item {
      position: relative;
      padding: 0 $size-5;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border: none;
      border-bottom: 3rpx solid rgba(160, 62, 64, 0.1);
    
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
    
      .input-label {
          font-size: 28rpx;
          color: $color-label;
          flex: 1;
          font-weight: 400;
          margin: $size-4 $size-4 $size-4 0;
      }
    
      .input-text, .picker{
          flex: 2;
          height: $size-10;
          font-size: $size-4;
          font-weight: 700;
          color: $color-input;
          padding: 0;
          box-sizing: border-box;
          align-content: center;
          text-align: right;
      }
      
      .input-text {
        font-weight: 700;
        letter-spacing: 1rpx;
      }
      .picker {
        font-weight: 600;
        letter-spacing: 2rpx;
      }
  }
}
.bmi-card {
  //background: #ffffff;
  background:rgba(255, 255, 255, 0.7);
  border-radius: $size-6;
  padding: $size-8;
  margin-top: $size-4;
  line-height: $size-9;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
    
  .bmi-label {
      display: block;
      font-size: $size-5;
      color: $color-primary;
      font-weight: 700;
      margin-bottom: $size-2;
  }
    
  .bmi-value {
      display: flex;
      font-size: 120rpx;
      font-weight: 700;
      color: $color-input;
      gap: $size-5;
      display: flex;
      align-items: center;
      margin-bottom: $size-4;

      .bmi-status {
        font-size: $size-4;
        padding: 0 $size-3;
        border-radius: $size-3;
        
        &.status-normal {
          background: $uni-success-bg;
          color: $uni-success;
        }
        
        &.status-warning {
          background: $uni-warning-bg;
          color: $uni-warning;
        }
        
        &.status-danger {
          background: $uni-error-bg;
          color: $uni-error;
        }
      }
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
  margin-top: $size-4;
      
  &[disabled] {
      opacity: 0.6;
  }
}
</style>