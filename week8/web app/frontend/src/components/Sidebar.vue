<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="avatar">📓</div>
      <div class="brand">网页记事本</div>
    </div>
    <nav class="nav-list">
      <button
        v-for="cat in displayCategories"
        :key="cat"
        class="nav-item"
        :class="{ active: store.activeCategory === cat }"
        @click="store.setActiveCategory(cat)"
      >
        {{ cat }}
      </button>
    </nav>
    <div class="sidebar-footer">
      <span class="settings-icon">⚙</span>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import { PRESET_CATEGORIES } from '../utils/categories.js'

const store = useNotesStore()

const displayCategories = computed(() => {
  const custom = store.categories.filter(c => !PRESET_CATEGORIES.includes(c))
  return [...PRESET_CATEGORIES, ...custom]
})
</script>

<style scoped>
.sidebar {
  width: 200px;
  min-width: 200px;
  background: #fafbfc;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.sidebar-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #4f6ef7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
  flex-shrink: 0;
}
.brand {
  font-weight: 700;
  font-size: 14px;
  color: #1a1a1a;
}
.nav-list {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}
.nav-item {
  display: block;
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.15s;
}
.nav-item:hover {
  background: #f0f4ff;
}
.nav-item.active {
  background: #e8f0fe;
  color: #4f6ef7;
  font-weight: 600;
}
.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #eee;
}
.settings-icon {
  font-size: 18px;
  color: #999;
  cursor: pointer;
}
</style>
