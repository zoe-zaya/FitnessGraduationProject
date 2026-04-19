<template>
  <view class="container">
    <view class="search-bar" :class="{ 'search-bar-focus': isSearchFocused }">
      <image src="/static/search.png" class="search-icon-left" mode="aspectFit" />
      <input
        v-model="keyword"
        type="text"
        placeholder="搜索器材名称或分类"
        placeholder-class="search-placeholder"
        class="search-input"
        :focus="isSearchFocused"
        @focus="onSearchFocus"
        @blur="onSearchBlur"
        @confirm="searchEquipment"
      />
      <view class="search-btn" @click="searchEquipment">
        <text class="search-btn-text">搜索</text>
      </view>
    </view>

    <view class="search-results" v-if="searchResults.length > 0">
      <view
        class="result-item"
        v-for="item in searchResults"
        :key="item.equipment_id"
        @click="selectEquipment(item)"
      >
        <view class="image-wrapper">
          <image
            v-if="item.image_url"
            :src="'/static/' + item.image_url"
            class="equipment-image"
            mode="aspectFill"
            lazy-load
          />
          <view class="image-placeholder" v-else>
            <text class="placeholder-icon">🏋️</text>
          </view>
        </view>

        <view class="equipment-info">
          <text class="item-name">{{ item.name }}</text>
          <text class="item-category">{{ item.category }}</text>
        </view>

        <view class="add-btn" @click.stop="addEquipmentToGym(item)">
          <image src="/static/add.png" class="add-icon" mode="aspectFit" />
        </view>
      </view>
    </view>

    <view class="empty-state" v-else-if="hasSearched">
      <image src="/static/empty-data.png" class="empty-image" mode="aspectFit" />
      <text class="empty-text">未找到匹配的器材</text>
      <text class="empty-subtext">请尝试其他关键词</text>
    </view>

    <view class="default-tip" v-else>
      <image src="/static/empty-data.png" class="default-image" mode="aspectFit" />
      <text class="tip-text">输入关键词搜索器材</text>
      <text class="tip-subtext">如"哑铃"、"跑步机"、"有氧器械"</text>
    </view>

    <view class="loading-mask" v-if="loading">
      <view class="loading-spinner" />
      <text class="loading-text">搜索中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API } from '@/utils/constants'

const inventoryId = ref('')
const keyword = ref('')
const searchResults = ref([])
const hasSearched = ref(false)
const loading = ref(false)
const isSearchFocused = ref(false)

onLoad((options) => {
  inventoryId.value = options.inventory_id || ''
})

const onSearchFocus = () => {
  isSearchFocused.value = true
}

const onSearchBlur = () => {
  isSearchFocused.value = false
}

const searchEquipment = async () => {
  if (!keyword.value || keyword.value.trim().length === 0) {
    uni.showToast({ title: '请输入搜索关键词', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res = await request.get(`${API.EQUIPMENT_SEARCH}?keyword=${keyword.value}`)
    searchResults.value = res
    hasSearched.value = true
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
    hasSearched.value = true
  } finally {
    loading.value = false
  }
}

const selectEquipment = (equipment) => {
  uni.navigateTo({
    url: `/pages/gym/add-equipment-manual-2?inventory_id=${inventoryId.value}&equipment_id=${equipment.equipment_id}`
  })
}

const addEquipmentToGym = async (equipment) => {
  loading.value = true
  try {
    await request.post(`${API.EQUIPMENT_ADD_MANUAL}/${inventoryId.value}/manual`, {
      inventory_id: inventoryId.value,
      equipment_id: equipment.equipment_id
    })
    uni.showToast({ title: '添加成功', icon: 'success' })
  } catch (error) {
    console.error('添加失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: #FFFFFF;
  padding: $size-3 $size-5;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  position: relative;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: $size-4;
  padding: 0 $size-3;
  margin-bottom: $size-3;
  height: $size-12;
  border: 2rpx solid rgba(160, 62, 64, 0.1);
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  .search-icon-left {
    width: $size-5;
    height: $size-5;
    margin-right: $size-2;
    flex-shrink: 0;
    opacity: 0.5;
  }

  .search-input {
    flex: 1;
    font-size: $size-4;
    color: $color-input;
    height: 100%;
  }

  .search-placeholder {
    color: $color-secondory;
    font-size: $size-4;
  }

  .search-btn {
    flex-shrink: 0;
    transition: all 0.2s ease;

    &:active {
      transform: scale(0.95);
      opacity: 0.9;
    }

    .search-btn-text {
      font-size: $size-4;
      font-weight: 700;
      color: $button-bg2;
      line-height: 1.2;
    }
  }
}

.search-bar-focus {
  border-color: rgba(160, 62, 64, 0.4);
  box-shadow: 0 2rpx 16rpx rgba(160, 62, 64, 0.15);
}

.search-results {
  .result-item {
    background: $glass-bg1;
    border: 2rpx solid $fitness-border;
    border-radius: $size-4;
    padding: $size-3;
    margin-bottom: $size-3;
    display: flex;
    align-items: center;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
    transition: all 0.2s ease;

    &:active {
      transform: scale(0.98);
      box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.08);
    }

    .image-wrapper {
      position: relative;
      width: 160rpx;
      height: 160rpx;
      margin-right: $size-4;
      flex-shrink: 0;

      .equipment-image {
        width: 100%;
        height: 100%;
        border-radius: $size-4;
        background: $fitness-secondary;
      }

      .image-placeholder {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: $fitness-secondary;
        border-radius: $size-4;
        display: flex;
        justify-content: center;
        align-items: center;

        .placeholder-icon {
          font-size: $size-8;
        }
      }
    }

    .equipment-info {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;

      .item-name {
        display: block;
        font-size: $size-4;
        font-weight: 700;
        color: $color-input;
        margin-bottom: $size-2;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.3;
      }

      .item-category {
        display: block;
        font-size: $size-3;
        font-weight: 700;
        color: $color-primary;
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .add-btn {
      width: $size-8;
      height: $size-8;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-left: $size-2;
      flex-shrink: 0;
      transition: all 0.2s ease;

      &:active {
        transform: scale(0.9);
        opacity: 0.7;
      }

      .add-icon {
        width: $size-8;
        height: $size-8;
      }
    }
  }
}

.empty-state,
.default-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx $size-5;
  text-align: center;

  .empty-image,
  .default-image {
    width: 400rpx;
    height: 300rpx;
    margin-bottom: $size-5;
  }

  .empty-text,
  .tip-text {
    font-size: $size-4;
    font-weight: 700;
    color: $color-input;
    margin-bottom: $size-2;
    line-height: 1.3;
  }

  .empty-subtext,
  .tip-subtext {
    font-size: $size-3;
    font-weight: 525;
    color: $color-secondory;
    line-height: 1.4;
  }
}

.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;

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
    font-size: $size-3;
    font-weight: 525;
    color: $color-label;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
