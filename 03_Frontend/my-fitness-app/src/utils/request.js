/**
 * Axios 请求封装
 * 对应《需求规格说明书》3.2 节 API 交互规范
 * 自动携带 Token，统一处理错误
 */
import axios from 'axios'
import { useUserStore } from '@/store/user'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:8000', // 开发环境后端地址
  // baseURL: 'http://your-server-ip:8000', // 生产环境
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 * 自动携带 JWT Token
 */
request.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    uni.showToast({ 
      title: '网络请求失败', 
      icon: 'none',
      duration: 2000
    })
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 统一处理业务错误和 Token 过期
 */
request.interceptors.response.use(
  response => {
    // 直接返回 data 部分
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      // 401 Token 过期或未授权
      if (status === 401) {
        uni.showToast({ 
          title: '登录已过期，请重新登录', 
          icon: 'none',
          duration: 2000
        })
        const userStore = useUserStore()
        userStore.logout()
        setTimeout(() => {
          uni.reLaunch({ url: '/pages/login/login' })
        }, 1500)
      }
      // 400 业务错误
      else if (status === 400) {
        uni.showToast({ 
          title: data.detail || '请求参数错误', 
          icon: 'none',
          duration: 2000
        })
      }
      // 403 禁止访问
      else if (status === 403) {
        uni.showToast({ 
          title: '无权访问', 
          icon: 'none',
          duration: 2000
        })
      }
      // 500 服务器错误
      else if (status === 500) {
        uni.showToast({ 
          title: '服务器错误，请稍后重试', 
          icon: 'none',
          duration: 2000
        })
      }
    } else {
      // 网络错误
      uni.showToast({ 
        title: '网络连接失败，请检查网络', 
        icon: 'none',
        duration: 2000
      })
    }
    
    return Promise.reject(error)
  }
)

export default request