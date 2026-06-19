import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserProfile } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(phone, smsCode) {
    const res = await loginApi(phone, smsCode)
    token.value = res.access_token
    localStorage.setItem('access_token', res.access_token)
    localStorage.setItem('refresh_token', res.refresh_token)
    await fetchUserProfile()
    return res
  }

  async function fetchUserProfile() {
    try {
      const res = await getUserProfile()
      user.value = res
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    login,
    fetchUserProfile,
    logout
  }
})
