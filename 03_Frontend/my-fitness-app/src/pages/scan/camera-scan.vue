<template>
  <view class="container">
    <!-- 相机区域（仅 H5/App 支持，小程序需使用 uni.chooseImage）-->
    <!-- #ifndef MP-WEIXIN -->
    <view class="camera-area" v-if="!isWeixinMiniProgram">
      <camera 
        device-position="back" 
        flash="off"
        class="camera"
        mode="normal"
        @error="onCameraError"
      />
      <view class="camera-overlay">
        <view class="scan-frame"></view>
        <text class="scan-tip">将健身器材放入框内</text>
      </view>
    </view>
    <!-- #endif -->

    <!-- 显示从相册选择的图片 -->
    <view class="camera-area" v-if="selectedImagePath">
      <image :src="selectedImagePath" class="selected-image" mode="aspectFill"></image>
      <view class="camera-overlay">
        <view class="scan-frame"></view>
        <text class="scan-tip">已选择图片</text>
      </view>
    </view>
    
    <!-- 小程序提示（当没有选择图片时显示） -->
    <!-- #ifdef MP-WEIXIN -->
    <view class="camera-hint" v-if="!selectedImagePath">
      <text class="hint-icon">📷</text>
      <text class="hint-text">请点击下方按钮选择图片</text>
    </view>
    <!-- #endif -->
    
    <!-- 加载中遮罩 -->
    <view class="loading-mask" v-if="recognizing">
      <view class="loading-content">
        <text class="loading-icon">🔄</text>
        <text class="loading-text">识别中...</text>
      </view>
    </view>
    
    <!-- 操作按钮区域 -->
    <view class="action-area">
      <!-- #ifdef MP-WEIXIN -->
      <button class="action-btn album-btn" @click="chooseFromAlbum">
        <image class="btn-icon" src="/static/album.png" mode="aspectFit"></image>
        <text class="btn-text">从相册选择</text>
      </button>
      <!-- #endif -->
      
      <!-- #ifndef MP-WEIXIN -->
      <view class="btn-container">
        <button class="action-btn album-btn" @click="chooseFromAlbum">
          <image class="btn-icon" src="/static/album.png" mode="aspectFit"></image>
          <text class="btn-text">从相册选择</text>
        </button>
        <button class="action-btn capture-btn" @click="captureImage">
          <image class="btn-icon" src="/static/take-photo.png" mode="aspectFit"></image>
          <text class="btn-text">拍摄</text>
        </button>
      </view>
      <!-- #endif -->
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import request from '@/utils/request'
import { API, CONFIG } from '@/utils/constants'

const inventoryId = ref('')
const recognizing = ref(false)
const recognitionResult = ref(null)
const isWeixinMiniProgram = ref(false)
const selectedImagePath = ref('')  // 新增：存储选择的图片路径

onLoad((options) => {
  inventoryId.value = options.inventory_id || ''
  
  // 检测是否为微信小程序环境
  // #ifdef MP-WEIXIN
  isWeixinMiniProgram.value = true
  // #endif
})

/**
 * 相机错误处理
 */
const onCameraError = (e) => {
  console.error('相机错误:', e)
  uni.showToast({ title: '相机访问失败', icon: 'none', duration: 2000 })
}

/**
 * 从相册选择图片（兼容多端）
 */
const chooseFromAlbum = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['album'],
    sizeType: ['compressed'], // 压缩图片，减少上传时间
    success: (res) => {
      const filePath = res.tempFilePaths[0]
      selectedImagePath.value = filePath  // 设置选择的图片路径
      uploadAndRecognize(filePath)
    },
    fail: (err) => {
      console.error('选择图片失败:', err)
      uni.showToast({ title: '选择图片失败', icon: 'none', duration: 2000 })
    }
  })
}

/**
 * 拍摄照片（仅非小程序环境）
 */
const captureImage = () => {
  // #ifndef MP-WEIXIN
  uni.chooseImage({
    count: 1,
    sourceType: ['camera'],
    sizeType: ['compressed'],
    success: (res) => {
      const filePath = res.tempFilePaths[0]
      selectedImagePath.value = filePath  // 设置拍摄的图片路径
      uploadAndRecognize(filePath)
    },
    fail: (err) => {
      console.error('拍摄失败:', err)
      uni.showToast({ title: '拍摄失败', icon: 'none', duration: 2000 })
    }
  })
  // #endif
  
  // #ifdef MP-WEIXIN
  uni.showToast({ title: '小程序请使用相册选择', icon: 'none', duration: 2000 })
  // #endif
}

/**
 * 上传图片并识别（✅ 核心修复：使用 uni.uploadFile）
 */
const uploadAndRecognize = (filePath) => {
  recognizing.value = true
  
  uni.uploadFile({
    url: `${CONFIG.API_BASE_URL}${API.EQUIPMENT_DETECT}`, // 后端接口地址
    filePath: filePath,
    name: 'image', // 与后端 UploadFile 参数名一致
    header: {
      // 携带认证 Token
      'Authorization': `Bearer ${uni.getStorageSync('token')}`
    },
    formData: {
      // 可添加额外表单数据
    },
    success: (uploadFileRes) => {
      console.log('上传响应:', uploadFileRes)
      
      try {
        // 解析响应数据
        const res = JSON.parse(uploadFileRes.data)
        
        if (uploadFileRes.statusCode === 200) {
          if (res.results && res.results.length > 0) {
            recognitionResult.value = res.results[0]
            
            // 检查置信度
            if (res.results[0].confidence < 0.7) {
              uni.showToast({ 
                title: '识别不确定，建议重试', 
                icon: 'none',
                duration: 2000
              })
            } else {
              // 识别成功后跳转到手动添加设备页面
              uni.navigateTo({
                url: `/pages/scan/equipment-detail?equipment_id=${encodeURIComponent(recognitionResult.value.equipment_id)}`
              })
            }
          } else {
            uni.showToast({ 
              title: res.message || '未识别到器材', 
              icon: 'none',
              duration: 2000
            })
          }
        } else {
          // 处理业务错误
          uni.showToast({ 
            title: res.detail || '识别失败', 
            icon: 'none',
            duration: 2000
          })
        }
      } catch (e) {
        console.error('解析响应失败:', e)
        uni.showToast({ title: '响应解析失败', icon: 'none', duration: 2000 })
      }
    },
    fail: (err) => {
      console.error('上传失败:', err)
      
      // 处理网络错误
      if (err.errMsg && err.errMsg.includes('timeout')) {
        uni.showToast({ title: '上传超时，请重试', icon: 'none', duration: 2000 })
      } else if (err.statusCode === 401) {
        uni.showToast({ title: '登录已过期', icon: 'none', duration: 2000 })
        setTimeout(() => {
          uni.reLaunch({ url: '/pages/login/login' })
        }, 1500)
      } else {
        uni.showToast({ title: '上传失败，请检查网络', icon: 'none', duration: 2000 })
      }
    },
    complete: () => {
      recognizing.value = false
    }
  })
}

</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.container {
  min-height: 100vh;
  background: #000000;
  display: flex;
  flex-direction: column;
  position: relative;
}

// 相机区域（非小程序）
// #ifndef MP-WEIXIN
.camera-area {
  position: relative;
  width: 100%;
  flex: 1;  // 占据除了按钮区域外的所有空间
  
  .camera {
    width: 100%;
    height: 100%;
  }
  
  .selected-image {
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
      border: 4rpx solid $uni-primary;
      border-radius: 20rpx;
      box-shadow: 0 0 0 1000rpx rgba(0, 0, 0, 0.5);
    }
    
    .scan-tip {
      margin-top: $size-5;
      font-size: $size-4;
      color: #FFFFFF;
    }
  }
}
// #endif

// 小程序提示
// #ifdef MP-WEIXIN
.camera-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx $size-5;
  background: #1A1A1A;
  flex: 1;  // 占据剩余空间
  
  .hint-icon {
    font-size: $size-10;
    margin-bottom: 20rpx;
  }
  
  .hint-text {
    font-size: $size-4;
    color: #FFFFFF;
    text-align: center;
  }
}
// #endif

.action-area {
  width: 100%;
  //padding: $size-5;
  background: #000000;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: fixed;
  bottom: 0;
  left: 0;
  z-index: 999;
  
  .btn-container {
    display: flex;
    justify-content: space-around;
    width: 100%;
    
    .action-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      background: transparent;
      border: none;
      padding: 20rpx;
      flex: 1;
      max-width: 300rpx;
      margin: 0 20rpx;
      
      .btn-icon {
        width: $size-6;
        height: $size-6;
        margin-bottom: 10rpx;
      }
      
      .btn-text {
        font-size: $size-3;
        color: #FFFFFF;
      }
      
      &.album-btn {
        .btn-icon {
          width: $size-5;
          height: $size-5;
        }
      }
      
      &.capture-btn {
        .btn-icon {
          width: $size-6;
          height: $size-6;
        }
      }
    }
  }
  
  // 小程序环境下居中显示一个按钮
  .action-btn.album-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: transparent;
    border: none;
    padding: 20rpx;
    margin: 0 auto;
    
    .btn-icon {
      width: $size-6;
      height: $size-6;
      margin-bottom: 10rpx;
    }
    
    .btn-text {
      font-size: $size-3;
      color: #FFFFFF;
    }
  }
}

.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  
  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .loading-icon {
      font-size: 60rpx;
      margin-bottom: 20rpx;
      animation: spin 1s linear infinite;
    }
    
    .loading-text {
      font-size: $size-4;
      color: #FFFFFF;
    }
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>