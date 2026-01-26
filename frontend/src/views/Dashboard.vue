<template>
  <div>
    <!-- Stats overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatsCard
        title="Total Routeurs"
        :value="routers.length"
        :icon="ServerIcon"
        color="blue"
      />
      <StatsCard
        title="En ligne"
        :value="onlineRouters.length"
        :icon="SignalIcon"
        color="green"
      />
      <StatsCard
        title="Hors ligne"
        :value="offlineRouters.length"
        :icon="ExclamationTriangleIcon"
        color="red"
      />
      <StatsCard
        title="Clients WiFi"
        :value="totalWifiClients"
        :icon="WifiIcon"
        color="purple"
      />
    </div>

    <!-- Grouping tabs -->
    <div class="mb-6">
      <div class="flex flex-wrap gap-2 mb-4">
        <button
          @click="groupBy = 'none'"
          :class="[groupBy === 'none' ? 'btn-primary' : 'btn-secondary', 'btn text-sm']"
        >
          Tous
        </button>
        <button
          @click="groupBy = 'site'"
          :class="[groupBy === 'site' ? 'btn-primary' : 'btn-secondary', 'btn text-sm']"
        >
          Par site
        </button>
        <button
          @click="groupBy = 'type'"
          :class="[groupBy === 'type' ? 'btn-primary' : 'btn-secondary', 'btn text-sm']"
        >
          Par type
        </button>
        <button
          @click="groupBy = 'group'"
          :class="[groupBy === 'group' ? 'btn-primary' : 'btn-secondary', 'btn text-sm']"
        >
          Par groupe
        </button>
        <button
          @click="groupBy = 'status'"
          :class="[groupBy === 'status' ? 'btn-primary' : 'btn-secondary', 'btn text-sm']"
        >
          Par status
        </button>
      </div>
    </div>

    <!-- Grouped routers view -->
    <div v-if="groupBy !== 'none'" class="space-y-6">
      <div v-for="(groupRouters, groupName) in groupedRouters" :key="groupName" class="card">
        <div class="p-4 border-b border-gray-200 bg-gray-50">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">
              {{ groupName || 'Non defini' }}
              <span class="text-sm text-gray-500 ml-2">({{ groupRouters.length }})</span>
            </h3>
            <div class="flex items-center gap-2">
              <span class="badge badge-success">{{ groupRouters.filter(r => r.is_online).length }} en ligne</span>
              <span class="badge badge-danger">{{ groupRouters.filter(r => !r.is_online).length }} hors ligne</span>
            </div>
          </div>
        </div>

        <ul class="divide-y divide-gray-200">
          <li v-for="router in groupRouters" :key="router.id" class="p-4 hover:bg-gray-50">
            <router-link :to="`/routers/${router.id}`" class="flex items-center justify-between">
              <div class="flex items-center">
                <div :class="[router.is_online ? 'bg-green-400' : 'bg-red-400', 'w-3 h-3 rounded-full mr-3 flex-shrink-0']"></div>
                <div>
                  <p class="font-medium text-gray-900">{{ router.name }}</p>
                  <p class="text-sm text-gray-500">{{ router.ip_address }} - {{ router.model || 'N/A' }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm text-gray-900">{{ router.ros_version || 'N/A' }}</p>
                <p class="text-xs text-gray-500">
                  <span v-if="router.tags" class="mr-2">
                    <span v-for="tag in router.tags.split(',')" :key="tag" class="inline-block bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs mr-1">
                      {{ tag.trim() }}
                    </span>
                  </span>
                  {{ router.location || '' }}
                </p>
              </div>
            </router-link>
          </li>
        </ul>
      </div>
    </div>

    <!-- Standard list view -->
    <div v-else class="card">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Routeurs</h3>
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500">
              Actualisation auto: {{ autoRefreshEnabled ? 'Active' : 'Desactivee' }}
            </span>
            <button @click="toggleAutoRefresh" class="btn btn-sm btn-secondary">
              <ArrowPathIcon class="w-4 h-4 mr-1" :class="{ 'animate-spin': refreshing }" />
              {{ autoRefreshEnabled ? 'Arreter' : 'Demarrer' }}
            </button>
            <router-link to="/routers" class="text-mikrotik-600 hover:text-mikrotik-700 text-sm font-medium">
              Gerer
            </router-link>
          </div>
        </div>
      </div>

      <div v-if="loading" class="p-6 text-center">
        <div class="inline-flex items-center">
          <svg class="animate-spin h-5 w-5 text-mikrotik-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          Chargement...
        </div>
      </div>

      <ul v-else-if="routers.length" class="divide-y divide-gray-200">
        <li v-for="router in routers" :key="router.id" class="p-4 hover:bg-gray-50">
          <router-link :to="`/routers/${router.id}`" class="flex items-center justify-between">
            <div class="flex items-center">
              <div :class="[router.is_online ? 'bg-green-400' : 'bg-red-400', 'w-3 h-3 rounded-full mr-3 flex-shrink-0 transition-colors']"></div>
              <div>
                <p class="font-medium text-gray-900">{{ router.name }}</p>
                <p class="text-sm text-gray-500">{{ router.ip_address }} - {{ router.model || 'N/A' }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-900">{{ router.ros_version || 'N/A' }}</p>
              <div class="flex items-center justify-end gap-2 mt-1">
                <span v-if="router.site" class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{{ router.site }}</span>
                <span v-if="router.router_type" class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">{{ router.router_type }}</span>
                <span class="text-xs text-gray-500">{{ router.location || 'Aucun emplacement' }}</span>
              </div>
            </div>
          </router-link>
        </li>
      </ul>

      <div v-else class="p-6 text-center text-gray-500">
        <ServerIcon class="h-12 w-12 mx-auto text-gray-300 mb-4" />
        <p>Aucun routeur enregistre</p>
        <router-link to="/routers" class="btn btn-primary mt-4 inline-block">
          Ajouter un routeur
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoutersStore } from '../stores/routers'
import StatsCard from '../components/StatsCard.vue'
import {
  ServerIcon,
  SignalIcon,
  ExclamationTriangleIcon,
  WifiIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const store = useRoutersStore()
const { routers, onlineRouters, offlineRouters, loading } = storeToRefs(store)

const groupBy = ref('none')
const autoRefreshEnabled = ref(false)
const refreshing = ref(false)
let refreshInterval = null

const totalWifiClients = computed(() => {
  // Sum wifi clients from all router stats
  return store.routers.reduce((sum, r) => {
    // Check if router has stats with wifi_clients
    if (r.current_stats && r.current_stats.wifi_clients) {
      return sum + r.current_stats.wifi_clients
    }
    return sum
  }, 0)
})

const groupedRouters = computed(() => {
  if (groupBy.value === 'none') return {}

  const groups = {}
  routers.value.forEach(router => {
    let key
    switch (groupBy.value) {
      case 'site':
        key = router.site || 'Non defini'
        break
      case 'type':
        key = router.router_type || 'Non defini'
        break
      case 'group':
        key = router.group || 'Non defini'
        break
      case 'status':
        key = router.is_online ? 'En ligne' : 'Hors ligne'
        break
      default:
        key = 'Tous'
    }

    if (!groups[key]) {
      groups[key] = []
    }
    groups[key].push(router)
  })

  // Sort groups alphabetically
  const sortedGroups = {}
  Object.keys(groups).sort().forEach(key => {
    sortedGroups[key] = groups[key]
  })

  return sortedGroups
})

async function refreshRouters() {
  refreshing.value = true
  try {
    await store.fetchRouters()
    // Test connection for each router to update status
    for (const router of routers.value) {
      try {
        await store.testConnection(router.id)
      } catch (e) {
        // Ignore individual failures
      }
    }
  } finally {
    refreshing.value = false
  }
}

function toggleAutoRefresh() {
  autoRefreshEnabled.value = !autoRefreshEnabled.value

  if (autoRefreshEnabled.value) {
    // Refresh immediately
    refreshRouters()
    // Then refresh every 30 seconds
    refreshInterval = setInterval(refreshRouters, 30000)
  } else {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }
}

onMounted(() => {
  store.fetchRouters()
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
