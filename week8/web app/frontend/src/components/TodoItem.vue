<template>
  <div
    class="todo-item"
    :class="{ completed: todo.is_completed }"
    @click="emit('select', todo)"
  >
    <input
      type="checkbox"
      class="checkbox"
      :checked="todo.is_completed"
      @click.stop
      @change="onToggle"
    />
    <span class="title">{{ todo.title }}</span>
    <span
      v-if="todo.category"
      class="category-tag"
      :style="{ background: categoryColor(todo.category) }"
    >{{ todo.category }}</span>
    <span class="date">{{ formatDate(todo.created_at) }}</span>
  </div>
</template>

<script setup>
import { useNotesStore } from '../stores/notes.js'
import { categoryColor, formatRelativeDate } from '../utils/categories.js'

const props = defineProps({
  todo: { type: Object, required: true },
})

const emit = defineEmits(['select', 'toast'])
const store = useNotesStore()

async function onToggle() {
  try {
    await store.toggleTodoComplete(props.todo)
  } catch (e) {
    emit('toast', { message: '操作失败', type: 'error' })
  }
}

function formatDate(dateStr) {
  return formatRelativeDate(dateStr)
}
</script>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.1s;
}
.todo-item:hover {
  background: #f8f9fb;
}
.todo-item + .todo-item {
  border-top: 1px solid #f0f0f0;
}
.completed .title {
  text-decoration: line-through;
  color: #bbb;
}
.checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #4f6ef7;
  flex-shrink: 0;
}
.title {
  flex: 1;
  font-size: 14px;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.completed .title {
  color: #bbb;
}
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
  flex-shrink: 0;
}
.date {
  font-size: 11px;
  color: #999;
  flex-shrink: 0;
}
</style>
