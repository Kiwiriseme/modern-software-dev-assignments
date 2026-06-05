<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="store.showSettings" class="overlay" @click.self="store.closeSettings()">
        <div class="dialog">
          <div class="dialog-header">
            <h2 class="dialog-title">⚙ API 设置</h2>
            <p class="dialog-subtitle">配置 AI 服务以使用待办事项总结功能</p>
          </div>

          <form class="dialog-body" @submit.prevent="save">
            <div class="form-group">
              <label class="form-label">API Base URL</label>
              <input
                v-model="form.base_url"
                type="url"
                class="form-input"
                placeholder="https://api.openai.com/v1"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Model</label>
              <input
                v-model="form.model"
                type="text"
                class="form-input"
                placeholder="gpt-4o-mini"
              />
            </div>

            <div class="form-group">
              <label class="form-label">API Key</label>
              <input
                v-model="form.api_key"
                type="password"
                class="form-input"
                placeholder="sk-..."
                autocomplete="off"
              />
              <p class="form-hint">密钥将加密存储在本地数据库中，不会上传到任何第三方服务</p>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn-cancel" @click="store.closeSettings()">取消</button>
              <button type="submit" class="btn-save">保存</button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useNotesStore } from '../stores/notes.js'

const store = useNotesStore()
const form = ref({ base_url: '', model: '', api_key: '' })

watch(() => store.aiSettings, (settings) => {
  if (settings) {
    form.value = {
      base_url: settings.base_url || '',
      model: settings.model || '',
      api_key: settings.api_key || '',
    }
  }
})

async function save() {
  const data = {
    base_url: form.value.base_url || 'https://api.openai.com/v1',
    model: form.value.model || 'gpt-4o-mini',
    api_key: form.value.api_key || '***',
  }
  store.saveAISettingsData(data)
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(45, 36, 24, 0.35);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10001;
}

.dialog {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  min-width: 420px;
  max-width: 480px;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-light);
}

.dialog-header {
  padding: var(--space-xl) var(--space-xl) 0;
}

.dialog-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-xs) 0;
}

.dialog-subtitle {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin: 0 0 var(--space-md) 0;
}

.dialog-body {
  padding: var(--space-lg) var(--space-xl) var(--space-xl);
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.form-input {
  width: 100%;
  padding: 9px var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: var(--bg-page);
  outline: none;
  transition: all var(--duration-fast) var(--ease-out);
  box-sizing: border-box;
  font-family: var(--font-mono);
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
  background: var(--bg-surface);
}

.form-hint {
  font-size: 0.6875rem;
  color: var(--text-muted);
  margin: var(--space-xs) 0 0 0;
}

.dialog-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: flex-end;
  padding-top: var(--space-sm);
}

.btn-cancel {
  padding: 9px var(--space-xl);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-cancel:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-save {
  padding: 9px var(--space-xl);
  border: none;
  border-radius: var(--radius-sm);
  background: var(--accent);
  color: var(--text-inverse);
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-save:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow-md);
}

/* Transition */
.modal-enter-active {
  transition: all 0.25s var(--ease-out);
}
.modal-leave-active {
  transition: all 0.15s ease-in;
}
.modal-enter-from {
  opacity: 0;
}
.modal-enter-from .dialog {
  transform: scale(0.95) translateY(8px);
}
.modal-leave-to {
  opacity: 0;
}
</style>
