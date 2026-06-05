<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="overlay" @click.self="$emit('cancel')">
        <div class="dialog">
          <div class="dialog-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
              <path d="M12 8v4M12 15.5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <p class="dialog-message">{{ message }}</p>
          <div class="dialog-actions">
            <button v-if="showDiscard" class="btn-discard" @click="$emit('discard')">{{ discardText }}</button>
            <button class="btn-cancel" @click="$emit('cancel')">{{ cancelText }}</button>
            <button class="btn-confirm" @click="$emit('confirm')">{{ confirmText }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '确定执行此操作？' },
  confirmText: { type: String, default: '确定删除' },
  cancelText: { type: String, default: '取消' },
  showDiscard: { type: Boolean, default: false },
  discardText: { type: String, default: '不保存' },
})

defineEmits(['confirm', 'cancel', 'discard'])
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
  z-index: 10000;
}

.dialog {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-2xl);
  min-width: 340px;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-light);
  text-align: center;
}

.dialog-icon {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-lg);
  color: var(--accent-warm);
}

.dialog-message {
  font-family: var(--font-display);
  font-size: 1rem;
  color: var(--text-primary);
  margin: 0 0 var(--space-xl) 0;
}

.dialog-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
}

.btn-cancel,
.btn-discard {
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

.btn-discard:hover {
  background: var(--error-bg);
  color: var(--error);
  border-color: var(--error);
}

.btn-confirm {
  padding: 9px var(--space-xl);
  border: none;
  border-radius: var(--radius-sm);
  background: var(--error);
  color: #fff;
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-confirm:hover {
  background: #b04a3a;
  box-shadow: var(--shadow-md);
}

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
