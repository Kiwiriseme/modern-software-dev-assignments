import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  fetchTodos,
  fetchNotes,
  fetchCategories,
  createTodo,
  createNote,
  fetchTodo,
  fetchNote,
  updateTodo,
  updateNote,
  patchTodo,
  deleteTodo,
  deleteNote,
  deleteCategory,
} from '../api/index.js'

export const useNotesStore = defineStore('notes', () => {
  const todos = ref([])
  const notes = ref([])
  const categories = ref([])
  const activeTab = ref('todo')
  const activeCategory = ref('全部')
  const searchQuery = ref('')
  const selectedItem = ref(null)
  const selectedType = ref(null)
  const isTodosLoading = ref(false)
  const isNotesLoading = ref(false)
  const isDetailLoading = ref(false)
  const error = ref(null)
  const deletedCategories = ref([])

  const currentPage = ref(1)
  const totalCount = ref(0)
  const pageSize = 20

  const todoCount = ref(0)
  const noteCount = ref(0)
  const isDirty = ref(false)
  const showLeaveConfirm = ref(false)
  const pendingLeave = ref(null)

  function getListParams() {
    const params = { page: currentPage.value, page_size: pageSize }
    if (activeCategory.value !== '全部') {
      params.category = activeCategory.value
    }
    if (searchQuery.value) {
      params.q = searchQuery.value
    }
    return params
  }

  async function loadTodos() {
    isTodosLoading.value = true
    error.value = null
    try {
      const params = getListParams()
      const res = await fetchTodos(params)
      todos.value = res.data.results
      totalCount.value = res.data.count
      todoCount.value = res.data.count
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || '加载待办失败'
      throw e
    } finally {
      isTodosLoading.value = false
    }
  }

  async function loadNotes() {
    isNotesLoading.value = true
    error.value = null
    try {
      const params = getListParams()
      const res = await fetchNotes(params)
      notes.value = res.data.results
      totalCount.value = res.data.count
      noteCount.value = res.data.count
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || '加载笔记失败'
      throw e
    } finally {
      isNotesLoading.value = false
    }
  }

  async function loadCategories() {
    try {
      const res = await fetchCategories()
      categories.value = res.data
    } catch (e) {
      console.error('Failed to load categories', e)
    }
  }

  function addCategory(name) {
    if (name && !categories.value.includes(name)) {
      categories.value.push(name)
      const idx = deletedCategories.value.indexOf(name)
      if (idx !== -1) {
        deletedCategories.value.splice(idx, 1)
      }
    }
  }

  async function addTodo(data) {
    const res = await createTodo(data)
    const hasFilter = activeCategory.value !== '全部' || searchQuery.value !== ''
    if (hasFilter || currentPage.value !== 1) {
      currentPage.value = 1
      await loadTodos()
    } else {
      todos.value.unshift(res.data)
      totalCount.value++
      todoCount.value++
      // 如果超出页面容量，移除最后一个
      if (todos.value.length > pageSize) {
        todos.value.pop()
      }
    }
    return res.data
  }

  async function addNote(data) {
    const res = await createNote(data)
    const hasFilter = activeCategory.value !== '全部' || searchQuery.value !== ''
    if (hasFilter || currentPage.value !== 1) {
      currentPage.value = 1
      await loadNotes()
    } else {
      notes.value.unshift(res.data)
      totalCount.value++
      noteCount.value++
      if (notes.value.length > pageSize) {
        notes.value.pop()
      }
    }
    return res.data
  }

  async function openDetail(id, type) {
    selectedType.value = type
    selectedItem.value = null
    isDetailLoading.value = true
    try {
      const fn = type === 'todo' ? fetchTodo : fetchNote
      const res = await fn(id)
      selectedItem.value = res.data
    } catch (e) {
      selectedType.value = null
      throw e
    } finally {
      isDetailLoading.value = false
    }
  }

  function closeDetail() {
    selectedItem.value = null
    selectedType.value = null
    isDirty.value = false
  }

  async function toggleTodoComplete(todo) {
    const item = todos.value.find(t => t.id === todo.id)
    const previousValue = item ? item.is_completed : todo.is_completed

    // 乐观更新列表中的项
    if (item) {
      item.is_completed = !item.is_completed
    }
    // 同步更新详情面板中可能单独持有的 selectedItem
    if (selectedItem.value && selectedItem.value.id === todo.id) {
      selectedItem.value = { ...selectedItem.value, is_completed: !previousValue }
    }
    try {
      await patchTodo(todo.id, { is_completed: !previousValue })
    } catch (e) {
      // 回滚
      if (item) {
        item.is_completed = previousValue
      }
      if (selectedItem.value && selectedItem.value.id === todo.id) {
        selectedItem.value = { ...selectedItem.value, is_completed: previousValue }
      }
      throw e
    }
  }

  async function saveTodoEdit(id, data) {
    const oldItem = todos.value.find(t => t.id === id)
    const oldData = oldItem ? { ...oldItem } : null
    try {
      const res = await updateTodo(id, data)
      if (oldItem) {
        Object.assign(oldItem, res.data)
      }
      if (selectedItem.value && selectedItem.value.id === id) {
        selectedItem.value = res.data
      }
      return res.data
    } catch (e) {
      if (oldItem && oldData) {
        Object.assign(oldItem, oldData)
      }
      throw e
    }
  }

  async function saveNoteEdit(id, data) {
    const oldItem = notes.value.find(n => n.id === id)
    const oldData = oldItem ? { ...oldItem } : null
    try {
      const res = await updateNote(id, data)
      if (oldItem) {
        Object.assign(oldItem, res.data)
      }
      if (selectedItem.value && selectedItem.value.id === id) {
        selectedItem.value = res.data
      }
      return res.data
    } catch (e) {
      if (oldItem && oldData) {
        Object.assign(oldItem, oldData)
      }
      throw e
    }
  }

  async function removeTodo(id) {
    await deleteTodo(id)
    const idx = todos.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      todos.value.splice(idx, 1)
      totalCount.value--
      todoCount.value--
    }
    if (todos.value.length === 0 && currentPage.value > 1) {
      currentPage.value = Math.max(1, currentPage.value - 1)
      await loadTodos()
    }
  }

  async function removeNote(id) {
    await deleteNote(id)
    const idx = notes.value.findIndex(n => n.id === id)
    if (idx !== -1) {
      notes.value.splice(idx, 1)
      totalCount.value--
      noteCount.value--
    }
    if (notes.value.length === 0 && currentPage.value > 1) {
      currentPage.value = Math.max(1, currentPage.value - 1)
      await loadNotes()
    }
  }

  async function removeCategory(name) {
    await deleteCategory(name)
    const idx = categories.value.indexOf(name)
    if (idx !== -1) {
      categories.value.splice(idx, 1)
    }
    if (!deletedCategories.value.includes(name)) {
      deletedCategories.value.push(name)
    }
    if (activeCategory.value === name) {
      activeCategory.value = '全部'
      if (activeTab.value === 'todo') {
        await loadTodos()
      } else {
        await loadNotes()
      }
    }
  }

  async function tryLeaveEdit() {
    if (!isDirty.value) {
      return { allowed: true, action: 'none' }
    }
    if (showLeaveConfirm.value) {
      return { allowed: false }
    }
    return new Promise((resolve) => {
      pendingLeave.value = { resolve }
      showLeaveConfirm.value = true
    })
  }

  function resolveLeave(action) {
    if (pendingLeave.value) {
      pendingLeave.value.resolve({ allowed: action !== 'cancel', action })
    }
    showLeaveConfirm.value = false
    pendingLeave.value = null
  }

  function setActiveTab(tab) {
    activeTab.value = tab
    currentPage.value = 1
  }

  function setActiveCategory(category) {
    activeCategory.value = category
    currentPage.value = 1
  }

  function setSearchQuery(query) {
    searchQuery.value = query
    currentPage.value = 1
  }

  function setPage(page) {
    currentPage.value = page
  }

  return {
    todos, notes, categories, deletedCategories,
    activeTab, activeCategory, searchQuery,
    selectedItem, selectedType,
    isTodosLoading, isNotesLoading, isDetailLoading,
    error, currentPage, totalCount, pageSize,
    todoCount, noteCount, isDirty, showLeaveConfirm,
    loadTodos, loadNotes, loadCategories,
    addTodo, addNote, addCategory,
    openDetail, closeDetail,
    toggleTodoComplete,
    saveTodoEdit, saveNoteEdit,
    removeTodo, removeNote, removeCategory,
    setActiveTab, setActiveCategory, setSearchQuery, setPage,
    tryLeaveEdit, resolveLeave,
  }
})
