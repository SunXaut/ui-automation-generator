<template>
  <div class="dashboard">
    <h1>仪表盘</h1>
    <div class="stats">
      <div class="stat-card">
        <h3>总用户数</h3>
        <p class="stat-value">{{ totalUsers }}</p>
        <button @click="refreshStats" class="refresh-btn">
          刷新
        </button>
      </div>
      <div class="stat-card">
        <h3>活跃用户</h3>
        <p class="stat-value">{{ activeUsers }}</p>
        <button @click="toggleActiveFilter" class="filter-btn">
          {{ showOnlyActive ? '显示全部' : '仅显示活跃' }}
        </button>
      </div>
    </div>
    <div class="actions">
      <button @click="exportData" class="action-btn export">
        导出数据
      </button>
      <button @click="importData" class="action-btn import">
        导入数据
      </button>
      <button @click="refreshAll" class="action-btn refresh">
        刷新全部
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const totalUsers = ref(1250)
const activeUsers = ref(843)
const showOnlyActive = ref(false)

const refreshStats = () => {
  console.log('刷新统计数据')
  totalUsers.value = Math.floor(Math.random() * 1000) + 1000
}

const toggleActiveFilter = () => {
  showOnlyActive.value = !showOnlyActive.value
  console.log('切换活跃筛选:', showOnlyActive.value)
}

const exportData = () => {
  console.log('导出数据')
}

const importData = () => {
  console.log('导入数据')
}

const refreshAll = () => {
  console.log('刷新全部')
  refreshStats()
}
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

.stats {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #42b983;
}

.actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.export {
  background-color: #42b983;
  color: white;
}

.import {
  background-color: #646cff;
  color: white;
}

.refresh {
  background-color: #ff6b6b;
  color: white;
}
</style>