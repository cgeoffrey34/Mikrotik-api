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

      <!-- Filters -->
      <div class="px-6 py-3 border-b border-gray-200 flex flex-wrap gap-2">
        <button
          v-for="f in filters"
          :key="f.value"
          @click="activeFilter = f.value"
          :class="[
            'px-3 py-1.5 text-xs font-medium rounded-full transition-colors',
            activeFilter === f.value
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ f.label }}
          <span
            v-if="f.count > 0"
            :class="[
              'ml-1.5 inline-flex items-center justify-center px-1.5 py-0.5 text-xs rounded-full',
              activeFilter === f.value ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-700'
            ]"
          >
            {{ f.count }}
          </span>
        </button>
      </div>

      <DataTable :columns="columns" :data="filteredRoutes" :loading="loading" empty-message="Aucune route">
        <template #cell-dst_address="{ row }">
          <span class="font-medium text-gray-900">{{ row.dst_address }}</span>
        </template>

        <template #cell-gateway="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.gateway || 'N/A' }}</code>
        </template>

        <template #cell-active="{ row }">
          <span :class="[row.active ? 'badge-success' : (row.disabled ? 'badge-warning' : 'badge-danger'), 'badge']">
            {{ row.active ? 'Active' : (row.disabled ? 'Desactivee' : 'Inactive') }}
          </span>
        </template>

        <template #cell-route_type="{ row }">
          <span :class="[typeClass(row.route_type), 'badge']">
            {{ typeLabel(row.route_type) }}
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
import { ref, reactive, computed, onMounted } from 'vue'
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
const activeFilter = ref('all')

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
  { key: 'active', label: 'Status' },
  { key: 'route_type', label: 'Type' },
  { key: 'routing_table', label: 'Table' },
  { key: 'comment', label: 'Commentaire' }
]

const typeLabels = {
  connected: 'Connectee',
  static: 'Statique',
  ospf: 'OSPF',
  bgp: 'BGP',
  rip: 'RIP',
  dhcp: 'DHCP',
  vpn: 'VPN',
  modem: 'Modem',
  dynamic: 'Dynamique',
  other: 'Autre'
}

const typeClasses = {
  connected: 'badge-info',
  static: 'badge-success',
  ospf: 'badge-primary',
  bgp: 'badge-purple',
  rip: 'badge-warning',
  dhcp: 'badge-teal',
  vpn: 'badge-indigo',
  modem: 'badge-warning',
  dynamic: 'badge-secondary',
  other: 'badge-secondary'
}

function typeLabel(type) {
  return typeLabels[type] || type
}

function typeClass(type) {
  return typeClasses[type] || 'badge-secondary'
}

function countByType(type) {
  if (type === 'all') return routes.value.length
  return routes.value.filter(r => r.route_type === type).length
}

const filters = computed(() => {
  const all = [{ value: 'all', label: 'Toutes', count: routes.value.length }]
  const types = ['connected', 'static', 'ospf', 'bgp', 'rip', 'dhcp', 'vpn', 'dynamic']
  for (const t of types) {
    const c = countByType(t)
    if (c > 0) {
      all.push({ value: t, label: typeLabels[t], count: c })
    }
  }
  return all
})

const filteredRoutes = computed(() => {
  if (activeFilter.value === 'all') return routes.value
  return routes.value.filter(r => r.route_type === activeFilter.value)
})

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

<style scoped>
.badge-primary {
  @apply bg-blue-100 text-blue-800;
}
.badge-purple {
  @apply bg-purple-100 text-purple-800;
}
.badge-teal {
  @apply bg-teal-100 text-teal-800;
}
.badge-indigo {
  @apply bg-indigo-100 text-indigo-800;
}
.badge-secondary {
  @apply bg-gray-100 text-gray-800;
}
</style>
