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

    <!-- Routers list -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Routeurs</h3>
          <router-link to="/routers" class="text-mikrotik-600 hover:text-mikrotik-700 text-sm font-medium">
            Voir tout
          </router-link>
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
        <li v-for="router in routers.slice(0, 5)" :key="router.id" class="p-4 hover:bg-gray-50">
          <router-link :to="`/routers/${router.id}`" class="flex items-center justify-between">
            <div class="flex items-center">
              <div :class="[router.is_online ? 'bg-green-400' : 'bg-red-400', 'w-3 h-3 rounded-full mr-3']"></div>
              <div>
                <p class="font-medium text-gray-900">{{ router.name }}</p>
                <p class="text-sm text-gray-500">{{ router.ip_address }} - {{ router.model || 'N/A' }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-900">{{ router.ros_version || 'N/A' }}</p>
              <p class="text-xs text-gray-500">{{ router.location || 'Aucun emplacement' }}</p>
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
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoutersStore } from '../stores/routers'
import StatsCard from '../components/StatsCard.vue'
import {
  ServerIcon,
  SignalIcon,
  ExclamationTriangleIcon,
  WifiIcon
} from '@heroicons/vue/24/outline'

const store = useRoutersStore()
const { routers, onlineRouters, offlineRouters, loading } = storeToRefs(store)

const totalWifiClients = computed(() => {
  return 0 // Will be updated when stats are loaded
})

onMounted(() => {
  store.fetchRouters()
})
</script>
