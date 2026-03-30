<template>
    <view class="container">
      <!-- 添加设备图片 -->
      <view class="equipment-image-container">
        <image :src="'/static/' + equipmentInfo.image_url" 
              class="equipment-image" 
              mode="aspectFit" />
      </view>
      
      <view class="info-card">
        <text class="equipment-name">{{ equipmentInfo.name }}</text>
        <text class="equipment-category">{{ equipmentInfo.category }}</text>
      </view>
      <view class="desc">
        <text class="desc-label">设备简介</text>
        <text class="desc-detail">{{ equipmentInfo.description }}</text>
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
      
      <!-- 支持的动作列表 -->
      <view class="section" v-if="equipmentInfo.supported_actions && equipmentInfo.supported_actions.length > 0">
        <view class="actions-header">
          <text class="section-title">相关动作列表 ({{ equipmentInfo.supported_actions_count }})</text>
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
            v-for="(action, index) in equipmentInfo.supported_actions" 
            :key="action.action_id"
            :class="{ 'border-none': index === equipmentInfo.supported_actions.length - 1 }"
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
    image_url: '', // 添加图片URL字段
    target_muscles: [],
    supported_actions_count: 0,
    supported_actions: []
  })
  
  // 控制动作列表展开/收起的状态
  const isActionsExpanded = ref(false)

  onLoad((options) => {
    equipmentId.value = options.equipment_id || ''
  })
  
  onShow(async () => {
    if (equipmentId.value) {
      await loadEquipmentDetail()
    }
  })
  
  /**
   * 切换动作列表的展开/收起状态
   */
  const toggleActionsExpand = () => {
    isActionsExpanded.value = !isActionsExpanded.value
  }
  
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
   * 根据动作类别返回相应的中文文本
   */
  const getActionCategoryText = (category) => {
    switch(category.toLowerCase()) {
      case 'warmup':
        return '热身'
      case 'main_cardio':
        return '有氧动作'
      case 'main_strength':  // 修复拼写错误 'mian_strength' -> 'main_strength'
        return '力量训练动作'
      case 'cooldown':
        return '拉伸'
      default:
        return category
    }
  }
  
  /**
   * 根据动作类别返回相应的CSS类
   */
  const getActionCategoryClass = (category) => {
    switch(category.toLowerCase()) {
      case 'warmup':
        return 'badge-warmup'
      case 'main_cardio':
        return 'badge-cardio'
      case 'main_strength':  // 修复拼写错误 'mian_strength' -> 'main_strength'
        return 'badge-strength'
      case 'cooldown':
        return 'badge-cooldown'
      default:
        return 'badge-default'
    }
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
  </style>