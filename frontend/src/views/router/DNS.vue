<template>
  <div class="space-y-6">
    <!-- DNS Settings -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Parametres DNS</h3>
        <button @click="flushCache" class="btn btn-secondary text-sm" :disabled="flushing">
          {{ flushing ? 'Vidage...' : 'Vider le cache' }}
        </button>
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
        <dl class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <dt class="text-sm text-gray-500">Serveurs DNS</dt>
            <dd class="text-gray-900 font-medium">{{ settings.servers || 'Non configure' }}</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">Serveurs dynamiques</dt>
            <dd class="text-gray-900">{{ settings.dynamic_servers || 'Aucun' }}</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">Requetes distantes</dt>
            <dd>
              <span :class="[settings.allow_remote_requests ? 'badge-success' : 'badge-warning', 'badge']">
                {{ settings.allow_remote_requests ? 'Autorisees' : 'Refusees' }}
              </span>
            </dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">Taille du cache</dt>
            <dd class="text-gray-900">{{ settings.cache_size }} KiB</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">Cache utilise</dt>
            <dd class="text-gray-900">{{ settings.cache_used }} KiB</dd>
          </div>
          <div>
            <dt class="text-sm text-gray-500">TTL max cache</dt>
            <dd class="text-gray-900">{{ settings.cache_max_ttl || 'Default' }}</dd>
          </div>
        </dl>
      </div>
    </div>

    <!-- DNS Entries -->
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
const settings = ref(null)
const loading = ref(true)
const loadingSettings = ref(true)
const deleting = ref(null)
const toggling = ref(null)
const flushing = ref(false)
const showAddModal = ref(false)
const adding = ref(false)

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

const columns = [
  { key: 'name', label: 'Nom' },
  { key: 'type', label: 'Type' },
  { key: 'value', label: 'Valeur' },
  { key: 'ttl', label: 'TTL' },
  { key: 'disabled', label: 'Status' },
  { key: 'dynamic', label: 'Source' },
  { key: 'comment', label: 'Commentaire' }
]

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

async function fetchSettings() {
  loadingSettings.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/dns/settings`)
    settings.value = response.data
  } catch (error) {
    // DNS settings might not be available on all routers
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

async function flushCache() {
  flushing.value = true
  try {
    await api.post(`/routers/${route.params.id}/dns/cache/flush`)
    notifications.success('Cache DNS vide')
    await fetchSettings()
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

onMounted(() => {
  fetchSettings()
  fetchEntries()
})
</script>
