<template>
  <view class="container">
    <!-- ✅ 新增：健身房信息卡片 -->
    <view class="gym-info-card" v-if="gymInfo">
      <view class="gym-header">
        <text class="gym-name">{{ gymInfo.location_tag }}</text>
        <text class="gym-count">器材数量：{{ gymInfo.equipment_count }} 个</text>
      </view>
      
      <view class="gym-description" v-if="gymInfo.description">
        <text class="desc-label">📝 描述：</text>
        <text class="desc-text">{{ gymInfo.description }}</text>
      </view>
      
      <view class="gym-description" v-else>
        <text class="desc-label">📝 描述：</text>
        <text class="desc-text-empty">暂无描述</text>
      </view>
      
      <view class="action-buttons">
        <button class="action-btn scan" @click="navigateToCameraScan">
          <text class="btn-icon">📷</text>
          <text class="btn-text">拍摄识别</text>
        </button>
        <button class="action-btn manual" @click="navigateToManualAdd">
          <text class="btn-icon">🔍</text>
          <text class="btn-text">手动添加</text>
        </button>
        <button class="action-btn plan" @click="generatePlan">
          <text class="btn-icon">📋</text>
          <text class="btn-text">生成计划</text>
        </button>
      </view>
    </view>
    
    <!-- 器材列表 -->
    <view class="equipment-list" v-if="equipmentList.length > 0">
      <view 
        class="equipment-card" 
        v-for="(equipment, index) in equipmentList" 
        :key="equipment.equipment_id"
        @click="navigateToEquipmentDetail(equipment.equipment_id)"
      >
        <!-- 器材图片 -->
        <view class="equipment-image-wrapper">
          <image 
            :src="'/static/' + equipment.image_url" 
            class="equipment-image"
            mode="aspectFill"
            @error="onImageError"
            lazy-load
          />
          <!-- 图片加载失败时的备用显示 -->
          <view class="image-placeholder" v-if="!equipment.image_url">
            <text class="placeholder-icon">🏋️</text>
          </view>
        </view>
        
        <!-- 器材信息 -->
        <view class="equipment-info">
          <text class="equipment-name">{{ equipment.name }}</text>
          <text class="equipment-category">{{ equipment.category }}</text>
          <text class="equipment-muscles" v-if="equipment.target_muscles && equipment.target_muscles.length > 0">
            目标肌群：{{ equipment.target_muscles.slice(0, 3).join('、') }}{{ equipment.target_muscles.length > 3 ? '...' : '' }}
          </text>
        </view>
        
        <!-- 删除按钮 -->
        <view class="delete-btn" @click.stop="confirmDeleteEquipment(equipment)">
          <text class="delete-icon">🗑️</text>
        </view>
      </view>
    </view>
    
    <!-- 空状态提示 -->
    <view class="empty-state" v-else>
      <image src="/static/empty-equipment.png" class="empty-image" mode="aspectFit" />
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
    title: '提示',
    content: `确定要从清单中删除"${equipment.name}"吗？`,
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
  background: $fitness-secondary;
}

// ✅ 新增：健身房信息卡片样式
.gym-info-card {
  background: $fitness-card-bg;
  margin: 30rpx $size-5;
  border-radius: $size-5;
  padding: $size-5;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  
  .gym-header {
    margin-bottom: 20rpx;
    
    .gym-name {
      display: block;
      font-size: $size-6;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 10rpx;
    }
    
    .gym-count {
      display: block;
      font-size: $size-3;
      color: $color-label;
    }
  }
  
  .gym-description {
    margin-bottom: 30rpx;
    padding: 20rpx;
    background: $fitness-input-bg;
    border-radius: $size-4;
    
    .desc-label {
      font-size: $size-3;
      color: $color-label;
      margin-right: 10rpx;
    }
    
    .desc-text {
      font-size: $size-3;
      color: $fitness-text;
      line-height: 1.6;
    }
    
    .desc-text-empty {
      font-size: $size-3;
      color: $color-label;
      font-style: italic;
    }
  }
  
  .action-buttons {
    display: flex;
    justify-content: space-between;
    gap: 20rpx;
    
    .action-btn {
      flex: 1;
      height: 100rpx;
      border-radius: $size-4;
      border: none;
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;
      
      .btn-icon {
        font-size: $size-5;
      }
      
      .btn-text {
        font-size: $size-2;
      }
      
      &.scan {
        background: linear-gradient(135deg, #007AFF, #00C6FB);
        color: #FFFFFF;
      }
      
      &.manual {
        background: linear-gradient(135deg, #34C759, #30D158);
        color: #FFFFFF;
      }
      
      &.plan {
        background: linear-gradient(135deg, #FF9500, #FFAD33);
        color: #FFFFFF;
      }
    }
  }
}

.equipment-list {
  padding: 0 $size-5 $size-5;
  
  .equipment-card {
    background: $fitness-card-bg;
    border-radius: $size-4;
    padding: 20rpx;
    margin-bottom: 30rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
    
    // 图片区域样式
    .equipment-image-wrapper {
      position: relative;
      width: 160rpx;
      height: 160rpx;
      margin-right: 20rpx;
      flex-shrink: 0;
      
      .equipment-image {
        width: 100%;
        height: 100%;
        border-radius: $size-3;
        background: #F5F5F5;
      }
      
      .image-placeholder {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #F5F5F5;
        border-radius: $size-3;
        display: flex;
        justify-content: center;
        align-items: center;
        
        .placeholder-icon {
          font-size: 60rpx;
        }
      }
    }
    
    .equipment-info {
      flex: 1;
      min-width: 0;
      
      .equipment-name {
        display: block;
        font-size: $size-5;
        font-weight: bold;
        color: $fitness-text;
        margin-bottom: 10rpx;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .equipment-category {
        display: block;
        font-size: $size-3;
        color: $uni-primary;
        margin-bottom: 10rpx;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .equipment-muscles {
        display: block;
        font-size: $size-2;
        color: $color-label;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
    
    .delete-btn {
      width: 60rpx;
      height: 60rpx;
      background: #FFEBEE;
      border-radius: 30rpx;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-left: 10rpx;
      flex-shrink: 0;
      
      .delete-icon {
        font-size: 2$size-1;
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx $size-5;
  
  .empty-image {
    width: 300rpx;
    height: 300rpx;
    margin-bottom: $size-5;
  }
  
  .empty-text {
    font-size: $size-5;
    color: $color-label;
    margin-bottom: 10rpx;
  }
  
  .empty-subtext {
    font-size: $size-3;
    color: $color-label;
  }
}
</style>