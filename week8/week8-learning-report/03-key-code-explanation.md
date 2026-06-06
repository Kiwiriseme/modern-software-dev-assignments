# Week8 关键代码详解

## 1. Pinia Store（前端状态管理）

**文件位置**：`frontend/src/stores/notes.js`

这是整个前端应用的数据中心。让我逐段解释：

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  fetchTodos,
  fetchNotes,
  // ... 其他API函数
} from '../api/index.js'
```

**解释**：
- `defineStore` - Pinia提供的函数，用来创建一个"store"（数据仓库）
- `ref` - Vue 3的响应式API，当ref包装的值变化时，使用它的地方会自动更新
- `fetchTodos`等 - 从api模块导入的API调用函数

---

```javascript
export const useNotesStore = defineStore('notes', () => {
```

**解释**：
- `defineStore('notes', ...)` - 创建名为'notes'的store
- 第二个参数是一个函数，在里面定义状态和方法
- `useNotesStore` - 约定俗成的命名方式（以use开头）

---

```javascript
  // ======= 状态定义 =======
  const todos = ref([])           // 待办列表，初始为空数组
  const notes = ref([])           // 笔记列表，初始为空数组
  const categories = ref([])      // 分类列表
  const activeTab = ref('todo')   // 当前激活的标签，'todo'或'note'
  const activeCategory = ref('全部')  // 当前选中的分类
  const searchQuery = ref('')     // 搜索关键词
  const selectedItem = ref(null)  // 当前选中的项目
```

**解释**：
- `ref([])` - 创建一个响应式的空数组
- 这些变量都是"响应式"的 - 当你修改它们时，UI会自动更新
- 例如：`todos.value = [{title: '新待办'}]` 会让页面上的待办列表自动显示新内容

---

```javascript
  async function loadTodos() {
    isTodosLoading.value = true   // 开始加载，显示loading状态
    error.value = null            // 清空之前的错误
    
    try {
      const params = getListParams()  // 获取查询参数（分页、分类、搜索）
      const res = await fetchTodos(params)  // 发送API请求
      todos.value = res.data.results  // 更新数据
      totalCount.value = res.data.count  // 更新总数
    } catch (e) {
      error.value = e.response?.data?.detail || e.message  // 保存错误信息
      throw e  // 重新抛出错误，让调用者知道出错了
    } finally {
      isTodosLoading.value = false  // 结束加载
    }
  }
```

**解释**：
- `async function` - 异步函数，用于处理需要等待的操作（如API请求）
- `await` - 等待Promise完成后再继续执行
- `try...catch...finally` - 错误处理结构
- `fetchTodos(params)` - 发送HTTP GET请求到 `/api/todos/`
- `res.data` - 服务器返回的JSON数据
- `res.data.results` - 列表数据
- `res.data.count` - 总记录数（用于分页）

---

```javascript
  return {
    todos,
    notes,
    categories,
    activeTab,
    // ... 其他状态和方法
  }
})
```

**解释**：
- `return` - 暴露给外部使用的内容
- 只有return的东西才能在组件中访问

---

## 2. Vue组件模板

**文件位置**：`frontend/src/views/MainLayout.vue`

```vue
<template>
  <div class="main-layout">
    <!-- 
      @delete-category 是 v-on:delete-category 的简写
      意思是监听 Sidebar 组件触发的 delete-category 事件
    -->
    <Sidebar @delete-category="onRequestDeleteCategory" />
    
    <!-- 
      :message 是 v-bind:message 的简写
      意思是把 toastMessage 的值传给 Toast 组件的 message prop
    -->
    <Toast
      :message="toastMessage"
      :type="toastType"
      :trigger="toastTrigger"
    />
  </div>
</template>
```

**关键概念**：
| 语法 | 全写 | 含义 |
|------|------|------|
| `@click` | `v-on:click` | 监听点击事件 |
| `:message` | `v-bind:message` | 绑定变量到prop |
| `v-model` | - | 双向绑定（输入框常用）|

---

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useNotesStore } from '../stores/notes.js'

// 创建store实例
const store = useNotesStore()

// 响应式数据
const toastMessage = ref('')
const toastType = ref('error')
const toastTrigger = ref(0)

// 方法定义
function showToast({ message, type = 'error' }) {
  toastMessage.value = message
  toastType.value = type
  toastTrigger.value++  // 递增，用于触发Toast组件重新显示
}

// 生命周期钩子
onMounted(() => {
  store.loadTodos()  // 组件挂载后加载数据
  store.loadNotes()
})
</script>
```

**解释**：
- `ref()` - 创建响应式变量
- `ref(0)` - 数字0的响应式包装
- `onMounted()` - Vue 3的生命周期钩子，组件挂载后自动调用
- `store.loadTodos()` - 调用store的方法加载数据

---

## 3. Django Model（数据模型）

**文件位置**：`backend/notes/models.py`

```python
from datetime import date
from django.db import models
```

**解释**：
- `from datetime import date` - 导入日期类型
- `from django.db import models` - Django模型核心模块

---

```python
class Todo(models.Model):
    """待办事项模型"""
    
    # CharField: 短文本字段，必须指定 max_length
    # blank=True: 表单验证时允许为空
    # default="": 默认值为空字符串
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    
    # DateField: 日期字段
    # null=True: 数据库可以存储 NULL
    # blank=True: 表单可以留空
    due_date = models.DateField(null=True, blank=True, default=date.today)
    
    # BooleanField: 布尔字段
    is_completed = models.BooleanField(default=False)
    
    # DateTimeField: 日期时间字段
    # auto_now_add=True: 创建记录时自动设置为当前时间
    # auto_now=True: 每次保存时自动更新为当前时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Django字段类型对比**：

| 字段类型 | 用途 | 需要max_length |
|---------|------|---------------|
| CharField | 短文本 | 是 |
| TextField | 长文本（文章内容）| 否 |
| BooleanField | True/False | 否 |
| DateField | 日期 | 否 |
| DateTimeField | 日期+时间 | 否 |
| URLField | URL地址 | 否 |
| EmailField | 邮箱地址 | 否 |

---

```python
    class Meta:
        # ordering 定义默认排序方式
        # ["-created_at"] 负号表示倒序（最新的在前面）
        ordering = ["-created_at"]
    
    def __str__(self):
        # __str__方法定义对象的字符串表示
        # 在Django admin和调试时很有用
        return self.title
```

**解释**：
- `class Meta` - 模型的元数据（关于模型的数据）
- `ordering` - 默认排序规则
- `__str__` - 对象的字符串表示，类似Python的`__str__`方法

---

## 4. Django ViewSet（视图）

**文件位置**：`backend/notes/views.py`

```python
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from notes.models import Note, Todo
from notes.serializers import NoteSerializer, TodoSerializer
```

**解释**：
- `viewsets.ModelViewSet` - Django REST Framework的核心视图类，提供完整的CRUD功能
- `Response` - 返回JSON响应
- `@action` - 自定义动作装饰器，用于添加非标准的API端点

---

```python
class TodoViewSet(viewsets.ModelViewSet):
    """
    Todo的视图集
    自动提供以下API端点：
    GET    /todos/         - 列表
    POST   /todos/         - 创建
    GET    /todos/{id}/    - 详情
    PUT    /todos/{id}/    - 更新
    DELETE /todos/{id}/    - 删除
    """
    serializer_class = TodoSerializer
    
    def get_queryset(self):
        # 返回所有待办事项
        return Todo.objects.all()
```

**ModelViewSet自动提供的CRUD方法**：

| HTTP方法 | URL | 方法 | 功能 |
|----------|-----|------|------|
| GET | `/todos/` | list | 获取列表 |
| POST | `/todos/` | create | 创建 |
| GET | `/todos/{id}/` | retrieve | 获取单个 |
| PUT | `/todos/{id}/` | update | 完整更新 |
| PATCH | `/todos/{id}/` | partial_update | 部分更新 |
| DELETE | `/todos/{id}/` | destroy | 删除 |

---

```python
class NoteViewSet(BaseItemViewSet):
    serializer_class = NoteSerializer
    
    def get_queryset(self):
        return self.filter_queryset_by_params(Note.objects.all())
    
    @action(detail=True, methods=["post"], url_path="summarize-todos")
    def summarize_todos(self, request, pk=None):
        """调用AI从笔记内容中提取待办事项"""
        note = self.get_object()  # 获取当前笔记
        
        try:
            todos, count = summarize_note_todos(note)  # 调用AI服务
        except AINotConfiguredError:
            return Response(
                {"detail": "请先配置 API 设置"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = TodoSerializer(todos, many=True)
        return Response({"todos": serializer.data, "count": count})
```

**解释**：
- `@action(detail=True)` - 这是一个"详情"动作，需要指定具体对象
- `detail=True, methods=["post"]` - 创建 `/notes/{id}/summarize-todos/` 端点
- `self.get_object()` - 获取URL中指定的对象（pk=id的那个）
- `serializer.data` - 将对象转换为JSON
- `many=True` - 表示序列化多个对象（列表）

---

## 5. API调用（前端）

**文件位置**：`frontend/src/api/index.js`

```javascript
import api from './index'

export const fetchTodos = (params) => api.get('/todos/', { params })
```

**完整解释**：

```javascript
// api.get('/todos/', { params }) 
// 会被转换为：
// GET /api/todos/?page=1&page_size=20&category=工作
//
// api 是 axios 实例，已经配置了 baseURL: '/api'
// { params } 是axios的请求配置，会将对象转换为查询字符串
```

---

```javascript
export const createTodo = (data) => api.post('/todos/', data)

// 会被转换为：
// POST /api/todos/
// Body: { "title": "新待办", "content": "", "category": "工作" }
```

---

```javascript
export const updateTodo = (id, data) => api.put(`/todos/${id}/`, data)

// 会被转换为：
// PUT /api/todos/5/
// Body: { "title": "更新后的标题", ... }
```

---

```javascript
export const deleteTodo = (id) => api.delete(`/todos/${id}/`)

// 会被转换为：
// DELETE /api/todos/5/
```

---

## 6. BaseItemViewSet（共享过滤逻辑）

**文件位置**：`backend/notes/views.py`

```python
class BaseItemViewSet(viewsets.ModelViewSet):
    """共享过滤逻辑的基类"""
    
    def filter_queryset_by_params(self, queryset):
        # 获取URL查询参数
        category = self.request.query_params.get("category", None)
        q = self.request.query_params.get("q", None)
        
        # 按分类过滤
        if category and category != "全部":
            queryset = queryset.filter(category=category)
        
        # 按关键词搜索（标题或内容包含关键词）
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q) | models.Q(content__icontains=q)
            )
        
        return queryset
```

**解释**：
- `self.request.query_params` - 获取URL中的查询参数（?category=工作&q=关键词）
- `queryset.filter(category=category)` - SQL: `WHERE category = '工作'`
- `models.Q(...)` - 构建复杂查询
- `__icontains` - 不区分大小写的模糊匹配，相当于SQL的 `LIKE '%keyword%'`
- `|` - OR逻辑

---

## 7. AISettings（单例模式）

**文件位置**：`backend/notes/models.py`

```python
class AISettings(models.Model):
    """Singleton model - 整个系统只有一条记录"""
    
    api_key = models.CharField(max_length=512, blank=True, default="")
    base_url = models.URLField(default="https://api.openai.com/v1")
    model = models.CharField(max_length=100, default="gpt-4o-mini")
    updated_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def get_solo(cls):
        """获取唯一的AISettings实例，如果没有则创建一个"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

**解释**：
- `get_or_create(pk=1)` - 查找pk=1的记录，如果不存在则创建
- `@classmethod` - 类方法，可以直接用 `AISettings.get_solo()` 调用
- 返回的 `(obj, _)` 中，`_` 是布尔值，表示是否新创建

---

## 8. AI Service（AI集成）

**文件位置**：`backend/notes/ai_service.py`

```python
def summarize_note_todos(note):
    """
    调用AI从笔记内容中提取待办事项
    
    Args:
        note: Note模型实例
    
    Returns:
        tuple: (Todo实例列表, 数量)
    """
    # 1. 获取AI配置（单例模式）
    settings = AISettings.get_solo()
    
    # 2. 构建提示词
    prompt = f"""从以下笔记内容中提取所有待办事项，以JSON数组格式返回：
    
    笔记内容：
    {note.content}
    
    只返回JSON数组，格式如：
    [{{"title": "待办1", "category": "工作"}}, {{"title": "待办2", "category": "学习"}}]
    """
    
    # 3. 调用AI API
    response = openai.ChatCompletion.create(
        model=settings.model,
        messages=[{"role": "user", "content": prompt}],
        api_key=settings.api_key,
        base_url=settings.base_url,
    )
    
    # 4. 解析AI返回的内容
    # ... 省略解析逻辑 ...
    
    # 5. 创建Todo记录
    todos = []
    for item in parsed_items:
        todo = Todo.objects.create(
            title=item['title'],
            category=item.get('category', ''),
            content=note.content,
        )
        todos.append(todo)
    
    return todos, len(todos)
```

**解释**：
- `openai.ChatCompletion.create` - 调用OpenAI兼容的Chat API
- `messages` - 对话消息列表
- `api_key` 和 `base_url` - 从数据库读取的配置

---

## 总结：关键概念速查表

| 概念 | 文件 | 简单理解 |
|------|------|---------|
| `ref()` | Vue | 创建响应式变量 |
| `defineStore` | Pinia | 创建数据仓库 |
| `ModelViewSet` | DRF | 提供CRUD的视图类 |
| `ModelSerializer` | DRF | 模型与JSON的转换器 |
| `@action` | DRF | 添加自定义API端点 |
| `__icontains` | Django | SQL的LIKE模糊查询 |
| `get_or_create` | Django | 查找或创建记录 |
| `async/await` | JavaScript | 异步编程语法 |
