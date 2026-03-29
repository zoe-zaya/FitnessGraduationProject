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
            <img src="/static/edit.png" class="action-icon" mode="aspectFit" />
          </view>
          <view class="action-btn delete" @click.stop="confirmDelete(gym)">
            <img src="/static/delete.png" class="action-icon" mode="aspectFit" />
          </view>
        </view>
      </view>
    </view>
    
    <!-- 空状态提示 -->
    <view class="empty-state" v-else>
      <image src="/static/empty-data.png" class="empty-image" mode="aspectFit" />
      <text class="empty-text">暂无健身房</text>
      <text class="empty-subtext">点击右下角按钮添加您的第一个健身房</text>
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
            :class="{ 'input-focus': focusedInput === 'location_tag' }"
            @focus="onInputFocus('location_tag')"
            @blur="onInputBlur"
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
            :class="{ 'input-focus': focusedInput === 'description' }"
            @focus="onInputFocus('description')"
            @blur="onInputBlur"
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
            :class="{ 'input-focus': focusedInput === 'location_tag' }"
            @focus="onInputFocus('location_tag')"
            @blur="onInputBlur"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">描述信息</text>
          <textarea 
            v-model="editForm.description" 
            placeholder="可选：24 小时营业，器械较新等"
            class="form-textarea"
            maxlength="200"
            :class="{ 'input-focus': focusedInput === 'description' }"
            @focus="onInputFocus('description')"
            @blur="onInputBlur"
          />
        </view>
        
        <view class="dialog-buttons">
          <button class="btn-cancel" @click="closeEditDialog">取消</button>
          <button class="btn-confirm" @click="handleEditGym" :loading="editLoading">确认</button>
        </view>
      </view>
    </view>
    
    <!-- 自定义删除确认模态框 -->
    <CustomModal
      :show="showDeleteConfirmModal"
      title="确认删除"
      :content="deleteConfirmContent"
      confirmText="确认删除"
      cancelText="取消"
      confirmColor="#FF4444"
      :borderRadius="customBorderRadius"
      @confirm="onConfirmDelete"
      @cancel="onCancelDelete"
    />
    
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
import CustomModal from '@/components/CustomModal.vue' // 导入自定义模态框组件

const userStore = useUserStore()
const gymList = ref([])
const loading = ref(false)
const focusedInput = ref(null)

// 弹窗控制
const showAddDialog = ref(false)
const showEditDialog = ref(false)

// 加载状态
const addLoading = ref(false)
const editLoading = ref(false)

// 删除确认模态框相关
const showDeleteConfirmModal = ref(false)
const deleteConfirmContent = ref('')
const gymToDelete = ref(null)
const customBorderRadius = ref('15px') // 自定义border-radius

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

const onInputFocus = (inputName) => {
    focusedInput.value = inputName
}
  
const onInputBlur = () => {
    focusedInput.value = null
}

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
  deleteConfirmContent.value = `确定要删除"${gym.location_tag}"吗？\n此操作不可恢复`
  gymToDelete.value = gym
  showDeleteConfirmModal.value = true
}

/**
 * 确认删除健身房回调
 */
const onConfirmDelete = async () => {
  if (gymToDelete.value) {
    await deleteGym(gymToDelete.value.inventory_id)
    showDeleteConfirmModal.value = false
    gymToDelete.value = null
  }
}

/**
 * 取消删除健身房回调
 */
const onCancelDelete = () => {
  showDeleteConfirmModal.value = false
  gymToDelete.value = null
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
    // 错误信息已在 request 拦icter 中处理
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: url('@/static/background3.png') no-repeat center center / cover;
  padding: 0 0 150rpx; /* 为悬浮按钮预留空间 */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx $size-5;
  background: #FFFFFF;
  border-bottom: 1rpx solid rgba(160, 62, 64, 0.1);
  
  .title {
    font-size: $size-6;
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
      font-size: $size-4;
      color: #FFFFFF;
      margin-right: 5rpx;
    }
    
    .add-text {
      font-size: $size-3;
      color: #FFFFFF;
    }
  }
}

.gym-list {
  padding: $size-5;
  
  .gym-card {
    background: #FFFFFF url('/static/foot-icon.png') no-repeat;
    background-size: $size-7 $size-7;     //背景图片的宽度
    background-position: right $size-3 top $size-3; /* 右上角 */
    border-radius: $size-4;
    padding: $size-4;
    margin-bottom: $size-3;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    box-shadow: 4rpx 4rpx 14rpx rgba(0, 0, 0, 0.12);
    position: relative; /* 添加相对定位 */
  }

  .gym-card::before {
    content: '';
    position: absolute;
    left: $size-3;
    bottom: $size-3;
    width: $size-7;
    height: $size-7;
    background: url('/static/foot-icon.png') no-repeat center;
    background-size: contain;
    z-index: 1;
  }

  .gym-card .gym-info {
    flex: 1;
    margin-right: 120rpx; /* 为右侧操作按钮留出空间 */
    position: relative; /* 确保内容在背景图标之上 */
    z-index: 2; /* 确保内容在伪元素之上 */
  }

  .gym-card .gym-info .gym-name {
    display: block;
    font-size: $size-5;
    font-weight: bold;
    color: $fitness-text;
    margin-bottom: 10rpx;
  }

  .gym-card .gym-info .gym-desc {
    display: block;
    font-size: $size-3;
    color: $color-label;
    margin-bottom: 15rpx;
  }

  .gym-card .gym-info .gym-meta {
    display: block;
    font-size: $size-2;
    color: $color-label;
  }

  .gym-card .gym-actions {
    position: absolute;
    display: flex;
    
    right: 20rpx;
    display: flex;
    gap: 20rpx;
    z-index: 2; /* 确保操作按钮在伪元素之上 */
  }

  .gym-card .gym-actions .action-btn {
    width: 60rpx;
    height: 60rpx;
    border-radius: 30rpx;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .gym-card .gym-actions .action-btn .action-icon {
    width: $size-5;
    height: $size-5;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  //相对于页面居中
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  .empty-image {
    width: 500rpx;
    height: 200rpx;
  }
  
  .empty-text {
    font-size: $size-4;
    color: $color-input;
    margin-bottom: 10rpx;
    font-weight: 600;
  }
  
  .empty-subtext {
    font-size: $size-3;
    color: $color-label;
    text-align: center;
    margin-bottom: $size-5;
    font-weight: 400;
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
  box-shadow: 0 $size-1 $size-3 rgba(7, 4, 4, 0.2);
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
  align-items: end;
  z-index: 999; /* 确保弹窗在最上层 */
  pointer-events: auto; /* 确保弹窗内元素可交互 */
}

.dialog-content {
  background: #FFFFFF;
  border-radius: $size-5 $size-5 0 0;
  padding: $size-5;
  width: stretch;  //适配不同屏幕宽度
  //max-height: 80vh;
  overflow-y: auto;
  pointer-events: auto; /* 确保内容区域可交互 */
  box-shadow: none; /* 移除默认阴影 */
  border: none; /* 移除默认边框 */
  
  .dialog-title {
    display: block;
    font-size: $size-5;
    font-weight: bold;
    text-align: center;
    margin-bottom: $size-4;
    color: $fitness-text;
  }
  
  .form-item {
    margin-bottom: $size-4;
    
    .form-label {
      font-weight: 700;
      font-size: 28rpx;
      display: block;
      margin-left: $size-1;
      color: $color-label;
      margin-bottom: $size-2;
    }
    
    .form-input, .form-textarea {
      width: 100%;
      background: $fitness-primary;
      border: 1rpx solid rgba(160, 62, 64, 0.2);
      border-radius: $size-4;
      padding: 20rpx 30rpx;
      font-size: $size-4;
      box-sizing: border-box;
      z-index: 1000; /* 确保输入框在最上层 */
    }
    .input-focus {
      border: 2px solid rgba(160, 62, 64, 0.4);
    }
    
    .form-input {
      height: $size-12;
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
    gap: $size-3;
    margin-top: $size-5;

    .btn-cancel, .btn-confirm {
      flex: 1;
      height: $size-10;
      border-radius: $size-4;
      font-size: $size-5;
      font-weight: 500;
      display: flex;
      align-content: center;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      border: none;
    }
    
    .btn-cancel {
      background: #F5F5F5;
      color: $color-label;
      border: 1rpx solid rgba(0, 0, 0, 0.2);
    }
    .btn-cancel:after {
      border: none;
    }
    
    .btn-confirm {
      background: $uni-primary;
      color: #FFFFFF;    
    }
  }
}
</style>