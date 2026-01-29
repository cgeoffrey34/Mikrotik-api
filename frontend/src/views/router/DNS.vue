<template>
  <div class="space-y-6">
    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- DNS Settings Tab -->
    <div v-if="activeTab === 'settings'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Parametres DNS</h3>
          <div class="flex gap-2">
            <button @click="showSettingsModal = true" class="btn btn-primary text-sm">
              <PencilIcon class="w-4 h-4 mr-1" /> Modifier
            </button>
            <button @click="flushCache" class="btn btn-secondary text-sm" :disabled="flushing">
              {{ flushing ? 'Vidage...' : 'Vider le cache' }}
            </button>
          </div>
        </div>

        <div v-if="loadingSettings" class="p-6 text-center">
          <div class="inline-flex items-center text-gray-500">
            <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            Chargement...
          </div>
        </div>

        <div v-else-if="settings" class="p-6">
          <dl class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="bg-gray-50 p-4 rounded-lg">
              <dt class="text-sm text-gray-500 mb-1">Serveurs DNS</dt>
              <dd class="text-gray-900 font-medium font-mono text-sm">{{ settings.servers || 'Non configure' }}</dd>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <dt class="text-sm text-gray-500 mb-1">Serveurs dynamiques</dt>
              <dd class="text-gray-900 font-mono text-sm">{{ settings.dynamic_servers || 'Aucun' }}</dd>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <dt class="text-sm text-gray-500 mb-1">Requetes distantes</dt>
              <dd>
                <span :class="[settings.allow_remote_requests ? 'badge-success' : 'badge-warning', 'badge']">
                  {{ settings.allow_remote_requests ? 'Autorisees' : 'Refusees' }}
                </span>
              </dd>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <dt class="text-sm text-gray-500 mb-1">Taille du cache</dt>
              <dd class="text-gray-900 font-medium">{{ settings.cache_size }} KiB</dd>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <dt class="text-sm text-gray-500 mb-1">Cache utilise</dt>
              <dd class="text-gray-900">
                {{ settings.cache_used }} KiB
                <span class="text-gray-500 text-sm">({{ cacheUsagePercent }}%)</span>
              </dd>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <dt class="text-sm text-gray-500 mb-1">TTL max cache</dt>
              <dd class="text-gray-900">{{ settings.cache_max_ttl || 'Default' }}</dd>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg" v-if="settings.use_doh_server">
              <dt class="text-sm text-gray-500 mb-1">Serveur DoH</dt>
              <dd class="text-gray-900 font-mono text-sm truncate">{{ settings.use_doh_server }}</dd>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg" v-if="settings.use_doh_server">
              <dt class="text-sm text-gray-500 mb-1">Verification certificat DoH</dt>
              <dd>
                <span :class="[settings.verify_doh_cert ? 'badge-success' : 'badge-warning', 'badge']">
                  {{ settings.verify_doh_cert ? 'Oui' : 'Non' }}
                </span>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>

    <!-- DNS Static Entries Tab -->
    <div v-if="activeTab === 'static'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Entrees DNS statiques ({{ filteredEntries.length }}/{{ entries.length }})</h3>
          <button @click="showAddModal = true" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" />
            Ajouter une entree
          </button>
        </div>

        <!-- Type filter -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50 flex flex-wrap gap-4" v-if="entryTypes.length > 1">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Type:</span>
            <button @click="entryTypeFilter = ''" :class="[!entryTypeFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Tous</button>
            <button v-for="t in entryTypes" :key="t" @click="entryTypeFilter = t" :class="[entryTypeFilter === t ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ t }}</button>
          </div>
        </div>

        <DataTable :columns="columns" :data="filteredEntries" :loading="loading" empty-message="Aucune entree DNS">
          <template #cell-name="{ row }">
            <span class="font-medium text-gray-900">{{ row.name }}</span>
          </template>

          <template #cell-type="{ row }">
            <span :class="[getTypeClass(row.type), 'badge']">{{ row.type || 'A' }}</span>
          </template>

          <template #cell-value="{ row }">
            <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ getRecordValue(row) }}</code>
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
            <div class="flex items-center gap-2">
              <button
                v-if="!row.dynamic"
                @click="toggleEntry(row)"
                :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
                :disabled="toggling === row.id"
              >
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button
                v-if="!row.dynamic"
                @click="deleteEntry(row)"
                class="text-red-600 hover:text-red-800"
                :disabled="deleting === row.id"
              >
                Supprimer
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- DNS Cache Tab -->
    <div v-if="activeTab === 'cache'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Cache DNS ({{ filteredCacheEntries.length }}/{{ cacheEntries.length }})</h3>
          <div class="flex gap-2">
            <button @click="fetchCache" class="btn btn-secondary text-sm" :disabled="loadingCache">
              <ArrowPathIcon class="w-4 h-4 mr-1" :class="{ 'animate-spin': loadingCache }" /> Actualiser
            </button>
            <button @click="flushCache" class="btn btn-warning text-sm" :disabled="flushing">
              {{ flushing ? 'Vidage...' : 'Vider le cache' }}
            </button>
          </div>
        </div>

        <!-- Cache filters -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50 flex flex-wrap gap-4" v-if="cacheTypes.length > 1">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Type:</span>
            <button @click="cacheTypeFilter = ''" :class="[!cacheTypeFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Tous</button>
            <button v-for="type in cacheTypes" :key="type" @click="cacheTypeFilter = type" :class="[cacheTypeFilter === type ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ type }}</button>
          </div>
          <div class="flex items-center gap-2 ml-auto">
            <input v-model="cacheSearchFilter" type="text" placeholder="Rechercher..." class="input text-sm py-1 px-2 w-48" />
          </div>
        </div>

        <DataTable :columns="cacheColumns" :data="filteredCacheEntries" :loading="loadingCache" empty-message="Cache DNS vide">
          <template #cell-name="{ row }">
            <span class="font-medium text-gray-900 font-mono text-sm">{{ row.name }}</span>
          </template>

          <template #cell-type="{ row }">
            <span :class="[getCacheTypeClass(row.type), 'badge']">{{ row.type }}</span>
          </template>

          <template #cell-data="{ row }">
            <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.data }}</code>
          </template>

          <template #cell-static="{ row }">
            <span :class="[row.static ? 'badge-info' : 'badge-success', 'badge']">
              {{ row.static ? 'Statique' : 'Cache' }}
            </span>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Settings Edit Modal -->
    <Modal v-model="showSettingsModal" title="Modifier les parametres DNS" size="lg">
      <form @submit.prevent="saveSettings" class="space-y-4">
        <div>
          <label class="label">Serveurs DNS (separes par des virgules)</label>
          <input v-model="settingsForm.servers" type="text" class="input font-mono" placeholder="8.8.8.8,8.8.4.4" />
          <p class="text-xs text-gray-500 mt-1">Exemple: 8.8.8.8,1.1.1.1</p>
        </div>

        <div class="flex items-center">
          <input type="checkbox" v-model="settingsForm.allow_remote_requests" id="allow-remote" class="mr-2" />
          <label for="allow-remote">Autoriser les requetes distantes</label>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Taille du cache (KiB)</label>
            <input v-model.number="settingsForm.cache_size" type="number" class="input" min="512" max="10240000" />
          </div>
          <div>
            <label class="label">TTL max cache</label>
            <input v-model="settingsForm.cache_max_ttl" type="text" class="input" placeholder="1w" />
            <p class="text-xs text-gray-500 mt-1">Format: 1s, 5m, 1h, 1d, 1w</p>
          </div>
        </div>

        <div class="border-t pt-4 mt-4">
          <h4 class="font-medium text-gray-700 mb-3">DNS over HTTPS (DoH)</h4>
          <div>
            <label class="label">URL du serveur DoH</label>
            <input v-model="settingsForm.use_doh_server" type="text" class="input font-mono text-sm" placeholder="https://cloudflare-dns.com/dns-query" />
            <p class="text-xs text-gray-500 mt-1">Laisser vide pour desactiver DoH</p>
          </div>
          <div class="flex items-center mt-3">
            <input type="checkbox" v-model="settingsForm.verify_doh_cert" id="verify-doh" class="mr-2" />
            <label for="verify-doh">Verifier le certificat DoH</label>
          </div>
        </div>
      </form>

      <template #footer>
        <button @click="saveSettings" class="btn btn-primary" :disabled="savingSettings">
          {{ savingSettings ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
        <button @click="showSettingsModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add entry modal -->
    <Modal v-model="showAddModal" title="Ajouter une entree DNS" size="md">
      <form @submit.prevent="addEntry" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Type d'enregistrement *</label>
            <select v-model="form.record_type" class="input" @change="resetFormFields">
              <option value="A">A (IPv4)</option>
              <option value="AAAA">AAAA (IPv6)</option>
              <option value="CNAME">CNAME (Alias)</option>
              <option value="MX">MX (Mail)</option>
              <option value="TXT">TXT (Texte)</option>
              <option value="NS">NS (Serveur de noms)</option>
              <option value="SRV">SRV (Service)</option>
              <option value="FWD">FWD (Forward)</option>
              <option value="NXDOMAIN">NXDOMAIN (Blocage)</option>
            </select>
          </div>
          <div>
            <label class="label">Nom de domaine *</label>
            <input v-model="form.name" type="text" class="input" placeholder="exemple.local" required />
          </div>
        </div>

        <!-- A / AAAA record -->
        <div v-if="form.record_type === 'A' || form.record_type === 'AAAA'">
          <label class="label">Adresse IP *</label>
          <input
            v-model="form.address"
            type="text"
            class="input"
            :placeholder="form.record_type === 'AAAA' ? '2001:db8::1' : '192.168.1.100'"
            required
          />
        </div>

        <!-- CNAME record -->
        <div v-if="form.record_type === 'CNAME'">
          <label class="label">Cible (CNAME) *</label>
          <input v-model="form.cname" type="text" class="input" placeholder="target.exemple.local" required />
        </div>

        <!-- MX record -->
        <div v-if="form.record_type === 'MX'" class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Serveur mail *</label>
            <input v-model="form.mx_exchange" type="text" class="input" placeholder="mail.exemple.local" required />
          </div>
          <div>
            <label class="label">Priorite</label>
            <input v-model.number="form.mx_preference" type="number" class="input" placeholder="10" min="0" />
          </div>
        </div>

        <!-- TXT record -->
        <div v-if="form.record_type === 'TXT'">
          <label class="label">Texte *</label>
          <textarea v-model="form.text" class="input" rows="3" placeholder="v=spf1 include:..." required></textarea>
        </div>

        <!-- NS record -->
        <div v-if="form.record_type === 'NS'">
          <label class="label">Serveur de noms *</label>
          <input v-model="form.ns" type="text" class="input" placeholder="ns1.exemple.local" required />
        </div>

        <!-- SRV record -->
        <div v-if="form.record_type === 'SRV'" class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Cible (serveur) *</label>
            <input v-model="form.srv_target" type="text" class="input" placeholder="server.exemple.local" required />
          </div>
          <div>
            <label class="label">Port *</label>
            <input v-model.number="form.srv_port" type="number" class="input" placeholder="5060" min="1" max="65535" required />
          </div>
        </div>

        <!-- FWD (Forward) record -->
        <div v-if="form.record_type === 'FWD'">
          <label class="label">Forward vers (serveur DNS) *</label>
          <input v-model="form.forward_to" type="text" class="input" placeholder="8.8.8.8" required />
        </div>

        <!-- NXDOMAIN - no additional fields needed -->
        <div v-if="form.record_type === 'NXDOMAIN'" class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-sm text-yellow-800">
            L'enregistrement NXDOMAIN permet de bloquer un domaine en retournant une erreur "domain not found".
          </p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">TTL</label>
            <input v-model="form.ttl" type="text" class="input" placeholder="1d" />
          </div>
          <div>
            <label class="label">Commentaire</label>
            <input v-model="form.comment" type="text" class="input" placeholder="Optionnel" />
          </div>
        </div>

        <div class="flex items-center">
          <input type="checkbox" v-model="form.disabled" id="dns-disabled" class="mr-2" />
          <label for="dns-disabled">Creer desactivee</label>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'
import Modal from '../../components/Modal.vue'
import { PlusIcon, PencilIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const notifications = useNotificationStore()

// Tabs
const tabs = [
  { id: 'settings', name: 'Parametres' },
  { id: 'static', name: 'Entrees statiques' },
  { id: 'cache', name: 'Cache DNS' }
]
const activeTab = ref('settings')

// Data
const entries = ref([])
const settings = ref(null)
const cacheEntries = ref([])

// Loading states
const loading = ref(true)
const loadingSettings = ref(true)
const loadingCache = ref(false)

// Action states
const deleting = ref(null)
const toggling = ref(null)
const flushing = ref(false)
const showAddModal = ref(false)
const showSettingsModal = ref(false)
const adding = ref(false)
const savingSettings = ref(false)

// Filters
const entryTypeFilter = ref('')
const cacheTypeFilter = ref('')
const cacheSearchFilter = ref('')

// Forms
const form = reactive({
  name: '',
  record_type: 'A',
  address: '',
  cname: '',
  mx_exchange: '',
  mx_preference: 10,
  text: '',
  ns: '',
  srv_target: '',
  srv_port: null,
  forward_to: '',
  ttl: '1d',
  comment: '',
  disabled: false
})

const settingsForm = reactive({
  servers: '',
  allow_remote_requests: false,
  cache_size: 2048,
  cache_max_ttl: '1w',
  use_doh_server: '',
  verify_doh_cert: false
})

// Columns
const columns = [
  { key: 'name', label: 'Nom' },
  { key: 'type', label: 'Type' },
  { key: 'value', label: 'Valeur' },
  { key: 'ttl', label: 'TTL' },
  { key: 'disabled', label: 'Status' },
  { key: 'dynamic', label: 'Source' },
  { key: 'comment', label: 'Commentaire' }
]

const cacheColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'type', label: 'Type' },
  { key: 'data', label: 'Donnee' },
  { key: 'ttl', label: 'TTL' },
  { key: 'static', label: 'Source' }
]

// Computed
const entryTypes = computed(() => {
  return [...new Set(entries.value.map(e => e.type || 'A').filter(Boolean))].sort()
})

const filteredEntries = computed(() => {
  if (!entryTypeFilter.value) return entries.value
  return entries.value.filter(e => (e.type || 'A') === entryTypeFilter.value)
})

const cacheUsagePercent = computed(() => {
  if (!settings.value || !settings.value.cache_size) return 0
  return Math.round((settings.value.cache_used / settings.value.cache_size) * 100)
})

const cacheTypes = computed(() => {
  return [...new Set(cacheEntries.value.map(e => e.type).filter(Boolean))].sort()
})

const filteredCacheEntries = computed(() => {
  let result = cacheEntries.value
  if (cacheTypeFilter.value) {
    result = result.filter(e => e.type === cacheTypeFilter.value)
  }
  if (cacheSearchFilter.value) {
    const search = cacheSearchFilter.value.toLowerCase()
    result = result.filter(e =>
      e.name.toLowerCase().includes(search) ||
      e.data.toLowerCase().includes(search)
    )
  }
  return result
})

// Helper functions
function getTypeClass(type) {
  const classes = {
    'A': 'badge-success',
    'AAAA': 'badge-info',
    'CNAME': 'badge-purple',
    'MX': 'badge-warning',
    'TXT': 'badge-info',
    'NS': 'badge-success',
    'SRV': 'badge-warning',
    'FWD': 'badge-info',
    'NXDOMAIN': 'badge-danger'
  }
  return classes[type] || 'badge-info'
}

function getCacheTypeClass(type) {
  const classes = {
    'A': 'badge-success',
    'AAAA': 'badge-info',
    'CNAME': 'badge-purple',
    'MX': 'badge-warning',
    'TXT': 'badge-info',
    'NS': 'badge-success',
    'SRV': 'badge-warning',
    'PTR': 'badge-secondary',
    'SOA': 'badge-secondary'
  }
  return classes[type] || 'badge-info'
}

function getRecordValue(row) {
  if (row.address) return row.address
  if (row.cname) return row.cname
  if (row.mx_exchange) return `${row.mx_exchange} (pref: ${row.mx_preference || 10})`
  if (row.text) return row.text.substring(0, 50) + (row.text.length > 50 ? '...' : '')
  if (row.ns) return row.ns
  if (row.srv_target) return `${row.srv_target}:${row.srv_port}`
  if (row.forward_to) return `-> ${row.forward_to}`
  if (row.type === 'NXDOMAIN') return 'BLOCKED'
  return '-'
}

function resetFormFields() {
  form.address = ''
  form.cname = ''
  form.mx_exchange = ''
  form.mx_preference = 10
  form.text = ''
  form.ns = ''
  form.srv_target = ''
  form.srv_port = null
  form.forward_to = ''
}

// API calls
async function fetchSettings() {
  loadingSettings.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dns/settings`)
    settings.value = response.data
    // Update form with current settings
    settingsForm.servers = response.data.servers || ''
    settingsForm.allow_remote_requests = response.data.allow_remote_requests || false
    settingsForm.cache_size = response.data.cache_size || 2048
    settingsForm.cache_max_ttl = response.data.cache_max_ttl || '1w'
    settingsForm.use_doh_server = response.data.use_doh_server || ''
    settingsForm.verify_doh_cert = response.data.verify_doh_cert || false
  } catch (error) {
    console.error('Error fetching DNS settings:', error)
  } finally {
    loadingSettings.value = false
  }
}

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

async function fetchCache() {
  loadingCache.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dns/cache`)
    cacheEntries.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement du cache DNS')
  } finally {
    loadingCache.value = false
  }
}

async function saveSettings() {
  savingSettings.value = true
  try {
    await api.put(`/routers/${route.params.id}/dns/settings`, {
      servers: settingsForm.servers || null,
      allow_remote_requests: settingsForm.allow_remote_requests,
      cache_size: settingsForm.cache_size,
      cache_max_ttl: settingsForm.cache_max_ttl || null,
      use_doh_server: settingsForm.use_doh_server || null,
      verify_doh_cert: settingsForm.verify_doh_cert
    })
    notifications.success('Parametres DNS mis a jour')
    showSettingsModal.value = false
    await fetchSettings()
  } catch (error) {
    notifications.error('Erreur lors de la mise a jour des parametres')
  } finally {
    savingSettings.value = false
  }
}

async function flushCache() {
  flushing.value = true
  try {
    await api.post(`/routers/${route.params.id}/dns/cache/flush`)
    notifications.success('Cache DNS vide')
    await fetchSettings()
    if (activeTab.value === 'cache') {
      await fetchCache()
    }
  } catch (error) {
    notifications.error('Erreur lors du vidage du cache')
  } finally {
    flushing.value = false
  }
}

async function addEntry() {
  adding.value = true
  try {
    const payload = {
      name: form.name,
      record_type: form.record_type,
      ttl: form.ttl,
      comment: form.comment,
      disabled: form.disabled
    }

    // Add type-specific fields
    switch (form.record_type) {
      case 'A':
      case 'AAAA':
        payload.address = form.address
        break
      case 'CNAME':
        payload.cname = form.cname
        break
      case 'MX':
        payload.mx_exchange = form.mx_exchange
        payload.mx_preference = form.mx_preference
        break
      case 'TXT':
        payload.text = form.text
        break
      case 'NS':
        payload.ns = form.ns
        break
      case 'SRV':
        payload.srv_target = form.srv_target
        payload.srv_port = form.srv_port
        break
      case 'FWD':
        payload.forward_to = form.forward_to
        break
    }

    await api.post(`/routers/${route.params.id}/dns/static`, payload)
    notifications.success('Entree DNS ajoutee')
    showAddModal.value = false
    resetForm()
    await fetchEntries()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout')
  } finally {
    adding.value = false
  }
}

async function toggleEntry(entry) {
  toggling.value = entry.id
  try {
    await api.post(`/routers/${route.params.id}/dns/static/${entry.id}/toggle`, null, {
      params: { enable: entry.disabled }
    })
    notifications.success(`Entree ${entry.disabled ? 'activee' : 'desactivee'}`)
    await fetchEntries()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    toggling.value = null
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

function resetForm() {
  form.name = ''
  form.record_type = 'A'
  form.address = ''
  form.cname = ''
  form.mx_exchange = ''
  form.mx_preference = 10
  form.text = ''
  form.ns = ''
  form.srv_target = ''
  form.srv_port = null
  form.forward_to = ''
  form.ttl = '1d'
  form.comment = ''
  form.disabled = false
}

// Watch tab changes for lazy loading
watch(activeTab, (newTab) => {
  if (newTab === 'static' && entries.value.length === 0) {
    fetchEntries()
  } else if (newTab === 'cache' && cacheEntries.value.length === 0) {
    fetchCache()
  }
})

onMounted(() => {
  fetchSettings()
  fetchEntries()
})
</script>
