export default {
  data() {
    return {
      isAuthenticated: false,
      username: ''
    }
  },
  methods: {
    handleLogin(credentials: { username: string; password: string }) {
      console.log('登录:', credentials)
      this.isAuthenticated = true
      this.username = credentials.username
    },
    handleLogout() {
      console.log('登出')
      this.isAuthenticated = false
      this.username = ''
    }
  }
}