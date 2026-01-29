<template>
  <div class="space-y-6">
    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-4">
        <div class="text-sm text-gray-500">Interfaces WiFi</div>
        <div class="text-2xl font-bold text-gray-900">{{ interfaces.length }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-500">Interfaces actives</div>
        <div class="text-2xl font-bold text-green-600">{{ interfaces.filter(i => i.running).length }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-500">Clients connectes</div>
        <div class="text-2xl font-bold text-blue-600">{{ clients.length }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-500">Profils de securite</div>
        <div class="text-2xl font-bold text-purple-600">{{ securityProfiles.length }}</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          :class="[activeTab === tab.id ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- ==================== Interfaces WiFi ==================== -->
    <div v-if="activeTab === 'interfaces'">
      <div class="card">
        <div class="p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Interfaces WiFi</h3>
        </div>

        <DataTable :columns="interfaceColumns" :data="interfaces" :loading="loadingInterfaces" empty-message="Aucune interface WiFi">
          <template #cell-name="{ row }">
            <span class="font-medium text-gray-900">{{ row.name }}</span>
          </template>
          <template #cell-ssid="{ row }">
            <code v-if="row.ssid" class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.ssid }}</code>
            <span v-else class="text-gray-400">N/A</span>
          </template>
          <template #cell-mode="{ row }">
            <span class="badge badge-info">{{ row.mode || 'N/A' }}</span>
          </template>
          <template #cell-security_profile="{ row }">
            <span v-if="row.security_profile" class="badge badge-success">{{ row.security_profile }}</span>
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #cell-running="{ row }">
            <span :class="[row.running ? 'badge-success' : 'badge-danger', 'badge']">
              {{ row.running ? 'Actif' : 'Inactif' }}
            </span>
          </template>
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
              {{ row.disabled ? 'Desactive' : 'Active' }}
            </span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="openEditInterface(row)" class="text-blue-600 hover:text-blue-800">Modifier</button>
              <button @click="toggleInterface(row)"
                :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
                :disabled="togglingIface === row.id">
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Security Profiles ==================== -->
    <div v-if="activeTab === 'profiles'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Profils de securite ({{ securityProfiles.length }})</h3>
          <button @click="openCreateProfile" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" /> Ajouter un profil
          </button>
        </div>

        <DataTable :columns="profileColumns" :data="securityProfiles" :loading="loadingProfiles" empty-message="Aucun profil de securite">
          <template #cell-name="{ row }">
            <span class="font-medium text-gray-900">{{ row.name }}</span>
            <span v-if="row.default" class="badge badge-info ml-2">Defaut</span>
          </template>
          <template #cell-mode="{ row }">
            <span class="badge badge-info">{{ row.mode || 'none' }}</span>
          </template>
          <template #cell-authentication_types="{ row }">
            <span v-if="row.authentication_types" class="text-sm">{{ row.authentication_types }}</span>
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #cell-unicast_ciphers="{ row }">
            <span v-if="row.unicast_ciphers" class="text-sm">{{ row.unicast_ciphers }}</span>
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #cell-group_ciphers="{ row }">
            <span v-if="row.group_ciphers" class="text-sm">{{ row.group_ciphers }}</span>
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #cell-password="{ row }">
            <div v-if="row.wpa_pre_shared_key || row.wpa2_pre_shared_key || row.passphrase" class="space-y-1">
              <div v-if="row.wpa_pre_shared_key" class="flex items-center gap-1 text-sm">
                <span class="text-gray-500">WPA:</span>
                <code class="bg-gray-100 px-1 rounded">{{ showPasswords[row.id] ? row.wpa_pre_shared_key : '••••••••' }}</code>
              </div>
              <div v-if="row.wpa2_pre_shared_key" class="flex items-center gap-1 text-sm">
                <span class="text-gray-500">WPA2:</span>
                <code class="bg-gray-100 px-1 rounded">{{ showPasswords[row.id] ? row.wpa2_pre_shared_key : '••••••••' }}</code>
              </div>
              <div v-if="row.passphrase" class="flex items-center gap-1 text-sm">
                <span class="text-gray-500">Pass:</span>
                <code class="bg-gray-100 px-1 rounded">{{ showPasswords[row.id] ? row.passphrase : '••••••••' }}</code>
              </div>
              <button @click="showPasswords[row.id] = !showPasswords[row.id]" class="text-xs text-blue-600 hover:text-blue-800">
                {{ showPasswords[row.id] ? 'Masquer' : 'Afficher' }}
              </button>
            </div>
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="openEditProfile(row)" class="text-blue-600 hover:text-blue-800">Modifier</button>
              <button v-if="!row.default" @click="deleteProfile(row)" class="text-red-600 hover:text-red-800"
                :disabled="deletingProfile === row.id">Supprimer</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Connected Clients ==================== -->
    <div v-if="activeTab === 'clients'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Clients connectes ({{ filteredClients.length }}/{{ clients.length }})</h3>
          <button @click="fetchClients" class="btn btn-secondary text-sm" :disabled="loadingClients">
            <ArrowPathIcon class="w-4 h-4 mr-1" :class="{ 'animate-spin': loadingClients }" /> Actualiser
          </button>
        </div>

        <!-- Interface filter -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50 flex flex-wrap gap-4" v-if="clientInterfaces.length > 0">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Interface:</span>
            <button @click="clientInterfaceFilter = ''" :class="[!clientInterfaceFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="iface in clientInterfaces" :key="iface" @click="clientInterfaceFilter = iface"
              :class="[clientInterfaceFilter === iface ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">
              {{ iface }}
            </button>
          </div>
        </div>

        <DataTable :columns="clientColumns" :data="filteredClients" :loading="loadingClients" empty-message="Aucun client connecte">
          <template #cell-mac_address="{ row }">
            <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.mac_address }}</code>
          </template>
          <template #cell-interface="{ row }">
            <span class="badge badge-info">{{ row.interface }}</span>
          </template>
          <template #cell-signal_strength="{ row }">
            <div class="flex items-center">
              <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                <div class="h-2 rounded-full" :class="getSignalColor(row.signal_strength)"
                  :style="{ width: getSignalPercent(row.signal_strength) + '%' }"></div>
              </div>
              <span class="text-sm">{{ row.signal_strength || 'N/A' }} dBm</span>
            </div>
          </template>
          <template #cell-tx_rate="{ row }">
            <span class="text-green-600 text-sm">{{ row.tx_rate || 'N/A' }}</span>
          </template>
          <template #cell-rx_rate="{ row }">
            <span class="text-blue-600 text-sm">{{ row.rx_rate || 'N/A' }}</span>
          </template>
          <template #cell-traffic="{ row }">
            <div class="text-sm">
              <div class="text-green-600">TX: {{ formatBytes(row.bytes_sent) }}</div>
              <div class="text-blue-600">RX: {{ formatBytes(row.bytes_received) }}</div>
            </div>
          </template>
          <template #actions="{ row }">
            <button @click="disconnectClient(row)" class="text-red-600 hover:text-red-800"
              :disabled="disconnecting === row.mac_address">Deconnecter</button>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Access List ==================== -->
    <div v-if="activeTab === 'access'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Liste d'acces ({{ accessList.length }})</h3>
          <button @click="showAccessModal = true" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" /> Ajouter une entree
          </button>
        </div>

        <DataTable :columns="accessColumns" :data="accessList" :loading="loadingAccess" empty-message="Aucune entree dans la liste d'acces">
          <template #cell-mac_address="{ row }">
            <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ row.mac_address }}</code>
          </template>
          <template #cell-interface="{ row }">
            <span class="badge badge-info">{{ row.interface || 'Toutes' }}</span>
          </template>
          <template #cell-authentication="{ row }">
            <span :class="[row.authentication ? 'badge-success' : 'badge-danger', 'badge']">
              {{ row.authentication ? 'Autorise' : 'Refuse' }}
            </span>
          </template>
          <template #cell-forwarding="{ row }">
            <span :class="[row.forwarding ? 'badge-success' : 'badge-warning', 'badge']">
              {{ row.forwarding ? 'Oui' : 'Non' }}
            </span>
          </template>
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
              {{ row.disabled ? 'Desactivee' : 'Active' }}
            </span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="toggleAccessEntry(row)"
                :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
                :disabled="togglingAccess === row.id">
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button @click="deleteAccessEntry(row)" class="text-red-600 hover:text-red-800"
                :disabled="deletingAccess === row.id">Supprimer</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== Edit Interface Modal ==================== -->
    <Modal v-model="showIfaceModal" title="Modifier l'interface WiFi" size="md">
      <form @submit.prevent="saveInterface" class="space-y-4">
        <div>
          <label class="label">SSID</label>
          <input v-model="ifaceForm.ssid" type="text" class="input" placeholder="Mon-WiFi" />
        </div>
        <div>
          <label class="label">Profil de securite</label>
          <select v-model="ifaceForm.security_profile" class="input">
            <option value="">-- Aucun --</option>
            <option v-for="p in securityProfiles" :key="p.id" :value="p.name">{{ p.name }}</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Mode</label>
            <input v-model="ifaceForm.mode" type="text" class="input" placeholder="ap-bridge" />
          </div>
          <div>
            <label class="label">Bande</label>
            <input v-model="ifaceForm.band" type="text" class="input" placeholder="2ghz-b/g/n" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Largeur de canal</label>
            <input v-model="ifaceForm.channel_width" type="text" class="input" placeholder="20/40mhz-XX" />
          </div>
          <div>
            <label class="label">Frequence</label>
            <input v-model="ifaceForm.frequency" type="text" class="input" placeholder="auto" />
          </div>
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="ifaceForm.comment" type="text" class="input" />
        </div>
      </form>
      <template #footer>
        <button @click="saveInterface" class="btn btn-primary" :disabled="savingIface">
          {{ savingIface ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
        <button @click="showIfaceModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- ==================== Create/Edit Profile Modal ==================== -->
    <Modal v-model="showProfileModal" :title="editingProfile ? 'Modifier le profil' : 'Creer un profil de securite'" size="md">
      <form @submit.prevent="saveProfile" class="space-y-4">
        <div v-if="!editingProfile">
          <label class="label">Nom *</label>
          <input v-model="profileForm.name" type="text" class="input" placeholder="mon-profil" required />
        </div>
        <div>
          <label class="label">Mode</label>
          <select v-model="profileForm.mode" class="input">
            <option value="none">none</option>
            <option value="static-keys-required">static-keys-required</option>
            <option value="static-keys-optional">static-keys-optional</option>
            <option value="dynamic-keys">dynamic-keys</option>
          </select>
        </div>
        <div>
          <label class="label">Types d'authentification</label>
          <input v-model="profileForm.authentication_types" type="text" class="input" placeholder="wpa2-psk" />
          <p class="text-xs text-gray-500 mt-1">Ex: wpa-psk, wpa2-psk, wpa2-eap</p>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Cle WPA</label>
            <input v-model="profileForm.wpa_pre_shared_key" type="password" class="input" placeholder="Mot de passe WPA" />
          </div>
          <div>
            <label class="label">Cle WPA2</label>
            <input v-model="profileForm.wpa2_pre_shared_key" type="password" class="input" placeholder="Mot de passe WPA2" />
          </div>
        </div>
        <div>
          <label class="label">Passphrase (WiFi 7.13+)</label>
          <input v-model="profileForm.passphrase" type="password" class="input" placeholder="Passphrase" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Unicast ciphers</label>
            <input v-model="profileForm.unicast_ciphers" type="text" class="input" placeholder="aes-ccm" />
          </div>
          <div>
            <label class="label">Group ciphers</label>
            <input v-model="profileForm.group_ciphers" type="text" class="input" placeholder="aes-ccm" />
          </div>
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="profileForm.comment" type="text" class="input" />
        </div>
      </form>
      <template #footer>
        <button @click="saveProfile" class="btn btn-primary" :disabled="savingProfile">
          {{ savingProfile ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
        <button @click="showProfileModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- ==================== Add Access List Modal ==================== -->
    <Modal v-model="showAccessModal" title="Ajouter a la liste d'acces" size="md">
      <form @submit.prevent="addAccessEntry" class="space-y-4">
        <div>
          <label class="label">Adresse MAC *</label>
          <input v-model="accessForm.mac_address" type="text" class="input font-mono" placeholder="00:11:22:33:44:55" required />
        </div>
        <div>
          <label class="label">Interface</label>
          <select v-model="accessForm.interface" class="input">
            <option value="">Toutes les interfaces</option>
            <option v-for="iface in interfaces" :key="iface.id" :value="iface.name">{{ iface.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Signal range</label>
          <input v-model="accessForm.signal_range" type="text" class="input" placeholder="-120..120" />
        </div>
        <div class="flex items-center gap-6">
          <div class="flex items-center">
            <input type="checkbox" v-model="accessForm.authentication" id="access-auth" class="mr-2" />
            <label for="access-auth">Autoriser l'authentification</label>
          </div>
          <div class="flex items-center">
            <input type="checkbox" v-model="accessForm.forwarding" id="access-fwd" class="mr-2" />
            <label for="access-fwd">Autoriser le forwarding</label>
          </div>
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="accessForm.comment" type="text" class="input" />
        </div>
        <div class="flex items-center">
          <input type="checkbox" v-model="accessForm.disabled" id="access-disabled" class="mr-2" />
          <label for="access-disabled">Creer desactivee</label>
        </div>
      </form>
      <template #footer>
        <button @click="addAccessEntry" class="btn btn-primary" :disabled="addingAccess">
          {{ addingAccess ? 'Ajout...' : 'Ajouter' }}
        </button>
        <button @click="showAccessModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import { useNotificationStore } from '../../stores/notifications'
import DataTable from '../../components/DataTable.vue'
import Modal from '../../components/Modal.vue'
import { PlusIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const notifications = useNotificationStore()

// Tabs
const tabs = [
  { id: 'interfaces', name: 'Interfaces' },
  { id: 'profiles', name: 'Profils de securite' },
  { id: 'clients', name: 'Clients connectes' },
  { id: 'access', name: 'Liste d\'acces' }
]
const activeTab = ref('interfaces')

// Data
const interfaces = ref([])
const clients = ref([])
const securityProfiles = ref([])
const accessList = ref([])

// Loading
const loadingInterfaces = ref(true)
const loadingClients = ref(false)
const loadingProfiles = ref(true)
const loadingAccess = ref(false)

// Action states
const togglingIface = ref(null)
const disconnecting = ref(null)
const deletingProfile = ref(null)
const togglingAccess = ref(null)
const deletingAccess = ref(null)
const savingIface = ref(false)
const savingProfile = ref(false)
const addingAccess = ref(false)

// Modals
const showIfaceModal = ref(false)
const showProfileModal = ref(false)
const showAccessModal = ref(false)
const editingProfile = ref(null)
const editingIface = ref(null)

// Password visibility toggle
const showPasswords = reactive({})

// Filters
const clientInterfaceFilter = ref('')

// Forms
const ifaceForm = reactive({
  ssid: '',
  security_profile: '',
  mode: '',
  band: '',
  channel_width: '',
  frequency: '',
  comment: ''
})

const profileForm = reactive({
  name: '',
  mode: 'dynamic-keys',
  authentication_types: '',
  wpa_pre_shared_key: '',
  wpa2_pre_shared_key: '',
  passphrase: '',
  unicast_ciphers: '',
  group_ciphers: '',
  comment: ''
})

const accessForm = reactive({
  mac_address: '',
  interface: '',
  signal_range: '',
  authentication: true,
  forwarding: true,
  comment: '',
  disabled: false
})

let refreshInterval = null

// Columns
const interfaceColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'ssid', label: 'SSID' },
  { key: 'mode', label: 'Mode' },
  { key: 'band', label: 'Bande' },
  { key: 'frequency', label: 'Frequence' },
  { key: 'security_profile', label: 'Securite' },
  { key: 'running', label: 'Etat' },
  { key: 'disabled', label: 'Status' }
]

const profileColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'mode', label: 'Mode' },
  { key: 'authentication_types', label: 'Auth. types' },
  { key: 'unicast_ciphers', label: 'Unicast ciphers' },
  { key: 'group_ciphers', label: 'Group ciphers' },
  { key: 'password', label: 'Mot de passe' },
  { key: 'comment', label: 'Commentaire' }
]

const clientColumns = [
  { key: 'interface', label: 'Interface' },
  { key: 'mac_address', label: 'Adresse MAC' },
  { key: 'signal_strength', label: 'Signal' },
  { key: 'tx_rate', label: 'Debit TX' },
  { key: 'rx_rate', label: 'Debit RX' },
  { key: 'uptime', label: 'Connecte depuis' },
  { key: 'traffic', label: 'Trafic' }
]

const accessColumns = [
  { key: 'mac_address', label: 'Adresse MAC' },
  { key: 'interface', label: 'Interface' },
  { key: 'signal_range', label: 'Signal range' },
  { key: 'authentication', label: 'Auth.' },
  { key: 'forwarding', label: 'Forwarding' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
]

// Computed
const clientInterfaces = computed(() => {
  return [...new Set(clients.value.map(c => c.interface).filter(Boolean))].sort()
})

const filteredClients = computed(() => {
  if (!clientInterfaceFilter.value) return clients.value
  return clients.value.filter(c => c.interface === clientInterfaceFilter.value)
})

// Helpers
function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function getSignalPercent(signal) {
  if (!signal) return 0
  const db = parseInt(signal)
  if (db >= -50) return 100
  if (db <= -100) return 0
  return Math.round((db + 100) * 2)
}

function getSignalColor(signal) {
  const percent = getSignalPercent(signal)
  if (percent >= 70) return 'bg-green-500'
  if (percent >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

// ==================== Fetch ====================

async function fetchInterfaces() {
  loadingInterfaces.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/interfaces`)
    interfaces.value = response.data
  } catch (error) {
    // WiFi might not be available
  } finally {
    loadingInterfaces.value = false
  }
}

async function fetchClients() {
  loadingClients.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/clients`)
    clients.value = response.data
  } catch (error) {
    // WiFi clients might not be available
  } finally {
    loadingClients.value = false
  }
}

async function fetchSecurityProfiles() {
  loadingProfiles.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/security-profiles`)
    securityProfiles.value = response.data
  } catch (error) {
    // Security profiles might not be available
  } finally {
    loadingProfiles.value = false
  }
}

async function fetchAccessList() {
  loadingAccess.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/wifi/access-list`)
    accessList.value = response.data
  } catch (error) {
    // Access list might not be available
  } finally {
    loadingAccess.value = false
  }
}

// ==================== Interface actions ====================

function openEditInterface(iface) {
  editingIface.value = iface
  ifaceForm.ssid = iface.ssid || ''
  ifaceForm.security_profile = iface.security_profile || ''
  ifaceForm.mode = iface.mode || ''
  ifaceForm.band = iface.band || ''
  ifaceForm.channel_width = iface.channel_width || ''
  ifaceForm.frequency = iface.frequency || ''
  ifaceForm.comment = iface.comment || ''
  showIfaceModal.value = true
}

async function saveInterface() {
  if (!editingIface.value) return
  savingIface.value = true
  try {
    await api.put(`/routers/${route.params.id}/wifi/interfaces/${editingIface.value.id}`, {
      ssid: ifaceForm.ssid || null,
      security_profile: ifaceForm.security_profile || null,
      mode: ifaceForm.mode || null,
      band: ifaceForm.band || null,
      channel_width: ifaceForm.channel_width || null,
      frequency: ifaceForm.frequency || null,
      comment: ifaceForm.comment || null
    })
    notifications.success('Interface mise a jour')
    showIfaceModal.value = false
    await fetchInterfaces()
  } catch (error) {
    notifications.error('Erreur lors de la mise a jour')
  } finally {
    savingIface.value = false
  }
}

async function toggleInterface(iface) {
  togglingIface.value = iface.id
  try {
    await api.post(`/routers/${route.params.id}/wifi/interfaces/${iface.id}/toggle`, null, {
      params: { enable: iface.disabled, interface_type: iface.interface_type || 'wireless' }
    })
    notifications.success(`Interface ${iface.disabled ? 'activee' : 'desactivee'}`)
    await fetchInterfaces()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    togglingIface.value = null
  }
}

// ==================== Profile actions ====================

function openCreateProfile() {
  editingProfile.value = null
  profileForm.name = ''
  profileForm.mode = 'dynamic-keys'
  profileForm.authentication_types = ''
  profileForm.wpa_pre_shared_key = ''
  profileForm.wpa2_pre_shared_key = ''
  profileForm.passphrase = ''
  profileForm.unicast_ciphers = ''
  profileForm.group_ciphers = ''
  profileForm.comment = ''
  showProfileModal.value = true
}

function openEditProfile(profile) {
  editingProfile.value = profile
  profileForm.name = profile.name
  profileForm.mode = profile.mode || 'dynamic-keys'
  profileForm.authentication_types = profile.authentication_types || ''
  profileForm.wpa_pre_shared_key = ''
  profileForm.wpa2_pre_shared_key = ''
  profileForm.passphrase = ''
  profileForm.unicast_ciphers = profile.unicast_ciphers || ''
  profileForm.group_ciphers = profile.group_ciphers || ''
  profileForm.comment = profile.comment || ''
  showProfileModal.value = true
}

async function saveProfile() {
  savingProfile.value = true
  try {
    if (editingProfile.value) {
      const data = {
        mode: profileForm.mode || null,
        authentication_types: profileForm.authentication_types || null,
        unicast_ciphers: profileForm.unicast_ciphers || null,
        group_ciphers: profileForm.group_ciphers || null,
        comment: profileForm.comment || null
      }
      if (profileForm.wpa_pre_shared_key) data.wpa_pre_shared_key = profileForm.wpa_pre_shared_key
      if (profileForm.wpa2_pre_shared_key) data.wpa2_pre_shared_key = profileForm.wpa2_pre_shared_key
      if (profileForm.passphrase) data.passphrase = profileForm.passphrase

      await api.put(`/routers/${route.params.id}/wifi/security-profiles/${editingProfile.value.id}`, data, {
        params: { profile_type: editingProfile.value.profile_type || 'wireless' }
      })
      notifications.success('Profil mis a jour')
    } else {
      const data = {
        name: profileForm.name,
        mode: profileForm.mode,
        authentication_types: profileForm.authentication_types || null,
        wpa_pre_shared_key: profileForm.wpa_pre_shared_key || null,
        wpa2_pre_shared_key: profileForm.wpa2_pre_shared_key || null,
        passphrase: profileForm.passphrase || null,
        unicast_ciphers: profileForm.unicast_ciphers || null,
        group_ciphers: profileForm.group_ciphers || null,
        comment: profileForm.comment || null
      }
      await api.post(`/routers/${route.params.id}/wifi/security-profiles`, data)
      notifications.success('Profil cree')
    }
    showProfileModal.value = false
    await fetchSecurityProfiles()
  } catch (error) {
    notifications.error('Erreur lors de l\'enregistrement du profil')
  } finally {
    savingProfile.value = false
  }
}

async function deleteProfile(profile) {
  if (!confirm(`Supprimer le profil "${profile.name}" ?`)) return
  deletingProfile.value = profile.id
  try {
    await api.delete(`/routers/${route.params.id}/wifi/security-profiles/${profile.id}`, {
      params: { profile_type: profile.profile_type || 'wireless' }
    })
    notifications.success('Profil supprime')
    await fetchSecurityProfiles()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deletingProfile.value = null
  }
}

// ==================== Client actions ====================

async function disconnectClient(client) {
  if (!confirm(`Deconnecter le client ${client.mac_address} ?`)) return
  disconnecting.value = client.mac_address
  try {
    await api.post(`/routers/${route.params.id}/wifi/clients/${client.mac_address}/disconnect`)
    notifications.success('Client deconnecte')
    await fetchClients()
  } catch (error) {
    notifications.error('Erreur lors de la deconnexion')
  } finally {
    disconnecting.value = null
  }
}

// ==================== Access List actions ====================

async function addAccessEntry() {
  addingAccess.value = true
  try {
    await api.post(`/routers/${route.params.id}/wifi/access-list`, {
      mac_address: accessForm.mac_address,
      interface: accessForm.interface || null,
      signal_range: accessForm.signal_range || null,
      authentication: accessForm.authentication,
      forwarding: accessForm.forwarding,
      comment: accessForm.comment || null,
      disabled: accessForm.disabled
    })
    notifications.success('Entree ajoutee a la liste d\'acces')
    showAccessModal.value = false
    resetAccessForm()
    await fetchAccessList()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout')
  } finally {
    addingAccess.value = false
  }
}

async function toggleAccessEntry(entry) {
  togglingAccess.value = entry.id
  try {
    await api.post(`/routers/${route.params.id}/wifi/access-list/${entry.id}/toggle`, null, {
      params: { enable: entry.disabled }
    })
    notifications.success(`Entree ${entry.disabled ? 'activee' : 'desactivee'}`)
    await fetchAccessList()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    togglingAccess.value = null
  }
}

async function deleteAccessEntry(entry) {
  if (!confirm('Supprimer cette entree de la liste d\'acces ?')) return
  deletingAccess.value = entry.id
  try {
    await api.delete(`/routers/${route.params.id}/wifi/access-list/${entry.id}`)
    notifications.success('Entree supprimee')
    await fetchAccessList()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deletingAccess.value = null
  }
}

function resetAccessForm() {
  accessForm.mac_address = ''
  accessForm.interface = ''
  accessForm.signal_range = ''
  accessForm.authentication = true
  accessForm.forwarding = true
  accessForm.comment = ''
  accessForm.disabled = false
}

// Lazy load tabs
watch(activeTab, (newTab) => {
  if (newTab === 'clients' && clients.value.length === 0) fetchClients()
  if (newTab === 'access' && accessList.value.length === 0) fetchAccessList()
})

onMounted(() => {
  fetchInterfaces()
  fetchSecurityProfiles()
  fetchClients()
  fetchAccessList()

  // Auto-refresh clients every 30 seconds
  refreshInterval = setInterval(() => {
    if (activeTab.value === 'clients') fetchClients()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>
