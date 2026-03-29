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
      
      <!-- 支持的动作列表 -->
      <view class="section" v-if="equipmentInfo.supported_actions && equipmentInfo.supported_actions.length > 0">
        <text class="section-title">支持动作 ({{ equipmentInfo.supported_actions_count }})</text>
        
        <view class="actions-list">
          <view 
            class="action-item" 
            v-for="(action, index) in equipmentInfo.supported_actions" 
            :key="action.action_id"
            :class="{ 'border-none': index === equipmentInfo.supported_actions.length - 1 }"
          >
            <view class="action-header">
              <text class="action-name">{{ action.name }}</text>
              <text class="action-badge" :class="getActionCategoryClass(action.action_category)">
                {{ getActionCategoryText(action.action_category) }}
              </text>
            </view>
            
            <view class="action-meta">
              <text class="action-difficulty" :class="getDifficultyClass(action.difficulty_level)">
                {{ action.difficulty_level }}
              </text>
              
              <text class="action-duration" v-if="action.estimated_seconds">
                {{ action.estimated_seconds }}秒
              </text>
            </view>
            
            <view class="action-target-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
              <text class="muscles-label">锻炼肌群：</text>
              <text class="muscles-value">{{ action.target_muscles.join('、') }}</text>
            </view>
            
            <view class="action-safety-tips" v-if="action.safety_tips">
              <text class="safety-label">⚠️ 安全提示：</text>
              <text class="safety-value">{{ action.safety_tips }}</text>
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
    background: $fitness-primary;
    padding: 30rpx;
  }

  .equipment-image-container {
    width: 100%;
    height: 350rpx;
    background: #FFFFFF;
    border-radius: $size-5;
    margin-bottom: 30rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
    
    .equipment-image {
      width: 100%;
      height: 100%;
      border-radius: $size-5;
    }
  }

  .info-card {
    background: #FFFFFF;
    border-radius: $size-5;
    padding: $size-5;
    margin-bottom: 30rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
    
    .equipment-name {
      display: block;
      font-size: $size-6;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 10rpx;
    }

    .equipment-category {
      display: block;
      font-size: $size-3;
      color: $uni-primary;
      margin-bottom: 20rpx;
      padding: $size-1 20rpx;
      background: #F5F7FF;
      border-radius: 20rpx;
      display: inline-block;
    }

    .equipment-desc {
      display: block;
      font-size: $size-4;
      color: $color-label;
      line-height: 1.6;
    }
  }

  .section {
    background: #FFFFFF;
    border-radius: $size-5;
    padding: 30rpx;
    margin-bottom: 30rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);

    .section-title {
      display: block;
      font-size: $size-5;
      font-weight: bold;
      color: $fitness-text;
      margin-bottom: 20rpx;
    }

    .muscles-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 12rpx;
      
      .muscle-tag {
        background: #E8F4FD;
        color: #1976D2;
        font-size: $size-3;
        padding: 10rpx 20rpx;
        border-radius: 20rpx;
        border: 1rpx solid #BBDEFB;
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
      .action-item {
        padding: 25rpx 0;
        border-bottom: 1rpx solid rgba(160, 62, 64, 0.1);
        
        &.border-none {
          border-bottom: none;
        }
        
        .action-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12rpx;
          
          .action-name {
            font-size: $size-4;
            font-weight: 600;
            color: $fitness-text;
            flex: 1;
            margin-right: 20rpx;
          }
          
          .action-badge {
            font-size: $size-2;
            padding: 6rpx $size-2;
            border-radius: $size-3;
            white-space: nowrap;
            
            &.badge-warmup {
              background: #E8F5E9;
              color: #4CAF50;
            }
            
            &.badge-cardio {
              background: #FFF3E0;
              color: #FF9800;
            }
            
            &.badge-strength {
              background: #E3F2FD;
              color: #2196F3;
            }
            
            &.badge-cooldown {
              background: #F3E5F5;
              color: #9C27B0;
            }
            
            &.badge-default {
              background: #E0E0E0;
              color: #666;
            }
          }
        }
        
        .action-meta {
          display: flex;
          gap: $size-2;
          margin-bottom: 12rpx;
          
          .action-difficulty {
            font-size: $size-2;
            padding: 6rpx $size-2;
            border-radius: 20rpx;
            
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
          
          .action-duration {
            font-size: $size-2;
            padding: 6rpx $size-2;
            border-radius: 20rpx;
            background: #F1F3F4;
            color: #5F6368;
          }
        }
        
        .action-target-muscles {
          display: flex;
          margin: 10rpx 0;
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
        
        .action-safety-tips {
          display: flex;
          margin-top: 10rpx;
          padding: 15rpx;
          background: #FFF9C4;
          border-radius: $size-3;
          
          .safety-label {
            font-size: $size-3;
            color: #FF8F00;
            font-weight: 500;
            margin-right: $size-1;
          }
          
          .safety-value {
            font-size: $size-3;
            color: #5F6368;
            flex: 1;
          }
        }
      }
    }
  }
  </style>