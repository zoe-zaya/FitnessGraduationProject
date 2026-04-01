<template>
    <view class="container">
      
      <!-- 器材信息卡片 -->
      <view class="equipment-card">
        <view class="equipment-image-wrapper">
          <image 
            :src="'/static/'+equipmentImageUrl" 
            class="equipment-image"
            mode="aspectFill"
            @error="onImageError"
          />
        </view>
        
        <view class="equipment-info">
          <text class="equipment-name">{{ equipmentName }}</text>
          <text class="equipment-category">{{ equipmentCategory }}</text>
          <text class="equipment-muscles" v-if="targetMuscles && targetMuscles.length > 0">
            目标肌群：{{ targetMuscles.slice(0, 3).join('、') }}{{ targetMuscles.length > 3 ? '...' : '' }}
          </text>
        </view>
      </view>
      
      <!-- 健身房选择区域 -->
      <view class="gym-selection-section">
        <text class="section-title">选择健身房 *</text>
        
        <!-- 健身房列表 -->
        <view class="gym-list" v-if="gymList.length > 0">
          <view 
            class="gym-item" 
            v-for="(gym, index) in gymList" 
            :key="gym.inventory_id"
            :class="{ 'selected': selectedGymId === gym.inventory_id }"
            @click="selectGym(gym.inventory_id)"
          >
            <view class="gym-info">
              <text class="gym-name">{{ gym.location_tag }}</text>
              <text class="gym-desc">{{ gym.description || '暂无描述' }}</text>
              <text class="gym-meta">{{ gym.equipment_count }} 个器材</text>
            </view>
            <view class="radio-icon" v-if="selectedGymId === gym.inventory_id">
              <text class="radio-checked">✓</text>
            </view>
            <view class="radio-icon empty" v-else></view>
          </view>
        </view>
        
        <!-- 空状态提示 -->
        <view class="empty-gym-tip" v-else>
          <text class="empty-text">暂无健身房</text>
          <text class="empty-subtext">请先创建健身房后再添加器材</text>
          <button class="create-gym-btn" @click="navigateToCreateGym">创建健身房</button>
        </view>
      </view>
      
      <!-- 确认添加按钮 -->
      <view class="action-section">
        <button 
          class="confirm-btn" 
          @click="confirmAdd" 
          :disabled="!selectedGymId || !equipmentId"
          :loading="adding"
        >
          确认添加
        </button>
        <button class="cancel-btn" @click="handleCancel">取消</button>
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
  
  // 页面参数
  const equipmentId = ref('')
  const equipmentName = ref('')
  const equipmentCategory = ref('')
  const equipmentImageUrl = ref('')
  const targetMuscles = ref([])
  
  // 健身房相关
  const gymList = ref([])
  const selectedGymId = ref('')
  const loading = ref(false)
  const adding = ref(false)
  
  /**
   * 页面加载时接收参数
   */
  onLoad((options) => {
    equipmentId.value = options.equipment_id || ''    
    console.log('添加器材页面参数:', {
      equipmentId: equipmentId.value
    })
  })
  
  /**
   * 页面显示时加载数据
   */
  onShow(async () => {
    if (userStore.isLogin) {
      // 如果器材信息不完整，加载详情
      if (equipmentId.value && !equipmentName.value) {
        await loadEquipmentDetail()
      }
      // 加载用户健身房列表
      await loadGymList()
    }
  })
  
  /**
   * 加载器材详情（如果参数不完整）
   */
  const loadEquipmentDetail = async () => {
    try {
      const res = await request.get(`${API.EQUIPMENT_DETAIL}/${equipmentId.value}`)
      equipmentName.value = res.name
      equipmentCategory.value = res.category
      equipmentImageUrl.value = res.image_url
      targetMuscles.value = res.target_muscles || []
    } catch (error) {
      console.error('加载器材详情失败:', error)
    }
  }
  
  /**
   * 加载用户健身房列表
   */
  const loadGymList = async () => {
    loading.value = true
    try {
      const res = await request.get(API.GYM_LIST)
      gymList.value = res
      
      // 如果有且仅有一个健身房，自动选中
      if (res.length === 1) {
        selectedGymId.value = res[0].inventory_id
      }
    } catch (error) {
      console.error('加载健身房列表失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 图片加载错误处理
   */
  const onImageError = (e) => {
    console.log('图片加载失败:', e)
    equipmentImageUrl.value = ''
  }
  
  /**
   * 选择健身房
   */
  const selectGym = (inventoryId) => {
    selectedGymId.value = inventoryId
  }
  
  /**
   * 跳转至创建健身房页面
   */
  const navigateToCreateGym = () => {
    uni.navigateTo({ url: '/pages/gym/add-gym' })
  }
  
  /**
   * 确认添加器材
   * 对应《需求规格说明书》3.2 节添加器材——自动添加用例步骤 4-5
   */
  const confirmAdd = async () => {
    // 1. 验证参数
    if (!equipmentId.value) {
      uni.showToast({ title: '器材信息错误', icon: 'none', duration: 2000 })
      return
    }
    
    if (!selectedGymId.value) {
      uni.showToast({ title: '请选择健身房', icon: 'none', duration: 2000 })
      return
    }
    
    adding.value = true
    
    try {
      // 2. 调用添加器材 API（手动添加模式）
      await request.post(`${API.EQUIPMENT_ADD_MANUAL}/${selectedGymId.value}/manual`, {
        inventory_id: selectedGymId.value,
        equipment_id: equipmentId.value
      })
      
      // 3. 添加成功提示
      uni.showToast({ 
        title: `"${equipmentName.value}"已添加`, 
        icon: 'success', 
        duration: 1500 
      })
      
      // 4. 跳转至健身房列表页面
      setTimeout(() => {
        uni.navigateTo({ url: '/pages/gym/gym-list' })
      }, 1000)
      
    } catch (error) {
      console.error('添加失败:', error)
      
      // 处理重复添加的情况
      if (error.response && error.response.status === 400) {
        uni.showToast({ 
          title: '该器材已在健身房中', 
          icon: 'none', 
          duration: 2000 
        })
      } else {
        uni.showToast({ 
          title: '添加失败，请重试', 
          icon: 'none', 
          duration: 2000 
        })
      }
    } finally {
      adding.value = false
    }
  }
  
  /**
   * 取消添加
   */
  const handleCancel = () => {
    uni.showModal({
      title: '提示',
      content: '确定要取消添加吗？',
      success: (res) => {
        if (res.confirm) {
          uni.navigateBack()
        }
      }
    })
  }
  </script>
  
  <style lang="scss" scoped>
  .container {
    min-height: 100vh;
    background: url('@/static/background3.png') no-repeat center center / cover;
    padding: $size-5 $size-3;
  }
  
  .equipment-card {
    background: #FFFFFF;
    margin: 24rpx 40rpx;
    border-radius: $size-4;
    padding: $size-5;
    display: flex;
    align-items: center;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
    
    .equipment-image-wrapper {
      width: 160rpx;
      height: 160rpx;
      margin-right: 20rpx;
      flex-shrink: 0;
      
      .equipment-image {
        width: 100%;
        height: 100%;
        border-radius: 8rpx;
        background: #F5F5F5;
      }
      
      .image-placeholder {
        width: 100%;
        height: 100%;
        background: #F5F5F5;
        border-radius: 8rpx;
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
        font-size: 32rpx;
        font-weight: bold;
        color: $color-input;
        margin-bottom: 10rpx;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .equipment-category {
        display: block;
        font-size: 26rpx;
        color: $color-primary;
        margin-bottom: 10rpx;
      }
      
      .equipment-muscles {
        display: block;
        font-size: 24rpx;
        color: #999999;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
  
  .gym-selection-section {
    padding: 0 40rpx;
    
    .section-title {
      display: block;
      font-size: 28rpx;
      font-weight: bold;
      color: $color-primary;
      margin-bottom: 20rpx;
    }
    
    .gym-list {
      .gym-item {
        background: #FFFFFF;
        border-radius: $size-4;
        padding: 30rpx;
        margin-bottom: 20rpx;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 2rpx solid transparent;
        
        &.selected {
          border-color: #df6860;
          background: rgb(250, 242, 242);
        }
        
        .gym-info {
          flex: 1;
          padding-right: 20rpx;
          
          .gym-name {
            display: block;
            font-size: 32rpx;
            font-weight: bold;
            color: $color-input;
            margin-bottom: 10rpx;
          }
          
          .gym-desc {
            display: block;
            font-size: 26rpx;
            color: #666666;
            margin-bottom: 8rpx;
          }
          
          .gym-meta {
            display: block;
            font-size: 24rpx;
            color: #999999;
          }
        }
        
        .radio-icon {
          width: 40rpx;
          height: 40rpx;
          border-radius: 20rpx;
          border: 2rpx solid #E5E5E5;
          display: flex;
          justify-content: center;
          align-items: center;
          flex-shrink: 0;
          
          &.empty {
            background: transparent;
          }
          
          .radio-checked {
            font-size: 24rpx;
            color: $color-primary;
            font-weight: 900;
          }
        }
      }
    }
    
    .empty-gym-tip {
      background: #FFFFFF;
      border-radius: 12rpx;
      padding: 60rpx 40rpx;
      text-align: center;
      
      .empty-text {
        display: block;
        font-size: 32rpx;
        color: #666666;
        margin-bottom: 10rpx;
      }
      
      .empty-subtext {
        display: block;
        font-size: 26rpx;
        color: #999999;
        margin-bottom: 30rpx;
      }
      
      .create-gym-btn {
        width: 280rpx;
        height: 80rpx;
        background: $color-primary;
        color: #FFFFFF;
        font-size: 28rpx;
        border-radius: 40rpx;
        border: none;
      }
    }
  }
  
  .action-section {
    padding: 0 40rpx 30rpx;
    margin-top: 40rpx;
    
    .confirm-btn, .cancel-btn {
      width: 100%;
      height: 90rpx;
      border-radius: 45rpx;
      font-size: 32rpx;
      border: none;
      margin-bottom: 20rpx;
    }
    
    .confirm-btn {
      background: $button-bg;
      color: #FFFFFF;
      
      &[disabled] {
        background: #CCCCCC;
      }
    }
    
    .cancel-btn {
      background: #FFFFFF;
      color: #666666;
      border: 1rpx solid #E5E5E5;

      &::after{
        border: none;
      }
    }
  }
  </style>