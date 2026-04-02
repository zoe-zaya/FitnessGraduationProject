<template>
    <view class="container">
      <!-- 搜索栏 -->
      <view class="search-bar">
        <view class="search-input-wrapper">
          <text class="search-icon">🔍</text>
          <input 
            v-model="searchKeyword" 
            type="text" 
            placeholder="搜索动作名称或肌群"
            class="search-input"
            @confirm="searchActions"
          />
        </view>
        <view class="search-btn" @click="searchActions">
          <text class="btn-text">搜索</text>
        </view>
      </view>
      
      <!-- 筛选条件 -->
      <view class="filter-bar">
        <view class="filter-item">
          <text class="filter-label">难度：</text>
          <picker 
            @change="onDifficultyChange" 
            :value="difficultyIndex" 
            :range="difficultyOptions"
            range-key="label"
            class="filter-picker"
          >
            <text class="filter-text">{{ difficultyOptions[difficultyIndex]?.label }}</text>
          </picker>
        </view>
      </view>
      
      <!-- 当前阶段信息 -->
      <view class="session-info-card">
        <text class="info-title">📍 添加到</text>
        <text class="info-value">{{ getSessionName(sessionType) }}</text>
      </view>
      
      <!-- 动作列表 -->
      <view class="action-list" v-if="actionList.length > 0">
        <view 
          class="action-card" 
          v-for="(action, index) in actionList" 
          :key="action.action_id"
          @click="selectAction(action)"
        >
          <view class="action-header">
            <text class="action-name">{{ action.name }}</text>
            <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
              {{ action.difficulty_level }}
            </text>
          </view>
          
          <view class="action-category">
            <text class="category-label">📊 类别：</text>
            <text class="category-value">{{ getCategoryName(action.action_category) }}</text>
          </view>
          
          <view class="action-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
            <text class="muscles-label">🎯 目标肌群：</text>
            <view class="muscles-tags">
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
          
          <view class="action-equipment" v-if="action.equipment_name">
            <text class="equipment-label">🏋️ 器材：</text>
            <text class="equipment-value">{{ action.equipment_name }}</text>
          </view>
          
          <view class="action-footer">
            <text class="action-duration">⏱️ {{ formatDuration(action.estimated_seconds) }}</text>
            <view class="select-btn">
              <text class="btn-icon">+</text>
              <text class="btn-text">添加</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-else-if="hasSearched">
        <image src="/static/empty-search.png" class="empty-image" mode="aspectFit" />
        <text class="empty-text">未找到匹配的动作</text>
        <text class="empty-subtext">请尝试其他关键词或筛选条件</text>
      </view>
      
      <!-- 默认提示 -->
      <view class="default-tip" v-else>
        <image src="/static/search-guide.png" class="tip-image" mode="aspectFit" />
        <text class="tip-text">输入关键词搜索动作</text>
        <text class="tip-subtext">如"深蹲"、"卧推"、"胸大肌"等</text>
      </view>
      
      <!-- 加载提示 -->
      <view class="loading-mask" v-if="loading">
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { onLoad, onShow } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API, SESSION_TYPE_MAP, DIFFICULTY_MAP } from '@/utils/constants'
  
  const planId = ref('')
  const sessionId = ref('')
  const sessionType = ref('')  // warmup/main/cooldown
  
  const searchKeyword = ref('')
  const difficultyIndex = ref(0)
  const difficultyOptions = ref([
    { label: '全部难度', value: '' },
    { label: '初级', value: '初级' },
    { label: '中级', value: '中级' },
    { label: '高级', value: '高级' }
  ])
  
  const actionList = ref([])
  const loading = ref(false)
  const hasSearched = ref(false)
  
  onLoad((options) => {
    planId.value = options.plan_id || ''
    sessionId.value = options.session_id || ''
    sessionType.value = options.session_type || 'main'
  })
  
  onShow(() => {
    // 首次进入时自动搜索适合该阶段的动作
    searchActionsBySession()
  })
  
  /**
   * 根据阶段类型搜索动作
   */
  const searchActionsBySession = async () => {
    let category = ''
    
    // 根据阶段类型确定动作类别
    if (sessionType.value === 'warmup') {
      category = 'warmup'
    } else if (sessionType.value === 'main') {
      // 正式训练需要从计划中获取健身目标
      category = 'main_strength'  // 默认力量训练
    } else if (sessionType.value === 'cooldown') {
      category = 'cooldown'
    }
    
    // 搜索动作
    await searchActions(category)
  }
  
  /**
   * 搜索动作
   */
  const searchActions = async (category = '') => {
    if (!searchKeyword.value.trim() && !category) {
      return
    }
    
    loading.value = true
    hasSearched.value = true
    
    try {
      let url = ''
      let params = {}
      
      if (category) {
        // 按类别查询
        url = `${API.ACTION_QUERY}`
        params = {
          action_category: category,
          target_muscle: searchKeyword.value.trim() || ''
        }
      } else {
        // 关键词搜索
        url = `${API.ACTION_QUERY}`
        params = {
          target_muscle: searchKeyword.value.trim()
        }
      }
      
      const res = await request.get(url, { params })
      
      // 过滤难度
      if (difficultyIndex.value > 0) {
        const selectedDifficulty = difficultyOptions.value[difficultyIndex.value]?.value
        actionList.value = res.filter(action => action.difficulty_level === selectedDifficulty)
      } else {
        actionList.value = res
      }
      
    } catch (error) {
      console.error('搜索失败:', error)
      actionList.value = []
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 选择难度
   */
  const onDifficultyChange = (e) => {
    difficultyIndex.value = e.detail.value
    searchActionsBySession()
  }
  
  /**
   * 获取阶段名称
   */
  const getSessionName = (type) => {
    return SESSION_TYPE_MAP[type]?.label || type
  }
  
  /**
   * 获取类别名称
   */
  const getCategoryName = (category) => {
    const map = {
      'warmup': '热身激活',
      'main_cardio': '有氧训练',
      'main_strength': '力量训练',
      'cooldown': '拉伸放松'
    }
    return map[category] || category
  }
  
  /**
   * 获取难度颜色
   */
  const getDifficultyColor = (level) => {
    return DIFFICULTY_MAP[level]?.color || '#999999'
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
   * 选择动作
   */
  const selectAction = async (action) => {
    // 根据阶段类型配置默认参数
    const addData = {
      session_id: sessionId.value,
      action_id: action.action_id
    }
    
    // 力量训练配置组数/次数/休息
    if (action.action_category === 'main_strength') {
      addData.sets = 3
      addData.reps_per_set = 12
      addData.rest_seconds = 60
    } else {
      // 有氧/热身/拉伸配置时长
      addData.duration_seconds = action.estimated_seconds || 30
    }
    
    try {
      await request.post(`${API.PLAN_ADD_ACTION}/${planId.value}`, addData)
      
      uni.showToast({ 
        title: `"${action.name}"已添加`, 
        icon: 'success',
        duration: 1500
      })
      
      setTimeout(() => {
        uni.navigateBack()
      }, 1000)
      
    } catch (error) {
      console.error('添加失败:', error)
      
      if (error.response && error.response.status === 400) {
        uni.showToast({ 
          title: '该动作已在计划中', 
          icon: 'none',
          duration: 2000
        })
      } else {
        uni.showToast({ 
          title: '添加失败', 
          icon: 'none',
          duration: 2000
        })
      }
    }
  }
  </script>
  
  <style lang="scss" scoped>
  .container {
    min-height: 100vh;
    background: #F5F5F5;
    padding: 0 0 40rpx;
  }
  
  .search-bar {
    display: flex;
    align-items: center;
    padding: 24rpx 30rpx;
    background: #FFFFFF;
    gap: 16rpx;
    
    .search-input-wrapper {
      flex: 1;
      display: flex;
      align-items: center;
      background: #F5F5F5;
      border-radius: 32rpx;
      padding: 0 24rpx;
      
      .search-icon {
        font-size: 32rpx;
        margin-right: 12rpx;
      }
      
      .search-input {
        flex: 1;
        height: 72rpx;
        font-size: 28rpx;
      }
    }
    
    .search-btn {
      padding: 0 32rpx;
      height: 72rpx;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 36rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .btn-text {
        font-size: 28rpx;
        color: #FFFFFF;
        font-weight: 600;
      }
    }
  }
  
  .filter-bar {
    display: flex;
    align-items: center;
    padding: 20rpx 30rpx;
    background: #FFFFFF;
    border-bottom: 1rpx solid #E5E5E5;
    gap: 24rpx;
    
    .filter-item {
      display: flex;
      align-items: center;
      
      .filter-label {
        font-size: 26rpx;
        color: #666666;
        margin-right: 12rpx;
      }
      
      .filter-picker {
        .filter-text {
          font-size: 26rpx;
          color: #007AFF;
          font-weight: 500;
        }
      }
    }
  }
  
  .session-info-card {
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
    margin: 30rpx 40rpx;
    border-radius: 20rpx;
    padding: 24rpx 32rpx;
    display: flex;
    align-items: center;
    border-left: 6rpx solid #1976D2;
    
    .info-title {
      font-size: 26rpx;
      color: #1565C0;
      margin-right: 12rpx;
    }
    
    .info-value {
      font-size: 28rpx;
      color: #1976D2;
      font-weight: 600;
    }
  }
  
  .action-list {
    padding: 0 40rpx;
    
    .action-card {
      background: #FFFFFF;
      border-radius: 20rpx;
      padding: 28rpx;
      margin-bottom: 20rpx;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
      
      .action-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16rpx;
        
        .action-name {
          font-size: 30rpx;
          font-weight: 600;
          color: #333333;
          flex: 1;
        }
        
        .action-difficulty {
          font-size: 22rpx;
          padding: 6rpx 16rpx;
          border-radius: 12rpx;
          color: #FFFFFF;
          margin-left: 16rpx;
        }
      }
      
      .action-category {
        display: flex;
        margin-bottom: 12rpx;
        
        .category-label {
          font-size: 24rpx;
          color: #666666;
          margin-right: 8rpx;
        }
        
        .category-value {
          font-size: 24rpx;
          color: #333333;
          font-weight: 500;
        }
      }
      
      .action-muscles {
        margin-bottom: 12rpx;
        
        .muscles-label {
          display: block;
          font-size: 24rpx;
          color: #666666;
          margin-bottom: 8rpx;
        }
        
        .muscles-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 10rpx;
          
          .muscle-tag {
            background: #F5F5F5;
            color: #333333;
            font-size: 22rpx;
            padding: 6rpx 16rpx;
            border-radius: 12rpx;
            
            &.more {
              background: #E0E0E0;
              color: #666666;
            }
          }
        }
      }
      
      .action-equipment {
        display: flex;
        margin-bottom: 16rpx;
        
        .equipment-label {
          font-size: 24rpx;
          color: #666666;
          margin-right: 8rpx;
        }
        
        .equipment-value {
          font-size: 24rpx;
          color: #333333;
          font-weight: 500;
        }
      }
      
      .action-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .action-duration {
          font-size: 24rpx;
          color: #999999;
        }
        
        .select-btn {
          display: flex;
          align-items: center;
          padding: 12rpx 28rpx;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 24rpx;
          
          .btn-icon {
            font-size: 28rpx;
            color: #FFFFFF;
            margin-right: 6rpx;
          }
          
          .btn-text {
            font-size: 24rpx;
            color: #FFFFFF;
            font-weight: 600;
          }
        }
      }
    }
  }
  
  .empty-state, .default-tip {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100rpx 40rpx;
    text-align: center;
    
    .empty-image, .tip-image {
      width: 280rpx;
      height: 280rpx;
      margin-bottom: 40rpx;
    }
    
    .empty-text, .tip-text {
      font-size: 30rpx;
      color: #333333;
      font-weight: 600;
      margin-bottom: 16rpx;
    }
    
    .empty-subtext, .tip-subtext {
      font-size: 26rpx;
      color: #666666;
    }
  }
  
  .loading-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;
    
    .loading-text {
      font-size: 28rpx;
      color: #666666;
    }
  }
  </style>