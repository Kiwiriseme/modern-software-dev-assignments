<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="overlay" @click.self="$emit('cancel')">
        <div class="dialog">
          <p class="dialog-message">{{ message }}</p>
          <div class="dialog-actions">
            <button class="btn-cancel" @click="$emit('cancel')">取消</button>
            <button class="btn-confirm" @click="$emit('confirm')">确定</button>
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
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}
.dialog {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  min-width: 320px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
.dialog-message {
  font-size: 15px;
  color: #1a1a1a;
  margin: 0 0 20px 0;
  text-align: center;
}
.dialog-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.btn-cancel {
  padding: 8px 24px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  color: #666;
  cursor: pointer;
  font-size: 14px;
}
.btn-confirm {
  padding: 8px 24px;
  border: none;
  border-radius: 8px;
  background: #4f6ef7;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}
.btn-confirm:hover {
  background: #3d5bd9;
}
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>
