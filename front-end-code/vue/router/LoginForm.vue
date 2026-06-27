<template>
  <div class="login-form">
    <h2>用户登录</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>用户名</label>
        <input 
          id="username"
          v-model="username" 
          type="text" 
          placeholder="请输入用户名"
          @blur="validateUsername"
          @focus="clearError"
        />
      </div>
      
      <div class="form-group">
        <label>密码</label>
        <input 
          id="password"
          v-model="password" 
          type="password" 
          placeholder="请输入密码"
          @blur="validatePassword"
        />
      </div>
      
      <div class="form-group">
        <label>记住我</label>
        <input 
          id="remember"
          v-model="rememberMe" 
          type="checkbox" 
          @change="toggleRemember"
        />
      </div>
      
      <button id="submit-btn" type="submit" @click="handleSubmit">
        登录
      </button>
      
      <button id="reset-btn" type="button" @click="handleReset">
        重置
      </button>
      
      <a href="#" class="forgot-link" @click.prevent="forgotPassword">
        忘记密码？
      </a>
    </form>
    
    <div class="social-login">
      <button class="btn-wechat" @click="loginWithWechat">
        微信登录
      </button>
      <button class="btn-qq" @dblclick="loginWithQQ">
        QQ登录
      </button>
    </div>
    
    <div 
      class="tooltip" 
      @mouseenter="showTooltip" 
      @mouseleave="hideTooltip"
    >
      帮助
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const username = ref('')
const password = ref('')
const rememberMe = ref(false)

const handleSubmit = () => {
  console.log('提交登录')
}

const handleReset = () => {
  username.value = ''
  password.value = ''
  rememberMe.value = false
}

const validateUsername = () => {
  console.log('验证用户名')
}

const validatePassword = () => {
  console.log('验证密码')
}

const clearError = () => {
  console.log('清除错误')
}

const toggleRemember = () => {
  console.log('切换记住我')
}

const forgotPassword = () => {
  console.log('忘记密码')
}

const loginWithWechat = () => {
  console.log('微信登录')
}

const loginWithQQ = () => {
  console.log('QQ登录')
}

const showTooltip = () => {
  console.log('显示提示')
}

const hideTooltip = () => {
  console.log('隐藏提示')
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 16px;
}

button {
  margin-right: 8px;
}
</style>
