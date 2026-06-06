<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand-mark">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <rect x="4" y="2" width="20" height="24" rx="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
          <line x1="10" y1="8" x2="18" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          <line x1="10" y1="12" x2="18" y2="12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          <line x1="10" y1="16" x2="15" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          <rect x="8" y="3" width="3" height="1.5" rx="0.75" fill="currentColor" opacity="0.4"/>
        </svg>
      </div>
      <div>
        <div class="brand-name">网页记事本</div>
        <div class="brand-subtitle">记录 · 整理 · 思考</div>
      </div>
    </div>

    <nav class="nav-list">
      <div class="nav-section-label">分类</div>
      <button
        v-for="cat in displayCategories"
        :key="cat"
        class="nav-item"
        :class="{ active: store.activeCategory === cat }"
        @click="store.setActiveCategory(cat)"
      >
        <span class="nav-dot" :class="{ filled: store.activeCategory === cat }"></span>
        <span class="nav-label">{{ cat }}</span>
        <span v-if="store.activeCategory === cat" class="nav-indicator"></span>
        <button
          v-if="cat !== '全部'"
          class="nav-delete-btn"
          @click.stop="emit('delete-category', cat)"
          aria-label="删除分类"
          title="删除分类"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
      </button>
    </nav>

    <div class="sidebar-footer">
      <div class="footer-stats">
        <span class="stat-item">
          <span class="stat-count">{{ store.todoCount }}</span>
          <span class="stat-label">待办</span>
        </span>
        <span class="stat-divider">·</span>
        <span class="stat-item">
          <span class="stat-count">{{ store.noteCount }}</span>
          <span class="stat-label">笔记</span>
        </span>
      </div>
      <div class="footer-divider"></div>
      <div class="footer-user">
        <span class="user-email">{{ authStore.user?.email || '未登录' }}</span>
      </div>
      <div class="footer-divider"></div>
      <div class="footer-actions">
        <button
          class="logout-btn"
          @click="handleLogout"
          aria-label="登出"
          title="登出"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3M11 11l3-3-3-3M14 8H6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <ThemeToggle />
        <span class="action-divider"></span>
        <button
          class="settings-btn"
          @click="store.openSettings()"
          aria-label="API 设置"
          title="API 设置"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1.06 1.06M11.54 11.54l1.06 1.06M3.4 12.6l1.06-1.06M11.54 4.46l1.06-1.06" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotesStore } from '../stores/notes.js'
import { useAuthStore } from '../stores/auth.js'
import { PRESET_CATEGORIES } from '../utils/categories.js'
import ThemeToggle from './ThemeToggle.vue'

const emit = defineEmits(['delete-category'])

const router = useRouter()
const authStore = useAuthStore()
const store = useNotesStore()

const displayCategories = computed(() => {
  const custom = store.categories.filter(c => !PRESET_CATEGORIES.includes(c))
  return [...PRESET_CATEGORIES, ...custom].filter(c => !store.deletedCategories.includes(c))
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  height: 100vh;
  user-select: none;
  /* Subtle inner shadow for depth */
  box-shadow: inset -1px 0 0 rgba(45, 36, 24, 0.03);
}

/* ── Header ── */
.sidebar-header {
  padding: var(--space-xl) var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  border-bottom: 1px solid var(--border-light);
}

.brand-mark {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.03em;
  line-height: 1.3;
}

.brand-subtitle {
  font-size: 0.6875rem;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  margin-top: 1px;
}

/* ── Navigation ── */
.nav-list {
  flex: 1;
  padding: var(--space-md) var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: 1px;
  overflow-y: auto;
}

.nav-section-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: var(--space-sm) var(--space-md) var(--space-xs);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  text-align: left;
  font-size: 0.875rem;
  color: var(--text-secondary);
  position: relative;
  transition: all var(--duration-fast) var(--ease-out);
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--bg-active);
  color: var(--text-primary);
  font-weight: 500;
}

.nav-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-focus);
  flex-shrink: 0;
  transition: all var(--duration-normal) var(--ease-out);
}

.nav-dot.filled {
  background: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.nav-label {
  flex: 1;
}

.nav-indicator {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: var(--accent);
  animation: indicatorIn var(--duration-normal) var(--ease-out);
}

@keyframes indicatorIn {
  from { height: 0; opacity: 0; }
  to { height: 16px; opacity: 1; }
}

.nav-delete-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  opacity: 0;
  transition: all var(--duration-fast) var(--ease-out);
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.nav-item:hover .nav-delete-btn {
  opacity: 1;
}

.nav-delete-btn:hover {
  background: var(--error-bg);
  color: var(--error);
}

/* ── Footer ── */
.sidebar-footer {
  padding: var(--space-md) var(--space-lg) var(--space-lg);
  border-top: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

.footer-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.stat-count {
  font-family: var(--font-display);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.6875rem;
  color: var(--text-muted);
}

.stat-divider {
  color: var(--border);
  font-size: 0.75rem;
}

.footer-divider {
  width: 60%;
  height: 1px;
  background: var(--border-light);
}

.footer-user {
  display: flex;
  justify-content: center;
  padding: var(--space-xs) 0;
}

.user-email {
  font-size: 0.6875rem;
  color: var(--text-muted);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.footer-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
}

.action-divider {
  width: 1px;
  height: 16px;
  background: var(--border-light);
}

.settings-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.settings-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.logout-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.logout-btn:hover {
  background: var(--error-bg);
  color: var(--error);
}
</style>
