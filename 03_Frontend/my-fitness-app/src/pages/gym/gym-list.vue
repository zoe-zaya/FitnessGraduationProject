<template>
  <view class="container">    
    <!-- 健身房列表 -->
    <view class="gym-list" v-if="gymList.length > 0">
      <view 
        class="gym-card" 
        v-for="(gym, index) in gymList" 
        :key="gym.inventory_id"
        @click="navigateToEquipmentList(gym.inventory_id)"
      >
        <view class="gym-info">
          <text class="gym-name">{{ gym.location_tag }}</text>
            <text class="gym-desc">{{ gym.description ? (gym.description.length > 20 ? gym.description.substring(0, 20) + '...' : gym.description) : '暂无描述' }}</text>
          <text class="gym-meta">
            {{ gym.equipment_count }} 个器材 · {{ formatDate(gym.create_time) }}
          </text>
        </view>
        <view class="gym-actions">
          <view class="action-btn edit" @click.stop="openEditDialog(gym)">
            <text class="action-icon">✏️</text>
          </view>
          <view class="action-btn delete" @click.stop="confirmDelete(gym)">
            <text class="action-icon">🗑️</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 空状态提示 -->
    <view class="empty-state" v-else>
      <image src="/static/empty-gym.png" class="empty-image" mode="aspectFit" />
      <text class="empty-text">暂无健身房</text>
      <text class="empty-subtext">点击下方按钮添加您的第一个健身房</text>
    </view>
    
    <!-- 添加健身房弹窗 -->
    <view class="dialog-mask" v-if="showAddDialog" @click="closeAddDialog">
      <view class="dialog-content" @click.stop>
        <text class="dialog-title">添加健身房</text>
        
        <view class="form-item">
          <text class="form-label">健身房名称 *</text>
          <textarea 
            v-model="addForm.location_tag" 
            placeholder="如：家附近健身房"
            class="form-input"
            maxlength="10"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">描述信息</text>
          <textarea 
            v-model="addForm.description" 
            placeholder="可选：24 小时营业，器械较新等"
            class="form-textarea"
            maxlength="200"
          />
        </view>
        
        <view class="dialog-buttons">
          <button class="btn-cancel" @click="closeAddDialog">取消</button>
          <button class="btn-confirm" @click="handleAddGym" :loading="addLoading">确认</button>
        </view>
      </view>
    </view>
    
    <!-- 编辑健身房弹窗 -->
    <view class="dialog-mask" v-if="showEditDialog" @click="closeEditDialog">
      <view class="dialog-content" @click.stop>
        <text class="dialog-title">编辑健身房</text>
        
        <view class="form-item">
          <text class="form-label">健身房名称 *</text>
          <textarea 
            v-model="editForm.location_tag" 
            type="text" 
            placeholder="请输入健身房名称"
            class="form-input"
            maxlength="10"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">描述信息</text>
          <textarea 
            v-model="editForm.description" 
            placeholder="可选：24 小时营业，器械较新等"
            class="form-textarea"
            maxlength="200"
          />
        </view>
        
        <view class="dialog-buttons">
          <button class="btn-cancel" @click="closeEditDialog">取消</button>
          <button class="btn-confirm" @click="handleEditGym" :loading="editLoading">确认</button>
        </view>
      </view>
    </view>
    
    <!-- 右下角悬浮添加按钮 -->
    <img src="/static/add.png" 
      class="fab-button" 
      mode="aspectFit" 
      @click="showAddDialog = true">
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import { API } from '@/utils/constants'

const userStore = useUserStore()
const gymList = ref([])
const loading = ref(false)

// 弹窗控制
const showAddDialog = ref(false)
const showEditDialog = ref(false)

// 加载状态
const addLoading = ref(false)
const editLoading = ref(false)

// 添加表单
const addForm = ref({
  location_tag: '',
  description: ''
})

// 编辑表单
const editForm = ref({
  inventory_id: '',
  location_tag: '',
  description: ''
})

/**
 * 页面显示时加载健身房列表
 */
onShow(async () => {
  if (userStore.isLogin) {
    await loadGymList()
  }
})

/**
 * 加载健身房列表
 */
const loadGymList = async () => {
  loading.value = true
  try {
    const res = await request.get(API.GYM_LIST)
    gymList.value = res
  } catch (error) {
    console.error('加载健身房列表失败:', error)
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
 * 跳转至器材清单页面
 */
const navigateToEquipmentList = (inventoryId) => {
  uni.navigateTo({ url: `/pages/gym/equipment-list?inventory_id=${inventoryId}` })
}

// ==================== 添加健身房 ====================

/**
 * 关闭添加弹窗
 */
const closeAddDialog = () => {
  showAddDialog.value = false
  addForm.value = {
    location_tag: '',
    description: ''
  }
}

/**
 * 处理添加健身房
 * 对应《需求规格说明书》3.2 节管理健身房用例
 */
const handleAddGym = async () => {
  // 1. 验证健身房名称
  if (!addForm.value.location_tag || addForm.value.location_tag.trim().length === 0) {
    uni.showToast({ title: '请输入健身房名称', icon: 'none', duration: 2000 })
    return
  }
  
  if (addForm.value.location_tag.trim().length > 10) {
    uni.showToast({ title: '健身房名称不能超过 10 个字符', icon: 'none', duration: 2000 })
    return
  }
  
  // 2. 验证描述长度
  if (addForm.value.description && addForm.value.description.length > 200) {
    uni.showToast({ title: '描述信息不能超过 200 个字符', icon: 'none', duration: 2000 })
    return
  }
  
  addLoading.value = true
  
  try {
    // 3. 调用创建健身房 API
    await request.post(API.GYM_CREATE, {
      location_tag: addForm.value.location_tag.trim(),
      description: addForm.value.description.trim()
    })
    
    uni.showToast({ title: '创建成功', icon: 'success', duration: 1500 })
    
    // 4. 关闭弹窗并刷新列表
    closeAddDialog()
    await loadGymList()
    
  } catch (error) {
    console.error('创建失败:', error)
    // 错误信息已在 request 拦截器中处理
  } finally {
    addLoading.value = false
  }
}

// ==================== 编辑健身房 ====================

/**
 * 打开编辑弹窗
 */
const openEditDialog = (gym) => {
  editForm.value = {
    inventory_id: gym.inventory_id,
    location_tag: gym.location_tag,
    description: gym.description || ''
  }
  showEditDialog.value = true
}

/**
 * 关闭编辑弹窗
 */
const closeEditDialog = () => {
  showEditDialog.value = false
  editForm.value = {
    inventory_id: '',
    location_tag: '',
    description: ''
  }
}

/**
 * 处理编辑健身房
 * 对应《需求规格说明书》3.2 节管理健身房扩展事件流 1a
 */
const handleEditGym = async () => {
  // 1. 验证健身房名称
  if (!editForm.value.location_tag || editForm.value.location_tag.trim().length === 0) {
    uni.showToast({ title: '请输入健身房名称', icon: 'none', duration: 2000 })
    return
  }
  
  if (editForm.value.location_tag.trim().length > 10) {
    uni.showToast({ title: '健身房名称不能超过 10 个字符', icon: 'none', duration: 2000 })
    return
  }
  
  // 2. 验证描述长度
  if (editForm.value.description && editForm.value.description.length > 200) {
    uni.showToast({ title: '描述信息不能超过 200 个字符', icon: 'none', duration: 2000 })
    return
  }
  
  editLoading.value = true
  
  try {
    // 3. 调用编辑健身房 API
    await request.put(`${API.GYM_EDIT}/${editForm.value.inventory_id}`, {
      location_tag: editForm.value.location_tag.trim(),
      description: editForm.value.description.trim()
    })
    
    uni.showToast({ title: '修改成功', icon: 'success', duration: 1500 })
    
    // 4. 关闭弹窗并刷新列表
    closeEditDialog()
    await loadGymList()
    
  } catch (error) {
    console.error('修改失败:', error)
    // 错误信息已在 request 拦截器中处理
  } finally {
    editLoading.value = false
  }
}

// ==================== 删除健身房 ====================

/**
 * 确认删除健身房
 * 对应《需求规格说明书》3.2 节管理健身房扩展事件流 1b
 */
const confirmDelete = (gym) => {
  uni.showModal({
    title: '警告',
    content: `确定要删除"${gym.location_tag}"吗？\n此操作不可恢复`,
    confirmText: '确认删除',
    confirmColor: '#FF4444',
    success: async (res) => {
      if (res.confirm) {
        await deleteGym(gym.inventory_id)
      }
    }
  })
}

/**
 * 删除健身房
 */
const deleteGym = async (inventoryId) => {
  loading.value = true
  
  try {
    await request.delete(`${API.GYM_DELETE}/${inventoryId}`)
    
    uni.showToast({ title: '删除成功', icon: 'success', duration: 1500 })
    
    // 刷新列表
    await loadGymList()
    
  } catch (error) {
    console.error('删除失败:', error)
    // 错误信息已在 request 拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: $fitness-primary;
  padding: 0 0 150rpx; /* 为悬浮按钮预留空间 */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx;
  background: #FFFFFF;
  border-bottom: 1rpx solid $fitness-border;
  
  .title {
    font-size: $font-xl;
    font-weight: bold;
    color: $fitness-text;
  }
  
  .add-btn {
    display: flex;
    align-items: center;
    padding: 10rpx 20rpx;
    background: $uni-primary;
    border-radius: 30rpx;
    
    .add-icon {
      font-size: 32rpx;
      color: #FFFFFF;
      margin-right: 5rpx;
    }
    
    .add-text {
      font-size: $font-sm;
      color: #FFFFFF;
    }
  }
}

.gym-list {
  padding: 30rpx 40rpx;
  
  .gym-card {
    background: $fitness-secondary;
    border-radius: $radius-md;
    padding: 30rpx;
    margin-bottom: 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .gym-info {
      flex: 1;
      
      .gym-name {
        display: block;
        font-size: $font-lg;
        font-weight: bold;
        color: $fitness-text;
        margin-bottom: 10rpx;
      }
      
      .gym-desc {
        display: block;
        font-size: $font-sm;
        color: $fitness-text-light;
        margin-bottom: 15rpx;
      }
      
      .gym-meta {
        display: block;
        font-size: $font-xs;
        color: $fitness-text-gray;
      }
    }
    
    .gym-actions {
      display: flex;
      gap: 20rpx;
      
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
        
        .action-icon {
          font-size: 28rpx;
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
    font-size: $font-lg;
    color: $fitness-text-light;
    margin-bottom: 10rpx;
  }
  
  .empty-subtext {
    font-size: $font-sm;
    color: $fitness-text-gray;
    margin-bottom: 40rpx;
  }
}

// ==================== 悬浮按钮样式 ====================

.fab-button {
  position: fixed;
  right: 30rpx;
  bottom: 100rpx;
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(7, 4, 4, 0.2);
  z-index: 998;
  margin-bottom: 20rpx;
  
  &:active {
    transform: scale(0.95);
    opacity: 0.9;
  }
}

// ==================== 弹窗样式 ====================

.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
  pointer-events: auto; /* 确保弹窗内元素可交互 */
}

.dialog-content {
  background: #FFFFFF;
  border-radius: $radius-lg;
  padding: 40rpx;
  width: 600rpx;
  max-height: 80vh;
  overflow-y: auto;
  pointer-events: auto; /* 确保内容区域可交互 */
  
  .dialog-title {
    display: block;
    font-size: $font-lg;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30rpx;
    color: $fitness-text;
  }
  
  .form-item {
    margin-bottom: 30rpx;
    
    .form-label {
      display: block;
      font-size: $font-md;
      color: $fitness-text;
      margin-bottom: 15rpx;
    }
    
    .form-input, .form-textarea {
      width: 100%;
      background: $fitness-primary;
      border: 1rpx solid $fitness-border;
      border-radius: $radius-sm;
      padding: 20rpx 30rpx;
      font-size: $font-md;
      box-sizing: border-box;
      z-index: 1000; /* 确保输入框在最上层 */
      
      &:focus {
        border-color: $uni-primary;
      }
    }
    
    .form-input {
      height: 80rpx;
    }
    .form-textarea {
      height: 200rpx;
      white-space: pre-wrap; /* 保证长文本自动换行 */
      word-wrap: break-word; /* 强制长单词换行 */
      overflow-wrap: break-word; /* 兼容性处理 */
    }
  }
  
  .dialog-buttons {
    display: flex;
    gap: 20rpx;
    margin-top: 40rpx;
    
    .btn-cancel, .btn-confirm {
      flex: 1;
      height: 80rpx;
      border-radius: 40rpx;
      font-size: $font-lg;
      align-content: center;
    }
    
    .btn-cancel {
      background: #F5F5F5;
      color: $fitness-text-light;
    }
    
    .btn-confirm {
      background: $uni-primary;
      color: #FFFFFF;
    }
  }
}
</style>