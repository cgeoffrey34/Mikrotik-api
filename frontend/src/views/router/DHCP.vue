<template>
  <div class="space-y-6">
    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            activeTab === tab.key
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ tab.label }}
          <span v-if="tab.count !== null" class="ml-2 bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- ==================== Baux DHCP ==================== -->
    <div v-if="activeTab === 'leases'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Baux DHCP</h3>
          <button @click="openAddLease" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" />
            Ajouter un bail statique
          </button>
        </div>

        <!-- Server filter -->
        <div v-if="leaseServers.length > 1" class="px-6 pt-4 flex flex-wrap gap-2">
          <button
            @click="leaseServerFilter = null"
            :class="[
              leaseServerFilter === null ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100',
              'px-3 py-1 rounded-full text-xs font-medium border transition-colors'
            ]"
          >
            Tous ({{ leases.length }})
          </button>
          <button
            v-for="srv in leaseServers"
            :key="srv"
            @click="leaseServerFilter = srv"
            :class="[
              leaseServerFilter === srv ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100',
              'px-3 py-1 rounded-full text-xs font-medium border transition-colors'
            ]"
          >
            {{ srv }} ({{ leases.filter(l => l.server === srv).length }})
          </button>
        </div>

        <DataTable :columns="leaseColumns" :data="filteredLeases" :loading="loadingLeases" empty-message="Aucun bail DHCP">
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

          <template #cell-disabled="{ row }">
            <span v-if="row.disabled" class="badge badge-warning">Desactive</span>
          </template>

          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button
                v-if="row.dynamic"
                @click="makeStatic(row)"
                class="text-blue-600 hover:text-blue-800 text-sm"
                :disabled="actionLoading === row.id"
              >
                Rendre statique
              </button>
              <button
                @click="deleteLease(row)"
                class="text-red-600 hover:text-red-800 text-sm"
                :disabled="actionLoading === row.id"
              >
                Supprimer
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Serveurs DHCP ==================== -->
    <div v-if="activeTab === 'servers'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Serveurs DHCP</h3>
          <button @click="openAddServer" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" />
            Ajouter un serveur
          </button>
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
            <div class="flex items-center gap-2">
              <button @click="openEditServer(row)" class="text-blue-600 hover:text-blue-800 text-sm">
                Modifier
              </button>
              <button
                @click="toggleServer(row)"
                :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800', 'text-sm']"
                :disabled="actionLoading === row.id"
              >
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button @click="deleteServer(row)" class="text-red-600 hover:text-red-800 text-sm" :disabled="actionLoading === row.id">
                Supprimer
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Reseaux DHCP ==================== -->
    <div v-if="activeTab === 'networks'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Reseaux DHCP</h3>
          <button @click="openAddNetwork" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" />
            Ajouter un reseau
          </button>
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

          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="openEditNetwork(row)" class="text-blue-600 hover:text-blue-800 text-sm">
                Modifier
              </button>
              <button @click="deleteNetwork(row)" class="text-red-600 hover:text-red-800 text-sm" :disabled="actionLoading === row.id">
                Supprimer
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Pools IP ==================== -->
    <div v-if="activeTab === 'pools'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Pools IP</h3>
          <button @click="openAddPool" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" />
            Ajouter un pool
          </button>
        </div>

        <DataTable :columns="poolColumns" :data="pools" :loading="loadingPools" empty-message="Aucun pool IP">
          <template #cell-name="{ row }">
            <span class="font-medium text-gray-900">{{ row.name }}</span>
          </template>

          <template #cell-ranges="{ row }">
            <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.ranges }}</code>
          </template>

          <template #cell-usage="{ row }">
            <div v-if="row.total > 0" class="min-w-[160px]">
              <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>{{ row.used }} / {{ row.total }}</span>
                <span>{{ Math.round((row.used / row.total) * 100) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all"
                  :class="[
                    (row.used / row.total) > 0.9 ? 'bg-red-500' :
                    (row.used / row.total) > 0.7 ? 'bg-yellow-500' : 'bg-green-500'
                  ]"
                  :style="{ width: Math.min((row.used / row.total) * 100, 100) + '%' }"
                ></div>
              </div>
              <div class="text-xs text-gray-500 mt-1">{{ row.available }} disponible(s)</div>
            </div>
            <span v-else class="text-gray-400">-</span>
          </template>

          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="openEditPool(row)" class="text-blue-600 hover:text-blue-800 text-sm">
                Modifier
              </button>
              <button @click="deletePool(row)" class="text-red-600 hover:text-red-800 text-sm" :disabled="actionLoading === row.id">
                Supprimer
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Options DHCP ==================== -->
    <div v-if="activeTab === 'options'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Options DHCP</h3>
          <button @click="openAddOption" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" />
            Ajouter une option
          </button>
        </div>

        <DataTable :columns="optionColumns" :data="options" :loading="loadingOptions" empty-message="Aucune option DHCP">
          <template #cell-name="{ row }">
            <span class="font-medium text-gray-900">{{ row.name }}</span>
          </template>

          <template #cell-code="{ row }">
            <span class="badge badge-info">{{ row.code }}</span>
          </template>

          <template #cell-value="{ row }">
            <code v-if="row.value" class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.value }}</code>
            <code v-else-if="row.raw_value" class="text-sm bg-gray-100 px-2 py-1 rounded text-gray-500">{{ row.raw_value }}</code>
            <span v-else class="text-gray-400">-</span>
          </template>

          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="openEditOption(row)" class="text-blue-600 hover:text-blue-800 text-sm">
                Modifier
              </button>
              <button @click="deleteOption(row)" class="text-red-600 hover:text-red-800 text-sm" :disabled="actionLoading === row.id">
                Supprimer
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== MODALS ==================== -->

    <!-- Add/Edit Lease Modal -->
    <Modal v-model="showLeaseModal" :title="'Ajouter un bail statique'" size="sm">
      <form @submit.prevent="saveLease" class="space-y-4">
        <div>
          <label class="label">Adresse IP *</label>
          <input v-model="leaseForm.address" type="text" class="input" placeholder="192.168.1.100" required />
        </div>
        <div>
          <label class="label">Adresse MAC *</label>
          <input v-model="leaseForm.mac_address" type="text" class="input" placeholder="AA:BB:CC:DD:EE:FF" required />
        </div>
        <div>
          <label class="label">Serveur DHCP</label>
          <select v-model="leaseForm.server" class="input">
            <option value="default">default</option>
            <option v-for="srv in servers" :key="srv.id" :value="srv.name">{{ srv.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Hostname</label>
          <input v-model="leaseForm.hostname" type="text" class="input" placeholder="pc-bureau" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="leaseForm.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>
      <template #footer>
        <button @click="saveLease" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Ajout...' : 'Ajouter' }}
        </button>
        <button @click="showLeaseModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add/Edit Server Modal -->
    <Modal v-model="showServerModal" :title="editingServer ? 'Modifier le serveur' : 'Ajouter un serveur'" size="sm">
      <form @submit.prevent="saveServer" class="space-y-4">
        <div>
          <label class="label">Nom *</label>
          <input v-model="serverForm.name" type="text" class="input" placeholder="dhcp1" required />
        </div>
        <div>
          <label class="label">Interface *</label>
          <input v-model="serverForm.interface" type="text" class="input" placeholder="bridge1" required />
        </div>
        <div>
          <label class="label">Pool d'adresses *</label>
          <select v-model="serverForm.address_pool" class="input">
            <option v-for="pool in pools" :key="pool.id" :value="pool.name">{{ pool.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Duree du bail</label>
          <input v-model="serverForm.lease_time" type="text" class="input" placeholder="10m" />
        </div>
        <div>
          <label class="label">Authoritative</label>
          <select v-model="serverForm.authoritative" class="input">
            <option value="yes">yes</option>
            <option value="no">no</option>
            <option value="after-2sec-delay">after-2sec-delay</option>
            <option value="after-10sec-delay">after-10sec-delay</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <input v-model="serverForm.disabled" type="checkbox" id="server-disabled" class="rounded" />
          <label for="server-disabled" class="text-sm text-gray-700">Desactive</label>
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="serverForm.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>
      <template #footer>
        <button @click="saveServer" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Sauvegarde...' : (editingServer ? 'Modifier' : 'Ajouter') }}
        </button>
        <button @click="showServerModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add/Edit Network Modal -->
    <Modal v-model="showNetworkModal" :title="editingNetwork ? 'Modifier le reseau' : 'Ajouter un reseau'" size="sm">
      <form @submit.prevent="saveNetwork" class="space-y-4">
        <div v-if="!editingNetwork">
          <label class="label">Adresse reseau *</label>
          <input v-model="networkForm.address" type="text" class="input" placeholder="192.168.1.0/24" required />
        </div>
        <div>
          <label class="label">Passerelle</label>
          <input v-model="networkForm.gateway" type="text" class="input" placeholder="192.168.1.1" />
        </div>
        <div>
          <label class="label">Serveur DNS</label>
          <input v-model="networkForm.dns_server" type="text" class="input" placeholder="192.168.1.1" />
        </div>
        <div>
          <label class="label">Domaine</label>
          <input v-model="networkForm.domain" type="text" class="input" placeholder="local" />
        </div>
        <div>
          <label class="label">Serveur NTP</label>
          <input v-model="networkForm.ntp_server" type="text" class="input" placeholder="192.168.1.1" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="networkForm.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>
      <template #footer>
        <button @click="saveNetwork" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Sauvegarde...' : (editingNetwork ? 'Modifier' : 'Ajouter') }}
        </button>
        <button @click="showNetworkModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add/Edit Pool Modal -->
    <Modal v-model="showPoolModal" :title="editingPool ? 'Modifier le pool' : 'Ajouter un pool'" size="sm">
      <form @submit.prevent="savePool" class="space-y-4">
        <div v-if="!editingPool">
          <label class="label">Nom *</label>
          <input v-model="poolForm.name" type="text" class="input" placeholder="pool1" required />
        </div>
        <div>
          <label class="label">Plages {{ editingPool ? '' : '*' }}</label>
          <input v-model="poolForm.ranges" type="text" class="input" placeholder="192.168.1.100-192.168.1.200" required />
        </div>
        <div>
          <label class="label">Pool suivant</label>
          <input v-model="poolForm.next_pool" type="text" class="input" placeholder="none" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="poolForm.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>
      <template #footer>
        <button @click="savePool" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Sauvegarde...' : (editingPool ? 'Modifier' : 'Ajouter') }}
        </button>
        <button @click="showPoolModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add/Edit Option Modal -->
    <Modal v-model="showOptionModal" :title="editingOption ? 'Modifier l\'option' : 'Ajouter une option'" size="sm">
      <form @submit.prevent="saveOption" class="space-y-4">
        <div v-if="!editingOption">
          <label class="label">Nom *</label>
          <input v-model="optionForm.name" type="text" class="input" placeholder="domain-name" required />
        </div>
        <div v-if="!editingOption">
          <label class="label">Code *</label>
          <input v-model.number="optionForm.code" type="number" class="input" placeholder="15" required />
        </div>
        <div>
          <label class="label">Valeur</label>
          <input v-model="optionForm.value" type="text" class="input" placeholder="'example.com'" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="optionForm.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>
      <template #footer>
        <button @click="saveOption" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Sauvegarde...' : (editingOption ? 'Modifier' : 'Ajouter') }}
        </button>
        <button @click="showOptionModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'
import Modal from '../../components/Modal.vue'
import { PlusIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const notifications = useNotificationStore()
const routerId = route.params.id

// State
const activeTab = ref('leases')
const leases = ref([])
const servers = ref([])
const networks = ref([])
const pools = ref([])
const options = ref([])
const loadingLeases = ref(false)
const loadingServers = ref(false)
const loadingNetworks = ref(false)
const loadingPools = ref(false)
const loadingOptions = ref(false)
const actionLoading = ref(null)
const saving = ref(false)
const leaseServerFilter = ref(null)

// Modals
const showLeaseModal = ref(false)
const showServerModal = ref(false)
const showNetworkModal = ref(false)
const showPoolModal = ref(false)
const showOptionModal = ref(false)
const editingServer = ref(null)
const editingNetwork = ref(null)
const editingPool = ref(null)
const editingOption = ref(null)

// Forms
const leaseForm = reactive({ address: '', mac_address: '', server: 'default', hostname: '', comment: '' })
const serverForm = reactive({ name: '', interface: '', address_pool: '', lease_time: '10m', authoritative: 'yes', disabled: false, comment: '' })
const networkForm = reactive({ address: '', gateway: '', dns_server: '', domain: '', ntp_server: '', comment: '' })
const poolForm = reactive({ name: '', ranges: '', next_pool: '', comment: '' })
const optionForm = reactive({ name: '', code: 0, value: '', comment: '' })

// Tabs
const tabs = computed(() => [
  { key: 'leases', label: 'Baux DHCP', count: leases.value.length },
  { key: 'servers', label: 'Serveurs', count: servers.value.length },
  { key: 'networks', label: 'Reseaux', count: networks.value.length },
  { key: 'pools', label: 'Pools IP', count: pools.value.length },
  { key: 'options', label: 'Options', count: options.value.length }
])

// Lease server grouping
const leaseServers = computed(() => {
  const srvSet = new Set(leases.value.map(l => l.server).filter(Boolean))
  return [...srvSet].sort()
})

const filteredLeases = computed(() => {
  if (!leaseServerFilter.value) return leases.value
  return leases.value.filter(l => l.server === leaseServerFilter.value)
})

// Columns
const leaseColumns = [
  { key: 'address', label: 'Adresse IP' },
  { key: 'mac_address', label: 'Adresse MAC' },
  { key: 'hostname', label: 'Hostname' },
  { key: 'status', label: 'Status' },
  { key: 'dynamic', label: 'Type' },
  { key: 'server', label: 'Serveur' },
  { key: 'expires_after', label: 'Expire dans' },
  { key: 'disabled', label: '' },
  { key: 'comment', label: 'Commentaire' }
]

const serverColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'interface', label: 'Interface' },
  { key: 'address_pool', label: 'Pool' },
  { key: 'lease_time', label: 'Duree bail' },
  { key: 'authoritative', label: 'Authoritative' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
]

const networkColumns = [
  { key: 'address', label: 'Reseau' },
  { key: 'gateway', label: 'Passerelle' },
  { key: 'dns_server', label: 'DNS' },
  { key: 'domain', label: 'Domaine' },
  { key: 'ntp_server', label: 'NTP' },
  { key: 'comment', label: 'Commentaire' }
]

const poolColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'ranges', label: 'Plages' },
  { key: 'usage', label: 'Utilisation' },
  { key: 'next_pool', label: 'Pool suivant' },
  { key: 'comment', label: 'Commentaire' }
]

const optionColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'code', label: 'Code' },
  { key: 'value', label: 'Valeur' },
  { key: 'comment', label: 'Commentaire' }
]

// ==================== Fetch ====================

async function fetchLeases() {
  loadingLeases.value = true
  try {
    const response = await api.get(`/routers/${routerId}/dhcp/leases`)
    leases.value = response.data
  } catch {
    notifications.error('Erreur lors du chargement des baux DHCP')
  } finally {
    loadingLeases.value = false
  }
}

async function fetchServers() {
  loadingServers.value = true
  try {
    const response = await api.get(`/routers/${routerId}/dhcp/servers`)
    servers.value = response.data
  } catch {
    notifications.error('Erreur lors du chargement des serveurs DHCP')
  } finally {
    loadingServers.value = false
  }
}

async function fetchNetworks() {
  loadingNetworks.value = true
  try {
    const response = await api.get(`/routers/${routerId}/dhcp/networks`)
    networks.value = response.data
  } catch {
    notifications.error('Erreur lors du chargement des reseaux DHCP')
  } finally {
    loadingNetworks.value = false
  }
}

async function fetchPools() {
  loadingPools.value = true
  try {
    const response = await api.get(`/routers/${routerId}/dhcp/pools`)
    pools.value = response.data
  } catch {
    notifications.error('Erreur lors du chargement des pools IP')
  } finally {
    loadingPools.value = false
  }
}

async function fetchOptions() {
  loadingOptions.value = true
  try {
    const response = await api.get(`/routers/${routerId}/dhcp/options`)
    options.value = response.data
  } catch {
    notifications.error('Erreur lors du chargement des options DHCP')
  } finally {
    loadingOptions.value = false
  }
}

// ==================== Lease Actions ====================

function openAddLease() {
  Object.assign(leaseForm, { address: '', mac_address: '', server: 'default', hostname: '', comment: '' })
  showLeaseModal.value = true
}

async function saveLease() {
  saving.value = true
  try {
    await api.post(`/routers/${routerId}/dhcp/leases`, {
      address: leaseForm.address,
      mac_address: leaseForm.mac_address,
      server: leaseForm.server,
      hostname: leaseForm.hostname,
      comment: leaseForm.comment
    })
    notifications.success('Bail ajoute avec succes')
    showLeaseModal.value = false
    await fetchLeases()
  } catch {
    notifications.error('Erreur lors de l\'ajout du bail')
  } finally {
    saving.value = false
  }
}

async function makeStatic(lease) {
  actionLoading.value = lease.id
  try {
    await api.post(`/routers/${routerId}/dhcp/leases/${lease.id}/make-static`)
    notifications.success('Bail converti en statique')
    await fetchLeases()
  } catch {
    notifications.error('Erreur lors de la conversion')
  } finally {
    actionLoading.value = null
  }
}

async function deleteLease(lease) {
  if (!confirm('Supprimer ce bail DHCP ?')) return
  actionLoading.value = lease.id
  try {
    await api.delete(`/routers/${routerId}/dhcp/leases/${lease.id}`)
    notifications.success('Bail supprime')
    await fetchLeases()
  } catch {
    notifications.error('Erreur lors de la suppression')
  } finally {
    actionLoading.value = null
  }
}

// ==================== Server Actions ====================

function openAddServer() {
  editingServer.value = null
  Object.assign(serverForm, { name: '', interface: '', address_pool: pools.value.length ? pools.value[0].name : '', lease_time: '10m', authoritative: 'yes', disabled: false, comment: '' })
  showServerModal.value = true
}

function openEditServer(srv) {
  editingServer.value = srv
  Object.assign(serverForm, {
    name: srv.name,
    interface: srv.interface,
    address_pool: srv.address_pool || '',
    lease_time: srv.lease_time || '10m',
    authoritative: srv.authoritative || 'yes',
    disabled: srv.disabled,
    comment: srv.comment || ''
  })
  showServerModal.value = true
}

async function saveServer() {
  saving.value = true
  try {
    if (editingServer.value) {
      await api.put(`/routers/${routerId}/dhcp/servers/${editingServer.value.id}`, {
        name: serverForm.name,
        interface: serverForm.interface,
        address_pool: serverForm.address_pool,
        lease_time: serverForm.lease_time,
        authoritative: serverForm.authoritative,
        disabled: serverForm.disabled,
        comment: serverForm.comment
      })
      notifications.success('Serveur modifie')
    } else {
      await api.post(`/routers/${routerId}/dhcp/servers`, {
        name: serverForm.name,
        interface: serverForm.interface,
        address_pool: serverForm.address_pool,
        lease_time: serverForm.lease_time,
        authoritative: serverForm.authoritative,
        disabled: serverForm.disabled,
        comment: serverForm.comment
      })
      notifications.success('Serveur ajoute')
    }
    showServerModal.value = false
    await fetchServers()
  } catch {
    notifications.error('Erreur lors de la sauvegarde du serveur')
  } finally {
    saving.value = false
  }
}

async function toggleServer(srv) {
  actionLoading.value = srv.id
  try {
    await api.post(`/routers/${routerId}/dhcp/servers/${srv.id}/toggle`, null, {
      params: { enable: srv.disabled }
    })
    notifications.success(`Serveur ${srv.disabled ? 'active' : 'desactive'}`)
    await fetchServers()
  } catch {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    actionLoading.value = null
  }
}

async function deleteServer(srv) {
  if (!confirm(`Supprimer le serveur DHCP "${srv.name}" ?`)) return
  actionLoading.value = srv.id
  try {
    await api.delete(`/routers/${routerId}/dhcp/servers/${srv.id}`)
    notifications.success('Serveur supprime')
    await fetchServers()
  } catch {
    notifications.error('Erreur lors de la suppression')
  } finally {
    actionLoading.value = null
  }
}

// ==================== Network Actions ====================

function openAddNetwork() {
  editingNetwork.value = null
  Object.assign(networkForm, { address: '', gateway: '', dns_server: '', domain: '', ntp_server: '', comment: '' })
  showNetworkModal.value = true
}

function openEditNetwork(net) {
  editingNetwork.value = net
  Object.assign(networkForm, {
    address: net.address,
    gateway: net.gateway || '',
    dns_server: net.dns_server || '',
    domain: net.domain || '',
    ntp_server: net.ntp_server || '',
    comment: net.comment || ''
  })
  showNetworkModal.value = true
}

async function saveNetwork() {
  saving.value = true
  try {
    if (editingNetwork.value) {
      await api.put(`/routers/${routerId}/dhcp/networks/${editingNetwork.value.id}`, {
        gateway: networkForm.gateway,
        dns_server: networkForm.dns_server,
        domain: networkForm.domain,
        ntp_server: networkForm.ntp_server,
        comment: networkForm.comment
      })
      notifications.success('Reseau modifie')
    } else {
      await api.post(`/routers/${routerId}/dhcp/networks`, {
        address: networkForm.address,
        gateway: networkForm.gateway,
        dns_server: networkForm.dns_server,
        domain: networkForm.domain,
        ntp_server: networkForm.ntp_server,
        comment: networkForm.comment
      })
      notifications.success('Reseau ajoute')
    }
    showNetworkModal.value = false
    await fetchNetworks()
  } catch {
    notifications.error('Erreur lors de la sauvegarde du reseau')
  } finally {
    saving.value = false
  }
}

async function deleteNetwork(net) {
  if (!confirm(`Supprimer le reseau "${net.address}" ?`)) return
  actionLoading.value = net.id
  try {
    await api.delete(`/routers/${routerId}/dhcp/networks/${net.id}`)
    notifications.success('Reseau supprime')
    await fetchNetworks()
  } catch {
    notifications.error('Erreur lors de la suppression')
  } finally {
    actionLoading.value = null
  }
}

// ==================== Pool Actions ====================

function openAddPool() {
  editingPool.value = null
  Object.assign(poolForm, { name: '', ranges: '', next_pool: '', comment: '' })
  showPoolModal.value = true
}

function openEditPool(pool) {
  editingPool.value = pool
  Object.assign(poolForm, {
    name: pool.name,
    ranges: pool.ranges,
    next_pool: pool.next_pool || '',
    comment: pool.comment || ''
  })
  showPoolModal.value = true
}

async function savePool() {
  saving.value = true
  try {
    if (editingPool.value) {
      await api.put(`/routers/${routerId}/dhcp/pools/${editingPool.value.id}`, {
        ranges: poolForm.ranges,
        next_pool: poolForm.next_pool,
        comment: poolForm.comment
      })
      notifications.success('Pool modifie')
    } else {
      await api.post(`/routers/${routerId}/dhcp/pools`, {
        name: poolForm.name,
        ranges: poolForm.ranges,
        next_pool: poolForm.next_pool,
        comment: poolForm.comment
      })
      notifications.success('Pool ajoute')
    }
    showPoolModal.value = false
    await fetchPools()
  } catch {
    notifications.error('Erreur lors de la sauvegarde du pool')
  } finally {
    saving.value = false
  }
}

async function deletePool(pool) {
  if (!confirm(`Supprimer le pool "${pool.name}" ?`)) return
  actionLoading.value = pool.id
  try {
    await api.delete(`/routers/${routerId}/dhcp/pools/${pool.id}`)
    notifications.success('Pool supprime')
    await fetchPools()
  } catch {
    notifications.error('Erreur lors de la suppression')
  } finally {
    actionLoading.value = null
  }
}

// ==================== Option Actions ====================

function openAddOption() {
  editingOption.value = null
  Object.assign(optionForm, { name: '', code: 0, value: '', comment: '' })
  showOptionModal.value = true
}

function openEditOption(opt) {
  editingOption.value = opt
  Object.assign(optionForm, {
    name: opt.name,
    code: opt.code,
    value: opt.value || '',
    comment: opt.comment || ''
  })
  showOptionModal.value = true
}

async function saveOption() {
  saving.value = true
  try {
    if (editingOption.value) {
      await api.put(`/routers/${routerId}/dhcp/options/${editingOption.value.id}`, {
        value: optionForm.value,
        comment: optionForm.comment
      })
      notifications.success('Option modifiee')
    } else {
      await api.post(`/routers/${routerId}/dhcp/options`, {
        name: optionForm.name,
        code: optionForm.code,
        value: optionForm.value,
        comment: optionForm.comment
      })
      notifications.success('Option ajoutee')
    }
    showOptionModal.value = false
    await fetchOptions()
  } catch {
    notifications.error('Erreur lors de la sauvegarde de l\'option')
  } finally {
    saving.value = false
  }
}

async function deleteOption(opt) {
  if (!confirm(`Supprimer l'option "${opt.name}" ?`)) return
  actionLoading.value = opt.id
  try {
    await api.delete(`/routers/${routerId}/dhcp/options/${opt.id}`)
    notifications.success('Option supprimee')
    await fetchOptions()
  } catch {
    notifications.error('Erreur lors de la suppression')
  } finally {
    actionLoading.value = null
  }
}

// ==================== Init ====================

// Load initial tab + servers (needed for lease form)
onMounted(() => {
  fetchLeases()
  fetchServers()
  fetchPools()
})

watch(activeTab, (tab) => {
  if (tab === 'networks' && networks.value.length === 0) fetchNetworks()
  if (tab === 'options' && options.value.length === 0) fetchOptions()
})
</script>
