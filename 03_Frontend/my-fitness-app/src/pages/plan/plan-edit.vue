<template>
    <view class="container">
      <!-- 计划基本信息编辑 -->
      <view class="section-card">
        <text class="section-title">📋 计划基本信息</text>
        
        <view class="form-item">
          <text class="form-label">计划名称</text>
          <input 
            v-model="planName" 
            type="text" 
            placeholder="请输入计划名称"
            class="form-input"
            maxlength="50"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">有效期（天）</text>
          <picker 
            @change="onValidDaysChange" 
            :value="validDaysIndex" 
            :range="validDaysOptions"
            range-key="label"
            class="form-picker"
          >
            <view class="picker-wrapper">
              <text class="picker-text">{{ validDaysOptions[validDaysIndex]?.label }}</text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>
        
        <button class="save-basic-btn" @click="saveBasicInfo" :loading="savingBasic">
          保存基本信息
        </button>
      </view>
      
      <!-- 三阶段编辑 -->
      <view class="section-card" v-for="(session, index) in planSessions" :key="session.session_id">
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
          >
            <view class="action-header">
              <text class="action-name">{{ action.action_name }}</text>
              <text class="action-difficulty" :style="{ backgroundColor: getDifficultyColor(action.difficulty_level) }">
                {{ action.difficulty_level }}
              </text>
            </view>
            
            <!-- 力量训练参数编辑 -->
            <view class="action-params" v-if="action.sets && action.reps_per_set">
              <view class="param-row">
                <text class="param-label">组数：</text>
                <input 
                  v-model="action.sets" 
                  type="number" 
                  class="param-input"
                  @blur="updateActionItem(action)"
                />
              </view>
              <view class="param-row">
                <text class="param-label">次数/组：</text>
                <input 
                  v-model="action.reps_per_set" 
                  type="number" 
                  class="param-input"
                  @blur="updateActionItem(action)"
                />
              </view>
              <view class="param-row">
                <text class="param-label">休息（秒）：</text>
                <input 
                  v-model="action.rest_seconds" 
                  type="number" 
                  class="param-input"
                  @blur="updateActionItem(action)"
                />
              </view>
            </view>
            
            <!-- 有氧/拉伸参数编辑 -->
            <view class="action-params" v-else-if="action.duration_seconds">
              <view class="param-row">
                <text class="param-label">时长（秒）：</text>
                <input 
                  v-model="action.duration_seconds" 
                  type="number" 
                  class="param-input"
                  @blur="updateActionItem(action)"
                />
              </view>
            </view>
            
            <view class="action-footer">
              <text class="action-duration">⏱️ {{ formatDuration(action.total_duration_seconds) }}</text>
              <view class="action-buttons">
                <view class="action-btn delete" @click="confirmDeleteAction(action, session)">
                  <text class="btn-icon">🗑️</text>
                </view>
              </view>
            </view>
          </view>
          
          <!-- 添加动作按钮 -->
          <view class="add-action-btn" @click="selectActionToAdd(session)">
            <text class="btn-icon">+</text>
            <text class="btn-text">添加动作</text>
          </view>
        </view>
      </view>
      
      <!-- 底部操作栏 -->
      <view class="bottom-bar">
        <button class="btn cancel-btn" @click="navigateBack">
          <text class="btn-text">返回</text>
        </button>
        <button class="btn save-btn" @click="saveAllChanges" :loading="savingAll">
          <text class="btn-text">保存全部修改</text>
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
  const actionItemId = ref('')  // 如果是从动作项编辑进入
  const sessionId = ref('')     // 如果是从动作项编辑进入
  const planName = ref('')
  const savingBasic = ref(false)
  const savingAll = ref(false)
  
  // 有效期选项
  const validDaysOptions = ref([
    { label: '7 天', value: 7 },
    { label: '15 天', value: 15 },
    { label: '30 天', value: 30 },
    { label: '60 天', value: 60 },
    { label: '90 天', value: 90 }
  ])
  const validDaysIndex = ref(2)  // 默认 30 天
  
  // 计划阶段
  const planSessions = ref([])
  
  onLoad((options) => {
    planId.value = options.plan_id || ''
    actionItemId.value = options.action_id || ''
    sessionId.value = options.session_id || ''
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
      planName.value = res.plan_name
      planSessions.value = res.sessions
      
      // 设置有效期选择器
      const daysIndex = validDaysOptions.value.findIndex(opt => opt.value === res.valid_days)
      if (daysIndex >= 0) {
        validDaysIndex.value = daysIndex
      }
      
      // 如果是从动作项编辑进入，滚动到对应动作
      if (actionItemId.value) {
        // 可以添加滚动逻辑
      }
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
   * 选择有效期
   */
  const onValidDaysChange = (e) => {
    validDaysIndex.value = e.detail.value
  }
  
  /**
   * 保存基本信息
   */
  const saveBasicInfo = async () => {
    if (!planName.value.trim()) {
      uni.showToast({ title: '请输入计划名称', icon: 'none' })
      return
    }
    
    savingBasic.value = true
    
    try {
      await request.put(`${API.PLAN_UPDATE}/${planId.value}`, {
        plan_name: planName.value.trim(),
        valid_days: validDaysOptions.value[validDaysIndex.value]?.value
      })
      
      uni.showToast({ title: '保存成功', icon: 'success' })
    } catch (error) {
      console.error('保存失败:', error)
      uni.showToast({ title: '保存失败', icon: 'none' })
    } finally {
      savingBasic.value = false
    }
  }
  
  /**
   * 更新动作项参数
   */
  const updateActionItem = async (action) => {
    try {
      // 防抖处理，实际项目中应添加防抖
      const updateData = {}
      
      if (action.sets) {
        updateData.sets = parseInt(action.sets)
        updateData.reps_per_set = parseInt(action.reps_per_set)
        updateData.rest_seconds = parseInt(action.rest_seconds)
      } else {
        updateData.duration_seconds = parseInt(action.duration_seconds)
      }
      
      await request.put(`${API.PLAN_UPDATE_ACTION}/${planId.value}/${action.item_id}`, updateData)
      
      // 重新加载计划以获取更新后的时长
      await loadPlanDetail()
    } catch (error) {
      console.error('更新失败:', error)
      uni.showToast({ title: '更新失败', icon: 'none' })
    }
  }
  
  /**
   * 选择动作添加到阶段
   */
  const selectActionToAdd = (session) => {
    uni.navigateTo({ 
      url: `/pages/plan/select-action?session_id=${session.session_id}&plan_id=${planId.value}&session_type=${session.session_type}` 
    })
  }
  
  /**
   * 确认删除动作项
   */
  const confirmDeleteAction = (action, session) => {
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
   * 保存全部修改
   */
  const saveAllChanges = async () => {
    savingAll.value = true
    
    try {
      // 先保存基本信息
      await request.put(`${API.PLAN_UPDATE}/${planId.value}`, {
        plan_name: planName.value.trim(),
        valid_days: validDaysOptions.value[validDaysIndex.value]?.value
      })
      
      uni.showToast({ title: '保存成功', icon: 'success' })
      
      setTimeout(() => {
        uni.navigateBack()
      }, 1000)
    } catch (error) {
      console.error('保存失败:', error)
      uni.showToast({ title: '保存失败', icon: 'none' })
    } finally {
      savingAll.value = false
    }
  }
  
  /**
   * 返回上一页
   */
  const navigateBack = () => {
    uni.showModal({
      title: '提示',
      content: '确定要放弃修改吗？',
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
    background: #F5F5F5;
    padding: 0 0 140rpx;
  }
  
  .section-card {
    background: #FFFFFF;
    margin: 30rpx 40rpx;
    border-radius: 24rpx;
    padding: 32rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
    
    .section-title {
      display: block;
      font-size: 30rpx;
      font-weight: bold;
      color: #333333;
      margin-bottom: 24rpx;
    }
    
    .form-item {
      margin-bottom: 24rpx;
      
      .form-label {
        display: block;
        font-size: 28rpx;
        font-weight: 600;
        color: #333333;
        margin-bottom: 12rpx;
      }
      
      .form-input {
        width: 100%;
        height: 88rpx;
        background: #F5F5F5;
        border-radius: 16rpx;
        padding: 0 30rpx;
        font-size: 28rpx;
        box-sizing: border-box;
      }
      
      .form-picker {
        .picker-wrapper {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24rpx 30rpx;
          background: #F5F5F5;
          border-radius: 16rpx;
          
          .picker-text {
            font-size: 28rpx;
            color: #333333;
          }
          
          .picker-arrow {
            font-size: 32rpx;
            color: #999999;
          }
        }
      }
    }
    
    .save-basic-btn {
      width: 100%;
      height: 88rpx;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #FFFFFF;
      font-size: 30rpx;
      font-weight: 600;
      border-radius: 44rpx;
      border: none;
      margin-top: 16rpx;
    }
    
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
          margin-bottom: 16rpx;
          
          .param-row {
            display: flex;
            align-items: center;
            margin-bottom: 12rpx;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .param-label {
              font-size: 24rpx;
              color: #666666;
              width: 140rpx;
            }
            
            .param-input {
              flex: 1;
              height: 64rpx;
              background: #FFFFFF;
              border: 1rpx solid #E5E5E5;
              border-radius: 12rpx;
              padding: 0 20rpx;
              font-size: 24rpx;
              text-align: center;
            }
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
      
      .btn-text {
        line-height: 1;
      }
      
      &.cancel-btn {
        background: #F5F5F5;
        color: #333333;
      }
      
      &.save-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #FFFFFF;
      }
    }
  }
  </style>