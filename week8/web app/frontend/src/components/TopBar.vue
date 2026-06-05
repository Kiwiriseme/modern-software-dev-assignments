<template>
  <div class="topbar">
    <div class="search-wrapper">
      <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.5"/>
        <path d="M11 11l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <input
        class="search-input"
        :placeholder="store.activeTab === 'todo' ? '搜索待办事项…' : '搜索笔记…'"
        :value="localSearch"
        @input="onSearchInput"
      />
      <button
        v-if="localSearch"
        class="search-clear"
        @click="clearSearch"
        aria-label="清除搜索"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <div class="tab-switch">
      <button
        class="tab-btn"
        :class="{ active: store.activeTab === 'todo' }"
        @click="store.setActiveTab('todo')"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="tab-icon">
          <rect x="2" y="2" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
          <path d="M4.5 7l2 2 3-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0"/>
        </svg>
        待办
      </button>
      <button
        class="tab-btn"
        :class="{ active: store.activeTab === 'text' }"
        @click="store.setActiveTab('text')"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="tab-icon">
          <rect x="2" y="2" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
          <path d="M5 6h4M5 8.5h3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        笔记
      </button>
      <div class="tab-slider" :class="{ right: store.activeTab === 'text' }"></div>
    </div>

    <button class="new-btn" @click="startCreate" aria-label="新建">
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
        <path d="M9 3v12M3 9h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span class="new-btn-label">新建</span>
    </button>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useNotesStore } from '../stores/notes.js'

const emit = defineEmits(['create', 'toast'])
const store = useNotesStore()
const localSearch = ref('')
let debounceTimer = null

onUnmounted(() => {
  clearTimeout(debounceTimer)
})

async function onSearchInput(e) {
  localSearch.value = e.target.value
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    store.setSearchQuery(localSearch.value)
    try {
      if (store.activeTab === 'todo') {
        await store.loadTodos()
      } else {
        await store.loadNotes()
      }
    } catch (e) {
      emit('toast', { message: '加载失败', type: 'error' })
    }
  }, 300)
}

async function clearSearch() {
  localSearch.value = ''
  store.setSearchQuery('')
  try {
    if (store.activeTab === 'todo') {
      await store.loadTodos()
    } else {
      await store.loadNotes()
    }
  } catch (e) {
    emit('toast', { message: '加载失败', type: 'error' })
  }
}

function startCreate() {
  emit('create')
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-light);
}

/* ── Search ── */
.search-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--space-md);
  color: var(--text-muted);
  pointer-events: none;
  transition: color var(--duration-fast) var(--ease-out);
}

.search-wrapper:focus-within .search-icon {
  color: var(--accent);
}

.search-input {
  width: 100%;
  padding: 9px var(--space-md) 9px 38px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  color: var(--text-primary);
  background: var(--bg-page);
  outline: none;
  transition: all var(--duration-fast) var(--ease-out);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
  background: var(--bg-surface);
}

.search-clear {
  position: absolute;
  right: var(--space-sm);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
}

.search-clear:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* ── Tab Switch ── */
.tab-switch {
  display: flex;
  position: relative;
  background: var(--bg-page);
  border-radius: var(--radius-md);
  padding: 3px;
  flex-shrink: 0;
  border: 1px solid var(--border);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border-radius: calc(var(--radius-md) - 2px);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
  transition: color var(--duration-normal) var(--ease-out);
}

.tab-btn.active {
  color: var(--text-primary);
}

.tab-icon {
  opacity: 0.6;
  transition: opacity var(--duration-normal) var(--ease-out);
}

.tab-btn.active .tab-icon {
  opacity: 1;
}

.tab-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  width: calc(50% - 3px);
  height: calc(100% - 6px);
  background: var(--bg-surface);
  border-radius: calc(var(--radius-md) - 2px);
  box-shadow: var(--shadow-xs);
  transition: transform var(--duration-normal) var(--ease-in-out);
}

.tab-slider.right {
  transform: translateX(100%);
}

/* ── New Button ── */
.new-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px var(--space-lg);
  background: var(--accent);
  color: var(--text-inverse);
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  font-weight: 500;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.new-btn:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.new-btn:active {
  transform: translateY(0);
  box-shadow: var(--shadow-xs);
}

.new-btn-label {
  letter-spacing: 0.02em;
}
</style>
