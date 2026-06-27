import { defineStore } from 'pinia'

interface Product {
  id: number
  name: string
  price: number
  category: string
}

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [] as Product[],
    categories: [] as string[],
    selectedCategory: null as string | null,
    isLoading: false,
    searchQuery: ''
  }),

  getters: {
    filteredProducts: (state) => {
      let result = state.products
      if (state.selectedCategory) {
        result = result.filter(p => p.category === state.selectedCategory)
      }
      if (state.searchQuery) {
        result = result.filter(p =>
          p.name.toLowerCase().includes(state.searchQuery.toLowerCase())
        )
      }
      return result
    },
    totalProducts: (state) => state.products.length,
    averagePrice: (state) => {
      if (state.products.length === 0) return 0
      const sum = state.products.reduce((acc, p) => acc + p.price, 0)
      return sum / state.products.length
    }
  },

  actions: {
    async fetchProducts() {
      this.isLoading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        this.products = [
          { id: 1, name: '笔记本电脑', price: 5999, category: '电子产品' },
          { id: 2, name: '无线鼠标', price: 99, category: '电子产品' },
          { id: 3, name: '机械键盘', price: 299, category: '电子产品' },
          { id: 4, name: '办公桌', price: 899, category: '家具' },
          { id: 5, name: '人体工学椅', price: 1299, category: '家具' }
        ]
        this.categories = [...new Set(this.products.map(p => p.category))]
      } finally {
        this.isLoading = false
      }
    },

    setCategory(category: string | null) {
      this.selectedCategory = category
    },

    setSearchQuery(query: string) {
      this.searchQuery = query
    },

    addProduct(product: Omit<Product, 'id'>) {
      const newId = Math.max(...this.products.map(p => p.id), 0) + 1
      this.products.push({ ...product, id: newId })
    }
  }
})