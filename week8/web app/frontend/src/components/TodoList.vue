<template>
  <div class="todo-list-container">
    <div v-if="store.isTodosLoading" class="loading">加载中...</div>
    <div v-else-if="store.todos.length === 0" class="empty">
      <p>{{ emptyMessage }}</p>
    </div>
    <div v-else class="todo-list">
      <TodoItem
        v-for="todo in store.todos"
        :key="todo.id"
        :todo="todo"
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

const emptyMessage = computed(() => {
  if (store.searchQuery) return '未找到匹配的记录'
  if (store.activeCategory !== '全部') return '当前分类下暂无记录'
  return '暂无记录，点击 + 创建'
})
</script>

<style scoped>
.todo-list-container {
  flex: 1;
  overflow-y: auto;
}
.todo-list {
  background: #fff;
  border-radius: 8px;
}
.loading, .empty {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>
