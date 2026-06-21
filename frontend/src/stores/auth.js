import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const userInfo = computed(() => user.value)

  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  async function login(username, password) {
    try {
      const res = await api.post('/auth/login', { username, password })
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('token', res.data.access_token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      api.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
      return true
    } catch (e) {
      throw e
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete api.defaults.headers.common['Authorization']
  }

  async function checkAuth() {
    if (!token.value) return false
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
      return true
    } catch (e) {
      logout()
      return false
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    userInfo,
    login,
    logout,
    checkAuth
  }
})
