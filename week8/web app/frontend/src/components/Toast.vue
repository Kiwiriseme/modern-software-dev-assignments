<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" class="toast" :class="type">
        <span class="toast-icon">
          <svg v-if="type === 'success'" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
            <path d="M5.5 8l2 2 3-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8 5v4M8 10.5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </span>
        {{ message }}
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  message: { type: String, default: '' },
  type: { type: String, default: 'error' },
  duration: { type: Number, default: 3000 },
  trigger: { type: Number, default: 0 },
})

const visible = ref(false)
let timer = null

onUnmounted(() => {
  clearTimeout(timer)
})

watch(() => props.trigger, () => {
  if (props.trigger > 0) {
    visible.value = true
    clearTimeout(timer)
    timer = setTimeout(() => {
      visible.value = false
    }, props.duration)
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  font-weight: 500;
  z-index: 9999;
  box-shadow: var(--shadow-lg);
  white-space: nowrap;
  backdrop-filter: blur(8px);
}

.toast.success {
  background: var(--success-bg);
  color: var(--success);
  border: 1px solid var(--success-border);
}

.toast.error {
  background: var(--error-bg);
  color: var(--error);
  border: 1px solid var(--error-border);
}

.toast-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.toast-enter-active {
  transition: all 0.35s var(--ease-out);
}

.toast-leave-active {
  transition: all 0.2s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-16px) scale(0.95);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-8px);
}
</style>
