<template>
  <div class="home">
    <h1>欢迎来到首页</h1>
    <p>这是一个Vue 3 + TypeScript + Vite项目</p>
    <button @click="incrementCounter" class="counter-btn">
      点击次数: {{ count }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)

const incrementCounter = () => {
  count.value++
  console.log('计数器增加:', count.value)
}
</script>

<style scoped>
.home {
  padding: 24px;
  text-align: center;
}

.counter-btn {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
}

.counter-btn:hover {
  background-color: #359268;
}
</style>