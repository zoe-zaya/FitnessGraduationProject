<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch')
  // 检查登录状态
  const token = uni.getStorageSync('token')
  if (token) {
    console.log('用户已登录')
  }
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
/* 全局样式 */
@import './uni.scss';

page {
  background-color: $fitness-bg;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 通用按钮样式 */
.primary-btn {
  width: 100%;
  height: 90rpx;
  background: linear-gradient(90deg, #007AFF, #00C6FB);
  color: #FFFFFF;
  font-size: 32rpx;
  border-radius: 45rpx;
  border: none;
  
  &[disabled] {
    background: #CCCCCC;
  }
}

/* 通用输入框样式 */
.common-input {
  width: 100%;
  height: 90rpx;
  background: #FFFFFF;
  border: 1rpx solid #E5E5E5;
  border-radius: 12rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

/* 通用卡片样式 */
.common-card {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}
</style>