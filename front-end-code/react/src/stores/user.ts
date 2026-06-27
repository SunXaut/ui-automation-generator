import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  id: number
  username: string
  email: string
}

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => currentUser.value?.username || 'Guest')

  async function login(username: string, password: string) {
    isLoading.value = true
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      token.value = 'mock-jwt-token'
      currentUser.value = {
        id: 1,
        username: username,
        email: `${username}@example.com`
      }
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    token.value = null
    currentUser.value = null
  }

  return {
    currentUser,
    token,
    isLoading,
    isLoggedIn,
    userName,
    login,
    logout
  }
})