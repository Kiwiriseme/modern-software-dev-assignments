<template>
  <div class="note-cards-container">
    <!-- Loading skeleton -->
    <div v-if="store.isNotesLoading" class="loading-state">
      <div v-for="n in 4" :key="n" class="skeleton-card">
        <div class="skeleton-box sk-title"></div>
        <div class="skeleton-box sk-tag"></div>
        <div class="skeleton-box sk-line"></div>
        <div class="skeleton-box sk-line short"></div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="store.notes.length === 0" class="empty-state">
      <div class="empty-illustration">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <rect x="10" y="6" width="44" height="52" rx="6" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.3"/>
          <path d="M22 20h20M22 26h16M22 32h12M22 38h18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.3"/>
          <circle cx="48" cy="52" r="8" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
          <path d="M48 48v8M44 52h8" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="empty-title">{{ emptyTitle }}</p>
      <p class="empty-desc">{{ emptyDesc }}</p>
    </div>

    <!-- Cards grid -->
    <div v-else class="note-cards-grid">
      <NoteCard
        v-for="(note, idx) in store.notes"
        :key="note.id"
        :note="note"
        :style="{ animationDelay: idx * 50 + 'ms' }"
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

const emptyTitle = computed(() => {
  if (store.searchQuery) return '未找到匹配的笔记'
  if (store.activeCategory !== '全部') return '此分类暂无笔记'
  return '开始记录你的想法'
})

const emptyDesc = computed(() => {
  if (store.searchQuery) return '尝试更换搜索关键词'
  if (store.activeCategory !== '全部') return '切换分类或创建新的笔记'
  return '点击右上角的「新建」按钮写下第一条笔记'
})
</script>

<style scoped>
.note-cards-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

/* ── Grid ── */
.note-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

@media (max-width: 900px) {
  .note-cards-grid {
    grid-template-columns: 1fr;
  }
}

/* ── Loading Skeleton ── */
.loading-state {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

.skeleton-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  animation: subtlePulse 1.8s ease-in-out infinite;
}

.skeleton-box {
  height: 12px;
  border-radius: 4px;
  background: var(--bg-hover);
}

.sk-title {
  width: 60%;
  height: 16px;
}

.sk-tag {
  width: 40px;
  height: 20px;
  border-radius: 4px;
}

.sk-line {
  width: 100%;
}

.sk-line.short {
  width: 70%;
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
