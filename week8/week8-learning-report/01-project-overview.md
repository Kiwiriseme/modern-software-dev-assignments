# Week8 网页记事本 (Web Notepad) - 项目总览

## 1. 项目简介

这是一个**现代化的笔记与待办事项管理应用**，名为"网页记事本"（Web Notepad）。它采用了日式禅意美学设计灵感，提供优雅的笔记管理和待办事项追踪功能，还集成了AI智能功能。

---

## 2. 技术栈分析

### 前端技术栈
| 技术 | 版本/说明 | 作用 |
|------|----------|------|
| **Vue 3** | 最新稳定版 | 前端框架，使用Composition API |
| **Vite** | 最新版 | 构建工具和开发服务器 |
| **Pinia** | 最新版 | 状态管理（类似Vuex但更简单） |
| **Vue Router** | 最新版 | 页面路由管理 |

### 后端技术栈
| 技术 | 版本/说明 | 作用 |
|------|----------|------|
| **Python** | 3.10+ | 编程语言 |
| **Django** | 最新版 | Python Web框架 |
| **Django REST Framework** | 最新版 | 构建RESTful API |
| **SQLite** | 内置 | 数据库（轻量级，无需安装） |

---

## 3. 项目解决问题

这个应用解决了以下问题：

1. **笔记管理** - 让你创建、编辑、删除和组织文本笔记
2. **待办事项追踪** - 创建待办事项，设置截止日期，标记完成
3. **分类组织** - 使用预设分类（工作/学习/生活/想法）或自定义分类
4. **搜索筛选** - 快速找到需要的内容
5. **AI智能提取** - 从笔记内容中自动提取待办事项（需要配置API）

---

## 4. 项目整体架构

```
week8/web app/
├── backend/                 # Django后端
│   ├── config/               # Django项目配置
│   │   ├── settings.py      # 项目设置（数据库、已安装应用等）
│   │   ├── urls.py          # URL路由配置
│   │   ├── wsgi.py          # WSGI入口（用于部署）
│   │   └── asgi.py          # ASGI入口（用于异步）
│   ├── notes/               # 笔记应用（核心业务逻辑）
│   │   ├── models.py        # 数据模型定义
│   │   ├── serializers.py   # 数据序列化（JSON转换）
│   │   ├── views.py        # 视图和业务逻辑
│   │   ├── urls.py         # API路由
│   │   └── ai_service.py   # AI服务集成
│   └── manage.py            # Django管理脚本
│
└── frontend/                # Vue前端
    ├── src/
    │   ├── components/      # Vue组件
    │   │   ├── Sidebar.vue        # 侧边栏
    │   │   ├── ContentArea.vue    # 内容区域
    │   │   ├── DetailPanel.vue    # 详情面板
    │   │   ├── TodoList.vue       # 待办列表
    │   │   ├── NoteCards.vue      # 笔记卡片
    │   │   └── ...                # 其他组件
    │   ├── stores/           # Pinia状态管理
    │   │   └── notes.js
    │   ├── views/
    │   │   └── MainLayout.vue    # 主布局
    │   ├── api/
    │   │   └── index.js          # API调用
    │   └── main.js               # Vue入口
    ├── index.html
    └── package.json
```

---

## 5. 数据模型

应用中有3个主要的数据模型：

### Todo（待办事项）
```
- id: 自动编号
- title: 标题（必填，最多200字符）
- content: 内容（可选）
- category: 分类（工作/学习/生活/想法/自定义）
- due_date: 截止日期
- is_completed: 是否完成（布尔值）
- created_at: 创建时间
- updated_at: 更新时间
```

### Note（笔记）
```
- id: 自动编号
- title: 标题（必填，最多200字符）
- content: 内容（可选，支持Markdown）
- category: 分类
- created_at: 创建时间
- updated_at: 更新时间
```

### AISettings（AI设置）
```
- api_key: API密钥
- base_url: API地址
- model: 使用的AI模型
- updated_at: 更新时间
```
这是一个"单例"模型 - 整个系统只有一条设置记录。

---

## 6. 前端-后端交互流程

```
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器                              │
├─────────────────────────────────────────────────────────────┤
│  Vue.js 前端 (localhost:5173)                               │
│    │                                                         │
│    │  用户操作（如点击按钮）                                  │
│    ▼                                                         │
│  Pinia Store (notes.js)  ────── 管理应用状态                  │
│    │                                                         │
│    │  调用API函数                                            │
│    ▼                                                         │
│  API模块 (api/index.js)  ────── 封装HTTP请求                  │
│    │                                                         │
│    │  发送请求到 /api/*                                      │
│    ▼                                                         │
└────│─────────────────────────────────────────────────────────┘
     │  Vite代理转发请求
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Django后端 (localhost:8000)                                │
│    │                                                         │
│    │  URL路由 (config/urls.py → notes/urls.py)               │
│    ▼                                                         │
│  ViewSet视图 (views.py)  ────── 处理CRUD操作                 │
│    │                                                         │
│    │  调用Serializer序列化数据                               │
│    ▼                                                         │
│  Model模型 (models.py)  ────── 与SQLite数据库交互             │
│    │                                                         │
└────▼─────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  SQLite 数据库 (db.sqlite3)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 关键功能说明

### 7.1 CRUD操作
- **C**reate - 创建新的笔记/待办
- **R**ead - 读取列表和详情
- **U**pdate - 更新内容
- **D**elete - 删除记录

### 7.2 分类和搜索
- 按分类筛选（侧边栏点击分类）
- 关键词搜索（支持标题和内容模糊匹配）

### 7.3 分页
- 每页显示20条记录
- 支持翻页导航

### 7.4 AI功能
- 从笔记内容中提取待办事项
- 需要用户配置AI API密钥

### 7.5 主题切换
- 支持亮色/暗色主题
- 主题设置保存在浏览器本地

---

## 8. 设计风格

应用采用了**日式禅意美学**设计：
- 纸质感背景
- 温暖的色调（米色、棕色、绿色点缀）
- 三栏布局：侧边栏 / 内容区 / 详情面板
- 使用 Noto Serif SC 衬线字体作为标题
- 圆润的边角和柔和的阴影

---

## 9. 如何运行项目

### 后端启动
```bash
cd week8/web app/backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 前端启动
```bash
cd week8/web app/frontend
npm install
npm run dev
```

然后访问 http://localhost:5173

---

## 10. 总结

这是一个**全栈Web应用**典型示例：
- **前端**：Vue 3 + Vite + Pinia，负责用户界面和交互
- **后端**：Django + DRF，负责数据处理和存储
- **API**：RESTful风格，前后端通过JSON数据通信

理解这个项目的关键是掌握：
1. Vue组件化开发思想
2. Pinia状态管理
3. Django REST Framework的ViewSet和Serializer
4. 前后端分离架构的基本原理
