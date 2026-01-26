<template>
  <div class="space-y-6">
    <!-- Filter rules -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Regles de filtrage</h3>
        <button @click="showFilterModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter une regle
        </button>
      </div>

      <DataTable :columns="filterColumns" :data="filterRules" :loading="loadingFilter" empty-message="Aucune regle de filtrage">
        <template #cell-chain="{ row }">
          <span class="badge badge-info">{{ row.chain }}</span>
        </template>

        <template #cell-action="{ row }">
          <span :class="[getActionClass(row.action), 'badge']">
            {{ row.action }}
          </span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactivee' : 'Active' }}
          </span>
        </template>

        <template #cell-stats="{ row }">
          <div class="text-sm text-gray-500">
            {{ formatNumber(row.packets) }} paquets / {{ formatBytes(row.bytes) }}
          </div>
        </template>

        <template #actions="{ row }">
          <div class="flex items-center gap-2">
            <button
              @click="toggleFilterRule(row)"
              :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
              :disabled="toggling === row.id"
            >
              {{ row.disabled ? 'Activer' : 'Desactiver' }}
            </button>
            <button
              @click="deleteFilterRule(row)"
              class="text-red-600 hover:text-red-800"
              :disabled="deleting === row.id"
            >
              Supprimer
            </button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- NAT rules -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Regles NAT</h3>
        <button @click="showNatModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter une regle NAT
        </button>
      </div>

      <DataTable :columns="natColumns" :data="natRules" :loading="loadingNat" empty-message="Aucune regle NAT">
        <template #cell-chain="{ row }">
          <span class="badge badge-info">{{ row.chain }}</span>
        </template>

        <template #cell-action="{ row }">
          <span :class="[getNatActionClass(row.action), 'badge']">
            {{ row.action }}
          </span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactivee' : 'Active' }}
          </span>
        </template>

        <template #cell-stats="{ row }">
          <div class="text-sm text-gray-500">
            {{ formatNumber(row.packets) }} paquets / {{ formatBytes(row.bytes) }}
          </div>
        </template>

        <template #actions="{ row }">
          <div class="flex items-center gap-2">
            <button
              @click="toggleNatRule(row)"
              :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']"
              :disabled="togglingNat === row.id"
            >
              {{ row.disabled ? 'Activer' : 'Desactiver' }}
            </button>
            <button
              @click="deleteNatRule(row)"
              class="text-red-600 hover:text-red-800"
              :disabled="deletingNat === row.id"
            >
              Supprimer
            </button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Add Filter Rule Modal -->
    <Modal v-model="showFilterModal" title="Ajouter une regle de filtrage" size="lg">
      <form @submit.prevent="addFilterRule" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Chaine *</label>
            <select v-model="filterForm.chain" class="input" required>
              <option value="input">input</option>
              <option value="forward">forward</option>
              <option value="output">output</option>
            </select>
          </div>
          <div>
            <label class="label">Action *</label>
            <select v-model="filterForm.action" class="input" required>
              <option value="accept">accept</option>
              <option value="drop">drop</option>
              <option value="reject">reject</option>
              <option value="log">log</option>
              <option value="jump">jump</option>
              <option value="passthrough">passthrough</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Adresse source</label>
            <input v-model="filterForm.src_address" type="text" class="input" placeholder="0.0.0.0/0" />
          </div>
          <div>
            <label class="label">Adresse destination</label>
            <input v-model="filterForm.dst_address" type="text" class="input" placeholder="0.0.0.0/0" />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Protocole</label>
            <select v-model="filterForm.protocol" class="input">
              <option value="">Tous</option>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
              <option value="icmp">ICMP</option>
              <option value="gre">GRE</option>
            </select>
          </div>
          <div>
            <label class="label">Port source</label>
            <input v-model="filterForm.src_port" type="text" class="input" placeholder="1-65535" />
          </div>
          <div>
            <label class="label">Port destination</label>
            <input v-model="filterForm.dst_port" type="text" class="input" placeholder="80,443" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Interface entree</label>
            <input v-model="filterForm.in_interface" type="text" class="input" placeholder="ether1" />
          </div>
          <div>
            <label class="label">Interface sortie</label>
            <input v-model="filterForm.out_interface" type="text" class="input" placeholder="ether2" />
          </div>
        </div>

        <div>
          <label class="label">Etat de connexion</label>
          <input v-model="filterForm.connection_state" type="text" class="input" placeholder="established,related" />
        </div>

        <div>
          <label class="label">Commentaire</label>
          <input v-model="filterForm.comment" type="text" class="input" placeholder="Description de la regle" />
        </div>

        <div class="flex items-center">
          <input type="checkbox" v-model="filterForm.disabled" id="filter-disabled" class="mr-2" />
          <label for="filter-disabled">Creer desactivee</label>
        </div>
      </form>

      <template #footer>
        <button @click="addFilterRule" class="btn btn-primary" :disabled="addingFilter">
          {{ addingFilter ? 'Ajout...' : 'Ajouter' }}
        </button>
        <button @click="showFilterModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add NAT Rule Modal -->
    <Modal v-model="showNatModal" title="Ajouter une regle NAT" size="lg">
      <form @submit.prevent="addNatRuleSubmit" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Chaine *</label>
            <select v-model="natForm.chain" class="input" required>
              <option value="srcnat">srcnat</option>
              <option value="dstnat">dstnat</option>
            </select>
          </div>
          <div>
            <label class="label">Action *</label>
            <select v-model="natForm.action" class="input" required>
              <option value="masquerade">masquerade</option>
              <option value="src-nat">src-nat</option>
              <option value="dst-nat">dst-nat</option>
              <option value="redirect">redirect</option>
              <option value="netmap">netmap</option>
              <option value="accept">accept</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Adresse source</label>
            <input v-model="natForm.src_address" type="text" class="input" placeholder="192.168.1.0/24" />
          </div>
          <div>
            <label class="label">Adresse destination</label>
            <input v-model="natForm.dst_address" type="text" class="input" placeholder="0.0.0.0/0" />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Protocole</label>
            <select v-model="natForm.protocol" class="input">
              <option value="">Tous</option>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </div>
          <div>
            <label class="label">Port source</label>
            <input v-model="natForm.src_port" type="text" class="input" placeholder="1-65535" />
          </div>
          <div>
            <label class="label">Port destination</label>
            <input v-model="natForm.dst_port" type="text" class="input" placeholder="80" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Vers adresse(s)</label>
            <input v-model="natForm.to_addresses" type="text" class="input" placeholder="192.168.1.100" />
          </div>
          <div>
            <label class="label">Vers port(s)</label>
            <input v-model="natForm.to_ports" type="text" class="input" placeholder="8080" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Interface entree</label>
            <input v-model="natForm.in_interface" type="text" class="input" placeholder="ether1-wan" />
          </div>
          <div>
            <label class="label">Interface sortie</label>
            <input v-model="natForm.out_interface" type="text" class="input" placeholder="ether2-lan" />
          </div>
        </div>

        <div>
          <label class="label">Commentaire</label>
          <input v-model="natForm.comment" type="text" class="input" placeholder="Description de la regle NAT" />
        </div>

        <div class="flex items-center">
          <input type="checkbox" v-model="natForm.disabled" id="nat-disabled" class="mr-2" />
          <label for="nat-disabled">Creer desactivee</label>
        </div>
      </form>

      <template #footer>
        <button @click="addNatRuleSubmit" class="btn btn-primary" :disabled="addingNat">
          {{ addingNat ? 'Ajout...' : 'Ajouter' }}
        </button>
        <button @click="showNatModal = false" class="btn btn-secondary mr-3">Annuler</button>
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

const filterRules = ref([])
const natRules = ref([])
const loadingFilter = ref(true)
const loadingNat = ref(true)
const toggling = ref(null)
const togglingNat = ref(null)
const deleting = ref(null)
const deletingNat = ref(null)
const showFilterModal = ref(false)
const showNatModal = ref(false)
const addingFilter = ref(false)
const addingNat = ref(false)

const filterForm = reactive({
  chain: 'forward',
  action: 'accept',
  src_address: '',
  dst_address: '',
  protocol: '',
  src_port: '',
  dst_port: '',
  in_interface: '',
  out_interface: '',
  connection_state: '',
  comment: '',
  disabled: false
})

const natForm = reactive({
  chain: 'srcnat',
  action: 'masquerade',
  src_address: '',
  dst_address: '',
  protocol: '',
  src_port: '',
  dst_port: '',
  to_addresses: '',
  to_ports: '',
  in_interface: '',
  out_interface: '',
  comment: '',
  disabled: false
})

const filterColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Protocole' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'dst_port', label: 'Port' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Statistiques' },
  { key: 'comment', label: 'Commentaire' }
]

const natColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Protocole' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'to_addresses', label: 'Vers IP' },
  { key: 'to_ports', label: 'Vers Port' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Statistiques' },
  { key: 'comment', label: 'Commentaire' }
]

function getActionClass(action) {
  const classes = {
    'accept': 'badge-success',
    'drop': 'badge-danger',
    'reject': 'badge-danger',
    'log': 'badge-warning',
    'jump': 'badge-info'
  }
  return classes[action] || 'badge-info'
}

function getNatActionClass(action) {
  const classes = {
    'masquerade': 'badge-success',
    'src-nat': 'badge-info',
    'dst-nat': 'badge-purple',
    'redirect': 'badge-warning',
    'accept': 'badge-success'
  }
  return classes[action] || 'badge-info'
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('fr-FR')
}

async function fetchFilterRules() {
  loadingFilter.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/firewall/filter`)
    filterRules.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des regles de filtrage')
  } finally {
    loadingFilter.value = false
  }
}

async function fetchNatRules() {
  loadingNat.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/firewall/nat`)
    natRules.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des regles NAT')
  } finally {
    loadingNat.value = false
  }
}

async function toggleFilterRule(rule) {
  toggling.value = rule.id
  try {
    await api.post(`/routers/${route.params.id}/firewall/filter/${rule.id}/toggle`, null, {
      params: { enable: rule.disabled }
    })
    notifications.success(`Regle ${rule.disabled ? 'activee' : 'desactivee'}`)
    await fetchFilterRules()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    toggling.value = null
  }
}

async function toggleNatRule(rule) {
  togglingNat.value = rule.id
  try {
    await api.post(`/routers/${route.params.id}/firewall/nat/${rule.id}/toggle`, null, {
      params: { enable: rule.disabled }
    })
    notifications.success(`Regle NAT ${rule.disabled ? 'activee' : 'desactivee'}`)
    await fetchNatRules()
  } catch (error) {
    notifications.error('Erreur lors du changement d\'etat')
  } finally {
    togglingNat.value = null
  }
}

async function deleteFilterRule(rule) {
  if (!confirm('Supprimer cette regle de filtrage ?')) return
  deleting.value = rule.id
  try {
    await api.delete(`/routers/${route.params.id}/firewall/filter/${rule.id}`)
    notifications.success('Regle supprimee')
    await fetchFilterRules()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deleting.value = null
  }
}

async function deleteNatRule(rule) {
  if (!confirm('Supprimer cette regle NAT ?')) return
  deletingNat.value = rule.id
  try {
    await api.delete(`/routers/${route.params.id}/firewall/nat/${rule.id}`)
    notifications.success('Regle NAT supprimee')
    await fetchNatRules()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deletingNat.value = null
  }
}

async function addFilterRule() {
  addingFilter.value = true
  try {
    const payload = {
      chain: filterForm.chain,
      action: filterForm.action,
      disabled: filterForm.disabled
    }
    if (filterForm.src_address) payload.src_address = filterForm.src_address
    if (filterForm.dst_address) payload.dst_address = filterForm.dst_address
    if (filterForm.protocol) payload.protocol = filterForm.protocol
    if (filterForm.src_port) payload.src_port = filterForm.src_port
    if (filterForm.dst_port) payload.dst_port = filterForm.dst_port
    if (filterForm.in_interface) payload.in_interface = filterForm.in_interface
    if (filterForm.out_interface) payload.out_interface = filterForm.out_interface
    if (filterForm.connection_state) payload.connection_state = filterForm.connection_state
    if (filterForm.comment) payload.comment = filterForm.comment

    await api.post(`/routers/${route.params.id}/firewall/filter`, payload)
    notifications.success('Regle de filtrage ajoutee')
    showFilterModal.value = false
    resetFilterForm()
    await fetchFilterRules()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout de la regle')
  } finally {
    addingFilter.value = false
  }
}

async function addNatRuleSubmit() {
  addingNat.value = true
  try {
    const payload = {
      chain: natForm.chain,
      action: natForm.action,
      disabled: natForm.disabled
    }
    if (natForm.src_address) payload.src_address = natForm.src_address
    if (natForm.dst_address) payload.dst_address = natForm.dst_address
    if (natForm.protocol) payload.protocol = natForm.protocol
    if (natForm.src_port) payload.src_port = natForm.src_port
    if (natForm.dst_port) payload.dst_port = natForm.dst_port
    if (natForm.to_addresses) payload.to_addresses = natForm.to_addresses
    if (natForm.to_ports) payload.to_ports = natForm.to_ports
    if (natForm.in_interface) payload.in_interface = natForm.in_interface
    if (natForm.out_interface) payload.out_interface = natForm.out_interface
    if (natForm.comment) payload.comment = natForm.comment

    await api.post(`/routers/${route.params.id}/firewall/nat`, payload)
    notifications.success('Regle NAT ajoutee')
    showNatModal.value = false
    resetNatForm()
    await fetchNatRules()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout de la regle NAT')
  } finally {
    addingNat.value = false
  }
}

function resetFilterForm() {
  filterForm.chain = 'forward'
  filterForm.action = 'accept'
  filterForm.src_address = ''
  filterForm.dst_address = ''
  filterForm.protocol = ''
  filterForm.src_port = ''
  filterForm.dst_port = ''
  filterForm.in_interface = ''
  filterForm.out_interface = ''
  filterForm.connection_state = ''
  filterForm.comment = ''
  filterForm.disabled = false
}

function resetNatForm() {
  natForm.chain = 'srcnat'
  natForm.action = 'masquerade'
  natForm.src_address = ''
  natForm.dst_address = ''
  natForm.protocol = ''
  natForm.src_port = ''
  natForm.dst_port = ''
  natForm.to_addresses = ''
  natForm.to_ports = ''
  natForm.in_interface = ''
  natForm.out_interface = ''
  natForm.comment = ''
  natForm.disabled = false
}

onMounted(() => {
  fetchFilterRules()
  fetchNatRules()
})
</script>
