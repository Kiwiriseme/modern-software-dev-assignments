import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index.js'
import { register, login, logout, fetchCurrentUser } from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)

  async function checkAuth() {
    try {
      // Fetch CSRF cookie first so subsequent POST/PUT/DELETE work
      await api.get('/auth/csrf')
      const res = await fetchCurrentUser()
      user.value = res.data
      return true
    } catch (e) {
      user.value = null
      return false
    }
  }

  async function registerUser(email, password, password2) {
    const res = await register({ email, password, password2 })
    user.value = res.data
    return res.data
  }

  async function loginUser(email, password) {
    const res = await login({ email, password })
    user.value = res.data
    return res.data
  }

  async function logoutUser() {
    await logout()
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    checkAuth,
    register: registerUser,
    login: loginUser,
    logout: logoutUser,
  }
})
