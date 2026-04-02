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
    { label: '女', value: 'female' }
  ]
  // 训练部位选项
  export const TRAINING_PARTS = [
    { label: '胸部', value: '胸部' },
    { label: '背部', value: '背部' },
    { label: '肩部', value: '肩部' },
    { label: '手臂', value: '手臂' },
    { label: '腿部', value: '腿部' },
    { label: '臀部', value: '臀部' },
    { label: '核心', value: '核心' },
    { label: '全身', value: '全身' }
  ]

  // 阶段类型映射
  export const SESSION_TYPE_MAP = {
    'warmup': { label: '热身激活', color: '#FF9F00', icon: '🔥' },
    'main': { label: '正式训练', color: '#007AFF', icon: '💪' },
    'cooldown': { label: '拉伸放松', color: '#34C759', icon: '🧘' }
  }

  // 难度等级映射
  export const DIFFICULTY_MAP = {
    '初级': { label: '初级', color: '#34C759' },
    '中级': { label: '中级', color: '#FF9F00' },
    '高级': { label: '高级', color: '#FF4444' }
  }
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
    CHECK_PROFILE_COMPLETE: '/api/user/check-profile-complete',

    // 器材管理
    EQUIPMENT_DETECT: '/api/equipment/detect', // ✅ 完整 URL
    GYM_CREATE: '/api/equipment/createGym',
    GYM_LIST: '/api/equipment/getAllGym',
    GYM_DETAIL: '/api/equipment/getGym',
    GYM_EDIT: '/api/equipment/editGym',
    GYM_DELETE: '/api/equipment/deleteGym',
    EQUIPMENT_ADD_MANUAL: '/api/equipment/addEquipment',
    EQUIPMENT_ADD_AUTO: '/api/equipment/addEquipment',
    EQUIPMENT_DETAIL: '/api/equipment/getEquipmentById',
    EQUIPMENT_SEARCH: '/api/equipment/getEquipmentByKey/search',
    EQUIPMENT_DELETE: '/api/equipment/deleteEquipment',

    //动作管理
    ACTION_RECOMMEND: 'api/action/recommend',
    ACTION_DETAIL: 'api/action/detail',
    ACTION_LIBRARY: 'api/action/library',
    ACTION_MUSCLES: 'api/action/muscles',
    ACTION_QUERY: 'api/action/query',

    // 训练计划
    PLAN_GENERATE: '/api/plan/generate',
    PLAN_LIST: '/api/plan/',
    PLAN_DETAIL: '/api/plan',
    PLAN_DELETE: '/api/plan',
    PLAN_UPDATE: '/api/plan',       //修改名称或有效日期
    PLAN_EDITNAME: 'api/plan/editName',
    PLAN_ADD_ACTION: '/api/plan/addActions',
    PLAN_UPDATE_ACTION: '/api/plan/editActions',
    PLAN_DELETE_ACTION: '/api/plan/deleteActions',
    PLAN_EXTEND: '/api/plan/extend',
  
  }
  
  // 默认配置
  export const CONFIG = {
    // 后端基础地址（开发环境）
    API_BASE_URL: 'http://localhost:8000',
    // 生产环境地址（部署时修改）
    // API_BASE_URL: 'https://your-server.com'
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