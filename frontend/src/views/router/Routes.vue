<template>
  <div>
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Table de routage</h3>
        <button @click="showAddModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter une route
        </button>
      </div>

      <DataTable :columns="columns" :data="routes" :loading="loading" empty-message="Aucune route">
        <template #cell-dst_address="{ row }">
          <span class="font-medium text-gray-900">{{ row.dst_address }}</span>
        </template>

        <template #cell-gateway="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.gateway || 'N/A' }}</code>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactivee' : 'Active' }}
          </span>
        </template>

        <template #cell-type="{ row }">
          <span :class="[row.dynamic ? 'badge-info' : (row.static ? 'badge-success' : 'badge-warning'), 'badge']">
            {{ row.dynamic ? 'Dynamique' : (row.static ? 'Statique' : 'Connectee') }}
          </span>
        </template>

        <template #actions="{ row }">
          <button
            v-if="row.static && !row.dynamic"
            @click="deleteRoute(row)"
            class="text-red-600 hover:text-red-800"
            :disabled="deleting === row.id"
          >
            Supprimer
          </button>
        </template>
      </DataTable>
    </div>

    <!-- Add route modal -->
    <Modal v-model="showAddModal" title="Ajouter une route" size="sm">
      <form @submit.prevent="addRoute" class="space-y-4">
        <div>
          <label class="label">Destination</label>
          <input v-model="form.dst_address" type="text" class="input" placeholder="10.0.0.0/8" required />
        </div>
        <div>
          <label class="label">Passerelle</label>
          <input v-model="form.gateway" type="text" class="input" placeholder="192.168.1.1" required />
        </div>
        <div>
          <label class="label">Distance</label>
          <input v-model.number="form.distance" type="number" class="input" min="1" max="255" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="form.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>

      <template #footer>
        <button @click="addRoute" class="btn btn-primary" :disabled="adding">
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

const routes = ref([])
const loading = ref(true)
const deleting = ref(null)
const showAddModal = ref(false)
const adding = ref(false)

const form = reactive({
  dst_address: '',
  gateway: '',
  distance: 1,
  comment: ''
})

const columns = [
  { key: 'dst_address', label: 'Destination' },
  { key: 'gateway', label: 'Passerelle' },
  { key: 'interface', label: 'Interface' },
  { key: 'distance', label: 'Distance' },
  { key: 'disabled', label: 'Status' },
  { key: 'type', label: 'Type' },
  { key: 'comment', label: 'Commentaire' }
]

async function fetchRoutes() {
  loading.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/ip/routes`)
    routes.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des routes')
  } finally {
    loading.value = false
  }
}

async function addRoute() {
  adding.value = true
  try {
    await api.post(`/routers/${route.params.id}/ip/routes`, null, { params: form })
    notifications.success('Route ajoutee')
    showAddModal.value = false
    form.dst_address = ''
    form.gateway = ''
    form.distance = 1
    form.comment = ''
    await fetchRoutes()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout')
  } finally {
    adding.value = false
  }
}

async function deleteRoute(r) {
  if (!confirm('Supprimer cette route ?')) return
  deleting.value = r.id
  try {
    await api.delete(`/routers/${route.params.id}/ip/routes/${r.id}`)
    notifications.success('Route supprimee')
    await fetchRoutes()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deleting.value = null
  }
}

onMounted(fetchRoutes)
</script>
