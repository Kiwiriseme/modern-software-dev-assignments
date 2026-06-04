<template>
  <div class="pagination">
    <button
      class="page-btn"
      :disabled="currentPage <= 1"
      @click="emit('page-change', currentPage - 1)"
    >
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M8.5 3.5L5 7l3.5 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      上一页
    </button>

    <div class="page-indicator">
      <span class="page-current">{{ currentPage }}</span>
      <span class="page-sep">/</span>
      <span class="page-total">{{ totalPages }}</span>
    </div>

    <button
      class="page-btn"
      :disabled="currentPage >= totalPages"
      @click="emit('page-change', currentPage + 1)"
    >
      下一页
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M5.5 3.5L9 7l-3.5 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})

const emit = defineEmits(['page-change'])
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--border-light);
  background: var(--bg-surface);
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 7px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.page-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-focus);
}

.page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-indicator {
  display: flex;
  align-items: baseline;
  gap: 2px;
  font-variant-numeric: tabular-nums;
}

.page-current {
  font-family: var(--font-display);
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--text-primary);
}

.page-sep {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin: 0 2px;
}

.page-total {
  font-size: 0.8125rem;
  color: var(--text-muted);
}
</style>
