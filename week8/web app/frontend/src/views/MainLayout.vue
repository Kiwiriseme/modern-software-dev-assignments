<template>
  <div class="main-layout">
    <Sidebar />
    <ContentArea
      @select="onSelect"
      @create="onCreate"
      @toast="showToast"
    />
    <DetailPanel
      @toast="showToast"
      @confirm-delete="onRequestDelete"
    />
    <Toast
      :message="toastMessage"
      :type="toastType"
      :trigger="toastTrigger"
    />
    <ConfirmDialog
      :visible="showConfirm"
      :message="confirmMessage"
      @confirm="onConfirmDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import { getTodayDateString } from '../utils/categories.js'
import Sidebar from '../components/Sidebar.vue'
import ContentArea from '../components/ContentArea.vue'
import DetailPanel from '../components/DetailPanel.vue'
import Toast from '../components/Toast.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const store = useNotesStore()

const toastMessage = ref('')
const toastType = ref('error')
const toastTrigger = ref(0)

function showToast({ message, type = 'error' }) {
  toastMessage.value = message
  toastType.value = type
  toastTrigger.value++
}

const showConfirm = ref(false)
const confirmMessage = ref('')
const pendingDelete = ref(null)

function onRequestDelete({ item, type }) {
  pendingDelete.value = { item, type }
  confirmMessage.value = '确定删除这条记录？'
  showConfirm.value = true
}

async function onConfirmDelete() {
  showConfirm.value = false
  if (!pendingDelete.value) return
  const { item, type } = pendingDelete.value
  try {
    if (type === 'todo') {
      await store.removeTodo(item.id)
    } else {
      await store.removeNote(item.id)
    }
    store.closeDetail()
    showToast({ message: '删除成功', type: 'success' })
  } catch (e) {
    showToast({ message: '删除失败', type: 'error' })
  }
  pendingDelete.value = null
}

async function onSelect(item, type) {
  try {
    await store.openDetail(item.id, type)
  } catch (e) {
    showToast({ message: '加载详情失败', type: 'error' })
  }
}

function onCreate() {
  const base = {
    title: '',
    category: '',
    content: '',
    is_completed: false,
  }
  if (store.activeTab === 'todo') {
    base.due_date = getTodayDateString()
  }
  store.selectedItem = base
  store.selectedType = store.activeTab === 'text' ? 'note' : 'todo'
}

watch(() => store.activeTab, async () => {
  try {
    if (store.activeTab === 'todo') {
      await store.loadTodos()
    } else {
      await store.loadNotes()
    }
  } catch (e) {
    showToast({ message: '加载失败', type: 'error' })
  }
})

let categoryDebounce = null
watch(() => store.activeCategory, () => {
  clearTimeout(categoryDebounce)
  categoryDebounce = setTimeout(async () => {
    try {
      if (store.activeTab === 'todo') {
        await store.loadTodos()
      } else {
        await store.loadNotes()
      }
    } catch (e) {
      showToast({ message: '加载失败', type: 'error' })
    }
  }, 150)
})

onMounted(async () => {
  try {
    await Promise.all([
      store.loadTodos(),
      store.loadCategories(),
    ])
  } catch (e) {
    showToast({ message: '加载失败', type: 'error' })
  }
})

onUnmounted(() => {
  clearTimeout(categoryDebounce)
})
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
</style>
