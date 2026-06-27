import { defineStore } from 'pinia'

interface User {
  id: number
  username: string
  email: string
  role: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null as User | null,
    token: null as string | null,
    isLoading: false,
    error: null as string | null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.currentUser?.role === 'admin',
    userName: (state) => state.currentUser?.username || 'Guest'
  },

  actions: {
    async login(username: string, password: string) {
      this.isLoading = true
      this.error = null
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        this.token = 'mock-jwt-token'
        this.currentUser = {
          id: 1,
          username: username,
          email: `${username}@example.com`,
          role: 'user'
        }
      } catch (e) {
        this.error = '登录失败'
        throw e
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      this.token = null
      this.currentUser = null
    },

    async fetchCurrentUser() {
      if (!this.token) return
      this.isLoading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 300))
      } finally {
        this.isLoading = false
      }
    }
  }
})