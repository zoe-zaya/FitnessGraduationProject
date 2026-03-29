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
        <button class="modal-btn confirm-btn" @click="handleConfirm" :style="`color: confirmColor`">{{ confirmText }}</button>
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
      default: '#007aff'
    },
    borderRadius: {
      type: String,
      default: '10px'
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
      // 点击遮罩层不关闭，只有点击按钮才会触发对应事件
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
  background-color: #fff;
  min-width: 300px;
  max-width: 80vw;
  overflow: hidden;
}

.modal-header {
  padding: 24rpx 24rpx 14rpx 24rpx;
  border-bottom: none;
  text-align: center;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
}

.modal-body {
  padding: 24rpx;
  text-align: center;
}

.modal-content-text {
  font-size: 16px;
  line-height: 1.4;
  color: #333;
}

.modal-footer {
  display: flex;
  border-top: 1px solid #eee;
}

.modal-btn {
  flex: 1;
  padding: 8rpx 0;
  border: none;
  background: none;
  font-size: 16px;
  outline: none;
  cursor: pointer;
}

.cancel-btn {
  border-right: 1px solid #eee;
  color: #888;
  font-weight: bolder;
}

.confirm-btn {
  color: #df6860;
  font-weight: bolder;
}
</style>