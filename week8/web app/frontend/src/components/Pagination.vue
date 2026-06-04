<template>
  <div class="pagination">
    <button
      class="page-btn"
      :disabled="currentPage <= 1"
      @click="emit('page-change', currentPage - 1)"
    >上一页</button>
    <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
    <button
      class="page-btn"
      :disabled="currentPage >= totalPages"
      @click="emit('page-change', currentPage + 1)"
    >下一页</button>
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
  gap: 16px;
  padding: 12px;
}
.page-btn {
  padding: 6px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  font-size: 13px;
  color: #4f6ef7;
  cursor: pointer;
}
.page-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}
.page-btn:not(:disabled):hover {
  background: #f0f4ff;
}
.page-info {
  font-size: 13px;
  color: #666;
}
</style>
