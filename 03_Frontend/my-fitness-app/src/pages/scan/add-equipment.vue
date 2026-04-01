
<template>
    <view class="container">
      <!-- 器材卡片 -->
      <view class="equipment-card">
        <view class="card-content">
          <image :src="'/static/' + equipmentImageUrl" 
                class="equipment-image" 
                mode="aspectFit" />
          <view class="equipment-info">
            <text class="equipment-name">{{ equipmentName }}</text>
            <text class="equipment-category">{{ equipmentCategory  }}</text>
          </view>
        </view>
      </view>
      
      <!-- 选择健身房 -->
      <view class="section gym-selection">
        <text class="section-title">选择健身房</text>
        <picker @change="onGymChange" :value="selectedGymIndex" :range="userGyms" range-key="location_tag">
          <view class="picker">
            <text v-if="selectedGymIndex !== null && userGyms[selectedGymIndex]">
              {{ userGyms[selectedGymIndex].location_tag }}
            </text>
            <text v-else class="picker-placeholder">请选择要添加到的健身房</text>
          </view>
        </picker>
      </view>
      
      <button class="confirm-btn" @click="confirmAdd" :loading="loading" :disabled="loading || selectedGymIndex === null">
          {{ loading ? '添加中...' : '确认添加到我的器材' }}
      </button>
        
      <button class="cancel-btn" @click="navigateToGymList" :disabled="loading">
          取消
      </button>
    </view>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { onLoad } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const equipmentId = ref('') // 设备ID
  const equipmentName = ref('') // 设备名称
  const equipmentCategory = ref('') // 设备类别
  const equipmentDescription = ref('') // 设备描述
  const equipmentImageUrl = ref('')
  const actionsCount = ref(0) // 相关动作数量
  const relatedActions = ref([]) // 相关动作列表
  const targetMuscles = ref([]) // 目标肌群
  const loading = ref(false)
  // 控制动作列表展开/收起的状态
  const isActionsExpanded = ref(false)
  
  // 健身房相关
  const userGyms = ref([])
  const selectedGymIndex = ref(null)
  
  onLoad((options) => {
    equipmentId.value = options.equipment_id || ''
    
    console.log('设备详情参数:', {
      equipmentId: equipmentId.value
    })
    
    // 获取用户健身房列表
    loadUserGyms()
    
    // 获取设备详情，包括图片
    loadEquipmentDetail()
  })
  
  /**
   * 加载用户健身房列表
   */
  const loadUserGyms = async () => {
    try {
      const res = await request.get(API.GYM_LIST)
      userGyms.value = res
      console.log('用户健身房列表:', res)
    } catch (error) {
      console.error('获取健身房列表失败:', error)
      uni.showToast({
        title: '获取健身房列表失败',
        icon: 'none'
      })
    }
  }
  
  /**
   * 选择健身房
   */
  const onGymChange = (event) => {
    selectedGymIndex.value = event.detail.value
  }
  
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
     * 切换动作列表的展开/收起状态
     */
     const toggleActionsExpand = () => {
      isActionsExpanded.value = !isActionsExpanded.value
    }
  
    
    /**
     * 根据难度级别返回相应的CSS类
     */
     const getDifficultyClass = (difficulty) => {
      switch(difficulty) {
        case '初级':
          return 'difficulty-beginner'
        case '中级':
          return 'difficulty-intermediate'
        case '高级':
          return 'difficulty-advanced'
        default:
          return ''
      }
    }
  /**
   * 确认添加
   */
  const confirmAdd = async () => {
    if (!equipmentId.value) {
      uni.showToast({ title: '参数错误', icon: 'none' })
      return
    }
    
    if (selectedGymIndex.value === null || !userGyms.value[selectedGymIndex.value]) {
      uni.showToast({ title: '请选择健身房', icon: 'none' })
      return
    }
    
    const selectedGymId = userGyms.value[selectedGymIndex.value].inventory_id
    
    loading.value = true
    try {
      await request.post(`${API.EQUIPMENT_ADD_MANUAL}/${selectedGymId}/manual`, {
        inventory_id: selectedGymId,
        equipment_id: equipmentId.value
      })
      uni.showToast({ title: '添加成功', icon: 'success' })
      await navigateToGymList();
    } catch (error) {
      console.error('添加失败:', error)
      uni.showToast({ title: error.message || '添加失败', icon: 'error' })
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 跳转至健身房列表页面
   */
  const navigateToGymList = () => {
    uni.reLaunch({ url: '/pages/gym/gym-list' })
  }
  </script>
  
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: url('@/static/background3.png') no-repeat center center / cover;
    padding-bottom: $size-9;
  }
  
  .equipment-card {
    background: #FFFFFF;
    padding: $size-5;
    margin: $size-5 $size-5 0 $size-5;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.12);
    border-radius: $size-5;
  }

  .card-content {
    display: flex;
    align-items: center;

    .equipment-image {
      width: 200rpx;
      height: 200rpx;
      margin-right: $size-5;
      border-radius: $size-3;
    }

    .equipment-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;

      .equipment-name {
        font-size: $size-8;
        font-weight: 700;
        color: $color-input;
        margin-bottom: $size-2;
      }

      .equipment-category {
        font-size: $size-3;
        color: $color-primary;
        padding: $size-1 $size-2;
        background: $color-primary-light;
        border-radius: 20rpx;
        font-weight: 500;
        display: inline-block;
        border: 1rpx solid $color-primary;
        width: fit-content;
      }
    }
  }
  
  .section {
    padding-left: $size-9;
    padding-right: $size-9;
    margin-top: $size-6;
  
    .section-title {
      display: block;
      font-size: $size-4;
      line-height: 1;
      font-weight: 700;
      color: rgb(160 62 64 / 0.6);
      letter-spacing: 1rpx;
      margin-bottom: $size-2;
      text-transform: uppercase;
    }
    
    .actions-header {
      display: flex;
      justify-content: space-between;
      
      .expand-toggle {
        font-size: $size-3;
        color: $color-primary;
        font-weight: 500;
        cursor: pointer;
        line-height: 1;
        
        &.expanded::before {
          content: '▲';
          margin-right: $size-1;
        }
        
        &:not(.expanded)::before {
          content: '▼';
          margin-right: $size-1;
        }
      }
    }
    
    .gym-selection {
      .picker {
        padding: $size-3;
        border: 1rpx solid #e0e0e0;
        border-radius: $size-3;
        background: white;
        min-height: $size-9;
        display: flex;
        align-items: center;
        
        .picker-placeholder {
          color: #999;
          font-size: $size-4;
        }
      }
    }

    .muscles-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 24rpx;
      
      .muscle-tag {
        background-color: rgb(228, 226, 225);
        color: $color-input;
        font-size: 28rpx;
        font-weight: 600;
        line-height: 1.25rem;
        padding: $size-2 $size-3;
        border-radius: $size-4;
        margin-bottom: $size-3;
      }
    }
  
    .actions-count {
      font-size: $size-4;
      color: $color-label;
      margin-bottom: 20rpx;
    }
      
    .empty-actions {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: $size-5 0;
      
      .empty-text {
        font-size: $size-4;
        color: $color-label;
      }
    }
      
    .actions-list {
      transition: max-height 0.3s ease;
      
      .action-item {
        background: #ffffffc5 url('/static/foot-icon.png') no-repeat;
        background-size: $size-6 $size-6;     //背景图片的宽度
        background-position: right $size-5 bottom $size-5; /* 右下角 */
        margin-top: $size-4;
        padding: $size-6;
        border-width: 1px;
        border-radius: 24px;
        box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.12);

        &.border-none {
          border-bottom: none;
        }
        .action-header {
          display: flex;
          justify-content: flex-start;
          align-items: center;
          margin-bottom: 24rpx;
          flex-direction: row;
          
          .action-name {
            font-size: $size-5;
            font-weight: 600;
            color: $color-input;
            margin-right: $size-3;
            line-height: 1;
            flex:1;
          }
          
          .action-badge {
            font-size: $size-3;
            padding: 4rpx $size-2;
            border-radius: $size-3;
            
            &.difficulty-beginner {
              background: #E8F5E9;
              color: #4CAF50;
            }
            
            &.difficulty-intermediate {
              background: #FFF3E0;
              color: #FF9800;
            }
            
            &.difficulty-advanced {
              background: #FFEBEE;
              color: #F44336;
            }
          }
        }
        
        .action-target-muscles {
          display: flex;
          flex-wrap: wrap;
          
          .muscles-label {
            font-size: $size-3;
            color: $color-label;
            margin-right: $size-1;
          }
          
          .muscles-value {
            font-size: $size-3;
            color: $fitness-text;
            flex: 1;
          }
        }
        
      }
    }
  }
  .confirm-btn {
      height: $size-12;
      margin: $size-4 $size-7;
      background: $uni-primary;
      color: #FFFFFF;
      font-size: $size-4;
      font-weight: 600;
      border-radius: 64rpx;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;
    }
    
    .cancel-btn {
      height: $size-12;
      margin: 0 $size-7;
      margin-top: $size-4;
      background:#efefef;
      color: $color-input;
      font-size: $size-4;
      font-weight: 600;
      border-radius: 64rpx;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;

      &::after{
        border: none;
      }
    }
  </style>