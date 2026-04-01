<template>
    <view class="container">
      <!-- ✅ 固定在顶部的筛选区域 -->
      <view class="filter-section">
        <!-- 第一行：分类筛选 -->
        <view class="filter-row">
          <text class="filter-label">动作类别：</text>
          <scroll-view 
            scroll-x 
            class="category-scroll"
            :scroll-into-view="scrollIntoView"
          >
            <view class="filter-buttons">
              <view 
                class="filter-btn" 
                :class="{ 'active': selectedCategory === '' }"
                @click="selectCategory('')"
              >
                <text class="btn-text">全部</text>
              </view>
              <view 
                class="filter-btn" 
                :class="{ 'active': selectedCategory === 'warmup' }"
                @click="selectCategory('warmup')"
              >
                <text class="btn-text">热身</text>
              </view>
              <view 
                class="filter-btn" 
                :class="{ 'active': selectedCategory === 'main_cardio' }"
                @click="selectCategory('main_cardio')"
              >
                <text class="btn-text">有氧</text>
              </view>
              <view 
                class="filter-btn" 
                :class="{ 'active': selectedCategory === 'main_strength' }"
                @click="selectCategory('main_strength')"
              >
                <text class="btn-text">力量</text>
              </view>
              <view 
                class="filter-btn" 
                :class="{ 'active': selectedCategory === 'cooldown' }"
                @click="selectCategory('cooldown')"
              >
                <text class="btn-text">拉伸</text>
              </view>
            </view>
          </scroll-view>
        </view>
        
        <!-- 第二行：肌群筛选 -->
        <view class="filter-row">
          <text class="filter-label">目标肌群：</text>
          <scroll-view 
            scroll-x 
            class="muscle-scroll"
          >
            <view class="filter-buttons">
              <view 
                class="filter-btn muscle-btn" 
                :class="{ 'active': selectedMuscle === '' }"
                @click="selectMuscle('')"
              >
                <text class="btn-text">全部</text>
              </view>
              <view 
                class="filter-btn muscle-btn" 
                v-for="(muscle, index) in muscleOptions" 
                :key="index"
                :class="{ 'active': selectedMuscle === muscle }"
                @click="selectMuscle(muscle)"
              >
                <text class="btn-text">{{ muscle }}</text>
              </view>
            </view>
          </scroll-view>
        </view>
        
        <!-- 筛选结果统计 -->
        <view class="filter-result">
          <text class="result-text">共找到 {{ filteredActions.length }} 个动作</text>
          <view class="reset-btn" v-if="selectedCategory || selectedMuscle" @click="resetFilters">
            <text class="reset-icon">↻</text>
            <text class="reset-text">重置</text>
          </view>
        </view>
      </view>
      
      <!-- ✅ 动作列表区域 -->
      <view class="action-list-section">
        <!-- 加载状态 -->
        <view class="loading-state" v-if="loading">
          <view class="loading-spinner"></view>
          <text class="loading-text">加载动作库中...</text>
        </view>
        
        <!-- 动作列表 -->
        <view class="action-list" v-else-if="filteredActions.length > 0">
          <view 
            class="action-card" 
            v-for="(action, index) in filteredActions" 
            :key="action.action_id"
            @click="viewActionDetail(action)"
          >
            <!-- 动作头部 -->
            <view class="card-header">
              <view class="action-info">
                <text class="action-name">{{ action.name }}</text>
                <view class="action-badges">
                  <text class="badge difficulty" :class="getDifficultyClass(action.difficulty_level)">
                    {{ action.difficulty_level }}
                  </text>
                  <text class="badge category" :class="getCategoryClass(action.action_category)">
                    {{ getCategoryText(action.action_category) }}
                  </text>
                </view>
              </view>
              <view class="favorite-btn" @click.stop="toggleFavorite(action)">
                <text class="favorite-icon">{{ action.isFavorited ? '❤️' : '🤍' }}</text>
              </view>
            </view>
            
            <!-- 目标肌群 -->
            <view class="card-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
              <text class="muscles-label">🎯 目标肌群：</text>
              <view class="muscles-wrapper">
                <text 
                  class="muscle-tag" 
                  v-for="(muscle, mIndex) in action.target_muscles.slice(0, 3)" 
                  :key="mIndex"
                >
                  {{ muscle }}
                </text>
                <text class="muscle-tag more" v-if="action.target_muscles.length > 3">
                  +{{ action.target_muscles.length - 3 }}
                </text>
              </view>
            </view>
            
            <!-- 所需器材 -->
            <view class="card-equipment" v-if="action.equipment_name">
              <text class="equipment-label">🏋️ 所需器材：</text>
              <text class="equipment-value">{{ action.equipment_name }}</text>
            </view>
            
            <!-- 动作时长 -->
            <view class="card-duration">
              <text class="duration-label">⏱️ 单次时长：</text>
              <text class="duration-value">{{ formatDuration(action.estimated_seconds) }}</text>
            </view>
            
            <!-- 底部操作栏 -->
            <view class="card-footer">
              <button class="footer-btn detail-btn" @click.stop="viewActionDetail(action)">
                <text class="btn-icon">👁️</text>
                <text class="btn-text">详情</text>
              </button>
              <button class="footer-btn plan-btn" @click.stop="addToPlan(action)">
                <text class="btn-icon">📋</text>
                <text class="btn-text">加入计划</text>
              </button>
            </view>
          </view>
        </view>
        
        <!-- 空状态 -->
        <view class="empty-state" v-else>
          <image src="/static/empty-actions.png" class="empty-image" mode="aspectFit" />
          <text class="empty-text">暂无匹配的动作</text>
          <text class="empty-subtext">请尝试其他筛选条件</text>
          <button class="reset-all-btn" @click="resetFilters">重置筛选</button>
        </view>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import {onShow} from '@dcloudio/uni-app'
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const userStore = useUserStore()
  
  // 加载状态
  const loading = ref(false)
  
  // 所有动作列表
  const allActions = ref([])
  
  // 筛选条件
  const selectedCategory = ref('') // '' 表示全部
  const selectedMuscle = ref('') // '' 表示全部
  
  // 肌群选项
  const muscleOptions = ref([])
  
  // 滚动控制
  const scrollIntoView = ref('')
  
  // 过滤后的动作列表
  const filteredActions = computed(() => {
    let result = allActions.value
    
    // 按类别筛选
    if (selectedCategory.value) {
      result = result.filter(action => action.action_category === selectedCategory.value)
    }
    
    // 按肌群筛选
    if (selectedMuscle.value) {
      result = result.filter(action => 
        action.target_muscles && action.target_muscles.includes(selectedMuscle.value)
      )
    }
    
    return result
  })
  
  onShow(async () => {
    await loadActionLibrary()
    await loadMuscleOptions()
  })
  
  /**
   * 加载动作库所有动作
   */
  const loadActionLibrary = async () => {
    loading.value = true
    
    try {
      const res = await request.get(API.ACTION_LIBRARY)
      
      // 添加收藏状态标记
      allActions.value = res.actions.map(action => ({
        ...action,
        isFavorited: false // 实际项目中应从用户收藏接口获取
      }))
      
    } catch (error) {
      console.error('加载动作库失败:', error)
      uni.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 加载肌群选项
   */
  const loadMuscleOptions = async () => {
    try {
      const res = await request.get(API.ACTION_MUSCLES)
      muscleOptions.value = res
    } catch (error) {
      console.error('加载肌群选项失败:', error)
    }
  }
  
  /**
   * 选择动作类别
   */
  const selectCategory = (category) => {
    selectedCategory.value = category
    scrollIntoView.value = ''
  }
  
  /**
   * 选择目标肌群
   */
  const selectMuscle = (muscle) => {
    selectedMuscle.value = muscle
  }
  
  /**
   * 重置筛选条件
   */
  const resetFilters = () => {
    selectedCategory.value = ''
    selectedMuscle.value = ''
    uni.pageScrollTo({ scrollTop: 0, duration: 300 })
  }
  
  /**
   * 根据难度级别返回相应的 CSS 类
   */
  const getDifficultyClass = (difficulty) => {
    switch (difficulty) {
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
  const getCategoryText = (category) => {
    switch (category?.toLowerCase()) {
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
  const getCategoryClass = (category) => {
    switch (category?.toLowerCase()) {
      case 'warmup':
        return 'category-warmup'
      case 'main_cardio':
        return 'category-cardio'
      case 'main_strength':
        return 'category-strength'
      case 'cooldown':
        return 'category-cooldown'
      default:
        return ''
    }
  }
  
  /**
   * 格式化时长
   */
  const formatDuration = (seconds) => {
    if (!seconds) return '0 秒'
    if (seconds < 60) return `${seconds}秒`
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return secs > 0 ? `${mins}分${secs}秒` : `${mins}分钟`
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
            url: `/pages/plan/select-plan?action_id=${action.action_id}&action_name=${encodeURIComponent(action.name)}`
          })
        }
      }
    })
  }
  </script>
  
  <style lang="scss" scoped>
  .container {
    min-height: 100vh;
    background: #F5F5F5;
    padding-bottom: 40rpx;
  }
  
  /* ========== 固定筛选区域 ========== */
  .filter-section {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #FFFFFF;
    padding: 24rpx 30rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  }
  
  .filter-row {
    display: flex;
    align-items: center;
    margin-bottom: 20rpx;
    
    &:last-of-type {
      margin-bottom: 16rpx;
    }
    
    .filter-label {
      font-size: 28rpx;
      font-weight: 600;
      color: #333333;
      margin-right: 16rpx;
      flex-shrink: 0;
      width: 140rpx;
    }
    
    .category-scroll, .muscle-scroll {
      flex: 1;
      white-space: nowrap;
      
      .filter-buttons {
        display: inline-flex;
        gap: 16rpx;
        
        .filter-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 12rpx 28rpx;
          background: #F5F5F5;
          border-radius: 32rpx;
          border: 2rpx solid transparent;
          
          .btn-text {
            font-size: 26rpx;
            color: #666666;
            font-weight: 500;
          }
          
          &.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #667eea;
            
            .btn-text {
              color: #FFFFFF;
              font-weight: 600;
            }
          }
        }
        
        .muscle-btn {
          padding: 12rpx 24rpx;
          
          .btn-text {
            font-size: 24rpx;
          }
        }
      }
    }
  }
  
  .filter-result {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16rpx;
    border-top: 1rpx solid #E5E5E5;
    
    .result-text {
      font-size: 26rpx;
      color: #666666;
    }
    
    .reset-btn {
      display: flex;
      align-items: center;
      gap: 8rpx;
      padding: 8rpx 20rpx;
      background: #F5F5F5;
      border-radius: 24rpx;
      
      .reset-icon {
        font-size: 28rpx;
        color: #667eea;
      }
      
      .reset-text {
        font-size: 24rpx;
        color: #667eea;
        font-weight: 500;
      }
    }
  }
  
  /* ========== 动作列表区域 ========== */
  .action-list-section {
    padding: 30rpx;
    
    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 100rpx 0;
      
      .loading-spinner {
        width: 60rpx;
        height: 60rpx;
        border: 4rpx solid #E5E5E5;
        border-top-color: #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20rpx;
      }
      
      .loading-text {
        font-size: 28rpx;
        color: #666666;
      }
    }
    
    .action-list {
      .action-card {
        background: #FFFFFF;
        border-radius: 24rpx;
        padding: 32rpx;
        margin-bottom: 24rpx;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
        
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24rpx;
          
          .action-info {
            flex: 1;
            margin-right: 20rpx;
            
            .action-name {
              display: block;
              font-size: 32rpx;
              font-weight: 700;
              color: #333333;
              margin-bottom: 16rpx;
            }
            
            .action-badges {
              display: flex;
              gap: 12rpx;
              
              .badge {
                font-size: 22rpx;
                padding: 6rpx 16rpx;
                border-radius: 16rpx;
                font-weight: 600;
                
                &.difficulty {
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
                
                &.category {
                  &.category-warmup {
                    background: #E3F2FD;
                    color: #1976D2;
                  }
                  &.category-cardio {
                    background: #E8F5E9;
                    color: #388E3C;
                  }
                  &.category-strength {
                    background: #FFF3E0;
                    color: #F57C00;
                  }
                  &.category-cooldown {
                    background: #F3E5F5;
                    color: #7B1FA2;
                  }
                }
              }
            }
          }
          
          .favorite-btn {
            width: 64rpx;
            height: 64rpx;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            
            .favorite-icon {
              font-size: 40rpx;
            }
          }
        }
        
        .card-muscles {
          margin-bottom: 20rpx;
          
          .muscles-label {
            display: block;
            font-size: 26rpx;
            color: #666666;
            margin-bottom: 12rpx;
          }
          
          .muscles-wrapper {
            display: flex;
            flex-wrap: wrap;
            gap: 12rpx;
            
            .muscle-tag {
              background: #F5F5F5;
              color: #333333;
              font-size: 24rpx;
              padding: 8rpx 20rpx;
              border-radius: 16rpx;
              font-weight: 500;
              
              &.more {
                background: #E0E0E0;
                color: #666666;
              }
            }
          }
        }
        
        .card-equipment {
          margin-bottom: 20rpx;
          
          .equipment-label {
            font-size: 26rpx;
            color: #666666;
            margin-right: 8rpx;
          }
          
          .equipment-value {
            font-size: 26rpx;
            color: #333333;
            font-weight: 500;
          }
        }
        
        .card-duration {
          margin-bottom: 24rpx;
          
          .duration-label {
            font-size: 26rpx;
            color: #666666;
            margin-right: 8rpx;
          }
          
          .duration-value {
            font-size: 26rpx;
            color: #333333;
            font-weight: 500;
          }
        }
        
        .card-footer {
          display: flex;
          gap: 16rpx;
          
          .footer-btn {
            flex: 1;
            height: 72rpx;
            border-radius: 36rpx;
            border: none;
            font-size: 26rpx;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8rpx;
            
            .btn-icon {
              font-size: 28rpx;
            }
            
            .btn-text {
              line-height: 1;
            }
            
            &.detail-btn {
              background: #F5F5F5;
              color: #333333;
            }
            
            &.plan-btn {
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: #FFFFFF;
            }
          }
        }
      }
    }
    
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 100rpx 0;
      
      .empty-image {
        width: 240rpx;
        height: 240rpx;
        margin-bottom: 40rpx;
      }
      
      .empty-text {
        font-size: 32rpx;
        color: #333333;
        font-weight: 600;
        margin-bottom: 16rpx;
      }
      
      .empty-subtext {
        font-size: 28rpx;
        color: #666666;
        margin-bottom: 40rpx;
      }
      
      .reset-all-btn {
        width: 280rpx;
        height: 80rpx;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #FFFFFF;
        font-size: 28rpx;
        font-weight: 600;
        border-radius: 40rpx;
        border: none;
      }
    }
  }
  
  /* 动画效果 */
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  </style>