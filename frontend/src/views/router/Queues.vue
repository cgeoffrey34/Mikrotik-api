<template>
  <div>
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Files d'attente simples (QoS)</h3>
      </div>

      <DataTable :columns="columns" :data="queues" :loading="loading" empty-message="Aucune file d'attente">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-target="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.target }}</code>
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
            @click="toggleQueue(row)"
            :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
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

const queues = ref([])
const loading = ref(true)
const toggling = ref(null)

const columns = [
  { key: 'name', label: 'Nom' },
  { key: 'target', label: 'Cible' },
  { key: 'max_limit', label: 'Limite max' },
  { key: 'burst_limit', label: 'Limite burst' },
  { key: 'priority', label: 'Priorite' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Statistiques' },
  { key: 'comment', label: 'Commentaire' }
]

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

async function fetchQueues() {
  loading.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/queues/simple`)
    queues.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des files')
  } finally {
    loading.value = false
  }
}

async function toggleQueue(queue) {
  toggling.value = queue.id
  try {
    await api.post(`/routers/${route.params.id}/queues/simple/${queue.id}/toggle`, null, {
      params: { enable: queue.disabled }
    })
    notifications.success(`File ${queue.disabled ? 'activee' : 'desactivee'}`)
    await fetchQueues()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    toggling.value = null
  }
}

onMounted(fetchQueues)
</script>
