<template>
  <view class="container">
    <view class="top-section" v-if="gymInfo">
      <view class="gym-info-card">
        <view class="gym-content">
          <view class="info-section">
            <view class="gym-header">
              <text class="gym-name">{{ gymInfo.location_tag }}</text>
              <text class="gym-extra-info">
                <text class="gym-count">{{ gymInfo.equipment_count }} 个器材</text>
                <text class="gym-created" v-if="gymInfo.create_time">· {{ formatDate(gymInfo.create_time) }}</text>
              </text>
            </view>
            <view class="gym-description" v-if="gymInfo.description">
              <text class="desc-text">{{ gymInfo.description }}</text>
            </view>
            <view class="gym-description" v-else>
              <text class="desc-text-empty">暂无描述</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="action-section">
        <button class="action-btn scan" @click="navigateToCameraScan">
          <image src="/static/camera3.png" class="btn-icon" mode="aspectFit" />
          <text class="btn-text">拍摄识别</text>
        </button>
        <button class="action-btn manual" @click="navigateToManualAdd">
          <image src="/static/search.png" class="btn-icon" mode="aspectFit" />
          <text class="btn-text">手动添加</text>
        </button>
        <button class="action-btn plan" @click="generatePlan">
          <image src="/static/generate3.png" class="btn-icon" mode="aspectFit" />
          <text class="btn-text">生成计划</text>
        </button>
      </view>
    </view>
    
    <view class="equipment-list" v-if="equipmentList.length > 0">
      <view 
        class="equipment-card" 
        v-for="equipment in equipmentList" 
        :key="equipment.equipment_id"
        @click="navigateToEquipmentDetail(equipment.equipment_id)"
      >
        <view class="equipment-image-wrapper">
          <image 
            :src="'/static/' + equipment.image_url" 
            class="equipment-image"
            mode="aspectFill"
            @error="onImageError"
            lazy-load
          />
          <view class="image-placeholder" v-if="!equipment.image_url">
            <text class="placeholder-icon">🏋️</text>
          </view>
        </view>
        
        <view class="equipment-info">
          <text class="equipment-name">{{ equipment.name }}</text>
          <text class="equipment-category">{{ equipment.category }}</text>
          <text class="equipment-muscles" v-if="equipment.target_muscles && equipment.target_muscles.length > 0">
            {{ equipment.target_muscles.slice(0, 3).join('、') }}{{ equipment.target_muscles.length > 3 ? '...' : '' }}
          </text>
        </view>
        
        <view class="delete-btn" @click.stop="confirmDeleteEquipment(equipment)">
          <image src="/static/delete.png" class="delete-icon" mode="aspectFit" />
        </view>
      </view>
    </view>
    
    <view class="empty-state" v-else>
      <image src="/static/empty-data.png" class="empty-image" mode="aspectFit" />
      <text class="empty-text">暂无器材</text>
      <text class="empty-subtext">拍摄识别或手动添加器材</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import { API } from '@/utils/constants'

const userStore = useUserStore()
const inventoryId = ref('')
const gymInfo = ref(null)
const equipmentList = ref([])

// 图片加载状态跟踪
const imageErrorMap = ref({})

onLoad((options) => {
  inventoryId.value = options.inventory_id || ''
})

onShow(async () => {
  if (userStore.isLogin && inventoryId.value) {
    await loadGymDetail()
  }
})

/**
 * 加载健身房详情
 */
const loadGymDetail = async () => {
  try {
    const res = await request.get(`${API.GYM_DETAIL}/${inventoryId.value}`)
    gymInfo.value = res
    console.log('健身房详情:', gymInfo.value)
    equipmentList.value = res.equipment_list || []
  } catch (error) {
    console.error('加载健身房详情失败:', error)
  }
}

/**
 * 格式化日期
 */
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

/**
 * 获取器材图片 URL
 * 处理空值和本地图片路径
 */
const getImageUrl = (imageUrl) => {
  if (!imageUrl) {
    return ''
  }
  // 如果是完整 URL，直接返回
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl
  }
  // 如果是本地路径，拼接后端服务器地址
  return 'http://localhost:8000' + imageUrl
}

/**
 * 图片加载错误处理
 */
const onImageError = (e) => {
  const index = e.currentTarget.dataset.index
  imageErrorMap.value[index] = true
  console.log('图片加载失败:', e)
}

/**
 * 跳转至拍摄识别页面
 */
const navigateToCameraScan = () => {
  uni.navigateTo({ url: `/pages/gym/camera-scan?inventory_id=${inventoryId.value}` })
}

/**
 * 跳转至手动添加页面
 */
const navigateToManualAdd = () => {
  uni.navigateTo({ url: `/pages/gym/add-equipment-manual-1?inventory_id=${inventoryId.value}` })
}

/**
 * 跳转至器材详情页面
 */
const navigateToEquipmentDetail = (equipmentId) => {
  uni.navigateTo({ url: `/pages/gym/equipment-detail?equipment_id=${equipmentId}` })
}

/**
 * 确认删除器材
 */
const confirmDeleteEquipment = (equipment) => {
  uni.showModal({
    content: `确定要从清单中删除"${equipment.name}"吗？`,
    confirmColor: '#FF4D4F',
    success: async (res) => {
      if (res.confirm) {
        await deleteEquipment(equipment.equipment_id)
      }
    }
  })
}

/**
 * 删除器材
 */
const deleteEquipment = async (equipmentId) => {
  try {
    await request.delete(`${API.EQUIPMENT_DELETE}/${inventoryId.value}/${equipmentId}`)
    uni.showToast({ title: '删除成功', icon: 'success' })
    await loadGymDetail()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

/**
 * 生成训练计划
 */
const generatePlan = () => {
  // 检查资料完整性
  if (!userStore.isProfileComplete) {
    uni.showModal({
      title: '提示',
      content: '请先完善身体数据后再生成训练计划',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/profile/body-data' })
        }
      }
    })
    return
  }
  
  // 检查器材数量
  if (equipmentList.value.length < 3) {
    uni.showToast({ title: '建议至少添加 3 个器材', icon: 'none' })
    return
  }
  
  uni.navigateTo({ url: `/pages/plan/generate-plan?inventory_id=${inventoryId.value}` })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: #FFFFFF;
  padding: 32rpx;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.top-section {
  display: flex;
  flex-direction: row;
  gap: 24rpx;
  margin-bottom: 48rpx;
  align-items: stretch;
}

.gym-info-card {
  flex: 1;
  background: rgba(252, 249, 248, 0.7);
  border-radius: 32rpx;
  padding: 48rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
  border: 2rpx solid #efefef;
  
  .gym-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    
    .info-section {
      flex: auto;

      .gym-header {
        .gym-name {
          display: block;
          font-size: 48rpx;
          font-weight: 700;
          color: #a03e40;
          margin-bottom: 16rpx;
          line-height: 1.3;
        }
        
        .gym-extra-info {
          display: flex;
          font-size: 24rpx;
          color: #8E8E93;
          line-height: 1.4;
          
          .gym-count,
          .gym-created {
            margin-right: 8rpx;
          }
        }
      }
      
      .gym-description {
        margin-top: 24rpx;
        
        .desc-text {
          display: block;
          font-size: 24rpx;
          color: #564241;
          line-height: 1.4;
        }
        
        .desc-text-empty {
          display: block;
          font-size: 24rpx;
          color: #8E8E93;
          line-height: 1.4;
          font-style: italic;
        }
      }
    }
  }
}

.action-section {
  width: max-content;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  flex-shrink: 0;

  .action-btn {
    width: 100%;
    height: 96rpx;
    border-radius: 32rpx;
    border: none;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    padding: 0 32rpx;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
    transition: all 0.2s ease;

    &:active {
      transform: scale(0.96);
      box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.08);
    }

    &::after {
      border: none;
    }
      
    .btn-icon {
      width: 40rpx;
      height: 40rpx;
      margin-right: 12rpx;
    }
      
    .btn-text {
      font-size: 32rpx;
      font-weight: 700;
      line-height: 1.2;
    }
      
    &.scan {
      background: rgba(82, 196, 26, 0.15);
      color: #52C41A;
    }
    
    &.manual {
      background: rgba(255, 107, 143, 0.15);
      color: #FF6B8F;
    }
    
    &.plan {
      background: rgba(255, 193, 7, 0.15);
      color: #E6AC00;
    }
  }
}

.equipment-list {
  .equipment-card {
    background: #FFFFFF;
    border-radius: 32rpx;
    padding: 32rpx;
    margin-bottom: 24rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
    border: 2rpx solid #efefef;
    transition: all 0.2s ease;
    
    &:active {
      transform: scale(0.98);
      box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.08);
    }
    
    .equipment-image-wrapper {
      position: relative;
      width: 160rpx;
      height: 160rpx;
      margin-right: 32rpx;
      flex-shrink: 0;
      
      .equipment-image {
        width: 100%;
        height: 100%;
        border-radius: 32rpx;
        background: #F2F2F7;
        object-fit: cover;
      }
      
      .image-placeholder {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #F2F2F7;
        border-radius: 32rpx;
        display: flex;
        justify-content: center;
        align-items: center;
        
        .placeholder-icon {
          font-size: 64rpx;
        }
      }
    }
    
    .equipment-info {
      flex: 1;
      min-width: 0;
      
      .equipment-name {
        display: block;
        font-size: 32rpx;
        font-weight: 700;
        color: #1B1C1C;
        margin-bottom: 12rpx;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.3;
      }
      
      .equipment-category {
        display: block;
        font-size: 24rpx;
        font-weight: 700;
        color: #a03e40;
        margin-bottom: 8rpx;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.4;
      }
      
      .equipment-muscles {
        display: block;
        font-size: 24rpx;
        color: #8E8E93;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.4;
      }
    }
    
    .delete-btn {
      width: 64rpx;
      height: 64rpx;
      background: transparent;
      border-radius: 32rpx;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-left: 16rpx;
      flex-shrink: 0;
      transition: all 0.2s ease;
      
      &:active {
        transform: scale(0.95);
        opacity: 0.6;
      }
      
      .delete-icon {
        width: 36rpx;
        height: 36rpx;
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx 0;
  
  .empty-image {
    width: 400rpx;
    height: 300rpx;
    margin-bottom: 40rpx;
  }
  
  .empty-text {
    font-size: 32rpx;
    color: #1B1C1C;
    margin-bottom: 16rpx;
    font-weight: 700;
    text-align: center;
    line-height: 1.3;
  }
  
  .empty-subtext {
    font-size: 24rpx;
    color: #8E8E93;
    text-align: center;
    font-weight: 525;
    line-height: 1.4;
  }
}
</style>