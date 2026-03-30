
<template>
  <view class="container">
    <!-- 添加设备图片 -->
    <view class="equipment-image-container">
      <image :src="'/static/' + equipmentImageUrl" 
            class="equipment-image" 
            mode="aspectFit" />
    </view>
    
    <view class="info-card">
      <text class="equipment-name">{{ equipmentName }}</text>
      <text class="equipment-category">{{ equipmentCategory  }}</text>
    </view>
    <view class="desc">
      <text class="desc-label">设备简介</text>
      <text class="desc-detail">{{ equipmentDescription }}</text>
    </view>
    <view class="section">
      <text class="section-title">目标肌群</text>
      <view class="muscles-tags">
        <!--{{ targetMuscles.join(', ') }}-->
        <text 
          class="muscle-tag" 
          v-for="(muscle, index) in targetMuscles" 
          :key="index"
        >
          {{ muscle }}
        </text>
      </view>
    </view>
    
    <!-- 支持的动作列表 -->
    <view class="section" v-if="relatedActions && relatedActions.length > 0">
      <view class="actions-header">
        <text class="section-title">相关动作列表 ({{ actionsCount }})</text>
        <text 
          class="expand-toggle" 
          @click="toggleActionsExpand"
          :class="{ 'expanded': isActionsExpanded }"
        >
          {{ isActionsExpanded ? '收起全部' : '展开全部' }}
        </text>
      </view>
      
      <view 
        class="actions-list" 
        :style="{ maxHeight: isActionsExpanded ? 'none' : '0px', overflow: 'hidden' }"
      >
        <view 
          class="action-item" 
          v-for="(action, index) in relatedActions" 
          :key="action.action_id"
          :class="{ 'border-none': index === relatedActions.length - 1 }"
        >
          <view class="action-header">
            <text class="action-name">{{ action.name }}</text>
              <text class="action-badge" :class="getDifficultyClass(action.difficulty_level)">
              {{ action.difficulty_level }}
            </text>
          </view>
          
          <view class="action-target-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
            <text class="muscles-label">锻炼肌群：</text>
            <text class="muscles-value">{{ action.target_muscles.join('、') }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 如果没有动作，只显示计数 -->
    <view class="section" v-else>
      <text class="section-title">支持动作</text>
      <view class="empty-actions">
        <text class="empty-text">暂无相关动作</text>
      </view>
    </view>
    <button class="confirm-btn" @click="confirmAdd" :loading="loading" :disabled="loading">
        {{ loading ? '添加中...' : '确认添加到我的器材' }}
    </button>
      
    <button class="cancel-btn" @click="navigateToEquipmentList(inventoryId)" :disabled="loading">
        取消
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
  background: url('@/static/background3.png') no-repeat center center / cover;
  padding-bottom: $size-9;
}

.equipment-image-container {
  width: 100%;
  height: 380rpx;
  background: #FFFFFF;
  padding: $size-2 0;
  //border-radius: $size-5;
  //margin-bottom: 30rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.12);
  
  .equipment-image {
    width: 100%;
    height: 100%;
    border-radius: $size-5;
  }
}

.info-card {
  background: #FFFFFF;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  border-bottom-left-radius: $size-5;
  border-bottom-right-radius: $size-5;
  padding: $size-5;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.12);
  display: flex;
  align-items: center;
  justify-content: flex-start;
  line-height: 1.1;
  
  .equipment-name {
    display: block;
    font-size: $size-10;
    font-weight: 700;
    color: $color-input;
    margin-right: $size-4;
    margin-left: $size-2;
  }

  .equipment-category {
    display: block;
    font-size: $size-3;
    color: $color-primary;
    padding: $size-1 $size-2;
    background: $color-primary-light;
    border-radius: 20rpx;
    font-weight: 500;
    display: inline-block;
    border: 1rpx solid $color-primary;
    line-height: 1;
  }
}

.desc{
  padding-left: $size-9;
  padding-right: $size-9;
  margin-top: $size-12;
  .desc-label {
    display: block;
    font-size: $size-4;
    line-height: 1;
    font-weight: 700;
    color: rgb(160 62 64 / 0.6);
    letter-spacing: 1rpx;
    margin-bottom: $size-2;
    text-transform: uppercase;
  }
  .desc-detail {
    display: block;
    font-size: $size-4;
    color: $color-label;
    line-height: 1.625;
    text-align: justify;
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
    //align-items: center;
    //margin-bottom: $size-4;
    
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
      //box-shadow: 3rpx 3rpx 8rpx rgba(160, 62, 64, 0.12);
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