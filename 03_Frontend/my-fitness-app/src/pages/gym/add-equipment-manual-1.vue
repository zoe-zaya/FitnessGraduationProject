<template>
    <view class="container">
      <!-- 搜索栏 -->
      <view class="search-bar">
        <input 
          v-model="keyword" 
          type="text" 
          placeholder="搜索器材名称或分类"
          class="search-input"
          @confirm="searchEquipment"
        />
        <view class="search-btn" @click="searchEquipment">
          <text class="search-icon">🔍</text>
        </view>
      </view>
      
      <!-- 搜索结果 -->
      <view class="search-results" v-if="searchResults.length > 0">
        <view 
          class="result-item" 
          v-for="(item, index) in searchResults" 
          :key="item.equipment_id"
          @click="selectEquipment(item)"
        >
          <text class="item-name">{{ item.name }}</text>
          <text class="item-category">{{ item.category }}</text>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-else-if="hasSearched">
        <text class="empty-text">未找到匹配的器材</text>
        <text class="empty-subtext">请尝试其他关键词</text>
      </view>
      
      <!-- 默认提示 -->
      <view class="default-tip" v-else>
        <text class="tip-text">输入关键词搜索器材</text>
        <text class="tip-subtext">如"哑铃"、"跑步机"、"有氧器械"</text>
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
  
  onLoad((options) => {
    inventoryId.value = options.inventory_id || ''
  })
  
  /**
   * 搜索器材
   */
  const searchEquipment = async () => {
    if (!keyword.value || keyword.value.trim().length === 0) {
      uni.showToast({ title: '请输入搜索关键词', icon: 'none' })
      return
    }
    
    try {
      const res = await request.get(`${API.EQUIPMENT_SEARCH}?keyword=${keyword.value}`)
      searchResults.value = res
      hasSearched.value = true
    } catch (error) {
      console.error('搜索失败:', error)
      searchResults.value = []
      hasSearched.value = true
    }
  }
  
  /**
   * 选择器材
   */
  const selectEquipment = (equipment) => {
    uni.navigateTo({ 
      url: `/pages/gym/add-equipment-manual-2?inventory_id=${inventoryId.value}&equipment_id=${equipment.equipment_id}&name=${equipment.name}` 
    })
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: $fitness-primary;
    padding: 30rpx 40rpx;
  }
  
  .search-bar {
    display: flex;
    align-items: center;
    background: #FFFFFF;
    border-radius: 40rpx;
    padding: 20rpx 30rpx;
    margin-bottom: 30rpx;
    
    .search-input {
      flex: 1;
      font-size: $font-md;
      padding: 10rpx 0;
    }
    
    .search-btn {
      padding: 10rpx 20rpx;
      
      .search-icon {
        font-size: 32rpx;
      }
    }
  }
  
  .search-results {
    .result-item {
      background: #FFFFFF;
      border-radius: $radius-md;
      padding: 30rpx;
      margin-bottom: 20rpx;
      
      .item-name {
        display: block;
        font-size: $font-lg;
        font-weight: bold;
        color: $fitness-text;
        margin-bottom: 10rpx;
      }
      
      .item-category {
        display: block;
        font-size: $font-sm;
        color: $uni-primary;
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
    
    .empty-text, .tip-text {
      font-size: $font-lg;
      color: $fitness-text-light;
      margin-bottom: 10rpx;
    }
    
    .empty-subtext, .tip-subtext {
      font-size: $font-sm;
      color: $fitness-text-gray;
    }
  }
  </style>