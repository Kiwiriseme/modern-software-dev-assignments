<template>
  <div class="topbar">
    <input
      class="search-input"
      :placeholder="store.activeTab === 'todo' ? '搜索 TODO...' : '搜索文本...'"
      :value="localSearch"
      @input="onSearchInput"
    />
    <div class="tab-switch">
      <button
        class="tab-btn"
        :class="{ active: store.activeTab === 'todo' }"
        @click="store.setActiveTab('todo')"
      >TODO</button>
      <button
        class="tab-btn"
        :class="{ active: store.activeTab === 'text' }"
        @click="store.setActiveTab('text')"
      >文本</button>
    </div>
    <button class="new-btn" @click="startCreate">＋</button>
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

function startCreate() {
  emit('create')
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
}
.search-input {
  flex: 1;
  padding: 8px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  background: #fff;
  color: #333;
}
.search-input::placeholder {
  color: #999;
}
.search-input:focus {
  border-color: #4f6ef7;
}
.tab-switch {
  display: flex;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
  flex-shrink: 0;
}
.tab-btn {
  padding: 7px 16px;
  border: none;
  background: #fff;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
}
.tab-btn:first-child {
  border-right: 1px solid #e0e0e0;
}
.tab-btn.active {
  background: #4f6ef7;
  color: #fff;
}
.new-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: #4f6ef7;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;
}
.new-btn:hover {
  background: #3d5bd9;
}
</style>
