<template>
  <div class="main-layout">
    <Sidebar @delete-category="onRequestDeleteCategory" />
    <ContentArea
      @select="onSelect"
      @create="onCreate"
      @toast="showToast"
    />
    <DetailPanel
      ref="detailPanelRef"
      @toast="showToast"
      @confirm-delete="onRequestDelete"
      @close="onCloseDetail"
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
    <ConfirmDialog
      :visible="store.showLeaveConfirm"
      message="你有未保存的更改，是否保存后再离开？"
      confirm-text="保存并离开"
      cancel-text="取消"
      :show-discard="true"
      discard-text="不保存"
      @confirm="store.resolveLeave('save')"
      @discard="store.resolveLeave('discard')"
      @cancel="store.resolveLeave('cancel')"
    />
    <SettingsDialog />
    <ConfirmDialog
      :visible="store.showAIConfigurePrompt"
      message="请先配置 AI API 设置"
      confirm-text="去设置"
      cancel-text="取消"
      :show-discard="false"
      @confirm="onAIConfigureGoSettings"
      @cancel="store.resolveAIConfigure('cancel')"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import { getTodayDateString } from '../utils/categories.js'
import Sidebar from '../components/Sidebar.vue'
import SettingsDialog from '../components/SettingsDialog.vue'
import ContentArea from '../components/ContentArea.vue'
import DetailPanel from '../components/DetailPanel.vue'
import Toast from '../components/Toast.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const store = useNotesStore()
const detailPanelRef = ref(null)

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
const pendingDeleteCategory = ref(null)

function onRequestDelete({ item, type }) {
  pendingDelete.value = { item, type }
  confirmMessage.value = '确定删除这条记录？'
  showConfirm.value = true
}

function onRequestDeleteCategory(name) {
  pendingDeleteCategory.value = name
  confirmMessage.value = `确定要删除分类「${name}」吗？所有属于该分类的条目将变为无分类状态。`
  showConfirm.value = true
}

function onAIConfigureGoSettings() {
  store.resolveAIConfigure('go-settings')
  store.openSettings()
}

async function onConfirmDelete() {
  showConfirm.value = false
  if (pendingDelete.value) {
    const { item, type } = pendingDelete.value
    const leaveResult = await store.tryLeaveEdit()
    if (!leaveResult.allowed) {
      pendingDelete.value = null
      return
    }
    if (leaveResult.action === 'save') {
      await detailPanelRef.value.save()
      if (store.isDirty) {
        pendingDelete.value = null
        return
      }
    }
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
    return
  }
  if (pendingDeleteCategory.value) {
    try {
      await store.removeCategory(pendingDeleteCategory.value)
      showToast({ message: `分类「${pendingDeleteCategory.value}」已删除`, type: 'success' })
    } catch (e) {
      showToast({ message: '删除分类失败', type: 'error' })
    }
    pendingDeleteCategory.value = null
  }
}

async function onSelect(item, type) {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

  try {
    await store.openDetail(item.id, type)
  } catch (e) {
    showToast({ message: '加载详情失败', type: 'error' })
  }
}

async function onCreate() {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

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

async function onCloseDetail() {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

  store.closeDetail()
}

let isRestoring = false

watch(() => store.activeTab, async (newVal, oldVal) => {
  if (isRestoring) { isRestoring = false; return }
  const result = await store.tryLeaveEdit()
  if (!result.allowed) {
    isRestoring = true
    store.activeTab = oldVal
    return
  }

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

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
watch(() => store.activeCategory, (newVal, oldVal) => {
  if (isRestoring) { isRestoring = false; return }
  clearTimeout(categoryDebounce)
  categoryDebounce = setTimeout(async () => {
    const result = await store.tryLeaveEdit()
    if (!result.allowed) {
      isRestoring = true
      store.activeCategory = oldVal
      return
    }

    if (result.action === 'save') {
      await detailPanelRef.value.save()
      if (store.isDirty) return
    }

    const results = await Promise.allSettled([
      store.loadTodos(),
      store.loadNotes()
    ])
    if (results.every(r => r.status === 'rejected')) {
      showToast({ message: '加载失败', type: 'error' })
    }
  }, 150)
})

onMounted(async () => {
  try {
    await Promise.all([
      store.loadTodos(),
      store.loadNotes(),
      store.loadCategories(),
      store.loadAISettings(),
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
