<template>
    <view class="container">
      <!-- 顶部导航栏 -->
      <view class="nav-bar">
        <view class="nav-back" @click="navigateBack">
          <text class="back-icon">‹</text>
          <text class="back-text">返回</text>
        </view>
        <text class="nav-title">动作详情</text>
        <view class="nav-favorite" @click="toggleFavorite">
          <text class="favorite-icon">{{ isFavorited ? '❤️' : '🤍' }}</text>
        </view>
      </view>
  
      <!-- 动作演示视频区域 -->
      <view class="video-section">
        <video
          :src="getVideoUrl(actionInfo.video_demo_url)"
          class="action-video"
          :poster="getImageUrl(actionInfo.image_url)"
          :show-play-btn="true"
          :enable-progress-gesture="true"
          @error="onVideoError"
        />
        <view class="video-overlay" v-if="!videoLoaded">
          <text class="loading-text">视频加载中...</text>
        </view>
      </view>
  
      <!-- 动作基本信息卡片 -->
      <view class="info-card">
        <view class="info-header">
          <text class="action-name">{{ actionInfo.name }}</text>
          <view class="badges">
            <text class="badge difficulty" :class="getDifficultyClass(actionInfo.difficulty_level)">
              {{ actionInfo.difficulty_level }}
            </text>
            <text class="badge category" :class="getCategoryClass(actionInfo.action_category)">
              {{ getCategoryText(actionInfo.action_category) }}
            </text>
          </view>
        </view>
  
        <!-- 目标肌群 -->
        <view class="info-section" v-if="actionInfo.target_muscles && actionInfo.target_muscles.length > 0">
          <text class="section-label">🎯 目标肌群</text>
          <view class="muscles-tags">
            <text
              class="muscle-tag"
              v-for="(muscle, index) in actionInfo.target_muscles"
              :key="index"
            >
              {{ muscle }}
            </text>
          </view>
        </view>
  
        <!-- 所需器材 -->
        <view class="info-section" v-if="actionInfo.equipment_name">
          <text class="section-label">🏋️ 所需器材</text>
          <text class="equipment-text">{{ actionInfo.equipment_name }}</text>
        </view>
  
        <!-- 预计时长 -->
        <view class="info-section" v-if="actionInfo.estimated_seconds">
          <text class="section-label">⏱️ 单次时长</text>
          <text class="duration-text">{{ formatDuration(actionInfo.estimated_seconds) }}</text>
        </view>
      </view>
  
      <!-- 建议执行参数（根据用户经验水平动态调整） -->
      <view class="params-card">
        <text class="card-title">💪 建议执行参数</text>
        <view class="params-grid">
          <view class="param-item">
            <text class="param-label">建议组数</text>
            <text class="param-value">{{ suggestedParams.sets }}</text>
          </view>
          <view class="param-item">
            <text class="param-label">每组次数</text>
            <text class="param-value">{{ suggestedParams.reps }}</text>
          </view>
          <view class="param-item">
            <text class="param-label">组间休息</text>
            <text class="param-value">{{ suggestedParams.rest }}</text>
          </view>
          <view class="param-item">
            <text class="param-label">总时长</text>
            <text class="param-value">{{ suggestedParams.totalDuration }}</text>
          </view>
        </view>
        <text class="params-note">* 参数根据您的健身经验水平（{{ userExperienceLevel }}）智能推荐</text>
      </view>
  
      <!-- 分步动作要领 -->
      <view class="steps-card">
        <text class="card-title">📖 分步动作要领</text>
        <view class="steps-list">
          <view class="step-item">
            <view class="step-number">1</view>
            <view class="step-content">
              <text class="step-title">起始姿势</text>
              <text class="step-desc">{{ actionSteps.start }}</text>
            </view>
          </view>
          <view class="step-item">
            <view class="step-number">2</view>
            <view class="step-content">
              <text class="step-title">执行过程</text>
              <text class="step-desc">{{ actionSteps.process }}</text>
            </view>
          </view>
          <view class="step-item">
            <view class="step-number">3</view>
            <view class="step-content">
              <text class="step-title">结束姿势</text>
              <text class="step-desc">{{ actionSteps.end }}</text>
            </view>
          </view>
        </view>
      </view>
  
      <!-- 常见错误示例 -->
      <view class="errors-card">
        <text class="card-title">⚠️ 常见错误与纠正</text>
        <view class="errors-list">
          <view class="error-item" v-for="(error, index) in commonErrors" :key="index">
            <view class="error-header">
              <text class="error-icon">❌</text>
              <text class="error-title">{{ error.title }}</text>
            </view>
            <text class="error-desc">{{ error.description }}</text>
            <view class="error-fix">
              <text class="fix-icon">✅</text>
              <text class="fix-text">{{ error.fix }}</text>
            </view>
          </view>
        </view>
      </view>
  
      <!-- 安全注意事项 -->
      <view class="safety-card">
        <text class="card-title">🛡️ 安全注意事项</text>
        <view class="safety-content">
          <text class="safety-text">{{ actionInfo.safety_tips || '请根据自身身体状况调整训练强度，如有不适请立即停止。' }}</text>
        </view>
      </view>
  
      <!-- 底部操作按钮 -->
      <view class="action-bar">
        <button class="btn btn-add-plan" @click="addToPlan">
          <text class="btn-icon">📋</text>
          <text class="btn-text">加入训练计划</text>
        </button>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref, computed} from 'vue'
  import {onShow, onLoad } from '@dcloudio/uni-app'
  import { useUserStore } from '@/store/user'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  // 页面参数
  const actionId = ref('')
  const actionInfo = ref({
    action_id: '',
    name: '',
    action_category: '',
    difficulty_level: '',
    target_muscles: [],
    equipment_id: '',
    equipment_name: '',
    video_demo_url: '',
    image_url: '',
    safety_tips: '',
    estimated_seconds: 0
  })
  
  // 用户信息
  const userStore = useUserStore()
  const userExperienceLevel = ref('初学者')
  
  // 收藏状态
  const isFavorited = ref(false)
  
  // 视频加载状态
  const videoLoaded = ref(false)
  
  // 建议执行参数（根据用户经验水平动态调整）
  const suggestedParams = computed(() => {
    const level = userExperienceLevel.value
    const category = actionInfo.value.action_category
  
    // 根据动作类别和经验水平返回不同参数
    if (category === 'main_strength') {
      // 力量训练
      if (level === '初学者') {
        return { sets: '2-3 组', reps: '8-10 次', rest: '60-90 秒', totalDuration: '5-8 分钟' }
      } else if (level === '中级') {
        return { sets: '3-4 组', reps: '10-12 次', rest: '60-90 秒', totalDuration: '8-12 分钟' }
      } else {
        return { sets: '4-5 组', reps: '12-15 次', rest: '45-60 秒', totalDuration: '12-15 分钟' }
      }
    } else if (category === 'main_cardio') {
      // 有氧训练
      if (level === '初学者') {
        return { sets: '1-2 组', reps: '30-45 秒', rest: '30-45 秒', totalDuration: '3-5 分钟' }
      } else if (level === '中级') {
        return { sets: '2-3 组', reps: '45-60 秒', rest: '30 秒', totalDuration: '5-8 分钟' }
      } else {
        return { sets: '3-4 组', reps: '60-90 秒', rest: '15-30 秒', totalDuration: '8-12 分钟' }
      }
    } else {
      // 热身/拉伸
      if (level === '初学者') {
        return { sets: '1-2 组', reps: '20-30 秒', rest: '15 秒', totalDuration: '2-3 分钟' }
      } else if (level === '中级') {
        return { sets: '2 组', reps: '30 秒', rest: '15 秒', totalDuration: '3-4 分钟' }
      } else {
        return { sets: '2-3 组', reps: '30-45 秒', rest: '15 秒', totalDuration: '4-5 分钟' }
      }
    }
  })
  
  // 分步动作要领（根据动作类别动态生成）
  const actionSteps = computed(() => {
    const category = actionInfo.value.action_category
    const name = actionInfo.value.name
  
    // 根据动作类别返回不同的分步说明
    if (category === 'main_strength') {
      return {
        start: '调整呼吸，收紧核心肌群，保持身体稳定，准备好起始姿势。',
        process: '按照标准动作轨迹缓慢执行，注意目标肌群发力感受，保持动作控制。',
        end: '缓慢回到起始位置，完成一次动作，调整呼吸准备下一次。'
      }
    } else if (category === 'main_cardio') {
      return {
        start: '保持身体直立，核心收紧，准备好开始有氧运动。',
        process: '保持稳定的节奏和呼吸，持续执行动作，注意心率控制。',
        end: '逐渐降低强度，缓慢停止动作，调整呼吸至平稳状态。'
      }
    } else if (category === 'warmup') {
      return {
        start: '放松身体，调整呼吸，准备好开始热身活动。',
        process: '动作幅度由小到大，逐渐激活目标肌群和关节。',
        end: '完成热身后，感受身体温度上升，准备进入正式训练。'
      }
    } else {
      return {
        start: '找到舒适的拉伸姿势，调整呼吸，放松目标肌群。',
        process: '缓慢加深拉伸幅度，感受肌肉拉伸感，保持均匀呼吸。',
        end: '缓慢释放拉伸，轻轻活动目标肌群，完成拉伸动作。'
      }
    }
  })
  
  // 常见错误示例（根据动作类别动态生成）
  const commonErrors = computed(() => {
    const category = actionInfo.value.action_category
  
    if (category === 'main_strength') {
      return [
        {
          title: '动作速度过快',
          description: '利用惯性完成动作，目标肌群发力感不强',
          fix: '放慢动作速度，注重肌肉收缩感受，建议 2-3 秒完成一次动作'
        },
        {
          title: '呼吸不规律',
          description: '憋气或呼吸混乱，影响动作稳定性和力量输出',
          fix: '发力时呼气，还原时吸气，保持呼吸节奏稳定'
        },
        {
          title: '核心未收紧',
          description: '腰部松弛，容易导致腰部代偿和受伤',
          fix: '全程收紧腹部，保持躯干稳定，避免腰部过度弯曲'
        }
      ]
    } else if (category === 'main_cardio') {
      return [
        {
          title: '姿势不正确',
          description: '身体姿态松散，影响训练效果和关节健康',
          fix: '保持核心收紧，身体直立，注意动作标准性'
        },
        {
          title: '强度过大',
          description: '心率过高，无法持续完成训练',
          fix: '根据自身能力调整强度，保持可以说话但不能唱歌的心率水平'
        }
      ]
    } else if (category === 'warmup') {
      return [
        {
          title: '热身时间不足',
          description: '身体未充分激活，容易在正式训练中受伤',
          fix: '保证 5-10 分钟热身时间，直到身体微微出汗'
        },
        {
          title: '动作幅度过大',
          description: '热身阶段过度拉伸，反而影响后续训练',
          fix: '热身动作幅度适中，以激活为主，不要过度拉伸'
        }
      ]
    } else {
      return [
        {
          title: '拉伸时间过短',
          description: '肌肉未充分放松，影响恢复效果',
          fix: '每个拉伸动作保持 20-30 秒，感受肌肉放松'
        },
        {
          title: '拉伸时憋气',
          description: '影响放松效果，可能导致肌肉紧张',
          fix: '拉伸时保持均匀深呼吸，帮助肌肉放松'
        }
      ]
    }
  })
  
  onLoad((options) => {
    actionId.value = options.action_id || ''
    // 从参数获取收藏状态（如果从收藏页面跳转）
    if (options.is_favorited) {
      isFavorited.value = options.is_favorited === 'true'
    }
  })
  
  onShow(async () => {
    if (actionId.value) {
      await loadActionDetail()
      // 获取用户经验水平
      userExperienceLevel.value = userStore.userInfo.experience_level || '初学者'
    }
  })
  
  /**
   * 加载动作详情
   */
  const loadActionDetail = async () => {
    try {
      const res = await request.get(`${API.ACTION_DETAIL}/${actionId.value}`)
      actionInfo.value = res
    } catch (error) {
      console.error('加载动作详情失败:', error)
      uni.showToast({ title: '加载失败', icon: 'none' })
    }
  }
  
  /**
   * 获取视频 URL（处理本地路径）
   */
  const getVideoUrl = (videoUrl) => {
    if (!videoUrl) return ''
    if (videoUrl.startsWith('http://') || videoUrl.startsWith('https://')) {
      return videoUrl
    }
    return 'http://localhost:8000' + videoUrl
  }
  
  /**
   * 获取图片 URL（处理本地路径）
   */
  const getImageUrl = (imageUrl) => {
    if (!imageUrl) return ''
    if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
      return imageUrl
    }
    return 'http://localhost:8000' + imageUrl
  }
  
  /**
   * 视频加载成功
   */
  const onVideoLoaded = () => {
    videoLoaded.value = true
  }
  
  /**
   * 视频加载错误
   */
  const onVideoError = (e) => {
    console.error('视频加载失败:', e)
    videoLoaded.value = true
    uni.showToast({ title: '视频加载失败', icon: 'none' })
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
   * 返回上一页
   */
  const navigateBack = () => {
    uni.navigateBack()
  }
  
  /**
   * 收藏/取消收藏动作
   */
  const toggleFavorite = () => {
    isFavorited.value = !isFavorited.value
  
    const message = isFavorited.value ? '已加入收藏' : '已取消收藏'
    uni.showToast({
      title: message,
      icon: 'none',
      duration: 1500
    })
  
    // 实际项目中应调用收藏接口
    // await request.post(API.ACTION_FAVORITE, {
    //   action_id: actionId.value,
    //   is_favorited: isFavorited.value
    // })
  }
  
  /**
   * 加入训练计划
   */
  const addToPlan = () => {
    uni.showModal({
      title: '加入训练计划',
      content: `确定要将"${actionInfo.value.name}"添加到训练计划吗？`,
      confirmText: '确认',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          // 跳转到训练计划选择页面
          uni.navigateTo({
            url: `/pages/plan/select-plan?action_id=${actionId.value}&action_name=${encodeURIComponent(actionInfo.value.name)}`
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
    padding-bottom: 140rpx;
  }
  
  /* 顶部导航栏 */
  .nav-bar {
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20rpx 30rpx;
    background: #FFFFFF;
    border-bottom: 1rpx solid #E5E5E5;
  
    .nav-back {
      display: flex;
      align-items: center;
  
      .back-icon {
        font-size: 48rpx;
        color: #333333;
        margin-right: 8rpx;
      }
  
      .back-text {
        font-size: 28rpx;
        color: #333333;
      }
    }
  
    .nav-title {
      font-size: 32rpx;
      font-weight: 700;
      color: #333333;
    }
  
    .nav-favorite {
      .favorite-icon {
        font-size: 40rpx;
      }
    }
  }
  
  /* 视频区域 */
  .video-section {
    position: relative;
    width: 100%;
    height: 500rpx;
    background: #000000;
  
    .action-video {
      width: 100%;
      height: 100%;
    }
  
    .video-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      align-items: center;
  
      .loading-text {
        font-size: 28rpx;
        color: #FFFFFF;
      }
    }
  }
  
  /* 基本信息卡片 */
  .info-card {
    background: #FFFFFF;
    margin: 30rpx;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  
    .info-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 30rpx;
  
      .action-name {
        flex: 1;
        font-size: 40rpx;
        font-weight: 700;
        color: #333333;
        margin-right: 20rpx;
        line-height: 1.3;
      }
  
      .badges {
        display: flex;
        flex-direction: column;
        gap: 12rpx;
  
        .badge {
          font-size: 24rpx;
          padding: 8rpx 20rpx;
          border-radius: 20rpx;
          font-weight: 600;
          text-align: center;
  
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
  
    .info-section {
      margin-bottom: 30rpx;
  
      &:last-child {
        margin-bottom: 0;
      }
  
      .section-label {
        display: block;
        font-size: 28rpx;
        font-weight: 600;
        color: #666666;
        margin-bottom: 16rpx;
      }
  
      .muscles-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 16rpx;
  
        .muscle-tag {
          background: #F5F5F5;
          color: #333333;
          font-size: 26rpx;
          padding: 10rpx 24rpx;
          border-radius: 16rpx;
          font-weight: 500;
        }
      }
  
      .equipment-text, .duration-text {
        font-size: 28rpx;
        color: #333333;
        font-weight: 500;
      }
    }
  }
  
  /* 建议执行参数卡片 */
  .params-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 0 30rpx 30rpx;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.3);
  
    .card-title {
      display: block;
      font-size: 32rpx;
      font-weight: 700;
      color: #FFFFFF;
      margin-bottom: 30rpx;
    }
  
    .params-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24rpx;
      margin-bottom: 20rpx;
  
      .param-item {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 16rpx;
        padding: 24rpx;
        text-align: center;
  
        .param-label {
          display: block;
          font-size: 24rpx;
          color: rgba(255, 255, 255, 0.8);
          margin-bottom: 12rpx;
        }
  
        .param-value {
          display: block;
          font-size: 32rpx;
          font-weight: 700;
          color: #FFFFFF;
        }
      }
    }
  
    .params-note {
      display: block;
      font-size: 24rpx;
      color: rgba(255, 255, 255, 0.7);
      text-align: center;
    }
  }
  
  /* 分步动作要领卡片 */
  .steps-card {
    background: #FFFFFF;
    margin: 0 30rpx 30rpx;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  
    .card-title {
      display: block;
      font-size: 32rpx;
      font-weight: 700;
      color: #333333;
      margin-bottom: 30rpx;
    }
  
    .steps-list {
      .step-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 30rpx;
  
        &:last-child {
          margin-bottom: 0;
        }
  
        .step-number {
          width: 56rpx;
          height: 56rpx;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #FFFFFF;
          font-size: 28rpx;
          font-weight: 700;
          border-radius: 50%;
          display: flex;
          justify-content: center;
          align-items: center;
          margin-right: 24rpx;
          flex-shrink: 0;
        }
  
        .step-content {
          flex: 1;
  
          .step-title {
            display: block;
            font-size: 30rpx;
            font-weight: 600;
            color: #333333;
            margin-bottom: 12rpx;
          }
  
          .step-desc {
            display: block;
            font-size: 28rpx;
            color: #666666;
            line-height: 1.6;
          }
        }
      }
    }
  }
  
  /* 常见错误卡片 */
  .errors-card {
    background: #FFFFFF;
    margin: 0 30rpx 30rpx;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  
    .card-title {
      display: block;
      font-size: 32rpx;
      font-weight: 700;
      color: #333333;
      margin-bottom: 30rpx;
    }
  
    .errors-list {
      .error-item {
        background: #FFF5F5;
        border-left: 6rpx solid #F44336;
        border-radius: 16rpx;
        padding: 30rpx;
        margin-bottom: 24rpx;
  
        &:last-child {
          margin-bottom: 0;
        }
  
        .error-header {
          display: flex;
          align-items: center;
          margin-bottom: 16rpx;
  
          .error-icon {
            font-size: 32rpx;
            margin-right: 12rpx;
          }
  
          .error-title {
            font-size: 30rpx;
            font-weight: 600;
            color: #F44336;
          }
        }
  
        .error-desc {
          display: block;
          font-size: 28rpx;
          color: #666666;
          margin-bottom: 20rpx;
          line-height: 1.5;
        }
  
        .error-fix {
          display: flex;
          align-items: flex-start;
          background: #E8F5E9;
          border-radius: 12rpx;
          padding: 20rpx;
  
          .fix-icon {
            font-size: 28rpx;
            margin-right: 12rpx;
            flex-shrink: 0;
          }
  
          .fix-text {
            font-size: 28rpx;
            color: #388E3C;
            line-height: 1.5;
            flex: 1;
          }
        }
      }
    }
  }
  
  /* 安全注意事项卡片 */
  .safety-card {
    background: #FFFFFF;
    margin: 0 30rpx 30rpx;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  
    .card-title {
      display: block;
      font-size: 32rpx;
      font-weight: 700;
      color: #333333;
      margin-bottom: 20rpx;
    }
  
    .safety-content {
      background: #E3F2FD;
      border-left: 6rpx solid #1976D2;
      border-radius: 16rpx;
      padding: 30rpx;
  
      .safety-text {
        display: block;
        font-size: 28rpx;
        color: #1565C0;
        line-height: 1.8;
      }
    }
  }
  
  /* 底部操作按钮 */
  .action-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #FFFFFF;
    padding: 30rpx;
    border-top: 1rpx solid #E5E5E5;
    box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.08);
  
    .btn {
      width: 100%;
      height: 96rpx;
      border-radius: 48rpx;
      border: none;
      font-size: 32rpx;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16rpx;
  
      .btn-icon {
        font-size: 36rpx;
      }
  
      .btn-text {
        line-height: 1;
      }
  
      &.btn-add-plan {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: #FFFFFF;
        box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
      }
    }
  }
  </style>