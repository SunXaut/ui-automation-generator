<template>
  <!-- 复杂 Vue 组件测试 - 包含各种语法特性 -->
  <div class="complex-component">
    <h1>{{ title }}</h1>

    <!-- 1. router-link 组件 -->
    <router-link to="/home" custom v-slot="{ navigate }">
      <button @click="navigate" role="link">首页</button>
    </router-link>

    <!-- 2. v-on:click 语法（非 @click） -->
    <button v-on:click="handleClick">v-on 按钮</button>

    <!-- 3. 键盘事件 -->
    <input 
      v-model="searchQuery" 
      @keyup.enter="handleSearch"
      @keydown.esc="clearSearch"
      @focus="onFocus"
      placeholder="搜索..."
    />

    <!-- 4. 鼠标事件 -->
    <div 
      @mouseenter="showTooltip" 
      @mouseleave="hideTooltip"
      @dblclick="handleDoubleClick"
    >
      鼠标悬停区域
    </div>

    <!-- 5. v-show 指令 -->
    <button v-show="isVisible" @click="toggle">显示/隐藏</button>

    <!-- 6. 动态组件 -->
    <component :is="currentComponent" @custom-event="handleCustom" />

    <!-- 7. v-for 在 template 上 -->
    <template v-for="item in items" :key="item.id">
      <button @click="selectItem(item)">{{ item.name }}</button>
    </template>

    <!-- 8. 自定义 UI 库组件 -->
    <el-button type="primary" @click="handleSubmit">提交</el-button>
    <a-button @click="handleCancel">取消</a-button>

    <!-- 9. 插槽内容 -->
    <custom-dialog v-model:visible="dialogVisible">
      <template #header>
        <h2>对话框标题</h2>
      </template>
      <template #default>
        <input v-model="dialogInput" placeholder="输入内容" />
        <button @click="confirmDialog">确认</button>
      </template>
      <template #footer>
        <button @click="closeDialog">关闭</button>
      </template>
    </custom-dialog>

    <!-- 10. v-html / v-text -->
    <div v-html="htmlContent"></div>
    <span v-text="textContent"></span>

    <!-- 11. Teleport -->
    <teleport to="body">
      <div class="modal">
        <button @click="closeModal">关闭模态框</button>
      </div>
    </teleport>

    <!-- 12. Keep-alive -->
    <keep-alive>
      <component :is="cachedComponent" />
    </keep-alive>

    <!-- 13. 内联表达式 -->
    <button @click="count++">计数: {{ count }}</button>

    <!-- 14. 多行属性 -->
    <input
      type="text"
      v-model="formData.username"
      @input="validateUsername"
      @blur="onUsernameBlur"
      :class="{ 'error': errors.username }"
      placeholder="用户名"
    />

    <!-- 15. v-bind 简写 -->
    <button 
      :disabled="isSubmitting"
      :aria-label="submitLabel"
      @click="handleSubmit"
    >
      提交表单
    </button>

    <!-- 16. 表单提交 -->
    <form @submit.prevent="handleSubmitForm">
      <input v-model="email" type="email" placeholder="邮箱" />
      <textarea v-model="message" placeholder="留言"></textarea>
      <select v-model="category">
        <option value="bug">Bug</option>
        <option value="feature">功能</option>
      </select>
      <button type="submit">发送</button>
    </form>

    <!-- 17. 条件渲染组合 -->
    <div v-if="status === 'loading'">加载中...</div>
    <div v-else-if="status === 'error'">
      <button @click="retry">重试</button>
    </div>
    <div v-else>
      <button @click="refresh">刷新</button>
    </div>

    <!-- 18. v-for 带索引 -->
    <ul>
      <li v-for="(item, index) in list" :key="index">
        <button @click="removeItem(index)">删除</button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

// Props 定义
const props = defineProps<{
  title: string
  initialCount?: number
}>()

// Emits 定义
const emit = defineEmits<{
  (e: 'submit', data: FormData): void
  (e: 'cancel'): void
  (e: 'custom-event', payload: any): void
}>()

// 响应式数据
const searchQuery = ref('')
const isVisible = ref(true)
const dialogVisible = ref(false)
const dialogInput = ref('')
const count = ref(0)
const isSubmitting = ref(false)
const status = ref<'loading' | 'error' | 'success'>('success')
const email = ref('')
const message = ref('')
const category = ref('bug')
const currentComponent = ref('div')
const cachedComponent = ref('div')
const htmlContent = ref('<p>HTML 内容</p>')
const textContent = ref('文本内容')
const formData = ref({ username: '' })
const errors = ref({ username: false })
const items = ref([
  { id: 1, name: '项目1' },
  { id: 2, name: '项目2' }
])
const list = ref([1, 2, 3])

// Computed
const submitLabel = computed(() => isSubmitting.value ? '提交中...' : '提交')

// Watch
watch(searchQuery, (newVal) => {
  console.log('搜索词变化:', newVal)
})

// 生命周期
onMounted(() => {
  console.log('组件已挂载')
})

// 方法
const handleClick = () => console.log('点击')
const handleSearch = () => console.log('搜索:', searchQuery.value)
const clearSearch = () => { searchQuery.value = '' }
const onFocus = () => console.log('聚焦')
const showTooltip = () => console.log('显示提示')
const hideTooltip = () => console.log('隐藏提示')
const handleDoubleClick = () => console.log('双击')
const toggle = () => { isVisible.value = !isVisible.value }
const handleCustom = (payload: any) => emit('custom-event', payload)
const selectItem = (item: any) => console.log('选择:', item)
const handleSubmit = () => console.log('提交')
const handleCancel = () => emit('cancel')
const confirmDialog = () => { console.log('确认:', dialogInput.value); dialogVisible.value = false }
const closeDialog = () => { dialogVisible.value = false }
const closeModal = () => console.log('关闭模态框')
const validateUsername = () => console.log('验证用户名')
const onUsernameBlur = () => console.log('用户名失焦')
const handleSubmitForm = () => {
  emit('submit', { email: email.value, message: message.value })
}
const retry = () => { status.value = 'loading' }
const refresh = () => console.log('刷新')
const removeItem = (index: number) => { list.value.splice(index, 1) }
</script>

<style scoped>
.complex-component {
  padding: 20px;
}
</style>
