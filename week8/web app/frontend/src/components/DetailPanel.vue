<template>
  <aside class="detail-panel" :class="{ open: store.selectedItem }">
    <template v-if="store.selectedItem">
      <!-- Header -->
      <div class="panel-header">
        <button class="back-btn" @click="store.closeDetail()" aria-label="关闭">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M11 4l-5 5 5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <span class="panel-type-badge" :class="store.selectedType">
          {{ store.selectedType === 'todo' ? '待办' : '笔记' }}
        </span>
        <div class="header-actions">
          <button
            v-if="!isEditing"
            class="action-btn icon-only"
            @click="startEdit"
            aria-label="编辑"
            title="编辑"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M11 2l3 3-9 9H2v-3l9-9z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
              <path d="M9.5 3.5l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
          <button
            v-if="!isEditing"
            class="action-btn icon-only danger"
            @click="requestDelete"
            aria-label="删除"
            title="删除"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 5h10M6 5V3.5a1 1 0 011-1h2a1 1 0 011 1V5M12.5 5v7a1.5 1.5 0 01-1.5 1.5H5A1.5 1.5 0 013.5 12V5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="store.isDetailLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <span>加载中…</span>
      </div>

      <!-- Read mode -->
      <template v-else-if="!isEditing">
        <div class="panel-body read-mode">
          <!-- Title -->
          <h2 class="detail-title">{{ store.selectedItem.title || '无标题' }}</h2>

          <!-- Meta row -->
          <div class="meta-row">
            <span
              v-if="store.selectedItem.category"
              class="category-tag"
              :style="tagStyle(store.selectedItem.category)"
            >
              {{ store.selectedItem.category }}
            </span>
            <span class="date-info">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" class="date-icon">
                <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.2"/>
                <path d="M6 3.5V6l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              创建于 {{ formatDate(store.selectedItem.created_at) }}
            </span>
            <span v-if="store.selectedItem.updated_at !== store.selectedItem.created_at" class="date-info edited">
              · 更新于 {{ formatDate(store.selectedItem.updated_at) }}
            </span>
          </div>

          <!-- Divider -->
          <hr class="content-divider" />

          <!-- Markdown content for notes -->
          <div
            v-if="store.selectedType === 'note'"
            class="markdown-content"
            v-html="renderedMarkdown"
          ></div>

          <!-- Todo detail content -->
          <div v-else class="todo-detail-content">
            <div class="completion-status" @click="onToggleComplete">
              <button
                class="status-toggle"
                :class="{ checked: store.selectedItem.is_completed }"
              >
                <svg
                  v-if="store.selectedItem.is_completed"
                  width="14"
                  height="11"
                  viewBox="0 0 14 11"
                  fill="none"
                >
                  <path d="M1.5 5.5l3.5 3.5 7.5-7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <span class="status-label">
                {{ store.selectedItem.is_completed ? '已完成' : '标记为完成' }}
              </span>
            </div>
            <div class="todo-content-text" v-if="store.selectedItem.content">
              <p>{{ store.selectedItem.content }}</p>
            </div>
            <div v-else class="todo-content-empty">
              <p>暂无详细描述</p>
            </div>
          </div>
        </div>
      </template>

      <!-- Edit mode -->
      <div v-else class="panel-body edit-mode">
        <div class="form-group">
          <label class="form-label">标题</label>
          <input
            v-model="editForm.title"
            class="form-input"
            :class="{ error: formErrors.title }"
            placeholder="输入标题…"
            maxlength="200"
          />
          <span v-if="formErrors.title" class="form-error">{{ formErrors.title }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">分类</label>
          <div class="category-chip-bar">
            <button
              type="button"
              class="category-chip"
              :class="{ selected: editForm.category === '' && !isCreatingCategory }"
              @click="selectCategory('')"
            >无分类</button>
            <button
              v-for="cat in availableCategories"
              :key="cat"
              type="button"
              class="category-chip"
              :class="{ selected: editForm.category === cat }"
              :style="editForm.category === cat ? chipActiveStyle(cat) : {}"
              @click="selectCategory(cat)"
            >{{ cat }}</button>
            <template v-if="!isCreatingCategory">
              <button
                type="button"
                class="category-chip new-category-chip"
                @click="startNewCategory"
              >＋ 新建分类</button>
            </template>
            <div v-else class="new-category-row">
              <input
                ref="newCatInput"
                v-model="newCategoryName"
                type="text"
                class="new-category-input"
                placeholder="输入新分类…"
                maxlength="50"
                @keydown.enter.prevent="saveNewCategory"
                @keydown.escape.prevent="cancelNewCategory"
              />
              <button
                type="button"
                class="new-category-save-btn"
                :disabled="!newCategoryName.trim()"
                @click="saveNewCategory"
                aria-label="保存分类"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M11 4l-5 5-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div v-if="store.selectedType === 'todo'" class="form-group">
          <label class="form-label">截止日期</label>
          <input
            v-model="editForm.due_date"
            type="date"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">内容 <span class="form-label-hint">（支持 Markdown）</span></label>
          <textarea
            v-model="editForm.content"
            class="form-textarea"
            rows="12"
            placeholder="开始书写…"
            maxlength="10000"
          ></textarea>
        </div>
        <div class="edit-actions">
          <button class="btn-cancel" @click="cancelEdit">取消</button>
          <button class="btn-save" @click="save">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M11 4l-5 5-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            保存
          </button>
        </div>
      </div>
    </template>

    <!-- Empty panel -->
    <div v-else class="panel-empty">
      <div class="empty-illustration">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <rect x="8" y="6" width="32" height="36" rx="5" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.25"/>
          <path d="M17 18h14M17 23h10M17 28h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.25"/>
        </svg>
      </div>
      <p class="empty-text">选择一条记录查看详情</p>
      <p class="empty-hint">点击左侧列表中的项目</p>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useNotesStore } from '../stores/notes.js'
import { categoryColor, categoryBgColor, formatDate, PRESET_CATEGORIES } from '../utils/categories.js'

const store = useNotesStore()
const isEditing = ref(false)
const editForm = ref({ title: '', category: '', content: '', due_date: '' })
const formErrors = ref({})
const isCreatingCategory = ref(false)
const newCategoryName = ref('')
const newCatInput = ref(null)
const isDirty = ref(false)
let skipDirty = false

let renderTimer = null
onUnmounted(() => {
  clearTimeout(renderTimer)
})

watch(() => store.selectedItem, (item) => {
  if (item && !item.id) {
    skipDirty = true
    editForm.value = {
      title: item.title || '',
      category: item.category || '',
      content: item.content || '',
      due_date: item.due_date || '',
    }
    formErrors.value = {}
    isDirty.value = false
    isEditing.value = true
  } else {
    isDirty.value = false
    isEditing.value = false
  }
})

watch([() => editForm.value.title, () => editForm.value.content,
       () => editForm.value.category, () => editForm.value.due_date],
  () => {
    if (skipDirty) {
      skipDirty = false
      return
    }
    isDirty.value = true
  },
  { deep: false }
)

watch(isDirty, (val) => {
  store.isDirty = val
})

watch(isCreatingCategory, (val) => {
  if (val) {
    setTimeout(() => {
      newCatInput.value?.focus()
    }, 50)
  }
})

const emit = defineEmits(['toast', 'confirm-delete'])

const renderedMarkdown = computed(() => {
  if (!store.selectedItem?.content) return '<p style="color: var(--text-muted); font-style: italic;">暂无内容</p>'
  const raw = marked(store.selectedItem.content)
  return DOMPurify.sanitize(raw)
})

const availableCategories = computed(() => {
  const presets = PRESET_CATEGORIES.filter(c => c !== '全部')
  const custom = store.categories.filter(c => !PRESET_CATEGORIES.includes(c))
  return [...presets, ...custom]
})

function selectCategory(cat) {
  isCreatingCategory.value = false
  newCategoryName.value = ''
  editForm.value.category = cat
}

function startNewCategory() {
  isCreatingCategory.value = true
  newCategoryName.value = ''
}

function saveNewCategory() {
  const trimmed = newCategoryName.value.trim()
  if (!trimmed) {
    isCreatingCategory.value = false
    newCategoryName.value = ''
    return
  }
  store.addCategory(trimmed)
  editForm.value.category = trimmed
  isCreatingCategory.value = false
  newCategoryName.value = ''
}

function cancelNewCategory() {
  isCreatingCategory.value = false
  newCategoryName.value = ''
}

function chipActiveStyle(cat) {
  return {
    borderColor: categoryColor(cat),
    background: categoryBgColor(cat),
    color: categoryColor(cat),
  }
}

function tagStyle(cat) {
  return {
    background: categoryBgColor(cat),
    color: categoryColor(cat),
  }
}

function startEdit() {
  const item = store.selectedItem
  skipDirty = true
  editForm.value = {
    title: item.title || '',
    category: item.category || '',
    content: item.content || '',
    due_date: item.due_date || '',
  }
  formErrors.value = {}
  isDirty.value = false
  isEditing.value = true
}

function cancelEdit() {
  isDirty.value = false
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
    if (store.selectedType === 'todo') {
      data.due_date = editForm.value.due_date || null
    }
    const isCreate = !store.selectedItem.id
    if (isCreate) {
      if (store.selectedType === 'todo') {
        store.selectedItem = await store.addTodo(data)
      } else {
        store.selectedItem = await store.addNote(data)
      }
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
    isDirty.value = false
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
/* ── Panel Layout ── */
.detail-panel {
  width: 0;
  overflow: hidden;
  background: var(--bg-surface);
  border-left: 1px solid var(--border);
  transition: width var(--duration-slow) var(--ease-in-out);
  display: flex;
  flex-direction: column;
  position: relative;
}

.detail-panel.open {
  width: var(--detail-width);
  min-width: var(--detail-width);
}

/* ── Header ── */
.panel-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}

.back-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all var(--duration-fast) var(--ease-out);
}

.back-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.panel-type-badge {
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.panel-type-badge.todo {
  background: var(--cat-idea-bg);
  color: var(--cat-idea);
}

.panel-type-badge.note {
  background: var(--accent-soft);
  color: var(--accent);
}

.header-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.action-btn.icon-only {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
}

.action-btn.icon-only:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.action-btn.icon-only.danger:hover {
  background: var(--error-bg);
  color: var(--error);
}

/* ── Body ── */
.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-xl);
  animation: fadeIn 0.3s var(--ease-out);
}

/* ── Read Mode ── */
.detail-title {
  font-family: var(--font-display);
  font-size: 1.375rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  margin-bottom: var(--space-md);
  letter-spacing: 0.02em;
}

.meta-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.category-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.date-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.date-info.edited {
  color: var(--text-muted);
}

.date-icon {
  opacity: 0.5;
}

.content-divider {
  border: none;
  border-top: 1px solid var(--border-light);
  margin: 0 0 var(--space-xl) 0;
}

/* ── Markdown Content ── */
.markdown-content {
  font-size: 0.9375rem;
  line-height: 1.8;
  color: var(--text-primary);
}

.markdown-content :deep(h1) {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: var(--space-2xl) 0 var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-light);
}

.markdown-content :deep(h2) {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: var(--space-xl) 0 var(--space-md);
}

.markdown-content :deep(h3) {
  font-family: var(--font-display);
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: var(--space-lg) 0 var(--space-sm);
}

.markdown-content :deep(p) {
  margin: 0 0 var(--space-md) 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0 0 var(--space-md) 0;
  padding-left: 1.5em;
}

.markdown-content :deep(li) {
  margin-bottom: var(--space-xs);
}

.markdown-content :deep(blockquote) {
  border-left: 3px solid var(--accent);
  margin: var(--space-md) 0;
  padding: var(--space-sm) var(--space-lg);
  background: var(--accent-soft);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
  font-style: italic;
}

.markdown-content :deep(code) {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  background: var(--bg-page);
  padding: 2px 6px;
  border-radius: 3px;
  color: var(--accent-warm);
}

.markdown-content :deep(pre) {
  background: #f5f2ec;
  border: 1px solid var(--border-light);
  padding: var(--space-lg);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: var(--space-md) 0;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
  color: var(--text-primary);
  font-size: 0.8125rem;
  line-height: 1.6;
}

.markdown-content :deep(a) {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.markdown-content :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-light);
  margin: var(--space-xl) 0;
}

/* ── Todo Detail ── */
.todo-detail-content {
  animation: fadeInUp 0.35s var(--ease-out);
}

.completion-status {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
  background: var(--bg-page);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
  margin-bottom: var(--space-xl);
}

.completion-status:hover {
  background: var(--bg-hover);
}

.status-toggle {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  border: 2px solid var(--border-focus);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
  background: transparent;
  color: transparent;
  padding: 0;
  cursor: pointer;
}

.status-toggle.checked {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-inverse);
}

.status-label {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  transition: color var(--duration-fast) var(--ease-out);
}

.status-toggle.checked + .status-label {
  color: var(--text-muted);
}

.todo-content-text p {
  font-size: 0.9375rem;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.todo-content-empty p {
  color: var(--text-muted);
  font-style: italic;
  font-size: 0.875rem;
}

/* ── Edit Mode ── */
.edit-mode {
  animation: slideInRight 0.3s var(--ease-out);
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.form-label-hint {
  font-weight: 400;
  color: var(--text-muted);
  text-transform: none;
  letter-spacing: 0;
}

.form-input {
  width: 100%;
  padding: 10px var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: var(--bg-page);
  outline: none;
  transition: all var(--duration-fast) var(--ease-out);
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
  background: var(--bg-surface);
}

.form-input.error {
  border-color: var(--error);
  box-shadow: 0 0 0 3px var(--error-bg);
}

.form-error {
  font-size: 0.75rem;
  color: var(--error);
  margin-top: var(--space-xs);
  display: block;
}

.form-textarea {
  width: 100%;
  padding: var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: var(--bg-page);
  outline: none;
  resize: vertical;
  line-height: 1.7;
  transition: all var(--duration-fast) var(--ease-out);
  font-family: var(--font-body);
  box-sizing: border-box;
  min-height: 200px;
}

.form-textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
  background: var(--bg-surface);
}

.edit-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: flex-end;
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-light);
}

.btn-cancel {
  padding: 9px var(--space-xl);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-page);
  border: 1px solid var(--border);
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-cancel:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-save {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px var(--space-xl);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-inverse);
  background: var(--accent);
  border: none;
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-save:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow-md);
}

/* ── Loading ── */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Empty Panel ── */
.panel-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl);
  text-align: center;
  color: var(--text-muted);
}

.empty-illustration {
  margin-bottom: var(--space-lg);
  opacity: 0.35;
}

.empty-text {
  font-family: var(--font-display);
  font-size: 0.9375rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
}

.empty-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* ── Category Chip Bar ── */
.category-chip-bar {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
  align-items: center;
}

.category-chip {
  padding: 4px 12px;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--bg-surface);
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
}

.category-chip:hover {
  border-color: var(--border-focus);
  color: var(--text-secondary);
}

.category-chip.selected {
  font-weight: 600;
}

.new-category-chip {
  border-style: dashed;
  color: var(--text-muted);
}

.new-category-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.new-category-input {
  width: 110px;
  padding: 4px 8px;
  border: 2px solid var(--accent);
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  color: var(--text-primary);
  background: var(--bg-surface);
  outline: none;
  box-shadow: 0 0 0 3px var(--accent-soft);
  box-sizing: border-box;
}

.new-category-save-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  color: var(--text-inverse);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
}

.new-category-save-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.new-category-save-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
