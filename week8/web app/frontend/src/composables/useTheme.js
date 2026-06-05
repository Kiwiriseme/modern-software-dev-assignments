import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'app-theme'
const LIGHT = 'light'
const DARK = 'dark'

const theme = ref(getInitialTheme())

function getInitialTheme() {
  // localStorage wins first
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === LIGHT || stored === DARK) return stored
  // Fall back to system preference
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) return DARK
  return LIGHT
}

function applyTheme(value) {
  document.documentElement.setAttribute('data-theme', value)
  // Update meta theme-color for browser chrome
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) {
    meta.content = value === DARK ? '#1a1d23' : '#faf7f2'
  }
}

// Apply on init
applyTheme(theme.value)

// Watch for system preference changes
const systemQuery = window.matchMedia('(prefers-color-scheme: dark)')
systemQuery.addEventListener('change', (e) => {
  // Only auto-switch if user hasn't explicitly set a preference
  if (!localStorage.getItem(STORAGE_KEY)) {
    theme.value = e.matches ? DARK : LIGHT
  }
})

function toggleTheme() {
  theme.value = theme.value === LIGHT ? DARK : LIGHT
}

function setTheme(value) {
  if (value !== LIGHT && value !== DARK) return
  theme.value = value
}

// Reactively apply theme + persist
watchEffect(() => {
  applyTheme(theme.value)
  try {
    localStorage.setItem(STORAGE_KEY, theme.value)
  } catch {
    // localStorage full — still works for this session
  }
})

export function useTheme() {
  return {
    theme,
    isDark: () => theme.value === DARK,
    toggleTheme,
    setTheme,
  }
}
