<template>
    <view class="container">
      <!-- 健身房信息 -->
      <view class="gym-header" v-if="gymInfo">
        <text class="gym-name">{{ gymInfo.location_tag }}</text>
        <text class="gym-count">{{ gymInfo.equipment_count }} 个器材</text>
      </view>
      
      <!-- 操作栏 -->
      <view class="action-bar">
        <view class="action-btn" @click="navigateToCameraScan">
          <text class="action-icon">📷</text>
          <text class="action-text">拍摄识别</text>
        </view>
        <view class="action-btn" @click="navigateToManualAdd">
          <text class="action-icon">🔍</text>
          <text class="action-text">手动添加</text>
        </view>
        <view class="action-btn" @click="generatePlan">
          <text class="action-icon">📋</text>
          <text class="action-text">生成计划</text>
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
          <view class="equipment-info">
            <text class="equipment-name">{{ equipment.name }}</text>
            <text class="equipment-category">{{ equipment.category }}</text>
            <text class="equipment-muscles" v-if="equipment.target_muscles">
              目标肌群：{{ equipment.target_muscles.join('、') }}
            </text>
          </view>
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
  import { onShow } from '@dcloudio/uni-app'
  import { onLoad } from '@dcloudio/uni-app'
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const userStore = useUserStore()
  const inventoryId = ref('')
  const gymInfo = ref(null)
  const equipmentList = ref([])
  
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
      equipmentList.value = res.equipment_list || []
    } catch (error) {
      console.error('加载健身房详情失败:', error)
    }
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
    background: $fitness-primary;
  }
  
  .gym-header {
    background: $fitness-primary;
    padding: 40rpx;
    
    .gym-name {
      display: block;
      font-size: $font-xl;
      font-weight: bold;
      color: #FFFFFF;
      margin-bottom: 10rpx;
    }
    
    .gym-count {
      display: block;
      font-size: $font-sm;
      color: rgba(255, 255, 255, 0.8);
    }
  }
  
  .action-bar {
    display: flex;
    justify-content: space-around;
    padding: 30rpx 40rpx;
    background: #FFFFFF;
    border-bottom: 1rpx solid $fitness-border;
    
    .action-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .action-icon {
        font-size: 40rpx;
        margin-bottom: 10rpx;
      }
      
      .action-text {
        font-size: $font-xs;
        color: $fitness-text;
      }
    }
  }
  
  .equipment-list {
    padding: 30rpx 40rpx;
    
    .equipment-card {
      background: #FFFFFF;
      border-radius: $radius-md;
      padding: 30rpx;
      margin-bottom: 30rpx;
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .equipment-info {
        flex: 1;
        
        .equipment-name {
          display: block;
          font-size: $font-lg;
          font-weight: bold;
          color: $fitness-text;
          margin-bottom: 10rpx;
        }
        
        .equipment-category {
          display: block;
          font-size: $font-sm;
          color: $uni-primary;
          margin-bottom: 10rpx;
        }
        
        .equipment-muscles {
          display: block;
          font-size: $font-xs;
          color: $fitness-text-gray;
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
        
        .delete-icon {
          font-size: 28rpx;
        }
      }
    }
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100rpx 40rpx;
    
    .empty-image {
      width: 300rpx;
      height: 300rpx;
      margin-bottom: 40rpx;
    }
    
    .empty-text {
      font-size: $font-lg;
      color: $fitness-text-light;
      margin-bottom: 10rpx;
    }
    
    .empty-subtext {
      font-size: $font-sm;
      color: $fitness-text-gray;
    }
  }
  </style>