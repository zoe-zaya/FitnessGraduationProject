<template>
    <view class="container">
      <view class="info-card">
        <text class="equipment-name">{{ equipmentInfo.name }}</text>
        <text class="equipment-category">{{ equipmentInfo.category }}</text>
        <text class="equipment-desc">{{ equipmentInfo.description }}</text>
      </view>
      
      <view class="section">
        <text class="section-title">目标肌群</text>
        <view class="muscles-tags">
          <text 
            class="muscle-tag" 
            v-for="(muscle, index) in equipmentInfo.target_muscles" 
            :key="index"
          >
            {{ muscle }}
          </text>
        </view>
      </view>
      
      <view class="section">
        <text class="section-title">支持动作</text>
        <text class="actions-count">{{ equipmentInfo.supported_actions_count }} 个标准动作</text>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { onShow, onLoad } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const equipmentId = ref('')
  const equipmentInfo = ref({
    name: '',
    category: '',
    description: '',
    target_muscles: [],
    supported_actions_count: 0
  })
  
  onLoad((options) => {
    equipmentId.value = options.equipment_id || ''
  })
  
  onShow(async () => {
    if (equipmentId.value) {
      await loadEquipmentDetail()
    }
  })
  
  /**
   * 加载器材详情
   */
  const loadEquipmentDetail = async () => {
    try {
      const res = await request.get(`${API.EQUIPMENT_DETAIL}/${equipmentId.value}`)
      equipmentInfo.value = res
    } catch (error) {
      console.error('加载失败:', error)
    }
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: $fitness-primary;
    padding: 40rpx;
  }
  
  .info-card {
    background: #FFFFFF;
    border-radius: $radius-md;
    padding: 40rpx;
    margin-bottom: 30rpx;
    
    .equipment-name {
      display: block;
      font-size: $font-xxl;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 15rpx;
    }
    
    .equipment-category {
      display: block;
      font-size: $font-sm;
      color: $uni-primary;
      margin-bottom: 20rpx;
    }
    
    .equipment-desc {
      display: block;
      font-size: $font-md;
      color: $fitness-text-light;
      line-height: 1.6;
    }
  }
  
  .section {
    background: #FFFFFF;
    border-radius: $radius-md;
    padding: 30rpx;
    margin-bottom: 30rpx;
    
    .section-title {
      display: block;
      font-size: $font-lg;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 20rpx;
    }
    
    .muscles-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 15rpx;
      
      .muscle-tag {
        background: #E3F2FD;
        color: #1976D2;
        font-size: $font-sm;
        padding: 10rpx 20rpx;
        border-radius: 20rpx;
      }
    }
    
    .actions-count {
      font-size: $font-md;
      color: $fitness-text-light;
    }
  }
  </style>