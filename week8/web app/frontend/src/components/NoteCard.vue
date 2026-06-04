<template>
  <div class="note-card" @click="emit('select', note, 'note')">
    <div class="card-accent" :style="{ background: categoryColor(note.category) }"></div>
    <div class="card-body">
      <h3 class="card-title">{{ note.title || '无标题' }}</h3>
      <div class="card-meta">
        <span
          v-if="note.category"
          class="category-tag"
          :style="tagStyle(note.category)"
        >{{ note.category }}</span>
      </div>
      <p class="card-excerpt">{{ excerpt }}</p>
      <div class="card-footer">
        <span class="card-date">{{ formatDate(note.created_at) }}</span>
        <span class="card-read-more">
          阅读
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M4.5 3l3 3-3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { categoryColor, categoryBgColor, formatDate } from '../utils/categories.js'

const props = defineProps({
  note: { type: Object, required: true },
})

const emit = defineEmits(['select'])

const excerpt = computed(() => {
  const text = props.note.content || ''
  return text.length > 120 ? text.slice(0, 120) + '…' : text || '暂无内容预览'
})

function tagStyle(cat) {
  return {
    background: categoryBgColor(cat),
    color: categoryColor(cat),
  }
}
</script>

<style scoped>
.note-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  box-shadow: var(--shadow-xs);
  display: flex;
  overflow: hidden;
  animation: fadeInUp 0.4s var(--ease-out) both;
  position: relative;
}

.note-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-out);
  box-shadow: var(--shadow-lg);
  pointer-events: none;
}

.note-card:hover {
  transform: translateY(-3px);
  border-color: var(--border);
}

.note-card:hover::after {
  opacity: 1;
}

/* ── Accent stripe ── */
.card-accent {
  width: 4px;
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity var(--duration-normal) var(--ease-out),
              width var(--duration-normal) var(--ease-out);
}

.note-card:hover .card-accent {
  opacity: 0.8;
  width: 5px;
}

/* ── Card body ── */
.card-body {
  flex: 1;
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  min-width: 0;
}

/* ── Title ── */
.card-title {
  font-family: var(--font-display);
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── Category Tag ── */
.card-meta {
  display: flex;
  gap: var(--space-xs);
}

.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* ── Excerpt ── */
.card-excerpt {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── Footer ── */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-xs);
}

.card-date {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.card-read-more {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--accent);
  opacity: 0;
  transform: translateX(-4px);
  transition: all var(--duration-normal) var(--ease-out);
}

.note-card:hover .card-read-more {
  opacity: 1;
  transform: translateX(0);
}
</style>
