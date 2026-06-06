import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
})

// Redirect to login on 403 (session expired mid-use)
api.interceptors.response.use(
  response => response,
  async (error) => {
    if (error.response?.status === 403) {
      // Only redirect if not already on a guest page
      const path = window.location.pathname
      if (path !== '/login' && path !== '/register') {
        const { useAuthStore } = await import('../stores/auth.js')
        useAuthStore().user = null
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

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

// Auth
export function register(data) {
  return api.post('/auth/register', data)
}

export function login(data) {
  return api.post('/auth/login', data)
}

export function logout() {
  return api.post('/auth/logout')
}

export function fetchCurrentUser() {
  return api.get('/auth/me')
}

export function fetchAISettings() {
  return api.get('/ai-settings')
}

export function saveAISettings(data) {
  return api.put('/ai-settings', data)
}

export function summarizeNoteTodos(noteId) {
  return api.post(`/notes/${noteId}/summarize-todos`)
}

export default api
