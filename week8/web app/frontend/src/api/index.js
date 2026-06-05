import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
})

export function fetchCategories() {
  return api.get('/categories')
}

export function fetchTodos(params = {}) {
  return api.get('/todos', { params })
}

export function createTodo(data) {
  return api.post('/todos', data)
}

export function fetchTodo(id) {
  return api.get(`/todos/${id}`)
}

export function updateTodo(id, data) {
  return api.put(`/todos/${id}`, data)
}

export function patchTodo(id, data) {
  return api.patch(`/todos/${id}`, data)
}

export function deleteTodo(id) {
  return api.delete(`/todos/${id}`)
}

export function fetchNotes(params = {}) {
  return api.get('/notes', { params })
}

export function createNote(data) {
  return api.post('/notes', data)
}

export function fetchNote(id) {
  return api.get(`/notes/${id}`)
}

export function updateNote(id, data) {
  return api.put(`/notes/${id}`, data)
}

export function deleteNote(id) {
  return api.delete(`/notes/${id}`)
}

export function deleteCategory(name) {
  return api.delete('/categories/delete', { params: { name } })
}

export function fetchAISettings() {
  return api.get('/ai-settings/1')
}

export function saveAISettings(data) {
  return api.put('/ai-settings/1', data)
}

export function summarizeNoteTodos(noteId) {
  return api.post(`/notes/${noteId}/summarize-todos`)
}

export default api
