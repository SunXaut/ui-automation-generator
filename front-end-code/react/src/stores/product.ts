import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Product {
  id: number
  name: string
  price: number
  category: string
}

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const categories = ref<string[]>([])
  const selectedCategory = ref<string | null>(null)
  const isLoading = ref(false)
  const searchQuery = ref('')

  const filteredProducts = computed(() => {
    let result = products.value
    if (selectedCategory.value) {
      result = result.filter(p => p.category === selectedCategory.value)
    }
    if (searchQuery.value) {
      result = result.filter(p =>
        p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    }
    return result
  })

  const totalProducts = computed(() => products.value.length)

  async function fetchProducts() {
    isLoading.value = true
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      products.value = [
        { id: 1, name: '笔记本电脑', price: 5999, category: '电子产品' },
        { id: 2, name: '无线鼠标', price: 99, category: '电子产品' },
        { id: 3, name: '机械键盘', price: 299, category: '电子产品' },
        { id: 4, name: '办公桌', price: 899, category: '家具' },
        { id: 5, name: '人体工学椅', price: 1299, category: '家具' }
      ]
      categories.value = [...new Set(products.value.map(p => p.category))]
    } finally {
      isLoading.value = false
    }
  }

  function setCategory(category: string | null) {
    selectedCategory.value = category
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  return {
    products,
    categories,
    selectedCategory,
    isLoading,
    searchQuery,
    filteredProducts,
    totalProducts,
    fetchProducts,
    setCategory,
    setSearchQuery
  }
})