<template>
  <div class="todo-list-container">
    <!-- Loading skeleton -->
    <div v-if="store.isTodosLoading" class="loading-state">
      <div v-for="n in 5" :key="n" class="skeleton-row">
        <div class="skeleton-box skeleton-check"></div>
        <div class="skeleton-box skeleton-title" :style="{ width: skeletonWidths[n - 1] }"></div>
        <div class="skeleton-box skeleton-tag"></div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="store.todos.length === 0" class="empty-state">
      <div class="empty-illustration">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <rect x="12" y="8" width="40" height="48" rx="6" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.3"/>
          <path d="M24 22h16M24 28h12M24 34h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.3"/>
          <circle cx="44" cy="20" r="12" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
          <path d="M44 15v10M39 20h10" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="empty-title">{{ emptyTitle }}</p>
      <p class="empty-desc">{{ emptyDesc }}</p>
    </div>

    <!-- List -->
    <div v-else class="todo-list">
      <TodoItem
        v-for="(todo, idx) in store.todos"
        :key="todo.id"
        :todo="todo"
        :style="{ animationDelay: idx * 40 + 'ms' }"
        @select="emit('select', todo, 'todo')"
        @toast="emit('toast', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import TodoItem from './TodoItem.vue'

const emit = defineEmits(['select'])
const store = useNotesStore()

const skeletonWidths = ['75%', '60%', '85%', '50%', '70%']

const emptyTitle = computed(() => {
  if (store.searchQuery) return '未找到匹配的待办事项'
  if (store.activeCategory !== '全部') return '此分类暂无待办'
  return '开始记录你的待办事项'
})

const emptyDesc = computed(() => {
  if (store.searchQuery) return '尝试更换搜索关键词'
  if (store.activeCategory !== '全部') return '切换分类或创建新的待办'
  return '点击右上角的「新建」按钮添加第一条待办'
})
</script>

<style scoped>
.todo-list-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

/* ── Todo List ── */
.todo-list {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
  overflow: hidden;
}

/* ── Loading Skeleton ── */
.loading-state {
  padding: var(--space-md);
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  animation: subtlePulse 1.8s ease-in-out infinite;
}

.skeleton-box {
  height: 14px;
  border-radius: 4px;
  background: var(--bg-hover);
}

.skeleton-check {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  flex-shrink: 0;
}

.skeleton-title {
  flex: 1;
}

.skeleton-tag {
  width: 40px;
  flex-shrink: 0;
}

/* ── Empty State ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl) var(--space-xl);
  text-align: center;
  animation: fadeInUp 0.5s var(--ease-out);
}

.empty-illustration {
  color: var(--text-muted);
  margin-bottom: var(--space-xl);
  opacity: 0.6;
}

.empty-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.empty-desc {
  font-size: 0.8125rem;
  color: var(--text-muted);
}
</style>
