<template>
  <div class="content-area">
    <TopBar @create="startCreate" @toast="emit('toast', $event)" />
    <TodoList
      v-if="store.activeTab === 'todo'"
      @select="onSelect"
      @toast="emit('toast', $event)"
    />
    <NoteCards
      v-if="store.activeTab === 'text'"
      @select="onSelect"
    />
    <Pagination
      v-if="totalPages > 1"
      :current-page="store.currentPage"
      :total-pages="totalPages"
      @page-change="onPageChange"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import TopBar from './TopBar.vue'
import TodoList from './TodoList.vue'
import NoteCards from './NoteCards.vue'
import Pagination from './Pagination.vue'

const emit = defineEmits(['select', 'create', 'toast'])
const store = useNotesStore()

const totalPages = computed(() => {
  return Math.ceil(store.totalCount / store.pageSize)
})

function onSelect(item, type) {
  emit('select', item, type)
}

function startCreate() {
  emit('create')
}

async function onPageChange(page) {
  store.setPage(page)
  if (store.activeTab === 'todo') {
    await store.loadTodos()
  } else {
    await store.loadNotes()
  }
}
</script>

<style scoped>
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
  overflow: hidden;
}
</style>
