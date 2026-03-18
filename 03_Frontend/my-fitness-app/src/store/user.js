/**
 * 用户状态管理
 * 对应《需求规格说明书》表 2-1 User 对象
 * 管理用户登录状态、个人信息、身体数据等
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // === 状态 ===
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref(JSON.parse(uni.getStorageSync('userInfo') || '{}'))
  
  // === 计算属性 ===
  
  /**
   * 是否已登录
   */
  const isLogin = computed(() => !!token.value)
  
  /**
   * 资料是否完整（对应《需求规格说明书》2.2.1 业务规则）
   * 用户首次使用系统时必须完成基本信息录入，否则无法生成个性化训练计划
   */
  const isProfileComplete = computed(() => {
    const info = userInfo.value
    return !!(info.age && info.gender && info.height && info.weight && 
              info.fitness_goal && info.experience_level)
  })
  
  /**
   * BMI 指数（动态计算）
   */
  const bmi = computed(() => {
    const info = userInfo.value
    if (info.height && info.weight) {
      return (info.weight / ((info.height / 100) ** 2)).toFixed(2)
    }
    return null
  })
  
  /**
   * BMI 状态
   */
  const bmiStatus = computed(() => {
    if (!bmi.value) return ''
    const val = parseFloat(bmi.value)
    if (val < 18.5) return '偏瘦'
    if (val < 24) return '正常'
    if (val < 28) return '偏胖'
    return '肥胖'
  })
  
  // === 方法 ===
  
  /**
   * 保存登录信息
   * @param {String} newToken - JWT Token
   * @param {Object} newUserInfo - 用户信息
   */
  function setLoginInfo(newToken, newUserInfo) {
    token.value = newToken
    userInfo.value = newUserInfo
    uni.setStorageSync('token', newToken)
    uni.setStorageSync('userInfo', JSON.stringify(newUserInfo))
  }
  
  /**
   * 更新用户信息
   * @param {Object} newInfo - 新的用户信息
   */
  function updateUserInfo(newInfo) {
    userInfo.value = { ...userInfo.value, ...newInfo }
    uni.setStorageSync('userInfo', JSON.stringify(userInfo.value))
  }
  
  /**
   * 退出登录
   */
  function logout() {
    token.value = ''
    userInfo.value = {}
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
  }
  
  /**
   * 检查资料完整性（对应《需求规格说明书》2.2.1 业务规则）
   * @returns {Boolean} 资料是否完整
   */
  function checkProfileComplete() {
    return isProfileComplete.value
  }
  
  /**
   * 获取缺失的字段列表
   * @returns {Array} 缺失字段名数组
   */
  function getMissingFields() {
    const info = userInfo.value
    const required = ['age', 'gender', 'height', 'weight', 'fitness_goal', 'experience_level']
    return required.filter(field => !info[field])
  }
  
  return {
    token,
    userInfo,
    isLogin,
    isProfileComplete,
    bmi,
    bmiStatus,
    setLoginInfo,
    updateUserInfo,
    logout,
    checkProfileComplete,
    getMissingFields
  }
})