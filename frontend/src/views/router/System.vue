<template>
  <div class="space-y-6">
    <!-- Actions -->
    <div class="card p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Actions systeme</h3>
      <div class="flex flex-wrap gap-4">
        <button @click="createBackup" class="btn btn-secondary" :disabled="creatingBackup">
          {{ creatingBackup ? 'Creation...' : 'Creer une sauvegarde' }}
        </button>
        <button @click="exportConfig" class="btn btn-secondary" :disabled="exporting">
          {{ exporting ? 'Export...' : 'Exporter la configuration' }}
        </button>
        <button @click="confirmReboot" class="btn btn-danger">
          Redemarrer le routeur
        </button>
      </div>
    </div>

    <!-- Users -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Utilisateurs systeme</h3>
      </div>

      <DataTable :columns="userColumns" :data="users" :loading="loadingUsers" empty-message="Aucun utilisateur">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-group="{ row }">
          <span class="badge badge-info">{{ row.group }}</span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactive' : 'Actif' }}
          </span>
        </template>
      </DataTable>
    </div>

    <!-- Logs -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Logs systeme</h3>
        <button @click="fetchLogs" class="btn btn-secondary text-sm">
          <ArrowPathIcon class="w-4 h-4 mr-1" />
          Actualiser
        </button>
      </div>

      <div v-if="loadingLogs" class="p-6 text-center">
        <div class="inline-flex items-center text-gray-500">
          <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          Chargement...
        </div>
      </div>

      <div v-else class="max-h-96 overflow-y-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Heure</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Topics</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Message</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="log in logs" :key="log.id" class="text-sm">
              <td class="px-4 py-2 whitespace-nowrap text-gray-500">{{ log.time }}</td>
              <td class="px-4 py-2 whitespace-nowrap">
                <span class="badge badge-info text-xs">{{ log.topics }}</span>
              </td>
              <td class="px-4 py-2 text-gray-900">{{ log.message }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Config export modal -->
    <Modal v-model="showConfigModal" title="Configuration exportee" size="lg">
      <div class="bg-gray-900 rounded-lg p-4 max-h-96 overflow-auto">
        <pre class="text-green-400 text-sm font-mono whitespace-pre-wrap">{{ configExport }}</pre>
      </div>

      <template #footer>
        <button @click="copyConfig" class="btn btn-primary">Copier</button>
        <button @click="showConfigModal = false" class="btn btn-secondary mr-3">Fermer</button>
      </template>
    </Modal>

    <!-- Reboot confirmation -->
    <Modal v-model="showRebootModal" title="Confirmer le redemarrage" size="sm">
      <p class="text-gray-600">
        Etes-vous sur de vouloir redemarrer ce routeur ? La connexion sera temporairement interrompue.
      </p>

      <template #footer>
        <button @click="reboot" class="btn btn-danger" :disabled="rebooting">
          {{ rebooting ? 'Redemarrage...' : 'Redemarrer' }}
        </button>
        <button @click="showRebootModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'
import Modal from '../../components/Modal.vue'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const notifications = useNotificationStore()

const users = ref([])
const logs = ref([])
const loadingUsers = ref(true)
const loadingLogs = ref(true)
const creatingBackup = ref(false)
const exporting = ref(false)
const rebooting = ref(false)
const showConfigModal = ref(false)
const showRebootModal = ref(false)
const configExport = ref('')

const userColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'group', label: 'Groupe' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
]

async function fetchUsers() {
  loadingUsers.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/system/users`)
    users.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des utilisateurs')
  } finally {
    loadingUsers.value = false
  }
}

async function fetchLogs() {
  loadingLogs.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/system/logs`, {
      params: { limit: 100 }
    })
    logs.value = response.data.reverse()
  } catch (error) {
    notifications.error('Erreur lors du chargement des logs')
  } finally {
    loadingLogs.value = false
  }
}

async function createBackup() {
  creatingBackup.value = true
  try {
    const response = await api.post(`/routers/${route.params.id}/system/backup`)
    notifications.success(`Sauvegarde creee: ${response.data.filename}`)
  } catch (error) {
    notifications.error('Erreur lors de la creation de la sauvegarde')
  } finally {
    creatingBackup.value = false
  }
}

async function exportConfig() {
  exporting.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/system/export`)
    configExport.value = response.data.config
    showConfigModal.value = true
  } catch (error) {
    notifications.error('Erreur lors de l\'export')
  } finally {
    exporting.value = false
  }
}

function copyConfig() {
  navigator.clipboard.writeText(configExport.value)
  notifications.success('Configuration copiee dans le presse-papier')
}

function confirmReboot() {
  showRebootModal.value = true
}

async function reboot() {
  rebooting.value = true
  try {
    await api.post(`/routers/${route.params.id}/system/reboot`)
    notifications.success('Le routeur redémarre...')
    showRebootModal.value = false
  } catch (error) {
    notifications.error('Erreur lors du redemarrage')
  } finally {
    rebooting.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchLogs()
})
</script>
