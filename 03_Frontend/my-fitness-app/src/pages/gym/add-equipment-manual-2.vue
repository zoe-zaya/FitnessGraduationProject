<template>
    <view class="container">
      <view class="info-card">
        <text class="info-title">确认添加器材</text>
        <text class="info-name">{{ equipmentName }}</text>
        <text class="info-tip">将添加至当前健身房器材清单</text>
      </view>
      
      <button class="confirm-btn" @click="confirmAdd" :loading="loading">
        确认添加
      </button>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { onLoad } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const inventoryId = ref('')
  const equipmentId = ref('')
  const equipmentName = ref('')
  const loading = ref(false)
  
  onLoad((options) => {
    inventoryId.value = options.inventory_id || ''
    equipmentId.value = options.equipment_id || ''
    equipmentName.value = options.name || '未知器材'
  })
  
  /**
   * 确认添加
   */
  const confirmAdd = async () => {
    loading.value = true
    
    try {
      await request.post(`${API.EQUIPMENT_ADD_MANUAL}/${inventoryId.value}/manual`, {
        inventory_id: inventoryId.value,
        equipment_id: equipmentId.value
      })
      
      uni.showToast({ title: '添加成功', icon: 'success' })
      
      setTimeout(() => {
        uni.navigateBack({ delta: 2 })
      }, 1000)
    } catch (error) {
      console.error('添加失败:', error)
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
    padding: 40rpx;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  
  .info-card {
    background: #FFFFFF;
    border-radius: $radius-lg;
    padding: 60rpx 40rpx;
    text-align: center;
    margin-bottom: 60rpx;
    
    .info-title {
      display: block;
      font-size: $font-md;
      color: $fitness-text-light;
      margin-bottom: 20rpx;
    }
    
    .info-name {
      display: block;
      font-size: $font-xxl;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 30rpx;
    }
    
    .info-tip {
      display: block;
      font-size: $font-sm;
      color: $fitness-text-gray;
    }
  }
  
  .confirm-btn {
    width: 100%;
    height: 90rpx;
    background: $fitness-primary;
    color: #FFFFFF;
    font-size: $font-lg;
    border-radius: 45rpx;
    border: none;
  }
  </style>