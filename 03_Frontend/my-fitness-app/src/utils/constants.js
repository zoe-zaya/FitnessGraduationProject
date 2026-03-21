/**
 * 系统常量配置
 * 对应《需求规格说明书》数据字典
 */

// 健身目标选项
export const FITNESS_GOALS = [
    { label: '增肌', value: '增肌' },
    { label: '减脂', value: '减脂' },
    { label: '塑形', value: '塑形' },
    { label: '增强体能', value: '增强体能' }
  ]
  
  // 经验水平选项
  export const EXPERIENCE_LEVELS = [
    { label: '初学者', value: '初学者' },
    { label: '中级', value: '中级' },
    { label: '高级', value: '高级' }
  ]
  
  // 性别选项
  export const GENDERS = [
    { label: '男', value: 'male' },
    { label: '女', value: 'female' },
    { label: '其他', value: 'other' }
  ]
  
  // 密码复杂度正则（对应《需求规格说明书》3.2 节扩展事件流）
  //密码需 8 位以上，含大小写字母、数字和特殊符号!@#$%^&*()_+-=
  export const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=-]).{8,}$/
  // 手机号码正则（对应《需求规格说明书》3.2 节扩展事件流）
  // 手机号码需以 1 开头，第二位为 3-9 的数字，后续为 9 位数字
  export const PHONE_REGEX = /^1[3-9]\d{9}$/
  
  // API 接口路径
  export const API = {
    // 认证
    REGISTER: '/api/auth/register',
    LOGIN: '/api/auth/login',
    RESET_PASSWORD: '/api/auth/reset-password',
    USER_ME: '/api/auth/me',
    SEND_CODE: '/api/auth/send-verification-code',
    VERIFY_CODE: '/api/auth/verify-code',
    RESET_PASSWORD: '/api/auth/reset-password',
    // 用户
    
    USER_BODY_DATA: '/api/user/body-data',
    USER_PROFILE: '/api/user/profile',
    USER_SECURITY_PHONE: '/api/user/security/phone',      
    USER_SECURITY_PASSWORD: '/api/user/security/password', 
    USER_SECURITY: '/api/user/security',
    CHECK_PROFILE_COMPLETE: '/api/user/check-profile-complete'
  }
  
  // 默认配置
  export const CONFIG = {
    // Token 有效期（分钟）
    TOKEN_EXPIRE_MINUTES: 60,
    
    // 验证码有效期（秒）
    CODE_EXPIRE_SECONDS: 300,
    
    // 验证码倒计时（秒）
    CODE_COUNTDOWN_SECONDS: 60,
    
    // 计划有效期（天）
    PLAN_VALID_DAYS: 30,

    // 计划总时长范围（分钟）
    PLAN_DURATION_MIN: 40,
    PLAN_DURATION_MAX: 65,
    
    // 计划总时长范围（分钟）
    PLAN_DURATION_MIN: 40,
    PLAN_DURATION_MAX: 65
  }