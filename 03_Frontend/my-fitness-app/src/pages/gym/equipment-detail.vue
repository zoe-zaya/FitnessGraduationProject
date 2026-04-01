<template>
  <view class="container">
    <!-- ✅ 修改点 1: Tab 标签切换到页面最顶部 -->
    <view class="tab-bar">
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'detail' }"
        @click="switchTab('detail')"
      >
        <text class="tab-text">器材详情</text>
        <view class="tab-indicator" v-if="activeTab === 'detail'"></view>
      </view>
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'actions' }"
        @click="switchTab('actions')"
      >
        <text class="tab-text">相关动作</text>
        <view class="tab-indicator" v-if="activeTab === 'actions'"></view>
      </view>
    </view>
    
    <!-- ✅ 修改点 2: 器材详情 Tab 内容（仅显示图片、名称、类别、简介、目标肌群） -->
    <view v-show="activeTab === 'detail'">
      <!-- 器材图片 -->
      <view class="equipment-image-container">
        <image :src="'/static/' + equipmentInfo.image_url" 
              class="equipment-image" 
              mode="aspectFit" />
      </view>
      
      <!-- 器材名称和类别 -->
      <view class="info-card">
        <text class="equipment-name">{{ equipmentInfo.name }}</text>
        <text class="equipment-category">{{ equipmentInfo.category }}</text>
      </view>
      
      <!-- 设备简介 -->
      <view class="desc">
        <text class="desc-label">设备简介</text>
        <text class="desc-detail">{{ equipmentInfo.description }}</text>
      </view>
      
      <!-- 目标肌群 -->
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
    </view>
    
    <!-- ✅ 修改点 3: 相关动作 Tab 内容（显示推荐动作列表） -->
    <view v-show="activeTab === 'actions'" class="actions-tab-content">
      <!-- 加载状态 -->
      <view class="loading-state" v-if="recommendLoading">
        <text class="loading-text">智能推荐中...</text>
      </view>
      
      <!-- 推荐列表 -->
      <view class="recommend-list" v-else-if="recommendedActions.length > 0">
        <view 
          class="recommend-card" 
          v-for="(action, index) in recommendedActions" 
          :key="action.action_id"
        >
          <!-- 动作头部：名称 + 难度 + 类别 -->
          <view class="card-header">
            <text class="action-name">{{ action.name }}</text>
            <view class="badges">
              <text class="action-badge" :class="getDifficultyClass(action.difficulty_level)">
                {{ action.difficulty_level }}
              </text>
              <text class="category-badge" :class="getActionCategoryClass(action.action_category)">
                {{ getActionCategoryText(action.action_category) }}
              </text>
            </view>
          </view>
          
          <!-- 目标肌群 -->
          <view class="card-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
            <text class="muscles-label">目标肌群：</text>
            <view class="muscles-wrapper">
              <text 
                class="muscle-tag-small" 
                v-for="(muscle, mIndex) in action.target_muscles.slice(0, 3)" 
                :key="mIndex"
              >
                {{ muscle }}
              </text>
              <text class="muscle-tag-small more" v-if="action.target_muscles.length > 3">
                +{{ action.target_muscles.length - 3 }}
              </text>
            </view>
          </view>
          
          <!-- 安全提示（截断显示） -->
          <view class="card-safety" v-if="action.safety_tips">
            <text class="safety-label">💡 提示：</text>
            <text class="safety-text">{{ action.safety_tips.slice(0, 30) }}{{ action.safety_tips.length > 30 ? '...' : '' }}</text>
          </view>
          
          <!-- 操作按钮 -->
          <view class="card-actions">
            <button class="action-btn detail-btn" @click="viewActionDetail(action)">
              <text class="btn-icon">👁️</text>
              <text class="btn-text">查看详情</text>
            </button>
            <button class="action-btn plan-btn" @click="addToPlan(action)">
              <text class="btn-icon">📋</text>
              <text class="btn-text">加入计划</text>
            </button>
            <button class="action-btn fav-btn" @click="toggleFavorite(action)">
              <text class="btn-icon">{{ action.isFavorited ? '❤️' : '🤍' }}</text>
            </button>
          </view>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-recommend" v-else>
        <image src="/static/empty-actions.png" class="empty-image" mode="aspectFit" />
        <text class="empty-text">暂无推荐动作</text>
        <text class="empty-subtext">该器材暂不支持相关训练动作</text>
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
  image_url: '',
  target_muscles: [],
  supported_actions_count: 0,
  supported_actions: []
})

// ✅ Tab 切换相关状态
const activeTab = ref('detail') // 'detail' | 'actions'
const recommendedActions = ref([]) // 推荐动作列表
const recommendLoading = ref(false) // 推荐加载状态

onLoad((options) => {
  equipmentId.value = options.equipment_id || ''
})

onShow(async () => {
  if (equipmentId.value) {
    await loadEquipmentDetail()
    // 如果默认在相关动作 tab，加载推荐动作
    if (activeTab.value === 'actions') {
      await loadRecommendedActions()
    }
  }
})

/**
 * 切换 Tab
 */
const switchTab = async (tab) => {
  if (activeTab.value === tab) return
  
  activeTab.value = tab
  
  // 如果切换到相关动作 tab 且未加载过，加载推荐动作
  if (tab === 'actions' && recommendedActions.value.length === 0) {
    await loadRecommendedActions()
  }
}

/**
 * 加载推荐动作列表
 * 调用动作推荐接口，不限制返回数量
 */
const loadRecommendedActions = async () => {
  recommendLoading.value = true
  
  try {
    const res = await request.post(API.ACTION_RECOMMEND, {
      equipment_id: equipmentId.value,
      top_k: null, // 不限制数量，返回所有匹配动作
      include_score: false // 不返回匹配评分
    })
    
    // 添加收藏状态标记（默认未收藏）
    recommendedActions.value = res.map(action => ({
      ...action,
      isFavorited: false // 实际项目中应从用户收藏接口获取
    }))
    
  } catch (error) {
    console.error('加载推荐动作失败:', error)
    recommendedActions.value = []
  } finally {
    recommendLoading.value = false
  }
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
 * 根据难度级别返回相应的 CSS 类
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
  switch(category?.toLowerCase()) {
    case 'warmup':
      return '热身'
    case 'main_cardio':
      return '有氧'
    case 'main_strength':
      return '力量'
    case 'cooldown':
      return '拉伸'
    default:
      return category
  }
}

/**
 * 根据动作类别返回相应的 CSS 类
 */
const getActionCategoryClass = (category) => {
  switch(category?.toLowerCase()) {
    case 'warmup':
      return 'badge-warmup'
    case 'main_cardio':
      return 'badge-cardio'
    case 'main_strength':
      return 'badge-strength'
    case 'cooldown':
      return 'badge-cooldown'
    default:
      return 'badge-default'
  }
}

/**
 * 查看动作详情
 */
const viewActionDetail = (action) => {
  uni.navigateTo({
    url: `/pages/action/action-detail?action_id=${action.action_id}`
  })
}

/**
 * 加入训练计划
 */
const addToPlan = (action) => {
  uni.showModal({
    title: '加入训练计划',
    content: `确定要将"${action.name}"添加到训练计划吗？`,
    success: (res) => {
      if (res.confirm) {
        uni.navigateTo({
          url: `/pages/plan/select-plan?action_id=${action.action_id}`
        })
      }
    }
  })
}

/**
 * 收藏/取消收藏动作
 */
const toggleFavorite = (action) => {
  action.isFavorited = !action.isFavorited
  
  const message = action.isFavorited ? '已加入收藏' : '已取消收藏'
  uni.showToast({
    title: message,
    icon: 'none',
    duration: 1500
  })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: url('@/static/background3.png') no-repeat center center / cover;
  padding-bottom: $size-9;
}

/* ✅ 修改点 1: Tab 标签样式（置顶） */
.tab-bar {
  display: flex;
  background: #FFFFFF;
  padding: 0 $size-9;
  border-bottom: 1rpx solid $fitness-border;
  position: sticky;
  top: 0;
  z-index: 100;
  
  .tab-item {
    flex: 1;
    padding: $size-4 0;
    text-align: center;
    position: relative;
    
    .tab-text {
      font-size: $size-4;
      color: $color-label;
      font-weight: 500;
    }
    
    &.active {
      .tab-text {
        color: $color-primary;
        font-weight: 700;
      }
    }
    
    .tab-indicator {
      position: absolute;
      bottom: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 40rpx;
      height: 4rpx;
      background: $color-primary;
      border-radius: 2rpx;
    }
  }
}

/* ✅ 修改点 2: 器材详情内容样式 */
.equipment-image-container {
  width: 100%;
  height: 380rpx;
  background: #FFFFFF;
  padding: $size-2 0;
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
}

/* ✅ 修改点 3: 相关动作内容样式 */
.actions-tab-content {
  padding: $size-6 $size-9 $size-9;
  
  .loading-state {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: $size-10 0;
    
    .loading-text {
      font-size: $size-4;
      color: $color-label;
    }
  }
  
  .recommend-list {
    .recommend-card {
      background: #ffffffc5;
      margin-top: $size-4;
      padding: $size-6;
      border-radius: 24rpx;
      box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.12);
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: $size-4;
        
        .action-name {
          font-size: $size-5;
          font-weight: 600;
          color: $color-input;
          flex: 1;
          margin-right: $size-3;
        }
        
        .badges {
          display: flex;
          gap: $size-2;
          flex-shrink: 0;
          
          .action-badge, .category-badge {
            font-size: $size-3;
            padding: 4rpx $size-2;
            border-radius: $size-3;
            font-weight: 500;
          }
          
          .action-badge {
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
          
          .category-badge {
            &.badge-warmup {
              background: #E3F2FD;
              color: #1976D2;
            }
            &.badge-cardio {
              background: #E8F5E9;
              color: #388E3C;
            }
            &.badge-strength {
              background: #FFF3E0;
              color: #F57C00;
            }
            &.badge-cooldown {
              background: #F3E5F5;
              color: #7B1FA2;
            }
            &.badge-default {
              background: #F5F5F5;
              color: #616161;
            }
          }
        }
      }
      
      .card-muscles {
        margin-bottom: $size-3;
        
        .muscles-label {
          font-size: $size-3;
          color: $color-label;
          margin-right: $size-1;
        }
        
        .muscles-wrapper {
          display: inline-flex;
          flex-wrap: wrap;
          gap: 12rpx;
          
          .muscle-tag-small {
            background: #F5F5F5;
            color: $color-input;
            font-size: 24rpx;
            padding: 6rpx 16rpx;
            border-radius: 12rpx;
            
            &.more {
              background: #E0E0E0;
              color: $color-label;
            }
          }
        }
      }
      
      .card-safety {
        margin-bottom: $size-4;
        padding: $size-3;
        background: rgba(0, 122, 255, 0.05);
        border-radius: $size-3;
        border-left: 4rpx solid $color-primary;
        
        .safety-label {
          font-size: $size-3;
          color: $color-primary;
          font-weight: 500;
          margin-right: $size-1;
        }
        
        .safety-text {
          font-size: $size-3;
          color: $color-label;
          line-height: 1.4;
        }
      }
      
      .card-actions {
        display: flex;
        gap: $size-3;
        
        .action-btn {
          flex: 1;
          height: 72rpx;
          border-radius: 36rpx;
          border: none;
          font-size: $size-3;
          font-weight: 500;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: $size-1;
          
          .btn-icon {
            font-size: $size-4;
          }
          
          .btn-text {
            line-height: 1;
          }
          
          &.detail-btn {
            background: #F5F5F5;
            color: $color-input;
          }
          
          &.plan-btn {
            background: $color-primary;
            color: #FFFFFF;
          }
          
          &.fav-btn {
            width: 72rpx;
            padding: 0;
            background: #FFF3E0;
            color: #FF9800;
          }
        }
      }
    }
  }
  
  .empty-recommend {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: $size-10 0;
    
    .empty-image {
      width: 240rpx;
      height: 240rpx;
      margin-bottom: $size-6;
    }
    
    .empty-text {
      font-size: $size-5;
      color: $color-input;
      font-weight: 500;
      margin-bottom: $size-2;
    }
    
    .empty-subtext {
      font-size: $size-4;
      color: $color-label;
    }
  }
}
</style>