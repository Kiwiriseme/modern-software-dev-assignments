<template>
  <aside class="detail-panel" :class="{ open: store.selectedItem }">
    <template v-if="store.selectedItem">
      <div class="panel-header">
        <button class="back-btn" @click="store.closeDetail()">←</button>
        <span class="panel-title" v-if="!isEditing">{{ store.selectedItem.title }}</span>
        <div class="header-actions">
          <button
            v-if="!isEditing"
            class="action-btn edit-btn"
            @click="startEdit"
          >编辑</button>
          <button
            v-if="isEditing"
            class="action-btn save-btn"
            @click="save"
          >保存</button>
          <button
            v-if="isEditing"
            class="action-btn cancel-btn"
            @click="cancelEdit"
          >取消</button>
          <button
            v-if="!isEditing"
            class="action-btn delete-btn"
            @click="requestDelete"
          >删除</button>
        </div>
      </div>

      <div v-if="store.isDetailLoading" class="loading">加载中...</div>

      <template v-else>
        <div v-if="!isEditing" class="panel-body read-mode">
          <div class="meta-row">
            <span
              v-if="store.selectedItem.category"
              class="category-tag"
              :style="{ background: categoryColor(store.selectedItem.category) }"
            >
              {{ store.selectedItem.category }}
            </span>
            <span class="date-info">
              创建于 {{ formatDate(store.selectedItem.created_at) }}
            </span>
          </div>
          <div
            v-if="store.selectedType === 'note'"
            class="markdown-content"
            v-html="renderedMarkdown"
          ></div>
          <div v-else class="todo-detail-content">
            <p>{{ store.selectedItem.content || '暂无详细描述' }}</p>
            <div class="completion-status">
              <label>
                <input
                  type="checkbox"
                  :checked="store.selectedItem.is_completed"
                  @change="onToggleComplete"
                />
                {{ store.selectedItem.is_completed ? '已完成' : '未完成' }}
              </label>
            </div>
          </div>
        </div>

        <div v-else class="panel-body edit-mode">
          <div class="form-group">
            <label class="form-label">标题</label>
            <input
              v-model="editForm.title"
              class="form-input"
              :class="{ error: formErrors.title }"
              maxlength="200"
            />
            <span v-if="formErrors.title" class="form-error">{{ formErrors.title }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">分类</label>
            <input
              v-model="editForm.category"
              class="form-input"
              maxlength="50"
            />
          </div>
          <div class="form-group">
            <label class="form-label">内容</label>
            <textarea
              v-model="editForm.content"
              class="form-textarea"
              rows="10"
              maxlength="10000"
            ></textarea>
          </div>
        </div>
      </template>
    </template>
    <div v-else class="panel-empty">
      <p>选择一条记录查看详情</p>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useNotesStore } from '../stores/notes.js'
import { categoryColor, formatDate } from '../utils/categories.js'

const store = useNotesStore()
const isEditing = ref(false)
const editForm = ref({ title: '', category: '', content: '' })
const formErrors = ref({})

// Markdown 解析 debounce timer 清理
let renderTimer = null
onUnmounted(() => {
  clearTimeout(renderTimer)
})

watch(() => store.selectedItem, (item) => {
  if (item && !item.id) {
    editForm.value = {
      title: item.title || '',
      category: item.category || '',
      content: item.content || '',
    }
    formErrors.value = {}
    isEditing.value = true
  } else {
    isEditing.value = false
  }
})

const emit = defineEmits(['toast', 'confirm-delete'])

const renderedMarkdown = computed(() => {
  if (!store.selectedItem?.content) return ''
  const raw = marked(store.selectedItem.content)
  return DOMPurify.sanitize(raw)
})

function startEdit() {
  const item = store.selectedItem
  editForm.value = {
    title: item.title || '',
    category: item.category || '',
    content: item.content || '',
  }
  formErrors.value = {}
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  formErrors.value = {}
}

function validate() {
  const errors = {}
  if (!editForm.value.title || !editForm.value.title.trim()) {
    errors.title = '标题不能为空'
  }
  if (editForm.value.title.length > 200) {
    errors.title = '标题不能超过200个字符'
  }
  formErrors.value = errors
  return Object.keys(errors).length === 0
}

async function save() {
  if (!validate()) return
  try {
    const data = {
      title: editForm.value.title.trim(),
      category: editForm.value.category.trim(),
      content: editForm.value.content,
    }
    const isCreate = !store.selectedItem.id
    if (isCreate) {
      if (store.selectedType === 'todo') {
        store.selectedItem = await store.addTodo(data)
      } else {
        store.selectedItem = await store.addNote(data)
      }
      // 修复新创建时的 selectedType（activeTab='text' → selectedType='note'）
      if (store.selectedType === 'text') {
        store.selectedType = 'note'
      }
    } else {
      if (store.selectedType === 'todo') {
        await store.saveTodoEdit(store.selectedItem.id, data)
      } else {
        await store.saveNoteEdit(store.selectedItem.id, data)
      }
    }
    isEditing.value = false
    emit('toast', { message: '保存成功', type: 'success' })
  } catch (e) {
    emit('toast', { message: '保存失败', type: 'error' })
  }
}

function requestDelete() {
  emit('confirm-delete', { item: store.selectedItem, type: store.selectedType })
}

async function onToggleComplete() {
  try {
    await store.toggleTodoComplete(store.selectedItem)
  } catch (e) {
    emit('toast', { message: '操作失败', type: 'error' })
  }
}
</script>

<style scoped>
.detail-panel {
  width: 0;
  overflow: hidden;
  background: #fff;
  border-left: 1px solid #eee;
  transition: width 0.25s ease;
  display: flex;
  flex-direction: column;
}
.detail-panel.open {
  width: 360px;
  min-width: 360px;
}
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}
.back-btn {
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 0;
}
.panel-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.header-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}
.action-btn {
  padding: 5px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}
.edit-btn { background: #e8f0fe; color: #4f6ef7; }
.save-btn { background: #4f6ef7; color: #fff; }
.cancel-btn { background: #f5f5f5; color: #666; }
.delete-btn { background: #fef2f2; color: #dc2626; }
.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
}
.date-info {
  font-size: 12px;
  color: #999;
}
.markdown-content {
  font-size: 14px;
  line-height: 1.7;
  color: #333;
}
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
  color: #1a1a1a;
}
.markdown-content :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
}
.markdown-content :deep(code) {
  font-size: 12px;
}
.markdown-content :deep(p) {
  margin: 0 0 8px 0;
}
.todo-detail-content p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}
.completion-status {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
.completion-status label {
  font-size: 14px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.completion-status input {
  width: 16px;
  height: 16px;
  accent-color: #4f6ef7;
}
.edit-mode .form-group {
  margin-bottom: 14px;
}
.form-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}
.form-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}
.form-input:focus, .form-textarea:focus {
  border-color: #4f6ef7;
}
.form-input.error {
  border-color: #dc2626;
}
.form-error {
  font-size: 11px;
  color: #dc2626;
}
.form-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}
.panel-empty {
  padding: 40px 16px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
.loading {
  padding: 40px 16px;
  text-align: center;
  color: #999;
}
</style>
