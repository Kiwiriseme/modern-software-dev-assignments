<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="brand-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect x="4" y="2" width="20" height="24" rx="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <line x1="10" y1="8" x2="18" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="10" y1="12" x2="18" y2="12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="10" y1="16" x2="15" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <rect x="8" y="3" width="3" height="1.5" rx="0.75" fill="currentColor" opacity="0.4"/>
          </svg>
        </div>
        <h1 class="auth-title">网页记事本</h1>
        <p class="auth-subtitle">创建新账户</p>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="field">
          <label class="field-label" for="reg-email">邮箱</label>
          <input
            id="reg-email"
            v-model="email"
            type="email"
            class="field-input"
            :class="{ 'field-input-error': errors.email }"
            placeholder="your@email.com"
            autocomplete="email"
            required
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="field">
          <label class="field-label" for="reg-password">密码</label>
          <input
            id="reg-password"
            v-model="password"
            type="password"
            class="field-input"
            :class="{ 'field-input-error': errors.password }"
            placeholder="至少6位"
            autocomplete="new-password"
            required
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <div class="field">
          <label class="field-label" for="reg-password2">确认密码</label>
          <input
            id="reg-password2"
            v-model="password2"
            type="password"
            class="field-input"
            :class="{ 'field-input-error': errors.password2 }"
            placeholder="再次输入密码"
            autocomplete="new-password"
            required
          />
          <span v-if="errors.password2" class="field-error">{{ errors.password2 }}</span>
        </div>

        <div v-if="formError" class="auth-error">{{ formError }}</div>

        <button type="submit" class="auth-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="auth-switch">
        已有账户？<router-link to="/login" class="auth-link">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const password2 = ref('')
const errors = reactive({ email: '', password: '', password2: '' })
const formError = ref('')
const loading = ref(false)

function clearErrors() {
  errors.email = ''
  errors.password = ''
  errors.password2 = ''
  formError.value = ''
}

function applyFieldErrors(data) {
  if (data.email) {
    errors.email = Array.isArray(data.email) ? data.email[0] : data.email
  }
  if (data.password) {
    errors.password = Array.isArray(data.password) ? data.password[0] : data.password
  }
  if (data.password2) {
    errors.password2 = Array.isArray(data.password2) ? data.password2[0] : data.password2
  }
}

async function handleRegister() {
  clearErrors()
  loading.value = true
  try {
    await authStore.register(email.value, password.value, password2.value)
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    if (data) {
      applyFieldErrors(data)
      if (!errors.email && !errors.password && !errors.password2) {
        formError.value = '注册失败，请重试'
      }
    } else {
      formError.value = '注册失败，请检查网络连接'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  padding: var(--space-lg);
}

.auth-card {
  width: 100%;
  max-width: 380px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-3xl) var(--space-2xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-light);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-2xl);
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-md);
}

.auth-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.03em;
  margin-bottom: var(--space-xs);
}

.auth-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.auth-error {
  background: var(--error-bg);
  color: var(--error);
  border: 1px solid var(--error-border);
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  font-size: 0.8125rem;
  text-align: center;
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.field-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.field-input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  font-size: 0.9375rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-page);
  color: var(--text-primary);
  outline: none;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.field-input-error {
  border-color: var(--error);
}

.field-input-error:focus {
  border-color: var(--error);
  box-shadow: 0 0 0 3px var(--error-bg);
}

.field-input::placeholder {
  color: var(--text-muted);
}

.field-error {
  font-size: 0.75rem;
  color: var(--error);
}

.auth-btn {
  width: 100%;
  padding: var(--space-md);
  background: var(--accent);
  color: var(--text-inverse);
  font-size: 0.9375rem;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}

.auth-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.auth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-switch {
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: var(--space-xl);
}

.auth-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
