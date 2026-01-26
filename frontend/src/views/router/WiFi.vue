<template>
  <div class="space-y-6">
    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-4">
        <div class="text-sm text-gray-500">Interfaces WiFi</div>
        <div class="text-2xl font-bold text-gray-900">{{ interfaces.length }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-500">Interfaces actives</div>
        <div class="text-2xl font-bold text-green-600">{{ interfaces.filter(i => i.running).length }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-500">Clients connectes</div>
        <div class="text-2xl font-bold text-blue-600">{{ clients.length }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-500">Profils de securite</div>
        <div class="text-2xl font-bold text-purple-600">{{ securityProfiles.length }}</div>
      </div>
    </div>

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
          <code v-if="row.ssid" class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.ssid }}</code>
          <span v-else class="text-gray-400">N/A</span>
        </template>

        <template #cell-mode="{ row }">
          <span class="badge badge-info">{{ row.mode || 'N/A' }}</span>
        </template>

        <template #cell-security="{ row }">
          <span v-if="row.security_profile" class="badge badge-success">{{ row.security_profile }}</span>
          <span v-else class="text-gray-400">-</span>
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

        <template #actions="{ row }">
          <button
            @click="toggleInterface(row)"
            :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
            :disabled="toggling === row.id"
          >
            {{ row.disabled ? 'Activer' : 'Desactiver' }}
          </button>
        </template>
      </DataTable>
    </div>

    <!-- Security Profiles -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Profils de securite</h3>
      </div>

      <DataTable :columns="profileColumns" :data="securityProfiles" :loading="loadingProfiles" empty-message="Aucun profil de securite">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-mode="{ row }">
          <span class="badge badge-info">{{ row.mode || 'none' }}</span>
        </template>

        <template #cell-authentication_types="{ row }">
          <span v-if="row.authentication_types" class="text-sm">{{ row.authentication_types }}</span>
          <span v-else class="text-gray-400">-</span>
        </template>

        <template #cell-unicast_ciphers="{ row }">
          <span v-if="row.unicast_ciphers" class="text-sm">{{ row.unicast_ciphers }}</span>
          <span v-else class="text-gray-400">-</span>
        </template>

        <template #cell-default="{ row }">
          <span v-if="row.default" class="badge badge-success">Defaut</span>
          <span v-else class="text-gray-400">-</span>
        </template>
      </DataTable>
    </div>

    <!-- Connected clients -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Clients connectes ({{ clients.length }})</h3>
        <button @click="fetchClients" class="btn btn-secondary text-sm" :disabled="loadingClients">
          <ArrowPathIcon class="w-4 h-4 mr-1" :class="{ 'animate-spin': loadingClients }" />
          Actualiser
        </button>
      </div>

      <DataTable :columns="clientColumns" :data="clients" :loading="loadingClients" empty-message="Aucun client connecte">
        <template #cell-mac_address="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.mac_address }}</code>
        </template>

        <template #cell-interface="{ row }">
          <span class="badge badge-info">{{ row.interface }}</span>
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
            <span class="text-sm">{{ row.signal_strength || 'N/A' }} dBm</span>
          </div>
        </template>

        <template #cell-tx_rate="{ row }">
          <span class="text-green-600 text-sm">{{ row.tx_rate || 'N/A' }}</span>
        </template>

        <template #cell-rx_rate="{ row }">
          <span class="text-blue-600 text-sm">{{ row.rx_rate || 'N/A' }}</span>
        </template>

        <template #cell-traffic="{ row }">
          <div class="text-sm">
            <div class="text-green-600">TX: {{ formatBytes(row.bytes_sent) }}</div>
            <div class="text-blue-600">RX: {{ formatBytes(row.bytes_received) }}</div>
          </div>
        </template>

        <template #actions="{ row }">
          <button
            @click="disconnectClient(row)"
            class="text-red-600 hover:text-red-800"
            :disabled="disconnecting === row.id"
          >
            Deconnecter
          </button>
        </template>
      </DataTable>
    </div>

    <!-- Access List -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Liste d'acces</h3>
      </div>

      <DataTable :columns="accessColumns" :data="accessList" :loading="loadingAccess" empty-message="Aucune entree dans la liste d'acces">
        <template #cell-mac_address="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.mac_address }}</code>
        </template>

        <template #cell-interface="{ row }">
          <span class="badge badge-info">{{ row.interface || 'Toutes' }}</span>
        </template>

        <template #cell-authentication="{ row }">
          <span :class="[row.authentication ? 'badge-success' : 'badge-danger', 'badge']">
            {{ row.authentication ? 'Autorise' : 'Refuse' }}
          </span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactivee' : 'Active' }}
          </span>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const notifications = useNotificationStore()

const interfaces = ref([])
const clients = ref([])
const securityProfiles = ref([])
const accessList = ref([])
const loadingInterfaces = ref(true)
const loadingClients = ref(true)
const loadingProfiles = ref(true)
const loadingAccess = ref(true)
const toggling = ref(null)
const disconnecting = ref(null)
let refreshInterval = null

const interfaceColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'ssid', label: 'SSID' },
  { key: 'mode', label: 'Mode' },
  { key: 'band', label: 'Bande' },
  { key: 'frequency', label: 'Frequence' },
  { key: 'security', label: 'Securite' },
  { key: 'running', label: 'Etat' },
  { key: 'disabled', label: 'Status' }
]

const profileColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'mode', label: 'Mode' },
  { key: 'authentication_types', label: 'Types auth.' },
  { key: 'unicast_ciphers', label: 'Ciphers' },
  { key: 'default', label: 'Defaut' },
  { key: 'comment', label: 'Commentaire' }
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

const accessColumns = [
  { key: 'mac_address', label: 'Adresse MAC' },
  { key: 'interface', label: 'Interface' },
  { key: 'authentication', label: 'Authentification' },
  { key: 'signal_range', label: 'Signal range' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
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
    // WiFi might not be available on all routers
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
    // WiFi clients might not be available
  } finally {
    loadingClients.value = false
  }
}

async function fetchSecurityProfiles() {
  loadingProfiles.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/security-profiles`)
    securityProfiles.value = response.data
  } catch (error) {
    // Security profiles might not be available
  } finally {
    loadingProfiles.value = false
  }
}

async function fetchAccessList() {
  loadingAccess.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/access-list`)
    accessList.value = response.data
  } catch (error) {
    // Access list might not be available
  } finally {
    loadingAccess.value = false
  }
}

async function toggleInterface(iface) {
  toggling.value = iface.id
  try {
    await api.post(`/routers/${route.params.id}/wifi/interfaces/${iface.id}/toggle`, null, {
      params: { enable: iface.disabled }
    })
    notifications.success(`Interface WiFi ${iface.disabled ? 'activee' : 'desactivee'}`)
    await fetchInterfaces()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    toggling.value = null
  }
}

async function disconnectClient(client) {
  if (!confirm(`Deconnecter le client ${client.mac_address} ?`)) return
  disconnecting.value = client.id
  try {
    await api.post(`/routers/${route.params.id}/wifi/clients/${client.mac_address}/disconnect`)
    notifications.success('Client deconnecte')
    await fetchClients()
  } catch (error) {
    notifications.error('Erreur lors de la deconnexion')
  } finally {
    disconnecting.value = null
  }
}

onMounted(() => {
  fetchInterfaces()
  fetchClients()
  fetchSecurityProfiles()
  fetchAccessList()

  // Auto-refresh clients every 30 seconds
  refreshInterval = setInterval(fetchClients, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
