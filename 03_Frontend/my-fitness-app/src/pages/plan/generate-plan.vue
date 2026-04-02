<template>
    <view class="container">
      <!-- 表单区域 -->
      <view class="form-section">
        <!-- 选择健身房 -->
        <view class="form-item">
          <text class="form-label">选择健身房 *</text>
          <picker 
            @change="onGymChange" 
            :value="selectedGymIndex" 
            :range="gymList"
            range-key="location_tag"
            class="form-picker"
          >
            <view class="picker-wrapper">
              <text class="picker-text">
                {{ gymList[selectedGymIndex]?.location_tag || '请选择健身房' }}
              </text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>
        
        <!-- 健身目标 -->
        <view class="form-item">
          <text class="form-label">健身目标 *</text>
          <picker 
            @change="onGoalChange" 
            :value="selectedGoalIndex" 
            :range="goalOptions"
            range-key="label"
            class="form-picker"
          >
            <view class="picker-wrapper">
              <text class="picker-text">
                {{ goalOptions[selectedGoalIndex]?.label || '请选择健身目标' }}
              </text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>
        
        <!-- 训练部位（增肌/塑形显示） -->
        <view class="form-item" v-if="showTrainingPart">
          <text class="form-label">训练部位 *</text>
          <picker 
            @change="onPartChange" 
            :value="selectedPartIndex" 
            :range="partOptions"
            range-key="label"
            class="form-picker"
          >
            <view class="picker-wrapper">
              <text class="picker-text">
                {{ partOptions[selectedPartIndex]?.label || '请选择训练部位' }}
              </text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
          <text class="form-tip">增肌/塑形需指定具体训练部位</text>
        </view>
        
        <!-- 计划名称（可选） -->
        <view class="form-item">
          <text class="form-label">计划名称</text>
          <input 
            v-model="planName" 
            type="text" 
            placeholder="可选，默认自动生成"
            class="form-input"
            maxlength="50"
          />
        </view>
      </view>
      
      <!-- 说明卡片 -->
      <view class="info-card">
        <text class="card-title">💡 计划生成说明</text>
        <view class="card-content">
          <text class="content-text">• 系统将根据您的健身目标和器材清单生成个性化训练计划</text>
          <text class="content-text">• 计划包含热身激活、正式训练、拉伸放松三个阶段</text>
          <text class="content-text">• 计划总时长约 40-65 分钟</text>
          <text class="content-text">• 计划有效期 30 天，过期后可重新生成</text>
        </view>
      </view>
      
      <!-- 生成按钮 -->
      <view class="action-section">
        <button 
          class="generate-btn" 
          @click="generatePlan" 
          :loading="loading"
          :disabled="!canGenerate"
        >
          {{ loading ? '生成中...' : '生成训练计划' }}
        </button>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import {onShow} from '@dcloudio/uni-app'
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API, FITNESS_GOALS, TRAINING_PARTS } from '@/utils/constants'
  
  const userStore = useUserStore()
  const loading = ref(false)
  
  // 健身房列表
  const gymList = ref([])
  const selectedGymIndex = ref(-1)
  
  // 健身目标
  const goalOptions = ref(FITNESS_GOALS)
  const selectedGoalIndex = ref(-1)
  
  // 训练部位
  const partOptions = ref(TRAINING_PARTS)
  const selectedPartIndex = ref(-1)
  
  // 计划名称
  const planName = ref('')
  
  // 是否显示训练部位选择
  const showTrainingPart = computed(() => {
    const goal = goalOptions.value[selectedGoalIndex.value]?.value
    return goal === '增肌' || goal === '塑形'
  })
  
  // 是否可以生成
  const canGenerate = computed(() => {
    if (selectedGymIndex.value < 0) return false
    if (selectedGoalIndex.value < 0) return false
    if (showTrainingPart.value && selectedPartIndex.value < 0) return false
    return true
  })
  
  onShow(async () => {
    await loadGymList()
    // 默认选择用户的健身目标
    const userGoal = userStore.userInfo.fitness_goal
    if (userGoal) {
      const index = FITNESS_GOALS.findIndex(g => g.value === userGoal)
      if (index >= 0) selectedGoalIndex.value = index
    }
  })
  
  /**
   * 加载健身房列表
   */
  const loadGymList = async () => {
    try {
      const res = await request.get(API.GYM_LIST)
      gymList.value = res
      if (res.length > 0) {
        selectedGymIndex.value = 0
      }
    } catch (error) {
      console.error('加载健身房列表失败:', error)
    }
  }
  
  /**
   * 选择健身房
   */
  const onGymChange = (e) => {
    selectedGymIndex.value = e.detail.value
  }
  
  /**
   * 选择健身目标
   */
  const onGoalChange = (e) => {
    selectedGoalIndex.value = e.detail.value
    // 如果切换到减脂/体能，重置训练部位为全身
    const goal = goalOptions.value[e.detail.value]?.value
    if (goal === '减脂' || goal === '增强体能') {
      selectedPartIndex.value = TRAINING_PARTS.findIndex(p => p.value === '全身')
    }
  }
  
  /**
   * 选择训练部位
   */
  const onPartChange = (e) => {
    selectedPartIndex.value = e.detail.value
  }
  
  /**
   * 生成训练计划
   */
  const generatePlan = async () => {
    if (!canGenerate.value) {
      uni.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }
    
    loading.value = true
    
    try {
      const goal = goalOptions.value[selectedGoalIndex.value]?.value
      const part = partOptions.value[selectedPartIndex.value]?.value
      const gym = gymList.value[selectedGymIndex.value]
      
      const res = await request.post(API.PLAN_GENERATE, {
        inventory_id: gym.inventory_id,
        fitness_goal: goal,
        training_part: showTrainingPart.value ? part : '全身',
        plan_name: planName.value || undefined
      })
      
      uni.showToast({ title: '生成成功', icon: 'success' })
      
      setTimeout(() => {
        uni.redirectTo({ url: `/pages/plan/plan-detail?plan_id=${res.plan_id}` })
      }, 1000)
      
    } catch (error) {
      console.error('生成失败:', error)
      uni.showToast({ 
        title: error.detail || '生成失败', 
        icon: 'none',
        duration: 3000
      })
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style lang="scss" scoped>
  .container {
    min-height: 100vh;
    background: #F5F5F5;
    padding: 0 0 60rpx;
  }
  
  .form-section {
    background: #FFFFFF;
    margin: 30rpx 40rpx;
    border-radius: 24rpx;
    padding: 32rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
    
    .form-item {
      margin-bottom: 32rpx;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .form-label {
        display: block;
        font-size: 28rpx;
        font-weight: 600;
        color: #333333;
        margin-bottom: 16rpx;
      }
      
      .form-picker {
        .picker-wrapper {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24rpx 30rpx;
          background: #F5F5F5;
          border-radius: 16rpx;
          
          .picker-text {
            font-size: 28rpx;
            color: #333333;
          }
          
          .picker-arrow {
            font-size: 32rpx;
            color: #999999;
          }
        }
      }
      
      .form-input {
        width: 100%;
        height: 88rpx;
        background: #F5F5F5;
        border-radius: 16rpx;
        padding: 0 30rpx;
        font-size: 28rpx;
        box-sizing: border-box;
      }
      
      .form-tip {
        display: block;
        font-size: 24rpx;
        color: #999999;
        margin-top: 12rpx;
      }
    }
  }
  
  .info-card {
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
    margin: 0 40rpx 30rpx;
    border-radius: 24rpx;
    padding: 32rpx;
    border-left: 6rpx solid #1976D2;
    
    .card-title {
      display: block;
      font-size: 30rpx;
      font-weight: bold;
      color: #1565C0;
      margin-bottom: 20rpx;
    }
    
    .card-content {
      .content-text {
        display: block;
        font-size: 26rpx;
        color: #1976D2;
        line-height: 1.8;
        margin-bottom: 8rpx;
      }
    }
  }
  
  .action-section {
    padding: 0 40rpx;
    
    .generate-btn {
      width: 100%;
      height: 96rpx;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #FFFFFF;
      font-size: 32rpx;
      font-weight: 600;
      border-radius: 48rpx;
      border: none;
      box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
      
      &[disabled] {
        background: #CCCCCC;
        box-shadow: none;
      }
    }
  }
  </style>