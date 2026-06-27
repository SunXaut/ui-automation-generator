import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    name: '计数器',
    isLoading: false
  }),

  getters: {
    doubleCount: (state) => state.count * 2,
    isPositive: (state) => state.count > 0
  },

  actions: {
    increment() {
      this.count++
    },
    decrement() {
      if (this.count > 0) {
        this.count--
      }
    },
    reset() {
      this.count = 0
    },
    async fetchData() {
      this.isLoading = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.count = 10
      } finally {
        this.isLoading = false
      }
    }
  }
})

// User Store
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: null,
    permissions: []
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    hasPermission: (state) => (permission) => {
      return state.permissions.includes(permission)
    }
  },

  actions: {
    login(username, password) {
      // 模拟登录
      this.token = 'mock-token'
      this.user = { username }
      this.permissions = ['read', 'write']
    },
    logout() {
      this.token = null
      this.user = null
      this.permissions = []
    },
    updatePermissions(newPermissions) {
      this.permissions = newPermissions
    }
  }
})
