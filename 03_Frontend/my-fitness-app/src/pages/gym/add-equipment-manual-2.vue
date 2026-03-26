<template>
  <view class="container">
    <!-- 添加设备图片 -->
    <view class="equipment-image-container">
      <image :src="'/static/'+equipmentImageUrl"
            class="equipment-image" 
            mode="aspectFit" 
            lazy-load
      />
    </view>
    
    <view class="info-card">
      <view class="info-header">
        <text class="info-label">器材名称</text>
        <text class="info-name">{{ equipmentName }}</text>
      </view>
      
      <view class="info-details">
        <view class="detail-item">
          <text class="detail-label">描述</text>
          <text class="detail-value">{{ equipmentDescription }}</text>
        </view>
        
        <view class="detail-item">
          <text class="detail-label">器材类别</text>
          <text class="detail-value">{{ equipmentCategory }}</text>
        </view>
        
        <view class="detail-item">
          <text class="detail-label">目标肌群</text>
          <text class="detail-value">{{ targetMuscles.join(', ') }}</text>
        </view>
      </view>
    </view>
    
    <!-- 相关动作列表 -->
    <view class="actions-card" v-if="relatedActions && relatedActions.length > 0">
      <view class="card-header">
        <text class="card-title">相关动作 ({{ actionsCount }})</text>
      </view>
      
      <view class="actions-list">
        <view 
          class="action-item" 
          v-for="(action, index) in relatedActions" 
          :key="action.id"
          :class="{ 'border-none': index === relatedActions.length - 1 }"
        >
          <text class="action-name">{{ action.name }}</text>
          <text class="action-description">{{ action.description }}</text>
        </view>
      </view>
    </view>
    
    <view class="action-section">
      <button class="confirm-btn" @click="confirmAdd" :loading="loading" :disabled="loading">
        {{ loading ? '添加中...' : '确认添加到我的器材' }}
      </button>
      
      <button class="cancel-btn" @click="navigateToEquipmentList(inventoryId)" :disabled="loading">
        取消
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API } from '@/utils/constants'

const inventoryId = ref('')
const equipmentId = ref('')
const equipmentName = ref('') // 设备名称
const equipmentCategory = ref('') // 设备类别
const equipmentDescription = ref('') // 设备描述
const equipmentImageUrl = ref('')
const actionsCount = ref(0) // 相关动作数量
const relatedActions = ref([]) // 相关动作列表
const targetMuscles = ref([]) // 目标肌群
const loading = ref(false)


onLoad((options) => {
  inventoryId.value = options.inventory_id || ''
  equipmentId.value = options.equipment_id || ''
  
  console.log('设备详情参数:', {
    inventoryId: inventoryId.value,
    equipmentId: equipmentId.value
  })
  // 获取设备详情，包括图片
  loadEquipmentDetail()
})

/**
 * 加载设备详情
 */
const loadEquipmentDetail = async () => {
  const res = await request.get(`${API.EQUIPMENT_DETAIL}/${equipmentId.value}`)
  console.log('设备详情数据:', res)
  equipmentName.value = res.name
  equipmentCategory.value = res.category
  equipmentDescription.value = res.description
  equipmentImageUrl.value = res.image_url
  actionsCount.value = res.supported_actions_count
  relatedActions.value = res.supported_actions
  targetMuscles.value = res.target_muscles
}

/**
 * 确认添加
 */
const confirmAdd = async () => {
  if (!inventoryId.value || !equipmentId.value) {
    uni.showToast({ title: '参数错误', icon: 'none' })
    return
  }
  
  loading.value = true
  try {
    await request.post(`${API.EQUIPMENT_ADD_MANUAL}/${inventoryId.value}/manual`, {
      inventory_id: inventoryId.value,
      equipment_id: equipmentId.value
    })
    uni.showToast({ title: '添加成功', icon: 'success' })
    await navigateToEquipmentList(inventoryId.value);
  } catch (error) {
    console.error('添加失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 跳转至器材清单页面
 */
const navigateToEquipmentList = (inventoryId) => {
  uni.navigateTo({ url: `/pages/gym/equipment-list?inventory_id=${inventoryId}` })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background-color: $fitness-primary;
  padding: 30rpx;
  box-sizing: border-box;
}

.equipment-image-container {
  width: 100%;
  height: 400rpx;
  border-radius: $radius-lg;
  margin-bottom: 40rpx;
  position: relative;
  overflow: hidden;
  background-color: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: center;
  
  .equipment-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .no-image-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    
    .icon-equipment {
      font-size: 120rpx;
      color: #ccc;
    }
  }
}

.info-card {
  background: #FFFFFF;
  border-radius: $radius-lg;
  padding: 40rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  
  .info-header {
    margin-bottom: 40rpx;
    padding-bottom: 30rpx;
    border-bottom: 1rpx solid $fitness-border;
    
    .info-label {
      display: block;
      font-size: $font-sm;
      color: $fitness-text-gray;
      margin-bottom: 10rpx;
    }
    
    .info-name {
      display: block;
      font-size: $font-xxl;
      font-weight: bold;
      color: $fitness-text;
    }
  }
  
  .info-details {
    .detail-item {
      display: flex;
      flex-direction: column;
      padding: 20rpx 0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .detail-label {
        font-size: $font-md;
        color: $fitness-text-light;
        margin-bottom: 10rpx;
      }
      
      .detail-value {
        font-size: $font-md;
        color: $fitness-text;
        word-break: break-word;
        line-height: 1.5;
      }
    }
  }
}

.actions-card {
  background: #FFFFFF;
  border-radius: $radius-lg;
  padding: 40rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  
  .card-header {
    margin-bottom: 30rpx;
    
    .card-title {
      font-size: $font-lg;
      font-weight: bold;
      color: $fitness-text;
    }
  }
  
  .actions-list {
    .action-item {
      padding: 20rpx 0;
      border-bottom: 1rpx solid $fitness-border;
      
      .action-name {
        display: block;
        font-size: $font-md;
        font-weight: bold;
        color: $fitness-text;
        margin-bottom: 10rpx;
      }
      
      .action-description {
        display: block;
        font-size: $font-sm;
        color: $fitness-text-gray;
        line-height: 1.4;
      }
    }
    
    .border-none {
      border-bottom: none;
    }
  }
}

.action-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  
  .confirm-btn {
    width: 100%;
    height: 90rpx;
    background: $uni-primary;
    color: #FFFFFF;
    font-size: $font-lg;
    border-radius: 45rpx;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .cancel-btn {
    width: 100%;
    height: 90rpx;
    background:$fitness-placeholder;
    color: $fitness-primary;
    font-size: $font-lg;
    border-radius: 45rpx;
    border: 1rpx solid $fitness-border;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>