<template>
  <div class="about">
    <h1>关于我们</h1>
    <p>这是一个关于页面</p>
    <button @click="showMessage" class="btn-about">
      查看更多信息
    </button>
  </div>
</template>

<script setup lang="ts">
const showMessage = () => {
  alert('这是关于页面的提示信息')
}
</script>

<style scoped>
.about {
  padding: 24px;
  text-align: center;
}

.btn-about {
  padding: 10px 20px;
  background-color: #646cff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>