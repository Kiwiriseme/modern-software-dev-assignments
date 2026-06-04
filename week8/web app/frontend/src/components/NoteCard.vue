<template>
  <div class="note-card" @click="emit('select', note, 'note')">
    <h3 class="card-title">{{ note.title }}</h3>
    <div class="card-meta">
      <span
        v-if="note.category"
        class="category-tag"
        :style="{ background: categoryColor(note.category) }"
      >{{ note.category }}</span>
    </div>
    <p class="card-excerpt">{{ excerpt }}</p>
    <span class="card-date">{{ formatDate(note.created_at) }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { categoryColor, formatDate } from '../utils/categories.js'

const props = defineProps({
  note: { type: Object, required: true },
})

const emit = defineEmits(['select'])

const excerpt = computed(() => {
  const text = props.note.content || ''
  return text.length > 100 ? text.slice(0, 100) + '...' : text
})
</script>

<style scoped>
.note-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.note-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}
.card-meta {
  display: flex;
  gap: 6px;
}
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
}
.card-excerpt {
  font-size: 12px;
  color: #999;
  margin: 0;
  line-height: 1.4;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-date {
  font-size: 11px;
  color: #999;
  align-self: flex-end;
}
</style>
