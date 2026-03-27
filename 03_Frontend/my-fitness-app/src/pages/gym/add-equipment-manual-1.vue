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
        >
        <view class="image-wrapper">
          <image 
            :src="'/static/' + item.image_url" 
            class="equipment-image"
            mode="aspectFill"
            lazy-load
          />
          <!-- 图片加载失败时的备用显示 -->
          <view class="image-placeholder" v-if="!item.image_url">
            <text class="placeholder-icon">🏋️</text>
          </view>
        </view>

          <view class="equipment-info">
            <text class="item-name">{{ item.name }}</text>
            <text class="item-category">{{ item.category }}</text>
          </view>
          
          <view class="button-group">
            <button class="select-btn" @click="selectEquipment(item)">选择</button>
            <button class="add-btn" @click="addEquipmentToGym(item)">添加</button>
          </view>
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
      console.log('搜索结果:', searchResults.value)
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
      url: `/pages/gym/add-equipment-manual-2?inventory_id=${inventoryId.value}&equipment_id=${equipment.equipment_id}` 
    })
  }

  /**
   * 添加器材到健身房
   */
  const addEquipmentToGym = async (equipment) => {
    //loading.value = true
    
    try {
      console.log('添加器材:', equipment) 
      console.log('健身房ID:', inventoryId.value)
      console.log('器材ID:', equipment.equipment_id)
      await request.post(`${API.EQUIPMENT_ADD_MANUAL}/${inventoryId.value}/manual`, {
        inventory_id: inventoryId.value,
        equipment_id: equipment.equipment_id
      })
      
      uni.showToast({ title: '添加成功', icon: 'success' })
      
      /*setTimeout(() => {
        uni.navigateBack({ delta: 1 })
      }, 1000)*/
    } catch (error) {
      console.error('添加失败:', error)
    } finally {
      //loading.value = false
    }
  }
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: $fitness-primary;
  padding: 30rpx $size-5;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: $size-5;
  padding: 20rpx 30rpx;
  margin-bottom: 30rpx;
  border: 1rpx solid $divider-ios; // iOS风格边框

  
  .search-input {
    flex: 1;
    font-size: $font-md;
    padding: 10rpx 0;
  }
  
  .search-btn {
    padding: 10rpx 20rpx;
    
    .search-icon {
      font-size: $size-4;
    }
  }
}

.search-results {
  .result-item {
    background:$fitness-secondary;
    border-radius: $radius-md;
    padding: 30rpx;
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;
    
    // 图片区域样式
    .image-wrapper {
      position: relative;
      width: 160rpx;
      height: 160rpx;
      margin-right: 20rpx;
      flex-shrink: 0;
      
      .equipment-image {
        width: 100%;
        height: 100%;
        border-radius: $radius-sm;
        background: #F5F5F5;
      }
      
      .image-placeholder {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #F5F5F5;
        border-radius: $radius-sm;
        display: flex;
        justify-content: center;
        align-items: center;
        
        .placeholder-icon {
          font-size: 60rpx;
        }
      }
    }
    
    .equipment-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    
    .button-group {
      display: flex;
      flex-direction: column;
      gap: 15rpx;
      
      .select-btn {
        background: $fitness-secondary;
        color: $fitness-text;
        border: none;
        border-radius: $radius-sm;
        font-size: $font-md;
        padding: 15rpx 20rpx;
        margin: 0;
        width: auto;
        height: auto;
      }
      
      .add-btn {
        background: $uni-primary;
        color: white;
        border: none;
        border-radius: $radius-sm;
        font-size: $font-md;
        padding: 15rpx 20rpx;
        margin: 0;
        width: auto;
        height: auto;
      }
    }
    
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
  padding: 100rpx $size-5;
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