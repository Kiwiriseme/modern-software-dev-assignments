# 网页记事本 (Web Notepad)

一款现代化的笔记与待办事项管理应用，采用日式禅意美学设计灵感。

**技术栈：** Vue 3 + Vite + Pinia + Django + Django REST Framework + SQLite

## 功能特性

### 笔记管理
- 创建、编辑、删除文本笔记
- Markdown 渲染支持
- 按分类组织笔记（工作/学习/生活/想法 + 自定义分类）
- 搜索和分类筛选
- 分页浏览

### 待办事项
- 创建、编辑、删除待办事项
- 标记完成/未完成（乐观更新）
- 设置截止日期
- AI 智能提取笔记中的待办事项（需配置 AI API）

### 界面特色
- 日式禅意美学设计（和纸质感背景）
- 三栏布局：侧边栏 / 内容区 / 详情面板
- 亮色/暗色主题切换
- 响应式设计

## 前置条件

- Python 3.10+
- Node.js 18+
- npm 9+

## 安装与运行

### 1. 后端 (Django)

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 执行数据库迁移
python manage.py migrate

# 启动开发服务器 (端口 8000)
python manage.py runserver
```

### 2. 前端 (Vue 3 + Vite)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (端口 5173)
npm run dev
```

### 3. 打开应用

访问 `http://localhost:5173`

Vite 开发服务器会将 `/api/*` 请求代理到 Django 后端（端口 8000）。

## 项目结构

```
web-notepad/
├── backend/                # Django REST API
│   ├── config/             # 项目配置 (settings, urls, wsgi, asgi)
│   └── notes/              # 笔记应用
│       ├── models.py       # 数据模型 (Note, Todo, Category, AISettings)
│       ├── serializers.py  # DRF 序列化器
│       ├── views.py       # 视图集与业务逻辑
│       ├── urls.py         # API 路由
│       └── ai_service.py   # AI 服务集成
├── frontend/               # Vue 3 单页应用
│   └── src/
│       ├── components/     # UI 组件
│       │   ├── Sidebar.vue       # 侧边栏（分类导航）
│       │   ├── ContentArea.vue    # 内容区（列表/看板）
│       │   ├── DetailPanel.vue    # 详情面板
│       │   ├── TodoList.vue       # 待办列表
│       │   ├── NoteCards.vue      # 笔记卡片网格
│       │   ├── ConfirmDialog.vue  # 确认对话框
│       │   ├── SettingsDialog.vue # AI 设置弹窗
│       │   └── ...
│       ├── views/
│       │   └── MainLayout.vue     # 主页面布局
│       ├── stores/
│       │   └── notes.js           # Pinia 状态管理
│       ├── api/
│       │   └── index.js           # Axios HTTP 客户端
│       ├── router/
│       │   └── index.js           # Vue Router 配置
│       └── utils/
│           └── categories.js      # 分类工具
├── docs/                  # 设计文档与开发计划
│   ├── specs/             # 功能设计规格
│   └── plans/             # 开发计划
└── README.md
```

## 数据模型

| 模型 | 字段 | 说明 |
|------|------|------|
| Note | title, content, category, created_at, updated_at | 笔记 |
| Todo | title, completed, category, due_date, created_at | 待办事项 |
| Category | name, color | 分类 |
| AISettings | api_type, api_key, base_url, model | AI API 配置 |

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/todos/` | GET, POST | 列表/创建待办 |
| `/api/todos/{id}/` | GET, PUT, PATCH, DELETE | 单个待办操作 |
| `/api/notes/` | GET, POST | 列表/创建笔记 |
| `/api/notes/{id}/` | GET, PUT, PATCH, DELETE | 单个笔记操作 |
| `/api/notes/{id}/summarize-todos/` | POST | AI 提取待办 |
| `/api/categories/` | GET | 获取分类列表 |
| `/api/ai-settings/` | GET, POST | AI 设置 |

## 配置说明

### AI 功能配置
应用支持 OpenAI 兼容 API（需自行配置 API Key）。首次使用 AI 功能时会提示进行设置。

### 主题切换
点击顶部工具栏的主题切换按钮可在亮色/暗色主题间切换，偏好设置会保存在浏览器本地存储。

## 已知限制

- 单用户本地使用场景，暂无认证系统
- 无批量操作功能
- Google OAuth 和高级 AI 功能不在本版本范围内

## 开发相关

```bash
# 前端构建生产版本
npm run build

# 预览生产构建
npm run preview
```
