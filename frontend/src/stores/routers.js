import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useRoutersStore = defineStore('routers', () => {
  const routers = ref([])
  const currentRouter = ref(null)
  const currentStats = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const onlineRouters = computed(() => routers.value.filter(r => r.is_online))
  const offlineRouters = computed(() => routers.value.filter(r => !r.is_online))

  async function fetchRouters() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/routers')
      routers.value = response.data.routers
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erreur lors du chargement des routeurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchRouter(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/routers/${id}`)
      currentRouter.value = response.data
      currentStats.value = response.data.current_stats
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erreur lors du chargement du routeur'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function addRouter(routerData) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/routers', routerData)
      routers.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erreur lors de l\'ajout du routeur'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateRouter(id, routerData) {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/routers/${id}`, routerData)
      const index = routers.value.findIndex(r => r.id === id)
      if (index !== -1) {
        routers.value[index] = response.data
      }
      if (currentRouter.value?.id === id) {
        currentRouter.value = { ...currentRouter.value, ...response.data }
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erreur lors de la mise à jour du routeur'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteRouter(id) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/routers/${id}`)
      routers.value = routers.value.filter(r => r.id !== id)
      if (currentRouter.value?.id === id) {
        currentRouter.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erreur lors de la suppression du routeur'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function testConnection(id) {
    try {
      const response = await api.post(`/routers/${id}/test`)
      const index = routers.value.findIndex(r => r.id === id)
      if (index !== -1) {
        routers.value[index].is_online = response.data.success
      }
      return response.data
    } catch (err) {
      throw err
    }
  }

  async function refreshStats(id) {
    try {
      const response = await api.post(`/routers/${id}/refresh`)
      currentStats.value = response.data
      return response.data
    } catch (err) {
      throw err
    }
  }

  return {
    routers,
    currentRouter,
    currentStats,
    loading,
    error,
    onlineRouters,
    offlineRouters,
    fetchRouters,
    fetchRouter,
    addRouter,
    updateRouter,
    deleteRouter,
    testConnection,
    refreshStats
  }
})
