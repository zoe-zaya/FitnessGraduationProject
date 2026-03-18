/**
 * 应用入口文件
 * 配置 Vue3 + Pinia + uView Plus
 */
import { createSSRApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import uviewPlus from 'uview-plus'

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()
  
  // 使用 Pinia 状态管理
  app.use(pinia)
  
  // 使用 uView Plus UI 组件库
  app.use(uviewPlus)
  
  return {
    app,
    Pinia: pinia
  }
}