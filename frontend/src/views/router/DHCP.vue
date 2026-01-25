<template>
  <div>
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Baux DHCP</h3>
        <button @click="showAddModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter un bail statique
        </button>
      </div>

      <DataTable :columns="columns" :data="leases" :loading="loading" empty-message="Aucun bail DHCP">
        <template #cell-address="{ row }">
          <span class="font-medium text-gray-900">{{ row.address }}</span>
        </template>

        <template #cell-mac_address="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.mac_address }}</code>
        </template>

        <template #cell-status="{ row }">
          <span :class="[row.status === 'bound' ? 'badge-success' : 'badge-warning', 'badge']">
            {{ row.status }}
          </span>
        </template>

        <template #actions="{ row }">
          <button
            @click="deleteLease(row)"
            class="text-red-600 hover:text-red-800"
            :disabled="deleting === row.id"
          >
            Supprimer
          </button>
        </template>
      </DataTable>
    </div>

    <!-- Add lease modal -->
    <Modal v-model="showAddModal" title="Ajouter un bail statique" size="sm">
      <form @submit.prevent="addLease" class="space-y-4">
        <div>
          <label class="label">Adresse IP</label>
          <input v-model="form.address" type="text" class="input" placeholder="192.168.1.100" required />
        </div>
        <div>
          <label class="label">Adresse MAC</label>
          <input v-model="form.mac_address" type="text" class="input" placeholder="AA:BB:CC:DD:EE:FF" required />
        </div>
        <div>
          <label class="label">Serveur DHCP</label>
          <input v-model="form.server" type="text" class="input" value="default" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="form.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>

      <template #footer>
        <button @click="addLease" class="btn btn-primary" :disabled="adding">
          {{ adding ? 'Ajout...' : 'Ajouter' }}
        </button>
        <button @click="showAddModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'
import Modal from '../../components/Modal.vue'
import { PlusIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const notifications = useNotificationStore()

const leases = ref([])
const loading = ref(true)
const deleting = ref(null)
const showAddModal = ref(false)
const adding = ref(false)

const form = reactive({
  address: '',
  mac_address: '',
  server: 'default',
  comment: ''
})

const columns = [
  { key: 'address', label: 'Adresse IP' },
  { key: 'mac_address', label: 'Adresse MAC' },
  { key: 'hostname', label: 'Hostname' },
  { key: 'status', label: 'Status' },
  { key: 'server', label: 'Serveur' },
  { key: 'expires_after', label: 'Expire dans' },
  { key: 'comment', label: 'Commentaire' }
]

async function fetchLeases() {
  loading.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dhcp/leases`)
    leases.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des baux DHCP')
  } finally {
    loading.value = false
  }
}

async function addLease() {
  adding.value = true
  try {
    await api.post(`/routers/${route.params.id}/dhcp/leases`, null, { params: form })
    notifications.success('Bail ajoute avec succes')
    showAddModal.value = false
    form.address = ''
    form.mac_address = ''
    form.comment = ''
    await fetchLeases()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout du bail')
  } finally {
    adding.value = false
  }
}

async function deleteLease(lease) {
  if (!confirm('Supprimer ce bail DHCP ?')) return
  deleting.value = lease.id
  try {
    await api.delete(`/routers/${route.params.id}/dhcp/leases/${lease.id}`)
    notifications.success('Bail supprime')
    await fetchLeases()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deleting.value = null
  }
}

onMounted(fetchLeases)
</script>
