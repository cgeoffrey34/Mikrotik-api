<template>
  <div v-if="loading" class="text-center py-12">
    <div class="inline-flex items-center">
      <svg class="animate-spin h-8 w-8 text-mikrotik-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      Chargement...
    </div>
  </div>

  <div v-else-if="currentRouter">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <router-link to="/routers" class="text-gray-400 hover:text-gray-600 mr-4">
            <ArrowLeftIcon class="w-5 h-5" />
          </router-link>
          <div>
            <div class="flex items-center">
              <h1 class="text-2xl font-bold text-gray-900 mr-3">{{ currentRouter.name }}</h1>
              <span :class="[currentRouter.is_online ? 'badge-success' : 'badge-danger', 'badge']">
                {{ currentRouter.is_online ? 'En ligne' : 'Hors ligne' }}
              </span>
            </div>
            <p class="text-gray-500">{{ currentRouter.ip_address }} - {{ currentRouter.model || 'N/A' }} - RouterOS {{ currentRouter.ros_version || 'N/A' }}</p>
          </div>
        </div>
        <button @click="refreshStats" class="btn btn-secondary" :disabled="refreshing">
          <ArrowPathIcon class="w-5 h-5 mr-2" :class="{ 'animate-spin': refreshing }" />
          Actualiser
        </button>
      </div>
    </div>

    <!-- Navigation tabs -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8 overflow-x-auto">
        <router-link
          v-for="tab in tabs"
          :key="tab.name"
          :to="tab.to"
          class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors"
          :class="isActiveTab(tab.to) ? 'border-mikrotik-500 text-mikrotik-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          <component :is="tab.icon" class="w-5 h-5 inline mr-2" />
          {{ tab.name }}
        </router-link>
      </nav>
    </div>

    <!-- Content -->
    <router-view :router="currentRouter" :stats="currentStats" />
  </div>

  <div v-else class="text-center py-12">
    <p class="text-gray-500">Routeur non trouve</p>
    <router-link to="/routers" class="btn btn-primary mt-4">Retour aux routeurs</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useRoutersStore } from '../stores/routers'
import { useNotificationStore } from '../stores/notifications'
import {
  ArrowLeftIcon,
  ArrowPathIcon,
  ChartBarIcon,
  ComputerDesktopIcon,
  WifiIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  ServerIcon,
  QueueListIcon,
  Cog6ToothIcon,
  MapIcon,
  Square3Stack3DIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const store = useRoutersStore()
const notifications = useNotificationStore()
const { currentRouter, currentStats, loading } = storeToRefs(store)

const refreshing = ref(false)

const tabs = [
  { name: 'Vue d\'ensemble', to: `/routers/${route.params.id}`, icon: ChartBarIcon },
  { name: 'Interfaces', to: `/routers/${route.params.id}/interfaces`, icon: ComputerDesktopIcon },
  { name: 'Bridges', to: `/routers/${route.params.id}/bridges`, icon: Square3Stack3DIcon },
  { name: 'DHCP', to: `/routers/${route.params.id}/dhcp`, icon: ServerIcon },
  { name: 'WiFi', to: `/routers/${route.params.id}/wifi`, icon: WifiIcon },
  { name: 'Firewall', to: `/routers/${route.params.id}/firewall`, icon: ShieldCheckIcon },
  { name: 'DNS', to: `/routers/${route.params.id}/dns`, icon: GlobeAltIcon },
  { name: 'Routes', to: `/routers/${route.params.id}/routes`, icon: MapIcon },
  { name: 'QoS', to: `/routers/${route.params.id}/queues`, icon: QueueListIcon },
  { name: 'Systeme', to: `/routers/${route.params.id}/system`, icon: Cog6ToothIcon }
]

function isActiveTab(to) {
  if (to === `/routers/${route.params.id}`) {
    return route.path === to
  }
  return route.path.startsWith(to)
}

async function refreshStats() {
  refreshing.value = true
  try {
    await store.refreshStats(route.params.id)
    notifications.success('Statistiques actualisees')
  } catch (error) {
    notifications.error('Erreur lors de l\'actualisation')
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  store.fetchRouter(route.params.id)
})
</script>
