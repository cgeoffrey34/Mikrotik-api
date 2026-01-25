<template>
  <div class="space-y-6">
    <!-- Filter rules -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Regles de filtrage</h3>
      </div>

      <DataTable :columns="filterColumns" :data="filterRules" :loading="loadingFilter" empty-message="Aucune regle de filtrage">
        <template #cell-chain="{ row }">
          <span class="badge badge-info">{{ row.chain }}</span>
        </template>

        <template #cell-action="{ row }">
          <span :class="[getActionClass(row.action), 'badge']">
            {{ row.action }}
          </span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactivee' : 'Active' }}
          </span>
        </template>

        <template #cell-stats="{ row }">
          <div class="text-sm text-gray-500">
            {{ formatNumber(row.packets) }} paquets / {{ formatBytes(row.bytes) }}
          </div>
        </template>

        <template #actions="{ row }">
          <button
            @click="toggleFilterRule(row)"
            :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
            :disabled="toggling === row.id"
          >
            {{ row.disabled ? 'Activer' : 'Desactiver' }}
          </button>
        </template>
      </DataTable>
    </div>

    <!-- NAT rules -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Regles NAT</h3>
      </div>

      <DataTable :columns="natColumns" :data="natRules" :loading="loadingNat" empty-message="Aucune regle NAT">
        <template #cell-chain="{ row }">
          <span class="badge badge-info">{{ row.chain }}</span>
        </template>

        <template #cell-action="{ row }">
          <span class="badge badge-info">{{ row.action }}</span>
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'

const route = useRoute()
const notifications = useNotificationStore()

const filterRules = ref([])
const natRules = ref([])
const loadingFilter = ref(true)
const loadingNat = ref(true)
const toggling = ref(null)

const filterColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Protocole' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'dst_port', label: 'Port' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Statistiques' },
  { key: 'comment', label: 'Commentaire' }
]

const natColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Protocole' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'to_addresses', label: 'Vers IP' },
  { key: 'to_ports', label: 'Vers Port' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
]

function getActionClass(action) {
  const classes = {
    'accept': 'badge-success',
    'drop': 'badge-danger',
    'reject': 'badge-danger',
    'log': 'badge-warning',
    'jump': 'badge-info'
  }
  return classes[action] || 'badge-info'
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('fr-FR')
}

async function fetchFilterRules() {
  loadingFilter.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/firewall/filter`)
    filterRules.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des regles de filtrage')
  } finally {
    loadingFilter.value = false
  }
}

async function fetchNatRules() {
  loadingNat.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/firewall/nat`)
    natRules.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des regles NAT')
  } finally {
    loadingNat.value = false
  }
}

async function toggleFilterRule(rule) {
  toggling.value = rule.id
  try {
    await api.post(`/routers/${route.params.id}/firewall/filter/${rule.id}/toggle`, null, {
      params: { enable: rule.disabled }
    })
    notifications.success(`Regle ${rule.disabled ? 'activee' : 'desactivee'}`)
    await fetchFilterRules()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    toggling.value = null
  }
}

onMounted(() => {
  fetchFilterRules()
  fetchNatRules()
})
</script>
