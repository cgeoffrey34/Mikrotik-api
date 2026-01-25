<template>
  <div class="space-y-6">
    <!-- Wireless interfaces -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Interfaces WiFi</h3>
      </div>

      <DataTable :columns="interfaceColumns" :data="interfaces" :loading="loadingInterfaces" empty-message="Aucune interface WiFi">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-ssid="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.ssid || 'N/A' }}</code>
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
      </DataTable>
    </div>

    <!-- Connected clients -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Clients connectes</h3>
      </div>

      <DataTable :columns="clientColumns" :data="clients" :loading="loadingClients" empty-message="Aucun client connecte">
        <template #cell-mac_address="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.mac_address }}</code>
        </template>

        <template #cell-signal_strength="{ row }">
          <div class="flex items-center">
            <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
              <div
                class="h-2 rounded-full"
                :class="getSignalColor(row.signal_strength)"
                :style="{ width: getSignalPercent(row.signal_strength) + '%' }"
              ></div>
            </div>
            <span class="text-sm">{{ row.signal_strength || 'N/A' }}</span>
          </div>
        </template>

        <template #cell-traffic="{ row }">
          <div class="text-sm">
            <div class="text-green-600">TX: {{ formatBytes(row.bytes_sent) }}</div>
            <div class="text-blue-600">RX: {{ formatBytes(row.bytes_received) }}</div>
          </div>
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
const clients = ref([])
const loadingInterfaces = ref(true)
const loadingClients = ref(true)

const interfaceColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'ssid', label: 'SSID' },
  { key: 'mode', label: 'Mode' },
  { key: 'band', label: 'Bande' },
  { key: 'frequency', label: 'Frequence' },
  { key: 'running', label: 'Etat' },
  { key: 'disabled', label: 'Status' }
]

const clientColumns = [
  { key: 'interface', label: 'Interface' },
  { key: 'mac_address', label: 'Adresse MAC' },
  { key: 'signal_strength', label: 'Signal' },
  { key: 'tx_rate', label: 'Debit TX' },
  { key: 'rx_rate', label: 'Debit RX' },
  { key: 'uptime', label: 'Connecte depuis' },
  { key: 'traffic', label: 'Trafic' }
]

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function getSignalPercent(signal) {
  if (!signal) return 0
  const db = parseInt(signal)
  if (db >= -50) return 100
  if (db <= -100) return 0
  return Math.round((db + 100) * 2)
}

function getSignalColor(signal) {
  const percent = getSignalPercent(signal)
  if (percent >= 70) return 'bg-green-500'
  if (percent >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

async function fetchInterfaces() {
  loadingInterfaces.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/interfaces`)
    interfaces.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des interfaces WiFi')
  } finally {
    loadingInterfaces.value = false
  }
}

async function fetchClients() {
  loadingClients.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/clients`)
    clients.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des clients WiFi')
  } finally {
    loadingClients.value = false
  }
}

onMounted(() => {
  fetchInterfaces()
  fetchClients()
})
</script>
