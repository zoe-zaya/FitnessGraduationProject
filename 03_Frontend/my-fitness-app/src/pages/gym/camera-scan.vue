<template>
    <view class="container">
      <!-- 相机区域 -->
      <view class="camera-area">
        <camera 
          device-position="back" 
          flash="off"
          class="camera"
          mode="scanCode"
          @error="onCameraError"
        />
        <view class="camera-overlay">
          <view class="scan-frame"></view>
          <text class="scan-tip">将健身器材放入框内</text>
        </view>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-area">
        <view class="btn-group">
          <button class="action-btn album" @click="chooseFromAlbum">
            <text class="btn-icon">🖼️</text>
            <text class="btn-text">从相册选择</text>
          </button>
          <button class="action-btn capture" @click="captureImage">
            <text class="btn-icon">📷</text>
            <text class="btn-text">拍摄</text>
          </button>
        </view>
      </view>
      
      <!-- 识别结果弹窗 -->
      <view class="result-modal" v-if="showResult">
        <view class="modal-content">
          <text class="modal-title">识别结果</text>
          
          <view class="result-info" v-if="recognitionResult">
            <text class="result-name">{{ recognitionResult.name }}</text>
            <text class="result-category">{{ recognitionResult.category }}</text>
            <text class="result-confidence">置信度：{{ (recognitionResult.confidence * 100).toFixed(1) }}%</text>
            <text class="result-muscles" v-if="recognitionResult.target_muscles">
              目标肌群：{{ recognitionResult.target_muscles.join('、') }}
            </text>
          </view>
          
          <view class="result-actions">
            <button class="action-btn retry" @click="retryRecognition">
              重新识别
            </button>
            <button class="action-btn confirm" @click="confirmAdd">
              添加至清单
            </button>
          </view>
        </view>
      </view>
    </view>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { onLoad } from '@dcloudio/uni-app'
  import request from '@/utils/request'
  import { API } from '@/utils/constants'
  
  const inventoryId = ref('')
  const showResult = ref(false)
  const recognitionResult = ref(null)
  const imageTempPath = ref('')
  
  onLoad((options) => {
    inventoryId.value = options.inventory_id || ''
  })
  
  /**
   * 相机错误处理
   */
  const onCameraError = (e) => {
    console.error('相机错误:', e)
    uni.showToast({ title: '相机访问失败', icon: 'none' })
  }
  
  /**
   * 从相册选择图片
   */
  const chooseFromAlbum = () => {
    uni.chooseImage({
      count: 1,
      sourceType: ['album'],
      success: (res) => {
        imageTempPath.value = res.tempFilePaths[0]
        uploadAndRecognize(res.tempFilePaths[0])
      }
    })
  }
  
  /**
   * 拍摄照片
   */
  const captureImage = () => {
    uni.chooseImage({
      count: 1,
      sourceType: ['camera'],
      success: (res) => {
        imageTempPath.value = res.tempFilePaths[0]
        uploadAndRecognize(res.tempFilePaths[0])
      }
    })
  }
  
  /**
   * 上传图片并识别
   */
  const uploadAndRecognize = async (filePath) => {
    uni.showLoading({ title: '识别中...' })
    
    try {
      // 创建 FormData 上传文件
      const formData = new FormData()
      formData.append('image', filePath)
      
      const res = await request.post(API.EQUIPMENT_DETECT, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (res.results && res.results.length > 0) {
        recognitionResult.value = res.results[0]
        showResult.value = true
        
        // 检查置信度
        if (res.results[0].confidence < 0.7) {
          uni.showToast({ title: '识别不确定，建议重试', icon: 'none' })
        }
      } else {
        uni.showToast({ title: '未识别到器材', icon: 'none' })
      }
    } catch (error) {
      console.error('识别失败:', error)
    } finally {
      uni.hideLoading()
    }
  }
  
  /**
   * 重新识别
   */
  const retryRecognition = () => {
    showResult.value = false
    recognitionResult.value = null
  }
  
  /**
   * 确认添加至清单
   */
  const confirmAdd = async () => {
    if (!recognitionResult.value || !inventoryId.value) {
      uni.showToast({ title: '参数错误', icon: 'none' })
      return
    }
    
    try {
      await request.post(`${API.EQUIPMENT_ADD_AUTO}/${inventoryId.value}/auto`, {
        inventory_id: inventoryId.value,
        equipment_id: recognitionResult.value.equipment_id,
        confidence: recognitionResult.value.confidence
      })
      
      uni.showToast({ title: '添加成功', icon: 'success' })
      
      setTimeout(() => {
        uni.navigateBack()
      }, 1000)
    } catch (error) {
      console.error('添加失败:', error)
    }
  }
  </script>
  
  <style lang="scss" scoped>
  @import '@/uni.scss';
  
  .container {
    min-height: 100vh;
    background: #000000;
  }
  
  .camera-area {
    position: relative;
    width: 100%;
    height: 60vh;
    
    .camera {
      width: 100%;
      height: 100%;
    }
    
    .camera-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      
      .scan-frame {
        width: 400rpx;
        height: 400rpx;
        border: 4rpx solid #007AFF;
        border-radius: 20rpx;
        box-shadow: 0 0 0 1000rpx rgba(0, 0, 0, 0.5);
      }
      
      .scan-tip {
        margin-top: 40rpx;
        font-size: $font-md;
        color: #FFFFFF;
      }
    }
  }
  
  .action-area {
    padding: 40rpx;
    background: #000000;
    
    .btn-group {
      display: flex;
      justify-content: space-around;
      
      .action-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        background: transparent;
        border: none;
        
        .btn-icon {
          font-size: 48rpx;
          margin-bottom: 10rpx;
        }
        
        .btn-text {
          font-size: $font-sm;
          color: #FFFFFF;
        }
        
        &.album {
          .btn-icon {
            font-size: 40rpx;
          }
        }
      }
    }
  }
  
  .result-modal {
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
    
    .modal-content {
      background: #FFFFFF;
      border-radius: $radius-lg;
      padding: 40rpx;
      width: 600rpx;
      
      .modal-title {
        display: block;
        font-size: $font-lg;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30rpx;
      }
      
      .result-info {
        margin-bottom: 30rpx;
        
        .result-name {
          display: block;
          font-size: $font-xl;
          font-weight: bold;
          color: $fitness-text;
          margin-bottom: 10rpx;
        }
        
        .result-category {
          display: block;
          font-size: $font-sm;
          color: $uni-primary;
          margin-bottom: 10rpx;
        }
        
        .result-confidence {
          display: block;
          font-size: $font-xs;
          color: $fitness-text-gray;
          margin-bottom: 10rpx;
        }
        
        .result-muscles {
          display: block;
          font-size: $font-xs;
          color: $fitness-text-gray;
        }
      }
      
      .result-actions {
        display: flex;
        gap: 20rpx;
        
        .action-btn {
          flex: 1;
          height: 80rpx;
          border-radius: 40rpx;
          font-size: $font-md;
          border: none;
          
          &.retry {
            background: #F5F5F5;
            color: $fitness-text;
          }
          
          &.confirm {
            background: $uni-primary;
            color: #FFFFFF;
          }
        }
      }
    }
  }
  </style>