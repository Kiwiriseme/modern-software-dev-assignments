<template>
  <div
    class="todo-item"
    :class="{ completed: todo.is_completed }"
    @click="emit('select', todo)"
  >
    <!-- Custom checkbox -->
    <button
      class="custom-checkbox"
      :class="{ checked: todo.is_completed }"
      @click.stop="onToggle"
      :aria-label="todo.is_completed ? '标记为未完成' : '标记为已完成'"
    >
      <svg
        v-if="todo.is_completed"
        class="check-mark"
        width="12"
        height="10"
        viewBox="0 0 12 10"
        fill="none"
      >
        <path
          d="M1 5l3 3 7-7"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>

    <span class="title">{{ todo.title }}</span>

    <span
      v-if="todo.category"
      class="category-tag"
      :style="tagStyle(todo.category)"
    >{{ todo.category }}</span>
    <span class="date">{{ formattedDueDate }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import { categoryColor, categoryBgColor, formatDate } from '../utils/categories.js'

const props = defineProps({
  todo: { type: Object, required: true },
})

const emit = defineEmits(['select', 'toast'])
const store = useNotesStore()

const formattedDueDate = computed(() => {
  if (props.todo.due_date) {
    return formatDate(props.todo.due_date)
  }
  return '---'
})

async function onToggle() {
  try {
    await store.toggleTodoComplete(props.todo)
  } catch (e) {
    emit('toast', { message: '操作失败', type: 'error' })
  }
}
function tagStyle(cat) {
  return {
    background: categoryBgColor(cat),
    color: categoryColor(cat),
  }
}
</script>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
  animation: fadeInUp 0.35s var(--ease-out) both;
  border-bottom: 1px solid var(--border-light);
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-item:hover {
  background: rgba(74, 103, 65, 0.03);
}

.todo-item.completed {
  opacity: 0.55;
}

/* ── Custom Checkbox ── */
.custom-checkbox {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-sm);
  border: 2px solid var(--border-focus);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
  background: transparent;
  padding: 0;
}

.custom-checkbox:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.custom-checkbox.checked {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-inverse);
}

.check-mark {
  animation: checkDraw 0.25s var(--ease-out);
}

@keyframes checkDraw {
  from {
    stroke-dasharray: 16;
    stroke-dashoffset: 16;
  }
  to {
    stroke-dasharray: 16;
    stroke-dashoffset: 0;
  }
}

/* ── Title ── */
.title {
  flex: 1;
  font-size: 0.875rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color var(--duration-fast) var(--ease-out);
}

.completed .title {
  text-decoration: line-through;
  color: var(--text-muted);
}

/* ── Category Tag ── */
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 500;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

/* ── Date ── */
.date {
  font-size: 0.75rem;
  color: var(--text-muted);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
</style>
