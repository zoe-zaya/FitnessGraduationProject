<template>
  <view v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <view class="modal-content" :style="`border-radius: ${borderRadius};`" @click.stop>
      <view class="modal-header" v-if="title">
        <text class="modal-title">{{ title }}</text>
      </view>
      <view class="modal-body">
        <text class="modal-content-text">{{ content }}</text>
      </view>
      <view class="modal-footer">
        <button class="modal-btn cancel-btn" @click="handleCancel">{{ cancelText }}</button>
        <button class="modal-btn confirm-btn" @click="handleConfirm" :style="`color: ${confirmColor}; border-color: ${confirmColor};`">{{ confirmText }}</button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CustomModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    content: {
      type: String,
      default: ''
    },
    confirmText: {
      type: String,
      default: '确认'
    },
    cancelText: {
      type: String,
      default: '取消'
    },
    confirmColor: {
      type: String,
      default: '#a03e40'
    },
    borderRadius: {
      type: String,
      default: '32rpx'
    }
  },
  emits: ['confirm', 'cancel'],
  methods: {
    handleConfirm() {
      this.$emit('confirm');
    },
    handleCancel() {
      this.$emit('cancel');
    },
    handleOverlayClick() {
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #FFFFFF;
  min-width: 560rpx;
  max-width: 80vw;
  border-radius: 32rpx;
  border: 1rpx solid rgba(160, 62, 64, 0.1);
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.modal-header {
  padding: 40rpx 32rpx 24rpx 32rpx;
  text-align: center;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 700;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #564241;
}

.modal-body {
  padding: 0 32rpx 32rpx 32rpx;
  text-align: center;
}

.modal-content-text {
  font-size: 24rpx;
  font-weight: 400;
  line-height: 1.4;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #8E8E93;
  white-space: pre-wrap;
}

.modal-footer {
  display: flex;
  border-top: 1rpx solid #efefef;
}

.modal-btn {
  flex: 1;
  height: 96rpx;
  border: none;
  background: transparent;
  font-size: 32rpx;
  font-weight: 700;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
  outline: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-btn:after {
  border: none;
}

.cancel-btn {
  color: #8E8E93;
  border-right: 1rpx solid #efefef;
}

.confirm-btn {
  color: #a03e40;
}
</style>