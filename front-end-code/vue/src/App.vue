<template>
  <div id="app">
    <header class="app-header">
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/about">关于</router-link>
        <router-link to="/login">登录</router-link>
        <router-link to="/dashboard">仪表盘</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-header {
  padding: 16px;
  background-color: #f5f5f5;
}

nav a {
  margin-right: 16px;
  text-decoration: none;
  color: #333;
}

nav a.router-link-active {
  color: #42b983;
}
</style>