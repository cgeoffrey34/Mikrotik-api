<template>
  <div class="space-y-6">
    <!-- DHCP Servers -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Serveurs DHCP</h3>
      </div>

      <DataTable :columns="serverColumns" :data="servers" :loading="loadingServers" empty-message="Aucun serveur DHCP">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-interface="{ row }">
          <span class="badge badge-info">{{ row.interface }}</span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactive' : 'Actif' }}
          </span>
        </template>

        <template #actions="{ row }">
          <button
            @click="toggleServer(row)"
            :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
            :disabled="togglingServer === row.id"
          >
            {{ row.disabled ? 'Activer' : 'Desactiver' }}
          </button>
        </template>
      </DataTable>
    </div>

    <!-- DHCP Networks -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Reseaux DHCP</h3>
      </div>

      <DataTable :columns="networkColumns" :data="networks" :loading="loadingNetworks" empty-message="Aucun reseau configure">
        <template #cell-address="{ row }">
          <span class="font-medium text-gray-900">{{ row.address }}</span>
        </template>

        <template #cell-gateway="{ row }">
          <code v-if="row.gateway" class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.gateway }}</code>
          <span v-else class="text-gray-400">-</span>
        </template>

        <template #cell-dns_server="{ row }">
          <code v-if="row.dns_server" class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.dns_server }}</code>
          <span v-else class="text-gray-400">-</span>
        </template>
      </DataTable>
    </div>

    <!-- IP Pools -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Pools IP</h3>
      </div>

      <DataTable :columns="poolColumns" :data="pools" :loading="loadingPools" empty-message="Aucun pool IP">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-ranges="{ row }">
          <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.ranges }}</code>
        </template>
      </DataTable>
    </div>

    <!-- DHCP Leases -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Baux DHCP</h3>
        <button @click="showAddModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter un bail statique
        </button>
      </div>

      <DataTable :columns="leaseColumns" :data="leases" :loading="loadingLeases" empty-message="Aucun bail DHCP">
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

        <template #cell-dynamic="{ row }">
          <span :class="[row.dynamic ? 'badge-info' : 'badge-success', 'badge']">
            {{ row.dynamic ? 'Dynamique' : 'Statique' }}
          </span>
        </template>

        <template #actions="{ row }">
          <div class="flex items-center gap-2">
            <button
              v-if="row.dynamic"
              @click="makeStatic(row)"
              class="text-blue-600 hover:text-blue-800"
              :disabled="makingStatic === row.id"
            >
              Rendre statique
            </button>
            <button
              @click="deleteLease(row)"
              class="text-red-600 hover:text-red-800"
              :disabled="deleting === row.id"
            >
              Supprimer
            </button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Add lease modal -->
    <Modal v-model="showAddModal" title="Ajouter un bail statique" size="sm">
      <form @submit.prevent="addLease" class="space-y-4">
        <div>
          <label class="label">Adresse IP *</label>
          <input v-model="form.address" type="text" class="input" placeholder="192.168.1.100" required />
        </div>
        <div>
          <label class="label">Adresse MAC *</label>
          <input v-model="form.mac_address" type="text" class="input" placeholder="AA:BB:CC:DD:EE:FF" required />
        </div>
        <div>
          <label class="label">Serveur DHCP</label>
          <select v-model="form.server" class="input">
            <option value="default">default</option>
            <option v-for="srv in servers" :key="srv.id" :value="srv.name">{{ srv.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Hostname</label>
          <input v-model="form.hostname" type="text" class="input" placeholder="pc-bureau" />
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

const servers = ref([])
const networks = ref([])
const pools = ref([])
const leases = ref([])
const loadingServers = ref(true)
const loadingNetworks = ref(true)
const loadingPools = ref(true)
const loadingLeases = ref(true)
const togglingServer = ref(null)
const deleting = ref(null)
const makingStatic = ref(null)
const showAddModal = ref(false)
const adding = ref(false)

const form = reactive({
  address: '',
  mac_address: '',
  server: 'default',
  hostname: '',
  comment: ''
})

const serverColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'interface', label: 'Interface' },
  { key: 'address_pool', label: 'Pool' },
  { key: 'lease_time', label: 'Duree bail' },
  { key: 'authoritative', label: 'Authoritative' },
  { key: 'disabled', label: 'Status' }
]

const networkColumns = [
  { key: 'address', label: 'Reseau' },
  { key: 'gateway', label: 'Passerelle' },
  { key: 'dns_server', label: 'DNS' },
  { key: 'domain', label: 'Domaine' },
  { key: 'comment', label: 'Commentaire' }
]

const poolColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'ranges', label: 'Plages' },
  { key: 'next_pool', label: 'Pool suivant' },
  { key: 'comment', label: 'Commentaire' }
]

const leaseColumns = [
  { key: 'address', label: 'Adresse IP' },
  { key: 'mac_address', label: 'Adresse MAC' },
  { key: 'hostname', label: 'Hostname' },
  { key: 'status', label: 'Status' },
  { key: 'dynamic', label: 'Type' },
  { key: 'server', label: 'Serveur' },
  { key: 'expires_after', label: 'Expire dans' },
  { key: 'comment', label: 'Commentaire' }
]

async function fetchServers() {
  loadingServers.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dhcp/servers`)
    servers.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des serveurs DHCP')
  } finally {
    loadingServers.value = false
  }
}

async function fetchNetworks() {
  loadingNetworks.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dhcp/networks`)
    networks.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des reseaux DHCP')
  } finally {
    loadingNetworks.value = false
  }
}

async function fetchPools() {
  loadingPools.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dhcp/pools`)
    pools.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des pools IP')
  } finally {
    loadingPools.value = false
  }
}

async function fetchLeases() {
  loadingLeases.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dhcp/leases`)
    leases.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des baux DHCP')
  } finally {
    loadingLeases.value = false
  }
}

async function toggleServer(server) {
  togglingServer.value = server.id
  try {
    await api.post(`/routers/${route.params.id}/dhcp/servers/${server.id}/toggle`, null, {
      params: { enable: server.disabled }
    })
    notifications.success(`Serveur DHCP ${server.disabled ? 'active' : 'desactive'}`)
    await fetchServers()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    togglingServer.value = null
  }
}

async function addLease() {
  adding.value = true
  try {
    await api.post(`/routers/${route.params.id}/dhcp/leases`, null, {
      params: {
        address: form.address,
        mac_address: form.mac_address,
        server: form.server,
        hostname: form.hostname,
        comment: form.comment
      }
    })
    notifications.success('Bail ajoute avec succes')
    showAddModal.value = false
    form.address = ''
    form.mac_address = ''
    form.server = 'default'
    form.hostname = ''
    form.comment = ''
    await fetchLeases()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout du bail')
  } finally {
    adding.value = false
  }
}

async function makeStatic(lease) {
  makingStatic.value = lease.id
  try {
    await api.post(`/routers/${route.params.id}/dhcp/leases/${lease.id}/make-static`)
    notifications.success('Bail converti en statique')
    await fetchLeases()
  } catch (error) {
    notifications.error('Erreur lors de la conversion')
  } finally {
    makingStatic.value = null
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

onMounted(() => {
  fetchServers()
  fetchNetworks()
  fetchPools()
  fetchLeases()
})
</script>
