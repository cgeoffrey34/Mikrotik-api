<template>
  <div>
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Entrees DNS statiques</h3>
        <button @click="showAddModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter une entree
        </button>
      </div>

      <DataTable :columns="columns" :data="entries" :loading="loading" empty-message="Aucune entree DNS">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-address="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.address }}</code>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactivee' : 'Active' }}
          </span>
        </template>

        <template #cell-dynamic="{ row }">
          <span :class="[row.dynamic ? 'badge-info' : 'badge-success', 'badge']">
            {{ row.dynamic ? 'Dynamique' : 'Statique' }}
          </span>
        </template>

        <template #actions="{ row }">
          <button
            v-if="!row.dynamic"
            @click="deleteEntry(row)"
            class="text-red-600 hover:text-red-800"
            :disabled="deleting === row.id"
          >
            Supprimer
          </button>
        </template>
      </DataTable>
    </div>

    <!-- Add entry modal -->
    <Modal v-model="showAddModal" title="Ajouter une entree DNS" size="sm">
      <form @submit.prevent="addEntry" class="space-y-4">
        <div>
          <label class="label">Nom de domaine</label>
          <input v-model="form.name" type="text" class="input" placeholder="exemple.local" required />
        </div>
        <div>
          <label class="label">Adresse IP</label>
          <input v-model="form.address" type="text" class="input" placeholder="192.168.1.100" required />
        </div>
        <div>
          <label class="label">TTL</label>
          <input v-model="form.ttl" type="text" class="input" placeholder="1d" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="form.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>

      <template #footer>
        <button @click="addEntry" class="btn btn-primary" :disabled="adding">
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

const entries = ref([])
const loading = ref(true)
const deleting = ref(null)
const showAddModal = ref(false)
const adding = ref(false)

const form = reactive({
  name: '',
  address: '',
  ttl: '1d',
  comment: ''
})

const columns = [
  { key: 'name', label: 'Nom' },
  { key: 'address', label: 'Adresse' },
  { key: 'type', label: 'Type' },
  { key: 'ttl', label: 'TTL' },
  { key: 'disabled', label: 'Status' },
  { key: 'dynamic', label: 'Source' },
  { key: 'comment', label: 'Commentaire' }
]

async function fetchEntries() {
  loading.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dns/static`)
    entries.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des entrees DNS')
  } finally {
    loading.value = false
  }
}

async function addEntry() {
  adding.value = true
  try {
    await api.post(`/routers/${route.params.id}/dns/static`, null, { params: form })
    notifications.success('Entree DNS ajoutee')
    showAddModal.value = false
    form.name = ''
    form.address = ''
    form.ttl = '1d'
    form.comment = ''
    await fetchEntries()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout')
  } finally {
    adding.value = false
  }
}

async function deleteEntry(entry) {
  if (!confirm('Supprimer cette entree DNS ?')) return
  deleting.value = entry.id
  try {
    await api.delete(`/routers/${route.params.id}/dns/static/${entry.id}`)
    notifications.success('Entree supprimee')
    await fetchEntries()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deleting.value = null
  }
}

onMounted(fetchEntries)
</script>
