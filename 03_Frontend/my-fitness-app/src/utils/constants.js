/**
 * 系统常量配置
 * 对应《生成训练计划模块需求分析》V2.1
 */

export const GENDERS = [
    { label: '男', value: 'male' },
    { label: '女', value: 'female' }
]

export const FITNESS_GOALS = [
    { label: '减脂', value: 'FAT_LOSS' },
    { label: '增肌', value: 'MUSCLE_GAIN' }
]

export const EXPERIENCE_LEVELS = [
    { label: '新手', value: 'BEGINNER', description: '刚接触健身' },
    { label: '初级', value: 'INTERMEDIATE', description: '健身经验一个月到三个月' },
    { label: '中级', value: 'ADVANCED', description: '健身经验三个月以上' },
    { label: '中高级', value: 'ADVANCED_PLUS', description: '健身经验一年以上' }
]

export const PLAN_TYPES = [
    { label: '减脂', value: 'FAT_LOSS' },
    { label: '增肌', value: 'MUSCLE_GAIN' }
]

export const SCHEME_TYPES = [
    { label: '一分化（全身）', value: 'ONE_SPLIT', description: '每周练3次，练遍全身肌群' },
    { label: '二分化（上下肢）', value: 'TWO_SPLIT', description: '练2休1，上肢+下肢循环' },
    { label: '三分化（推拉腿）', value: 'THREE_SPLIT', description: '练3休1，推+拉+腿循环' },
    { label: '四分化（胸背肩腿）', value: 'FOUR_SPLIT', description: '练2休1循环' }
]

export const SESSION_TYPE_MAP = {
    'warmup': { label: '热身激活', color: '#FF9F00', icon: '🔥' },
    'main': { label: '正式训练', color: '#007AFF', icon: '💪' },
    'cooldown': { label: '拉伸放松', color: '#34C759', icon: '🧘' }
}

export const DIFFICULTY_MAP = {
    '初级': { label: '初级', color: '#34C759' },
    '中级': { label: '中级', color: '#FF9F00' },
    '高级': { label: '高级', color: '#FF4444' }
}

export const SCHEDULE_STATUS = {
    'PLANNED': { label: '计划中', color: '#007AFF' },
    'COMPLETED': { label: '已完成', color: '#34C759' },
    'POSTPONED': { label: '已延后', color: '#FF9F00' },
    'REST': { label: '休息日', color: '#999999' }
}

export const ACTION_CATEGORY_MAP = {
    'warmup': '热身激活',
    'main_strength': '力量训练',
    'main_cardio': '有氧训练',
    'cooldown': '拉伸放松'
}

export const DEFAULT_REST_SECONDS = 60
export const MIN_REST_SECONDS = 30
export const MAX_REST_SECONDS = 300
export const DEFAULT_SETS = 4
export const DEFAULT_REPS = 12
export const DEFAULT_DURATION_MINUTES = 30

export const API_V2 = {
    PLAN_GENERATE: '/api/plan/v2/generate',
    PLAN_LIST: '/api/plan/v2/getAllPlan',
    PLAN_DETAIL: '/api/plan/v2/getPlan',
    PLAN_UPDATE: '/api/plan/v2/updatePlan',
    PLAN_DELETE: '/api/plan/v2/deletePlan',
    PLAN_ADD_ACTION: '/api/plan/v2/addAction',
    PLAN_UPDATE_ACTION: '/api/plan/v2/updateAction',
    PLAN_DELETE_ACTION: '/api/plan/v2/deleteAction',
    PLAN_REPLACE_ACTION: '/api/plan/v2/replaceAction',
    SCHEDULE_LIST: '/api/plan/v2/schedule',
    SCHEDULE_POSTPONE: '/api/plan/v2/postponeSchedule'
}

export const API = {
    REGISTER: '/api/auth/register',
    LOGIN: '/api/auth/login',
    RESET_PASSWORD: '/api/auth/reset-password',
    USER_ME: '/api/auth/me',
    SEND_CODE: '/api/auth/send-verification-code',
    VERIFY_CODE: '/api/auth/verify-code',
    USER_BODY_DATA: '/api/user/body-data',
    USER_PROFILE: '/api/user/profile',
    USER_SECURITY_PHONE: '/api/user/security/phone',
    USER_SECURITY_PASSWORD: '/api/user/security/password',
    USER_SECURITY: '/api/user/security',
    CHECK_PROFILE_COMPLETE: '/api/user/check-profile-complete',

    EQUIPMENT_DETECT: '/api/equipment/detect',
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

    ACTION_RECOMMEND: '/api/action/recommend',
    ACTION_DETAIL: '/api/action/detail',
    ACTION_LIBRARY: '/api/action/library',
    ACTION_MUSCLES: '/api/action/muscles',
    ACTION_QUERY: '/api/action/query',

    PLAN_GENERATE: '/api/plan/generate',
    PLAN_LIST: '/api/plan/',
    PLAN_DETAIL: '/api/plan',
    PLAN_DELETE: '/api/plan',
    PLAN_UPDATE: '/api/plan',
    PLAN_EDITNAME: 'api/plan/editName',
    PLAN_ADD_ACTION: '/api/plan/addActions',
    PLAN_UPDATE_ACTION: '/api/plan/editActions',
    PLAN_DELETE_ACTION: '/api/plan/deleteActions',
    PLAN_EXTEND: '/api/plan/extend'
}

export const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    TOKEN_EXPIRE_MINUTES: 60,
    CODE_EXPIRE_SECONDS: 300,
    CODE_COUNTDOWN_SECONDS: 60,
    PLAN_VALID_DAYS: 30,
    PLAN_DURATION_MIN: 40,
    PLAN_DURATION_MAX: 65
}
//密码需 8 位以上，含大小写字母、数字和特殊符号!@#$%^&*()_+-=
export const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=-]).{8,}$/
// 手机号码需以 1 开头，第二位为 3-9 的数字，后续为 9 位数字
export const PHONE_REGEX = /^1[3-9]\d{9}$/