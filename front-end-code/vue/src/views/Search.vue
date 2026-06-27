<template>
  <div class="search-box">
    <h2>搜索页面</h2>
    <div class="search-container">
      <input
        v-model="searchQuery"
        type="search"
        placeholder="输入搜索关键词"
        class="search-input"
        @input="handleSearch"
        @focus="onFocus"
        @blur="onBlur"
      />
      <button @click="performSearch" class="search-btn" :disabled="!searchQuery">
        搜索
      </button>
      <button @click="clearSearch" class="clear-btn">
        清除
      </button>
    </div>
    <div v-if="results.length > 0" class="results">
      <p>找到 {{ results.length }} 个结果:</p>
      <ul>
        <li v-for="(result, index) in results" :key="index">
          {{ result }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const searchQuery = ref('')
const results = ref<string[]>([])

const handleSearch = () => {
  console.log('搜索中:', searchQuery.value)
}

const performSearch = () => {
  console.log('执行搜索:', searchQuery.value)
  if (searchQuery.value) {
    results.value = [
      `结果1: ${searchQuery.value}相关内容`,
      `结果2: ${searchQuery.value}更多信息`,
      `结果3: ${searchQuery.value}相关条目`
    ]
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  results.value = []
}

const onFocus = () => {
  console.log('输入框获得焦点')
}

const onBlur = () => {
  console.log('输入框失去焦点')
}
</script>

<style scoped>
.search-box {
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.search-container {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-btn, .clear-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-btn {
  background-color: #42b983;
  color: white;
}

.search-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.clear-btn {
  background-color: #ff6b6b;
  color: white;
}

.results ul {
  list-style: none;
  padding: 0;
}

.results li {
  padding: 8px;
  border-bottom: 1px solid #eee;
}
</style>