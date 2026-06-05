<template>
  <button
    class="theme-toggle"
    :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
    @click="toggleTheme"
    :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'"
  >
    <!-- Sun icon — visible in dark mode (click to switch to light) -->
    <svg
      class="toggle-icon sun"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.6"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
    <!-- Moon icon — visible in light mode (click to switch to dark) -->
    <svg
      class="toggle-icon moon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.6"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useTheme } from '../composables/useTheme.js'

const { theme, toggleTheme } = useTheme()
const isDark = computed(() => theme.value === 'dark')
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--bg-hover);
  color: var(--text-secondary);
  transition:
    background var(--duration-fast) var(--ease-out),
    color var(--duration-normal) var(--ease-in-out);
}

.theme-toggle:hover {
  background: var(--bg-active);
  color: var(--text-primary);
}

.toggle-icon {
  width: 18px;
  height: 18px;
  position: absolute;
  transition:
    transform var(--duration-slow) var(--ease-out),
    opacity var(--duration-slow) var(--ease-out);
}

/* Light mode: show moon, hide sun */
.toggle-icon.moon {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}

.toggle-icon.sun {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}

/* Dark mode: show sun, hide moon */
[data-theme="dark"] .toggle-icon.moon {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}

[data-theme="dark"] .toggle-icon.sun {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}
</style>
