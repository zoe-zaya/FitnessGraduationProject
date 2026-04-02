<template>
    <view class="container">
      <!-- 顶部操作栏 -->
      <view class="header">
        <text class="title">我的训练计划</text>
        <view class="generate-btn" @click="navigateToGenerate">
          <text class="btn-icon">+</text>
          <text class="btn-text">生成计划</text>
        </view>
      </view>
      
      <!-- 计划列表 -->
      <view class="plan-list" v-if="planList.length > 0">
        <view 
          class="plan-card" 
          v-for="(plan, index) in planList" 
          :key="plan.plan_id"
          @click="viewPlanDetail(plan)"
        >
          <view class="plan-header">
            <text class="plan-name">{{ plan.plan_name }}</text>
            <text class="plan-status" :class="{ 'expired': plan.is_expired }">
              {{ plan.is_expired ? '已过期' : '进行中' }}
            </text>
          </view>
          
          <view class="plan-info">
            <view class="info-item">
              <text class="info-label">🎯 目标：</text>
              <text class="info-value">{{ plan.fitness_goal }}</text>
            </view>
            <view class="info-item">
              <text class="info-label">📍 部位：</text>
              <text class="info-value">{{ plan.training_part }}</text>
            </view>
            <view class="info-item">
              <text class="info-label">⏱️ 时长：</text>
              <text class="info-value">{{ plan.total_duration_minutes }}分钟</text>
            </view>
            <view class="info-item">
              <text class="info-label">📅 有效期：</text>
              <text class="info-value">{{ formatDate(plan.create_time) }} 起 {{ plan.valid_days }}天</text>
            </view>
          </view>
          
          <view class="plan-footer">
            <text class="gym-name">🏋️ {{ plan.inventory_name }}</text>
            <view class="action-buttons">
              <view class="action-btn edit" @click.stop="editPlan(plan)">
                <text class="btn-icon">✏️</text>
              </view>
              <view class="action-btn delete" @click.stop="confirmDelete(plan)">
                <text class="btn-icon">🗑️</text>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 空状态提示 -->
      <view class="empty-state" v-else>
        <image src="/static/empty-plan.png" class="empty-image" mode="aspectFit" />
        <text class="empty-text">暂无训练计划</text>
        <text class="empty-subtext">点击下方按钮生成您的第一个训练计划</text>
        <button class="generate-plan-btn" @click="navigateToGenerate">生成训练计划</button>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { onShow } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const planList = ref([])
  const loading = ref(false)
  
  onShow(async () => {
    await loadPlanList()
  })
  
  /**
   * 加载训练计划列表
   */
  const loadPlanList = async () => {
    loading.value = true
    try {
      const res = await request.get(API.PLAN_LIST)
      planList.value = res
    } catch (error) {
      console.error('加载计划列表失败:', error)
      uni.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 格式化日期
   */
  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }
  
  /**
   * 跳转至生成计划页面
   */
  const navigateToGenerate = () => {
    uni.navigateTo({ url: '/pages/plan/generate-plan' })
  }
  
  /**
   * 查看计划详情
   */
  const viewPlanDetail = (plan) => {
    uni.navigateTo({ url: `/pages/plan/plan-detail?plan_id=${plan.plan_id}` })
  }
  
  /**
   * 编辑计划
   */
  const editPlan = (plan) => {
    uni.navigateTo({ url: `/pages/plan/plan-edit?plan_id=${plan.plan_id}` })
  }
  
  /**
   * 确认删除计划
   */
  const confirmDelete = (plan) => {
    uni.showModal({
      title: '提示',
      content: `确定要删除"${plan.plan_name}"吗？删除后无法恢复。`,
      success: async (res) => {
        if (res.confirm) {
          await deletePlan(plan.plan_id)
        }
      }
    })
  }
  
  /**
   * 删除计划
   */
  const deletePlan = async (planId) => {
    try {
      await request.delete(`${API.PLAN_DELETE}/${planId}`)
      uni.showToast({ title: '删除成功', icon: 'success' })
      await loadPlanList()
    } catch (error) {
      console.error('删除失败:', error)
      uni.showToast({ title: '删除失败', icon: 'none' })
    }
  }
  </script>
  
  <style lang="scss" scoped>
  .container {
    min-height: 100vh;
    background: #F5F5F5;
    padding: 0 0 40rpx;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx 40rpx;
    background: #FFFFFF;
    border-bottom: 1rpx solid #E5E5E5;
    
    .title {
      font-size: 36rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .generate-btn {
      display: flex;
      align-items: center;
      padding: 12rpx 24rpx;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 32rpx;
      
      .btn-icon {
        font-size: 32rpx;
        color: #FFFFFF;
        margin-right: 8rpx;
      }
      
      .btn-text {
        font-size: 26rpx;
        color: #FFFFFF;
      }
    }
  }
  
  .plan-list {
    padding: 30rpx 40rpx;
    
    .plan-card {
      background: #FFFFFF;
      border-radius: 24rpx;
      padding: 32rpx;
      margin-bottom: 24rpx;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
      
      .plan-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24rpx;
        
        .plan-name {
          font-size: 32rpx;
          font-weight: bold;
          color: #333333;
          flex: 1;
        }
        
        .plan-status {
          font-size: 24rpx;
          padding: 8rpx 20rpx;
          background: #E8F5E9;
          color: #34C759;
          border-radius: 20rpx;
          
          &.expired {
            background: #FFEBEE;
            color: #FF4444;
          }
        }
      }
      
      .plan-info {
        margin-bottom: 24rpx;
        
        .info-item {
          display: flex;
          margin-bottom: 12rpx;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .info-label {
            font-size: 26rpx;
            color: #666666;
          }
          
          .info-value {
            font-size: 26rpx;
            color: #333333;
            font-weight: 500;
          }
        }
      }
      
      .plan-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 24rpx;
        border-top: 1rpx solid #F5F5F5;
        
        .gym-name {
          font-size: 26rpx;
          color: #666666;
        }
        
        .action-buttons {
          display: flex;
          gap: 16rpx;
          
          .action-btn {
            width: 60rpx;
            height: 60rpx;
            border-radius: 30rpx;
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
              font-size: 28rpx;
            }
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
    padding: 100rpx 40rpx;
    
    .empty-image {
      width: 300rpx;
      height: 300rpx;
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
    
    .generate-plan-btn {
      width: 300rpx;
      height: 88rpx;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #FFFFFF;
      font-size: 30rpx;
      font-weight: 600;
      border-radius: 44rpx;
      border: none;
    }
  }
  </style>