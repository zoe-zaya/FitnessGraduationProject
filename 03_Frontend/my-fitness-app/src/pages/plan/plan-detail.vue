<template>
    <view class="container">
      <!-- 计划基本信息 -->
      <view class="plan-header">
        <text class="plan-name">{{ planInfo.plan_name }}</text>
        <view class="plan-status" :class="{ 'expired': planInfo.is_expired }">
          {{ planInfo.is_expired ? '已过期' : '进行中' }}
        </view>
      </view>
      
      <view class="plan-meta">
        <view class="meta-item">
          <text class="meta-icon">🎯</text>
          <text class="meta-text">{{ planInfo.fitness_goal }} · {{ planInfo.training_part }}</text>
        </view>
        <view class="meta-item">
          <text class="meta-icon">⏱️</text>
          <text class="meta-text">{{ planInfo.total_duration_minutes }}分钟</text>
        </view>
        <view class="meta-item">
          <text class="meta-icon">📅</text>
          <text class="meta-text">有效期{{ planInfo.valid_days }}天</text>
        </view>
      </view>
      
      <!-- 三阶段 -->
      <view class="sessions-section">
        <view 
          class="session-card" 
          v-for="(session, index) in planInfo.sessions" 
          :key="session.session_id"
        >
          <view class="session-header" :style="{ borderLeftColor: getSessionColor(session.session_type) }">
            <text class="session-icon">{{ getSessionIcon(session.session_type) }}</text>
            <view class="session-info">
              <text class="session-name">{{ getSessionName(session.session_type) }}</text>
              <text class="session-duration">⏱️ {{ session.estimated_duration_minutes }}分钟</text>
            </view>
            <text class="session-order">{{ session.sequence_order }}/3</text>
          </view>
          
          <!-- 目标肌群 -->
          <view class="session-muscles" v-if="session.target_muscles && session.target_muscles.length > 0">
            <text class="muscles-label">🎯 目标肌群：</text>
            <view class="muscles-tags">
              <text 
                class="muscle-tag" 
                v-for="(muscle, mIndex) in session.target_muscles" 
                :key="mIndex"
              >
                {{ muscle }}
              </text>
            </view>
          </view>
          
          <!-- 动作列表 -->
          <view class="action-list">
            <view 
              class="action-item" 
              v-for="(action, aIndex) in session.action_items" 
              :key="action.item_id"
              @click="viewActionDetail(action)"
            >
              <view class="action-header">
                <text class="action-name">{{ action.action_name }}</text>
                <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                  {{ action.difficulty_level }}
                </text>
              </view>
              
              <!-- 力量训练参数 -->
              <view class="action-params" v-if="action.sets && action.reps_per_set">
                <text class="param-item">📊 {{ action.sets }}组 × {{ action.reps_per_set }}次</text>
                <text class="param-item">⏸️ 休息{{ action.rest_seconds }}秒</text>
              </view>
              
              <!-- 有氧/拉伸参数 -->
              <view class="action-params" v-else-if="action.duration_seconds">
                <text class="param-item">⏱️ 持续{{ action.duration_seconds }}秒</text>
              </view>
              
              <view class="action-footer">
                <text class="action-duration">⏱️ {{ formatDuration(action.total_duration_seconds) }}</text>
                <view class="action-buttons">
                  <view class="action-btn edit" @click.stop="editActionItem(action, session)">
                    <text class="btn-icon">✏️</text>
                  </view>
                  <view class="action-btn delete" @click.stop="confirmDeleteAction(action)">
                    <text class="btn-icon">🗑️</text>
                  </view>
                </view>
              </view>
            </view>
            
            <!-- 添加动作按钮 -->
            <view class="add-action-btn" @click="addActionToSession(session)">
              <text class="btn-icon">+</text>
              <text class="btn-text">添加动作</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 底部操作栏 -->
      <view class="bottom-bar">
        <button class="btn extend-btn" @click="extendPlan">
          <text class="btn-icon">📅</text>
          <text class="btn-text">延长有效期</text>
        </button>
        <button class="btn edit-btn" @click="editPlan">
          <text class="btn-icon">✏️</text>
          <text class="btn-text">编辑计划</text>
        </button>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { onLoad, onShow } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API, SESSION_TYPE_MAP, DIFFICULTY_MAP } from '@/utils/constants'
  
  const planId = ref('')
  const planInfo = ref({
    plan_name: '',
    fitness_goal: '',
    training_part: '',
    total_duration_minutes: 0,
    valid_days: 30,
    is_expired: false,
    sessions: []
  })
  
  onLoad((options) => {
    planId.value = options.plan_id || ''
  })
  
  onShow(async () => {
    if (planId.value) {
      await loadPlanDetail()
    }
  })
  
  /**
   * 加载计划详情
   */
  const loadPlanDetail = async () => {
    try {
      const res = await request.get(`${API.PLAN_DETAIL}/${planId.value}`)
      planInfo.value = res
    } catch (error) {
      console.error('加载失败:', error)
      uni.showToast({ title: '加载失败', icon: 'none' })
    }
  }
  
  /**
   * 获取阶段名称
   */
  const getSessionName = (type) => {
    return SESSION_TYPE_MAP[type]?.label || type
  }
  
  /**
   * 获取阶段图标
   */
  const getSessionIcon = (type) => {
    return SESSION_TYPE_MAP[type]?.icon || '💪'
  }
  
  /**
   * 获取阶段颜色
   */
  const getSessionColor = (type) => {
    return SESSION_TYPE_MAP[type]?.color || '#007AFF'
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
    if (seconds < 60) return `${seconds}秒`
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return secs > 0 ? `${mins}分${secs}秒` : `${mins}分钟`
  }
  
  /**
   * 查看动作详情
   */
  const viewActionDetail = (action) => {
    uni.navigateTo({ url: `/pages/action/action-detail?action_id=${action.action_id}` })
  }
  
  /**
   * 编辑动作项
   */
  const editActionItem = (action, session) => {
    uni.navigateTo({ 
      url: `/pages/plan/plan-edit?action_id=${action.item_id}&session_id=${session.session_id}&plan_id=${planId.value}` 
    })
  }
  
  /**
   * 添加动作到阶段
   */
  const addActionToSession = (session) => {
    uni.navigateTo({ 
      url: `/pages/plan/select-action?session_id=${session.session_id}&plan_id=${planId.value}&session_type=${session.session_type}` 
    })
  }
  
  /**
   * 确认删除动作项
   */
  const confirmDeleteAction = (action) => {
    uni.showModal({
      title: '提示',
      content: `确定要删除"${action.action_name}"吗？`,
      success: async (res) => {
        if (res.confirm) {
          await deleteActionItem(action.item_id)
        }
      }
    })
  }
  
  /**
   * 删除动作项
   */
  const deleteActionItem = async (itemId) => {
    try {
      await request.delete(`${API.PLAN_DELETE_ACTION}/${planId.value}/${itemId}`)
      uni.showToast({ title: '删除成功', icon: 'success' })
      await loadPlanDetail()
    } catch (error) {
      console.error('删除失败:', error)
      uni.showToast({ title: '删除失败', icon: 'none' })
    }
  }
  
  /**
   * 延长有效期
   */
  const extendPlan = () => {
    uni.showModal({
      title: '延长有效期',
      content: '确定要延长 30 天有效期吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await request.post(`${API.PLAN_EXTEND}/${planId.value}`, { days: 30 })
            uni.showToast({ title: '延长成功', icon: 'success' })
            await loadPlanDetail()
          } catch (error) {
            console.error('延长失败:', error)
            uni.showToast({ title: '延长失败', icon: 'none' })
          }
        }
      }
    })
  }
  
  /**
   * 编辑计划
   */
  const editPlan = () => {
    uni.navigateTo({ url: `/pages/plan/plan-edit?plan_id=${planId.value}` })
  }
  </script>
  
  <style lang="scss" scoped>
  .container {
    min-height: 100vh;
    background: #F5F5F5;
    padding: 0 0 140rpx;
  }
  
  .plan-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40rpx;
    
    .plan-name {
      display: block;
      font-size: 40rpx;
      font-weight: bold;
      color: #FFFFFF;
      margin-bottom: 16rpx;
    }
    
    .plan-status {
      display: inline-block;
      font-size: 24rpx;
      padding: 8rpx 20rpx;
      background: rgba(255, 255, 255, 0.3);
      color: #FFFFFF;
      border-radius: 20rpx;
      
      &.expired {
        background: rgba(255, 68, 68, 0.3);
      }
    }
  }
  
  .plan-meta {
    background: #FFFFFF;
    padding: 24rpx 40rpx;
    display: flex;
    flex-wrap: wrap;
    gap: 24rpx;
    
    .meta-item {
      display: flex;
      align-items: center;
      
      .meta-icon {
        font-size: 32rpx;
        margin-right: 8rpx;
      }
      
      .meta-text {
        font-size: 26rpx;
        color: #666666;
      }
    }
  }
  
  .sessions-section {
    padding: 30rpx 40rpx;
    
    .session-card {
      background: #FFFFFF;
      border-radius: 24rpx;
      padding: 32rpx;
      margin-bottom: 24rpx;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
      
      .session-header {
        display: flex;
        align-items: center;
        margin-bottom: 24rpx;
        padding-left: 20rpx;
        border-left: 6rpx solid #007AFF;
        
        .session-icon {
          font-size: 40rpx;
          margin-right: 16rpx;
        }
        
        .session-info {
          flex: 1;
          
          .session-name {
            display: block;
            font-size: 30rpx;
            font-weight: bold;
            color: #333333;
            margin-bottom: 8rpx;
          }
          
          .session-duration {
            display: block;
            font-size: 24rpx;
            color: #666666;
          }
        }
        
        .session-order {
          font-size: 24rpx;
          color: #999999;
          font-weight: bold;
        }
      }
      
      .session-muscles {
        margin-bottom: 24rpx;
        
        .muscles-label {
          display: block;
          font-size: 26rpx;
          color: #666666;
          margin-bottom: 12rpx;
        }
        
        .muscles-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 12rpx;
          
          .muscle-tag {
            background: #F5F5F5;
            color: #333333;
            font-size: 24rpx;
            padding: 8rpx 20rpx;
            border-radius: 16rpx;
          }
        }
      }
      
      .action-list {
        .action-item {
          background: #F9F9F9;
          border-radius: 16rpx;
          padding: 24rpx;
          margin-bottom: 16rpx;
          
          .action-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16rpx;
            
            .action-name {
              font-size: 28rpx;
              font-weight: 600;
              color: #333333;
            }
            
            .action-difficulty {
              font-size: 22rpx;
              padding: 6rpx 16rpx;
              border-radius: 12rpx;
              color: #FFFFFF;
            }
          }
          
          .action-params {
            display: flex;
            gap: 24rpx;
            margin-bottom: 16rpx;
            
            .param-item {
              font-size: 24rpx;
              color: #666666;
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
            
            .action-buttons {
              display: flex;
              gap: 12rpx;
              
              .action-btn {
                width: 56rpx;
                height: 56rpx;
                border-radius: 28rpx;
                display: flex;
                justify-content: center;
                align-items: center;
                
                &.edit {
                  background: #FFF3E0;
                }
                
                &.delete {
                  background: #FFEBEE;
                }
                
                .btn-icon {
                  font-size: 26rpx;
                }
              }
            }
          }
        }
        
        .add-action-btn {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 24rpx;
          background: #F5F5F5;
          border-radius: 16rpx;
          border: 2rpx dashed #CCCCCC;
          
          .btn-icon {
            font-size: 32rpx;
            color: #007AFF;
            margin-right: 8rpx;
          }
          
          .btn-text {
            font-size: 26rpx;
            color: #007AFF;
          }
        }
      }
    }
  }
  
  .bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #FFFFFF;
    padding: 24rpx 40rpx;
    border-top: 1rpx solid #E5E5E5;
    display: flex;
    gap: 20rpx;
    
    .btn {
      flex: 1;
      height: 88rpx;
      border-radius: 44rpx;
      border: none;
      font-size: 28rpx;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12rpx;
      
      .btn-icon {
        font-size: 32rpx;
      }
      
      &.extend-btn {
        background: #F5F5F5;
        color: #333333;
      }
      
      &.edit-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #FFFFFF;
      }
    }
  }
  </style>