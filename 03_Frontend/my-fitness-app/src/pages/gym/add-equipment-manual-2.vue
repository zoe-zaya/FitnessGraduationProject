<template>
  <view class="page">
    <view class="loading-state" v-if="pageLoading">
      <view class="loading-spinner" />
      <text class="loading-text">加载中...</text>
    </view>

    <view v-else class="page-content">
      <scroll-view scroll-y class="scroll-area">
        <view class="hero-image-section">
          <image :src="'/static/' + equipmentImageUrl" class="hero-image" mode="aspectFit" />
          <view class="hero-gradient" />
        </view>

        <view class="content-body">
          <view class="glass-card info-card">
            <view class="info-header">
              <text class="equipment-name">{{ equipmentName }}</text>
              <text class="equipment-category">{{ equipmentCategory }}</text>
            </view>
            <view class="info-desc" v-if="equipmentDescription">
              <text class="desc-text">{{ equipmentDescription }}</text>
            </view>
          </view>

          <view class="glass-card muscles-card" v-if="targetMuscles && targetMuscles.length > 0">
            <text class="card-label">目标肌群</text>
            <view class="muscles-tags">
              <text class="muscle-tag" v-for="(muscle, index) in targetMuscles" :key="index">
                {{ muscle }}
              </text>
            </view>
          </view>

          <view class="glass-card actions-card" v-if="relatedActions && relatedActions.length > 0">
            <view class="card-label-row">
              <text class="card-label">相关动作</text>
              <text class="actions-count">{{ actionsCount }}个</text>
            </view>
            <view class="actions-list">
              <view class="action-item" v-for="action in displayedActions" :key="action.action_id" @click="navigateToActionDetail(action.action_id)">
                <view class="action-image-wrapper">
                  <image
                    v-if="action.image_url"
                    :src="'/static/action/' + action.image_url"
                    class="action-image"
                    mode="aspectFill"
                    lazy-load
                  />
                  <view class="action-image-placeholder" v-else>
                    <text class="placeholder-icon">🏋️</text>
                  </view>
                </view>
                <view class="action-content">
                  <view class="action-row">
                    <text class="action-name">{{ action.name }}</text>
                    <text class="action-badge" :class="getDifficultyClass(action.difficulty_level)">
                      {{ action.difficulty_level }}
                    </text>
                  </view>
                  <view class="action-muscles" v-if="action.target_muscles && action.target_muscles.length > 0">
                    <text class="action-muscles-text">{{ action.target_muscles.join('、') }}</text>
                  </view>
                </view>
              </view>
            </view>
            <view class="expand-area" v-if="showExpandToggle" @click="toggleActionsExpand">
              <text class="expand-text">{{ isActionsExpanded ? '收起' : '展开全部' }}</text>
              <text class="expand-arrow" :class="{ 'arrow-up': isActionsExpanded }">▼</text>
            </view>
          </view>

          <view class="glass-card empty-card" v-else>
            <text class="card-label">相关动作</text>
            <text class="empty-text">暂无相关动作</text>
          </view>

          <view class="bottom-spacer" />
        </view>
      </scroll-view>

      <view class="fixed-footer">
        <button class="confirm-btn" @click="confirmAdd" :loading="loading" :disabled="loading">
          {{ loading ? '添加中...' : '确认添加到我的健身房' }}
        </button>
        <button class="cancel-btn" @click="handleCancel" :disabled="loading">
          取消
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API } from '@/utils/constants'

const PREVIEW_COUNT = 3

const inventoryId = ref('')
const equipmentId = ref('')
const equipmentName = ref('')
const equipmentCategory = ref('')
const equipmentDescription = ref('')
const equipmentImageUrl = ref('')
const actionsCount = ref(0)
const relatedActions = ref([])
const targetMuscles = ref([])
const loading = ref(false)
const pageLoading = ref(true)
const isActionsExpanded = ref(false)

const displayedActions = computed(() => {
  if (isActionsExpanded.value || relatedActions.value.length <= PREVIEW_COUNT) {
    return relatedActions.value
  }
  return relatedActions.value.slice(0, PREVIEW_COUNT)
})

const showExpandToggle = computed(() => {
  return relatedActions.value.length > PREVIEW_COUNT
})

onLoad((options) => {
  inventoryId.value = options.inventory_id || ''
  equipmentId.value = options.equipment_id || ''

  if (!equipmentId.value) {
    uni.showToast({ title: '参数错误，缺少器材ID', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1500)
    return
  }

  loadEquipmentDetail()
})

const loadEquipmentDetail = async () => {
  pageLoading.value = true
  try {
    const res = await request.get(`${API.EQUIPMENT_DETAIL}/${equipmentId.value}`)
    equipmentName.value = res.name
    equipmentCategory.value = res.category
    equipmentDescription.value = res.description
    equipmentImageUrl.value = res.image_url
    actionsCount.value = res.supported_actions_count
    relatedActions.value = res.supported_actions
    targetMuscles.value = res.target_muscles
  } catch (error) {
    console.error('加载设备详情失败:', error)
    uni.showToast({ title: '加载失败，请重试', icon: 'none' })
  } finally {
    pageLoading.value = false
  }
}

const toggleActionsExpand = () => {
  isActionsExpanded.value = !isActionsExpanded.value
}

const getDifficultyClass = (difficulty) => {
  switch (difficulty) {
    case '初级': return 'difficulty-beginner'
    case '中级': return 'difficulty-intermediate'
    case '高级': return 'difficulty-advanced'
    default: return ''
  }
}

const confirmAdd = async () => {
  if (!inventoryId.value || !equipmentId.value) {
    uni.showToast({ title: '参数错误', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await request.post(`${API.EQUIPMENT_ADD_MANUAL}/${inventoryId.value}/manual`, {
      inventory_id: inventoryId.value,
      equipment_id: equipmentId.value
    })
    uni.showToast({ title: '添加成功', icon: 'success' })
    setTimeout(async () => {
      await handleCancel()
    }, 1500)
  } catch (error) {
    console.error('添加失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  uni.navigateTo({ url: `/pages/gym/equipment-list?inventory_id=${inventoryId.value}` })
}

const navigateToActionDetail = (actionId) => {
  uni.navigateTo({ url: `/pages/action/action-detail?action_id=${actionId}` })
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.page {
  min-height: 100vh;
  background: #FFFFFF;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
}

.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;

  .loading-spinner {
    width: $size-8;
    height: $size-8;
    border: 6rpx solid rgba(160, 62, 64, 0.2);
    border-top-color: $color-primary;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: $size-3;
  }

  .loading-text {
    font-size: $size-4;
    font-weight: 525;
    color: $color-label;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.scroll-area {
  flex: 1;
}

.hero-image-section {
  position: relative;
  width: 100%;
  height: 440rpx;
  background: #FFFFFF;

  .hero-image {
    width: 100%;
    height: 100%;
  }

  .hero-gradient {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 80rpx;
    background: linear-gradient(to top, #FFFFFF, transparent);
  }
}

.content-body {
  padding: 0 $size-5;
  margin-top: -$size-6;
  position: relative;
  z-index: 1;
}

.glass-card {
  background: $glass-bg1;
  border-radius: $size-4;
  padding: $size-6;
  margin-bottom: $size-4;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
  border: 2rpx solid $fitness-border;
}

.info-card {
  .info-header {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: $size-2;
    margin-bottom: $size-4;

    .equipment-name {
      font-size: $size-10;
      font-weight: 700;
      color: $color-input;
      line-height: 1.2;
    }

    .equipment-category {
      font-size: $size-3;
      color: $color-primary;
      padding: $size-1 $size-2;
      background: $color-primary-light;
      border-radius: 20rpx;
      font-weight: 500;
      border: 1rpx solid $color-primary;
      line-height: 1;
    }
  }

  .info-desc {
    .desc-text {
      font-size: $size-4;
      color: $color-label;
      line-height: 1.625;
      text-align: justify;
    }
  }
}

.muscles-card {
  .card-label {
    display: block;
    font-size: $size-3;
    font-weight: 700;
    color: rgba(160, 62, 64, 0.6);
    letter-spacing: 1rpx;
    text-transform: uppercase;
    margin-bottom: $size-3;
  }

  .muscles-tags {
    display: flex;
    flex-wrap: wrap;
    gap: $size-2;

    .muscle-tag {
      background: $fitness-secondary;
      color: $color-input;
      font-size: 28rpx;
      font-weight: 600;
      padding: $size-2 $size-3;
      border-radius: $size-3;
      line-height: 1.25;
    }
  }
}

.actions-card {
  .card-label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $size-3;

    .card-label {
      font-size: $size-3;
      font-weight: 700;
      color: rgba(160, 62, 64, 0.6);
      letter-spacing: 1rpx;
      text-transform: uppercase;
    }

    .actions-count {
      font-size: $size-3;
      color: $color-secondory;
      font-weight: 500;
    }
  }

  .actions-list {
    .action-item {
      display: flex;
      align-items: center;
      padding: $size-4 0;
      border-bottom: 1rpx solid $fitness-border;

      &:first-child {
        padding-top: 0;
      }

      &:last-child {
        border-bottom: none;
        padding-bottom: 0;
      }

      .action-image-wrapper {
        width: 96rpx;
        height: 96rpx;
        border-radius: $size-3;
        overflow: hidden;
        flex-shrink: 0;
        margin-right: $size-3;
        background: $fitness-secondary;

        .action-image {
          width: 100%;
          height: 100%;
        }

        .action-image-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;

          .placeholder-icon {
            font-size: $size-6;
          }
        }
      }

      .action-content {
        flex: 1;
        min-width: 0;

        .action-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: $size-1;

          .action-name {
            font-size: $size-4;
            font-weight: 600;
            color: $color-input;
            flex: 1;
            margin-right: $size-3;
            line-height: 1.3;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .action-badge {
            font-size: 24rpx;
            padding: 4rpx $size-2;
            border-radius: $size-2;
            font-weight: 500;
            flex-shrink: 0;

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
        }

        .action-muscles {
          .action-muscles-text {
            font-size: $size-3;
            color: $color-label;
            line-height: 1.4;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
      }
    }
  }

  .expand-area {
    display: flex;
    justify-content: center;
    align-items: center;
    padding-top: $size-4;
    margin-top: $size-2;
    border-top: 1rpx solid $fitness-border;
    gap: $size-1;

    &:active {
      opacity: 0.7;
    }

    .expand-text {
      font-size: $size-3;
      color: $color-primary;
      font-weight: 700;
    }

    .expand-arrow {
      font-size: 20rpx;
      color: $color-primary;
      transition: transform 0.3s ease;

      &.arrow-up {
        transform: rotate(180deg);
      }
    }
  }
}

.empty-card {
  .card-label {
    display: block;
    font-size: $size-3;
    font-weight: 700;
    color: rgba(160, 62, 64, 0.6);
    letter-spacing: 1rpx;
    text-transform: uppercase;
    margin-bottom: $size-3;
  }

  .empty-text {
    font-size: $size-4;
    color: $color-secondory;
    text-align: center;
    display: block;
    padding: $size-4 0;
  }
}

.bottom-spacer {
  height: 240rpx;
}

.fixed-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #FFFFFF;
  padding: $size-4 $size-5;
  padding-bottom: calc(#{$size-4} + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.08);
  z-index: 100;

  .confirm-btn {
    height: $size-12;
    width: 100%;
    background: $button-bg2;
    color: #FFFFFF;
    font-size: $size-4;
    font-weight: 700;
    border-radius: $size-4;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;

    &:active {
      opacity: 0.9;
    }

    &[disabled] {
      opacity: 0.6;
    }

    &::after {
      border: none;
    }
  }

  .cancel-btn {
    height: 80rpx;
    width: 100%;
    margin-top: $size-2;
    background: transparent;
    color: $color-secondory;
    font-size: $size-3;
    font-weight: 500;
    border-radius: $size-4;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;

    &::after {
      border: none;
    }

    &:active {
      opacity: 0.7;
    }

    &[disabled] {
      opacity: 0.6;
    }
  }
}
</style>
