<template>
  <div>
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Interfaces reseau</h3>
      </div>

      <DataTable :columns="columns" :data="interfaces" :loading="loading" empty-message="Aucune interface">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-type="{ row }">
          <span class="badge badge-info">{{ row.type }}</span>
        </template>

        <template #cell-running="{ row }">
          <span :class="[row.running ? 'badge-success' : 'badge-danger', 'badge']">
            {{ row.running ? 'Actif' : 'Inactif' }}
          </span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactive' : 'Active' }}
          </span>
        </template>

        <template #cell-traffic="{ row }">
          <div class="text-sm">
            <div class="text-green-600">TX: {{ formatBytes(row.tx_bytes) }}</div>
            <div class="text-blue-600">RX: {{ formatBytes(row.rx_bytes) }}</div>
          </div>
        </template>

        <template #actions="{ row }">
          <button
            @click="toggleInterface(row)"
            class="text-mikrotik-600 hover:text-mikrotik-800"
            :disabled="toggling === row.id"
          >
            {{ row.disabled ? 'Activer' : 'Desactiver' }}
          </button>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'

const route = useRoute()
const notifications = useNotificationStore()

const interfaces = ref([])
const loading = ref(true)
const toggling = ref(null)

const columns = [
  { key: 'name', label: 'Nom' },
  { key: 'type', label: 'Type' },
  { key: 'mac_address', label: 'MAC' },
  { key: 'mtu', label: 'MTU' },
  { key: 'running', label: 'Etat' },
  { key: 'disabled', label: 'Status' },
  { key: 'traffic', label: 'Trafic' }
]

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

async function fetchInterfaces() {
  loading.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/interfaces`)
    interfaces.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des interfaces')
  } finally {
    loading.value = false
  }
}

async function toggleInterface(iface) {
  toggling.value = iface.id
  try {
    await api.post(`/routers/${route.params.id}/interfaces/${iface.id}/toggle`, null, {
      params: { enable: iface.disabled }
    })
    notifications.success(`Interface ${iface.disabled ? 'activee' : 'desactivee'}`)
    await fetchInterfaces()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    toggling.value = null
  }
}

onMounted(fetchInterfaces)
</script>
