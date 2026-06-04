<template>
  <div class="note-cards-container">
    <div v-if="store.isNotesLoading" class="loading">加载中...</div>
    <div v-else-if="store.notes.length === 0" class="empty">
      <p>{{ emptyMessage }}</p>
    </div>
    <div v-else class="note-cards-grid">
      <NoteCard
        v-for="note in store.notes"
        :key="note.id"
        :note="note"
        @select="emit('select', note, 'note')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import NoteCard from './NoteCard.vue'

const emit = defineEmits(['select'])
const store = useNotesStore()

const emptyMessage = computed(() => {
  if (store.searchQuery) return '未找到匹配的记录'
  if (store.activeCategory !== '全部') return '当前分类下暂无记录'
  return '暂无记录，点击 + 创建'
})
</script>

<style scoped>
.note-cards-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}
.note-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.loading, .empty {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>
