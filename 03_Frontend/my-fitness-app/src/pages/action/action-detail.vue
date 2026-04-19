<template>
  <view class="container">
    <view class="video-section">
      <view class="poster-wrapper" v-if="!isVideoPlaying" @click="playVideo">
        <image
          v-if="actionInfo.image_url"
          :src="'/static/action/' + actionInfo.image_url"
          class="poster-image"
          mode="aspectFill"
        />
        <view class="play-btn">
          <text class="play-icon">▶</text>
        </view>
      </view>
      <video
        v-else
        :src="'/static/action/' + actionInfo.video_demo_url"
        class="action-video"
        :autoplay="true"
        :show-play-btn="true"
        :enable-progress-gesture="true"
        @error="onVideoError"
      />
    </view>

    <view class="info-card">
      <view class="info-header">
        <text class="action-name">{{ actionInfo.name }}</text>
        <view class="header-actions">
          <view class="favorite-btn" @click="toggleFavorite">
            <text class="favorite-icon">{{ isFavorited ? '❤️' : '🤍' }}</text>
          </view>
        </view>
      </view>
      <view class="badges">
        <text class="badge difficulty" :class="getDifficultyClass(actionInfo.difficulty_level)">
          {{ actionInfo.difficulty_level }}
        </text>
        <text class="badge category" :class="getCategoryClass(actionInfo.action_category)">
          {{ getCategoryText(actionInfo.action_category) }}
        </text>
      </view>

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

      <view class="info-section" v-if="actionInfo.equipment_name">
        <text class="section-label">🏋️ 所需器材</text>
        <text class="equipment-text">{{ actionInfo.equipment_name }}</text>
      </view>

      <view class="info-section" v-if="actionInfo.estimated_seconds">
        <text class="section-label">⏱️ 单次时长</text>
        <text class="duration-text">{{ formatDuration(actionInfo.estimated_seconds) }}</text>
      </view>
    </view>

    <view class="keypoints-card">
      <text class="card-title">🎯 动作要点</text>
      <view class="keypoints-content">
        <text class="keypoint-text" v-for="(item, index) in keypointItems" :key="index">{{ item }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import {onShow, onLoad, onBackPress } from '@dcloudio/uni-app'
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
  
  // 收藏状态
  const isFavorited = ref(false)
  const isVideoPlaying = ref(false)
  const videoLoaded = ref(false)

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
    }
  })
  
  /**
   * 加载动作详情
   */
  const playVideo = () => {
    isVideoPlaying.value = true
  }

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
   * 收藏/取消收藏动作
   */
  const keypointItems = computed(() => {
    const text = actionInfo.value.safety_tips || '请根据自身身体状况调整训练强度，如有不适请立即停止。'
    const parts = text.split('·')
    return parts.filter(p => p.trim()).map((part, index) => {
      if (index === 0) return part.trim()
      return '·' + part.trim()
    })
  })

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
  
  </script>
  
<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: #FFFFFF;
  padding-bottom: 140rpx;
  font-family: Manrope;
}

.video-section {
  position: relative;
  width: 100%;
  height: 500rpx;
  background: #000000;

  .poster-wrapper {
    position: relative;
    width: 100%;
    height: 100%;

    .poster-image {
      width: 100%;
      height: 100%;
    }

    .play-btn {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 120rpx;
      height: 120rpx;
      background: rgba(0, 0, 0, 0.5);
      border-radius: 50%;
      display: flex;
      justify-content: center;
      align-items: center;

      &:active {
        background: rgba(0, 0, 0, 0.7);
      }

      .play-icon {
        font-size: 48rpx;
        color: #FFFFFF;
        margin-left: 6rpx;
      }
    }
  }

  .action-video {
    width: 100%;
    height: 100%;
  }
}

.info-card {
  background: rgba(252, 249, 248, 0.7);
  margin: $size-4;
  border-radius: $size-4;
  padding: $size-5;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);

  .info-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: $size-3;

    .action-name {
      flex: 1;
      font-size: $size-5;
      font-weight: 700;
      color: $fitness-text;
      margin-right: $size-3;
      line-height: 1.3;
    }

    .header-actions {
      display: flex;
      gap: $size-2;

      .favorite-btn {
        width: 56rpx;
        height: 56rpx;
        display: flex;
        justify-content: center;
        align-items: center;
        background: rgba(251, 231, 231, 0.5);
        border-radius: $size-2;

        .favorite-icon {
          font-size: 36rpx;
        }
      }
    }
  }

  .badges {
    display: flex;
    gap: $size-2;
    margin-bottom: $size-4;

    .badge {
      font-size: $size-3;
      padding: $size-1 $size-3;
      border-radius: $size-2;
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

  .info-section {
    margin-bottom: $size-4;

    &:last-child {
      margin-bottom: 0;
    }

    .section-label {
      display: block;
      font-size: $size-4;
      font-weight: 600;
      color: $color-label;
      margin-bottom: $size-2;
    }

    .muscles-tags {
      display: flex;
      flex-wrap: wrap;
      gap: $size-2;

      .muscle-tag {
        background: $fitness-secondary;
        color: $fitness-text;
        font-size: $size-3;
        padding: $size-1 $size-4;
        border-radius: $size-2;
        font-weight: 500;
      }
    }

    .equipment-text, .duration-text {
      font-size: $size-4;
      color: $fitness-text;
      font-weight: 500;
    }
  }
}

.keypoints-card {
  background: rgba(252, 249, 248, 0.7);
  margin: 0 $size-4 $size-4;
  border-radius: $size-4;
  padding: $size-5;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);

  .card-title {
    display: block;
    font-size: $size-5;
    font-weight: 700;
    color: $fitness-text;
    margin-bottom: $size-3;
  }

  .keypoints-content {
    background: rgba(251, 231, 231, 0.5);
    border-left: 6rpx solid $color-primary;
    border-radius: $size-2;
    padding: $size-4;

    .keypoint-text {
      display: block;
      font-size: $size-4;
      color: $color-primary;
      line-height: 1.6;
    }
  }
}
</style>
