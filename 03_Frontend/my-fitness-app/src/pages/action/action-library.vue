<template>
  <view class="container">
    <!-- 固定在顶部的筛选区域 -->
    <view class="filter-section">
      <!-- 第一行：分类筛选 -->
      <view class="filter-row">
        <text class="filter-label">动作类别</text>
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
        <text class="filter-label">目标肌群</text>
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
    
    <!-- 动作列表区域 -->
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
          v-for="(action, index) in paginatedActions" 
          :key="action.action_id"
          @click="viewActionDetail(action)"
        >
          <!-- 动作图片 -->
          <view class="card-image">
            <image 
              :src="action.image || '/static/action-placeholder.png'" 
              mode="aspectFill"
              class="action-image"
            />
          </view>
          
          <!-- 动作信息 -->
          <view class="card-content">
            <view class="card-header">
              <text class="action-name">{{ action.name }}</text>
              <view class="more-btn" @click.stop="showMoreOptions(action)">
                <text class="more-icon">•••</text>
              </view>
            </view>
            
            <view class="action-badges">
              <text class="badge difficulty" :class="getDifficultyClass(action.difficulty_level)">
                {{ action.difficulty_level }}
              </text>
              <text class="badge category" :class="getCategoryClass(action.action_category)">
                {{ getCategoryText(action.action_category) }}
              </text>
            </view>
          </view>
          
          <!-- 更多选项弹窗 -->
          <view v-if="showMore === action.action_id" class="more-options">
            <view class="option-item" @click.stop="toggleFavorite(action)">
              <text class="option-icon">{{ action.isFavorited ? '❤️' : '🤍' }}</text>
              <text class="option-text">{{ action.isFavorited ? '取消收藏' : '收藏' }}</text>
            </view>
            <view class="option-item" @click.stop="addToPlan(action)">
              <text class="option-icon">📋</text>
              <text class="option-text">加入计划</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 分页组件 -->
      <view class="pagination" v-if="totalPages > 1">
        <view class="pagination-controls">
          <view class="page-btn" @click="prevPage" :class="{ 'disabled': currentPage === 1 }">
            <text class="page-icon">←</text>
            <text class="page-text">上一页</text>
          </view>
          
          <view class="page-info">
            <text class="page-number">{{ currentPage }} / {{ totalPages }}</text>
          </view>
          
          <view class="page-btn" @click="nextPage" :class="{ 'disabled': currentPage === totalPages }">
            <text class="page-text">下一页</text>
            <text class="page-icon">→</text>
          </view>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-else>
        <image src="/static/empty-data.png" class="empty-image" mode="aspectFit" />
        <text class="empty-text">暂无匹配的动作</text>
        <text class="empty-subtext">请尝试其他筛选条件</text>
        <button class="reset-all-btn" @click="resetFilters">重置筛选</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import {onShow, onBackPress} from '@dcloudio/uni-app'
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

// 更多选项控制
const showMore = ref(null)

// 分页控制
const currentPage = ref(1)
const pageSize = ref(10)

// 分页后的动作列表
const paginatedActions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredActions.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredActions.value.length / pageSize.value)
})

// 切换页面
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    // 滚动到页面顶部
    uni.pageScrollTo({ scrollTop: 0, duration: 300 })
  }
}

// 上一页
const prevPage = () => {
  changePage(currentPage.value - 1)
}

// 下一页
const nextPage = () => {
  changePage(currentPage.value + 1)
}

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

/**
 * 显示/隐藏更多选项
 */
const showMoreOptions = (action) => {
  if (showMore.value === action.action_id) {
    showMore.value = null
  } else {
    showMore.value = action.action_id
  }
}

/**
 * 自定义返回路径
 */
onBackPress(() => {
  uni.switchTab({
    url: '/pages/index/index'
  })
  return true
})
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background-color: $fitness-secondary;
  padding-bottom: $size-5;
  font-family: Manrope;
}

/* ========== 固定筛选区域 ========== */
.filter-section {
  position: sticky;
  top: 0;
  z-index: 998;
  background: rgba(252, 249, 248, 0.95);
  padding: $size-3 $size-4;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(10px);
}

.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: $size-3;
  
  &:last-of-type {
    margin-bottom: $size-2;
  }
  
  .filter-label {
    font-size: $size-4;
    font-weight: 700;
    color: $color-label;
    margin-right: $size-2;
    flex-shrink: 0;
    width: 160rpx;
  }
  
  .category-scroll, .muscle-scroll {
    flex: 1;
    white-space: nowrap;
    
    .filter-buttons {
      display: inline-flex;
      gap: $size-2;
      margin-right: auto;
      padding-right: 40rpx;
      
      .filter-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: $size-1 $size-2;
          background: $fitness-secondary;
          border-radius: $size-3;
          border: 2rpx solid transparent;
          transition: all 0.2s ease;
          width: max-content;
          height: 20px;
          
          .btn-text {
            font-size: $size-3;
            color: $color-secondory;
            font-weight: 500;
            font-family: Manrope;
          }
          
          &.active {
            background: $button-bg2;
            border-color: $button-bg2;
            
            .btn-text {
              color: #FFFFFF;
              font-weight: 700;
            }
          }
        }
      
      .muscle-btn {
        padding: $size-1 $size-2;
        
        .btn-text {
          font-size: $size-3;
        }
      }
    }
  }
}

.filter-result {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: $size-2;
  border-top: 1rpx solid $color-line;
  
  .result-text {
    font-size: $size-3;
    color: $color-secondory;
  }
  
  .reset-btn {
    display: flex;
    align-items: center;
    gap: $size-1;
    padding: $size-1 $size-3;
    background: $fitness-secondary;
    border-radius: $size-5;
    
    .reset-icon {
      font-size: $size-4;
      color: $color-primary;
    }
    
    .reset-text {
      font-size: $size-3;
      color: $color-primary;
      font-weight: 500;
    }
  }
}

/* ========== 动作列表区域 ========== */
.action-list-section {
  padding: $size-4;
  
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: $size-8 0;
    
    .loading-spinner {
      width: 60rpx;
      height: 60rpx;
      border: 4rpx solid $color-line;
      border-top-color: $color-primary;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: $size-3;
    }
    
    .loading-text {
      font-size: $size-4;
      color: $color-secondory;
    }
  }
  
  .action-list {
    .action-card {
      background: rgba(252, 249, 248, 0.7);
      border-radius: $size-4;
      margin-bottom: $size-3;
      box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
      transition: transform 0.2s ease;
      overflow: hidden;
      position: relative;
      
      &:hover {
        transform: translateY(-4rpx);
      }
      
      .card-image {
        width: 100%;
        height: 200rpx;
        overflow: hidden;
        
        .action-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }
      
      .card-content {
        padding: $size-4;
        
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: $size-3;
          
          .action-name {
            font-size: $size-5;
            font-weight: 700;
            color: $fitness-text;
            flex: 1;
            margin-right: $size-3;
          }
          
          .more-btn {
            width: 40rpx;
            height: 40rpx;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            cursor: pointer;
            
            .more-icon {
              font-size: 24rpx;
              color: $color-secondory;
            }
          }
        }
        
        .action-badges {
          display: flex;
          gap: $size-2;
          
          .badge {
            font-size: $size-3;
            padding: $size-1 $size-3;
            border-radius: $size-2;
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
      
      .more-options {
        position: absolute;
        top: 80rpx;
        right: 20rpx;
        background: #FFFFFF;
        border-radius: $size-3;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.12);
        z-index: 10;
        min-width: 160rpx;
        
        .option-item {
          display: flex;
          align-items: center;
          padding: $size-3 $size-4;
          cursor: pointer;
          
          &:hover {
            background: $fitness-secondary;
          }
          
          .option-icon {
            font-size: 24rpx;
            margin-right: $size-2;
          }
          
          .option-text {
            font-size: $size-3;
            color: $fitness-text;
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
    padding: $size-8 0;
    
    .empty-image {
      width: 240rpx;
      height: 240rpx;
      margin-bottom: $size-5;
    }
    
    .empty-text {
      font-size: $size-5;
      color: $fitness-text;
      font-weight: 700;
      margin-bottom: $size-2;
    }
    
    .empty-subtext {
      font-size: $size-4;
      color: $color-secondory;
      margin-bottom: $size-5;
    }
    
    .reset-all-btn {
      width: 280rpx;
      height: $size-12;
      background: $button-bg2;
      color: #FFFFFF;
      font-size: $size-4;
      font-weight: 700;
      border-radius: $size-6;
      border: none;
      font-family: Manrope;
    }
  }
  
  /* ========== 分页组件 ========== */
  .pagination {
    margin-top: $size-5;
    margin-bottom: $size-5;
    
    .pagination-controls {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: $size-4;
      
      .page-btn {
        display: flex;
        align-items: center;
        gap: $size-1;
        padding: $size-2 $size-4;
        background: $fitness-secondary;
        border-radius: $size-4;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover:not(.disabled) {
          background: $button-bg2;
          
          .page-text, .page-icon {
            color: #FFFFFF;
          }
        }
        
        &.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .page-text {
          font-size: $size-3;
          color: $fitness-text;
          font-weight: 500;
        }
        
        .page-icon {
          font-size: $size-3;
          color: $fitness-text;
        }
      }
      
      .page-info {
        padding: $size-2 $size-4;
        
        .page-number {
          font-size: $size-3;
          color: $color-primary;
          font-weight: 700;
        }
      }
    }
  }
}

/* 动画效果 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>