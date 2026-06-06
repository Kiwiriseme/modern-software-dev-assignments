# Week8 项目学习路线图

## 学习目标
本学习路线旨在帮助初学者从头理解这个 Vue 3 + Django 全栈项目。我们将按照**从简单到复杂、从外围到核心**的顺序学习。

---

## 学习顺序安排

### 第一阶段：了解整体结构（容易）

#### 1. 先读 README.md
**为什么从这里开始？**
- README是项目的"门脸"，包含项目简介、功能特性、技术栈和运行方法
- 读完后你能回答："这是一个什么项目？用什么技术做的？"

**重点理解：**
- 技术栈：Vue 3 + Vite + Pinia + Django + DRF + SQLite
- 三栏布局：侧边栏 / 内容区 / 详情面板
- 两个主要功能：笔记管理 + 待办事项

---

### 第二阶段：理解前端入口（简单）

#### 2. frontend/index.html
**为什么从这里开始？**
- 这是浏览器加载的第一个文件，是Vue应用的入口点
- 简单，容易理解

**需要理解的概念：**
- `<div id="app">` - Vue.js挂载的位置
- `<script type="module" src="/src/main.js">` - 告诉浏览器从这里加载JavaScript

#### 3. frontend/src/main.js
**为什么从这里开始？**
- 这是Vue应用的初始化文件
- 包含Vue实例的创建过程

**需要理解的概念：**
```javascript
import { createApp } from 'vue'      // 从vue包导入创建应用函数
import App from './App.vue'         // 导入根组件
import router from './router'       // 导入路由配置
import { createPinia } from 'pinia' // 导入状态管理

const app = createApp(App)          // 创建Vue应用实例
app.use(createPinia())              // 使用Pinia状态管理
app.use(router)                     // 使用路由
app.mount('#app')                   // 挂载到HTML的#app位置
```

---

### 第三阶段：理解Vue组件结构（中等）

#### 4. frontend/src/App.vue
**为什么从这里开始？**
- App.vue是根组件，里面只包含`<router-view />`
- 理解路由的工作方式

**需要理解的概念：**
- `<router-view />` - 路由视图，类似于"占位符"，显示当前路由对应的组件
- 整个应用实际上是通过路由跳转到不同的页面

#### 5. frontend/src/views/MainLayout.vue
**为什么从这里开始？**
- 这是应用的主要布局组件
- 包含侧边栏、内容区、详情面板等主要UI部分
- 使用了大量的Vue组件组合

**需要理解的概念：**
```vue
<template>
  <div class="main-layout">
    <Sidebar @delete-category="onRequestDeleteCategory" />
    <ContentArea @select="onSelect" @create="onCreate" @toast="showToast" />
    <DetailPanel ref="detailPanelRef" @toast="showToast" ... />
    <Toast :message="toastMessage" :type="toastType" :trigger="toastTrigger" />
    ...
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useNotesStore } from '../stores/notes.js'  // 导入状态管理
import Sidebar from '../components/Sidebar.vue'    // 导入子组件

const store = useNotesStore()  // 创建store实例
</script>
```

**重点理解：**
- 组件之间的父子关系和通信
- `@`符号是`v-on`的简写，用于监听事件
- `ref()`创建响应式变量

---

### 第四阶段：理解状态管理（中等难度）

#### 6. frontend/src/stores/notes.js
**为什么从这里开始？**
- Pinia store是前端的数据中心
- 所有组件都从这里获取和修改数据
- 理解数据流向对理解整个应用至关重要

**需要理解的概念：**

```javascript
import { defineStore } from 'pinia'  // 导入Pinia
import { ref } from 'vue'            // 导入ref创建响应式数据

export const useNotesStore = defineStore('notes', () => {
  // ======= 状态定义 =======
  const todos = ref([])       // 待办事项列表
  const notes = ref([])      // 笔记列表
  const activeTab = ref('todo')  // 当前激活的标签（todo/note）
  
  // ======= 方法定义 =======
  async function loadTodos() {
    // 加载待办事项
  }
  
  async function loadNotes() {
    // 加载笔记
  }
  
  // ======= 返回状态和方法 =======
  return { todos, notes, activeTab, loadTodos, loadNotes }
})
```

**重点理解：**
- `defineStore` - 定义一个store
- `ref()` - 创建响应式数据（当数据变化时，UI自动更新）
- `async/await` - 异步操作，用于API调用
- store是全局的，任何组件都可以访问

---

### 第五阶段：理解API调用（中等难度）

#### 7. frontend/src/api/index.js
**为什么从这里开始？**
- 这里封装了所有向后端发送请求的函数
- 理解HTTP请求是如何发送的

**需要理解的概念：**

```javascript
import api from './index'

// 获取所有待办
export const fetchTodos = (params) => api.get('/todos/', { params })

// 创建待办
export const createTodo = (data) => api.post('/todos/', data)

// 更新待办
export const updateTodo = (id, data) => api.put(`/todos/${id}/`, data)

// 删除待办
export const deleteTodo = (id) => api.delete(`/todos/${id}/`)
```

**重点理解：**
- `api.get()` - 发送GET请求
- `api.post()` - 发送POST请求（创建数据）
- `api.put()` - 发送PUT请求（更新数据）
- `api.delete()` - 发送DELETE请求
- `params` - URL查询参数（如?page=1&category=工作）
- `data` - 请求体数据（JSON格式）

---

### 第六阶段：理解后端Django（较难）

#### 8. backend/notes/models.py
**为什么从这里开始？**
- 数据模型是后端的基础
- 定义了数据库表的结构

**需要理解的概念：**

```python
from django.db import models  # Django的模型基类

class Todo(models.Model):
    # CharField - 短文本（需要指定max_length）
    title = models.CharField(max_length=200)
    
    # TextField - 长文本（可以存储大量文字）
    content = models.TextField(blank=True, default="")
    
    # CharField - 存储分类选择
    category = models.CharField(max_length=50, blank=True, default="")
    
    # DateField - 日期字段
    due_date = models.DateField(null=True, blank=True)
    
    # BooleanField - 布尔值（True/False）
    is_completed = models.BooleanField(default=False)
    
    # DateTimeField - 日期时间，自动设置
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时自动设置
    updated_at = models.DateTimeField(auto_now=True)      # 每次保存时自动更新
    
    # Meta类 - 模型的元数据
    class Meta:
        ordering = ["-created_at"]  # 默认按创建时间倒序排列
    
    # __str__方法 - 返回对象的字符串表示
    def __str__(self):
        return self.title
```

**重点理解：**
- `models.Model` - Django模型基类
- `CharField` vs `TextField` - 短文本vs长文本
- `blank=True` - 表单允许为空
- `null=True` - 数据库允许NULL
- `default=` - 默认值
- `auto_now_add=True` - 创建时自动设置时间

#### 9. backend/notes/serializers.py
**为什么从这里开始？**
- Serializer将Django模型转换为JSON
- 也负责验证输入数据

**需要理解的概念：**

```python
from rest_framework import serializers
from .models import Todo, Note, AISettings

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo  # 指定对应的模型
        fields = ['id', 'title', 'content', 'category', 'due_date', 
                  'is_completed', 'created_at', 'updated_at']
        # fields指定要序列化的字段
    
    # 如果需要，可以添加额外的验证逻辑
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("标题不能为空")
        return value
```

**重点理解：**
- `ModelSerializer` - 自动根据模型生成序列化器
- `fields` - 指定哪些字段需要转换
- `ValidationError` - 验证失败时抛出错误

#### 10. backend/notes/views.py
**为什么从这里开始？**
- 视图是业务逻辑的核心
- 处理HTTP请求并返回响应

**需要理解的概念：**

```python
from rest_framework import viewsets
from .models import Todo
from .serializers import TodoSerializer

class TodoViewSet(viewsets.ModelViewSet):
    # ModelViewSet提供了完整的CRUD功能：
    # - list:   GET /todos/     - 获取列表
    # - create: POST /todos/    - 创建
    # - retrieve: GET /todos/1/ - 获取单个
    # - update: PUT /todos/1/  - 更新
    # - partial_update: PATCH /todos/1/ - 部分更新
    # - destroy: DELETE /todos/1/ - 删除
    
    serializer_class = TodoSerializer  # 使用TodoSerializer
    
    def get_queryset(self):
        # 返回查询集，可以在这里添加过滤逻辑
        return Todo.objects.all()
```

**重点理解：**
- `viewsets.ModelViewSet` - 提供完整的CRUD视图
- `queryset` - 查询数据库用的结果集
- `serializer_class` - 指定序列化器

#### 11. backend/notes/urls.py
**为什么从这里开始？**
- URL配置将HTTP请求路由到正确的视图

**需要理解的概念：**

```python
from rest_framework.routers import DefaultRouter
from .views import TodoViewSet, NoteViewSet, AISettingsViewSet

router = DefaultRouter()
router.register(r'todos', TodoViewSet)  # 注册路由
router.register(r'notes', NoteViewSet)
router.register(r'ai-settings', AISettingsViewSet)

urlpatterns = router.urls  # 导出路由列表
```

**重点理解：**
- `DefaultRouter` - 自动生成RESTful URL
- `router.register()` - 注册视图集
- `/api/todos/` - 列表
- `/api/todos/1/` - 单个

---

### 第七阶段：理解AI功能（较难）

#### 12. backend/notes/ai_service.py
**为什么从这里开始？**
- 这是AI集成的核心代码
- 使用外部API来生成内容

**需要理解的概念：**
- 如何调用外部API
- 错误处理
- 返回数据格式

---

## 学习建议

1. **不要急于求成**：每个文件都仔细阅读，不懂的概念要及时查资料
2. **动手实践**：尝试修改代码，看效果变化
3. **画图理解**：尝试画出数据流向图
4. **对比学习**：对比前端store和后端models的结构

---

## 快速参考：文件阅读顺序

| 顺序 | 文件路径 | 难度 | 重要性 |
|------|---------|------|--------|
| 1 | README.md | ★☆☆☆☆ | ★★★★★ |
| 2 | frontend/index.html | ★☆☆☆☆ | ★★★★☆ |
| 3 | frontend/src/main.js | ★★☆☆☆ | ★★★★☆ |
| 4 | frontend/src/App.vue | ★★☆☆☆ | ★★★☆☆ |
| 5 | frontend/src/views/MainLayout.vue | ★★★☆☆ | ★★★★★ |
| 6 | frontend/src/stores/notes.js | ★★★★☆ | ★★★★★ |
| 7 | frontend/src/api/index.js | ★★★☆☆ | ★★★★★ |
| 8 | backend/notes/models.py | ★★★☆☆ | ★★★★★ |
| 9 | backend/notes/serializers.py | ★★★☆☆ | ★★★★☆ |
| 10 | backend/notes/views.py | ★★★★☆ | ★★★★★ |
| 11 | backend/notes/urls.py | ★★☆☆☆ | ★★★★☆ |
| 12 | backend/notes/ai_service.py | ★★★★★ | ★★★☆☆ |
