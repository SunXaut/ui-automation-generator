<template>
  <div class="login">
    <h1>用户登录</h1>
    <form @submit.prevent="handleSubmit" class="login-form">
      <div class="form-group">
        <label for="username">用户名</label>
        <input
          id="username"
          v-model="formData.username"
          type="text"
          placeholder="请输入用户名"
          data-testid="username-input"
          @blur="validateUsername"
          @focus="clearError"
        />
        <span v-if="errors.username" class="error">{{ errors.username }}</span>
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          v-model="formData.password"
          type="password"
          placeholder="请输入密码"
          data-testid="password-input"
          @blur="validatePassword"
        />
        <span v-if="errors.password" class="error">{{ errors.password }}</span>
      </div>

      <div class="form-group checkbox-group">
        <input
          id="remember"
          v-model="formData.rememberMe"
          type="checkbox"
          data-testid="remember-checkbox"
          @change="toggleRemember"
        />
        <label for="remember">记住我</label>
      </div>

      <div class="form-actions">
        <button type="submit" data-testid="login-button" class="btn-login">
          登录
        </button>
        <button type="button" @click="handleReset" class="btn-reset">
          重置
        </button>
      </div>

      <a href="#" @click.prevent="forgotPassword" class="forgot-link" data-testid="forgot-link">
        忘记密码？
      </a>
    </form>

    <div class="social-login">
      <button @click="loginWithWechat" class="btn-wechat" data-testid="wechat-login">
        微信登录
      </button>
      <button @dblclick="loginWithQQ" class="btn-qq" data-testid="qq-login">
        QQ登录
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const formData = reactive({
  username: '',
  password: '',
  rememberMe: false
})

const errors = reactive({
  username: '',
  password: ''
})

const validateUsername = () => {
  if (!formData.username) {
    errors.username = '用户名不能为空'
  } else {
    errors.username = ''
  }
}

const validatePassword = () => {
  if (!formData.password) {
    errors.password = '密码不能为空'
  } else if (formData.password.length < 6) {
    errors.password = '密码至少6位'
  } else {
    errors.password = ''
  }
}

const clearError = () => {
  errors.username = ''
  errors.password = ''
}

const toggleRemember = () => {
  console.log('记住我状态:', formData.rememberMe)
}

const handleSubmit = () => {
  validateUsername()
  validatePassword()
  if (!errors.username && !errors.password) {
    console.log('提交登录:', formData)
  }
}

const handleReset = () => {
  formData.username = ''
  formData.password = ''
  formData.rememberMe = false
  errors.username = ''
  errors.password = ''
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
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 0 auto;
  padding: 24px;
}

.login h1 {
  text-align: center;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-group label {
  display: inline;
  font-weight: normal;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin: 20px 0;
}

.btn-login, .btn-reset {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-login {
  background-color: #42b983;
  color: white;
}

.btn-reset {
  background-color: #ff6b6b;
  color: white;
}

.forgot-link {
  display: block;
  text-align: right;
  color: #646cff;
  text-decoration: none;
}

.social-login {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-wechat, .btn-qq {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-wechat {
  background-color: #07c160;
  color: white;
}

.btn-qq {
  background-color: #1296db;
  color: white;
}

.error {
  color: #ff6b6b;
  font-size: 12px;
}
</style>