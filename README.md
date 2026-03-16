D:\FitnessGraduationProject\
├── 01_DeepLearning\                 # [阶段 2] 深度学习模型训练目录
│   ├── datasets\                    # 数据集 (≥500 张标注图片)
│   │   ├── images\                  # 训练集/验证集/测试集图片
│   │   └── labels\                  # YOLO 格式标注文件
│   ├── models\                      # 模型权重
│   │   ├── best.pt                  # PyTorch 训练权重
│   │   └── best.onnx                # [关键] 导出用于后端部署的 ONNX 模型
│   ├── scripts\                     # 训练与导出脚本
│   │   ├── train.py                 # YOLOv5 训练脚本
│   │   └── export.py                # 模型导出脚本
│   └── docs\                        # 训练日志、混淆矩阵、准确率报告
│
├── 02_Backend\                      # [阶段 3-4] 后端系统目录 (FastAPI)
│   ├── venv\                        # [关键] Python 虚拟环境 (建议在 D 盘此目录下创建)
│   ├── app\                         # 核心代码目录
│   │   ├── __init__.py
│   │   ├── main.py                  # 应用入口 (UVicorn 启动点)
│   │   ├── core\                    # 核心配置
│   │   │   ├── config.py            # 读取 .env 配置 (数据库、密钥)
│   │   │   ├── security.py          # JWT 认证、密码加密 (Passlib)
│   │   │   └── exceptions.py        # 自定义异常处理
│   │   ├── models\                  # [对应需求 2.2] 数据库 ORM 模型 (7 个业务对象)
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User 对象 (userId, fitnessGoal, etc.)
│   │   │   ├── equipment.py         # EquipmentInventory, GymEquipment 对象
│   │   │   ├── action.py            # TrainingAction 对象 (≥100 个动作)
│   │   │   └── plan.py              # TrainingPlan, PlanSession, SessionActionItem 对象
│   │   ├── schemas\                 # Pydantic 数据验证模型 (请求/响应)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── equipment.py
│   │   │   └── plan.py
│   │   ├── api\                     # [对应需求 3.2] API 路由接口 (用例实现)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # 注册、登录、忘记密码
│   │   │   ├── user.py              # 编辑身体数据、个人资料
│   │   │   ├── equipment.py         # 识别器材、管理健身房、添加/删除器材
│   │   │   └── plan.py              # 生成训练计划、推荐动作
│   │   ├── services\                # 业务逻辑层 (核心算法)
│   │   │   ├── __init__.py
│   │   │   ├── detection.py         # 调用 ONNX 模型进行推理 (响应时间<2 秒)
│   │   │   ├── recommendation.py    # 动作推荐算法 (匹配器材与用户经验)
│   │   │   └── plan_generator.py    # 训练计划生成引擎 (三阶段逻辑、时长计算)
│   │   ├── utils\                   # 工具函数
│   │   │   ├── db.py                # 数据库会话管理
│   │   │   └── image_processor.py   # 图片预处理 (OpenCV)
│   │   └── resources\               # 静态资源
│   │       └── models\              # [关键] 存放 best.onnx 模型文件
│   │           └── best.onnx
│   ├── tests\                       # 单元测试 (pytest)
│   ├── .env                         # 环境变量 (数据库连接、密钥)
│   ├── .gitignore                   # Git 忽略文件 (忽略 venv, __pycache__)
│   ├── requirements.txt             # Python 依赖列表
│   ├── Dockerfile                   # 容器化部署配置
│   └── README.md                    # 后端说明文档
│
├── 03_Frontend\                     # [阶段 4] 前端小程序目录 (Uni-app)
│   ├── components\                  # 公共组件
│   ├── pages\                       # [对应需求 4] 页面原型 (17 个页面)
│   │   ├── login\                   # 图 4-1 登录
│   │   ├── register\                # 图 4-2 注册
│   │   ├── forget-password\         # 图 4-3, 4-4 忘记密码
│   │   ├── index\                   # 图 4-5 首页
│   │   ├── action-library\          # 图 4-6 动作库
│   │   ├── action-detail\           # 图 4-7 动作详情
│   │   ├── gym-list\                # 图 4-8 健身房列表
│   │   ├── equipment-list\          # 图 4-9 器材清单
│   │   ├── add-equipment\           # 图 4-10, 4-11 手动添加
│   │   ├── add-gym\                 # 图 4-12, 4-14 添加健身房
│   │   ├── camera-scan\             # 图 4-13 拍摄识别
│   │   ├── plan-list\               # 图 4-15 训练计划
│   │   └── generate-plan\           # 图 4-16, 4-17 生成与保存
│   ├── static\                      # 静态图片、图标
│   ├── store\                       # Pinia 状态管理 (用户信息、全局配置)
│   ├── utils\                       # 工具 (axios 请求封装、常量)
│   ├── App.vue                      # 小程序入口
│   ├── main.js                      # 初始化入口
│   ├── manifest.json                # 应用配置 (小程序 AppID 等)
│   ├── pages.json                   # 页面路由配置
│   ├── uni.scss                     # 全局样式
│   └── README.md                    # 前端说明文档
│
├── 04_Docs\                         # [阶段 7] 文档与论文材料
│   ├── 原始文档\                    # 存放您上传的三个 PDF
│   │   ├── 6322000326-吉雅 - 需求规格说明书 -2026.02.21.pdf
│   │   ├── 6322000326_吉雅_开题报告_260125.pdf
│   │   └── 6322000326_吉雅_任务书_260122.pdf
│   ├── 设计文档\                    # 后续生成的文档
│   │   ├── 数据库设计 ER 图.png
│   │   ├── 系统架构图.png
│   │   └── API 接口文档.md
│   └── 论文\                        # 论文初稿、定稿
│
├── .gitignore                       # 全局忽略文件
└── README.md                        # 项目总说明 (含启动步骤)
