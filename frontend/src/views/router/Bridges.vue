<template>
  <div class="space-y-6">
    <!-- Bridges -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Bridges</h3>
        <button @click="showAddBridgeModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter un bridge
        </button>
      </div>

      <DataTable :columns="bridgeColumns" :data="bridges" :loading="loadingBridges" empty-message="Aucun bridge">
        <template #cell-name="{ row }">
          <span class="font-medium text-gray-900">{{ row.name }}</span>
        </template>

        <template #cell-vlan_filtering="{ row }">
          <span :class="[row.vlan_filtering ? 'badge-success' : 'badge-warning', 'badge']">
            {{ row.vlan_filtering ? 'Active' : 'Inactive' }}
          </span>
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
          <button
            @click="deleteBridge(row)"
            class="text-red-600 hover:text-red-800"
            :disabled="deletingBridge === row.id"
          >
            Supprimer
          </button>
        </template>
      </DataTable>
    </div>

    <!-- Bridge Ports -->
    <div class="card">
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Ports de Bridge</h3>
        <button @click="showAddPortModal = true" class="btn btn-primary text-sm">
          <PlusIcon class="w-4 h-4 mr-1" />
          Ajouter un port
        </button>
      </div>

      <DataTable :columns="portColumns" :data="bridgePorts" :loading="loadingPorts" empty-message="Aucun port de bridge">
        <template #cell-bridge="{ row }">
          <span class="badge badge-info">{{ row.bridge }}</span>
        </template>

        <template #cell-interface="{ row }">
          <span class="font-medium text-gray-900">{{ row.interface }}</span>
        </template>

        <template #cell-hw="{ row }">
          <span :class="[row.hw ? 'badge-success' : 'badge-warning', 'badge']">
            {{ row.hw ? 'HW' : 'SW' }}
          </span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactive' : 'Active' }}
          </span>
        </template>

        <template #actions="{ row }">
          <button
            @click="deletePort(row)"
            class="text-red-600 hover:text-red-800"
            :disabled="deletingPort === row.id"
          >
            Retirer
          </button>
        </template>
      </DataTable>
    </div>

    <!-- Bridge VLANs -->
    <div class="card">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">VLANs de Bridge</h3>
      </div>

      <DataTable :columns="vlanColumns" :data="bridgeVlans" :loading="loadingVlans" empty-message="Aucun VLAN configure">
        <template #cell-bridge="{ row }">
          <span class="badge badge-info">{{ row.bridge }}</span>
        </template>

        <template #cell-vlan_ids="{ row }">
          <span class="font-medium text-gray-900">{{ row.vlan_ids }}</span>
        </template>

        <template #cell-tagged="{ row }">
          <span v-if="row.tagged" class="text-sm text-gray-600">{{ row.tagged }}</span>
          <span v-else class="text-gray-400">-</span>
        </template>

        <template #cell-untagged="{ row }">
          <span v-if="row.untagged" class="text-sm text-gray-600">{{ row.untagged }}</span>
          <span v-else class="text-gray-400">-</span>
        </template>

        <template #cell-disabled="{ row }">
          <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">
            {{ row.disabled ? 'Desactive' : 'Active' }}
          </span>
        </template>
      </DataTable>
    </div>

    <!-- Add Bridge Modal -->
    <Modal v-model="showAddBridgeModal" title="Ajouter un bridge" size="sm">
      <form @submit.prevent="addBridge" class="space-y-4">
        <div>
          <label class="label">Nom *</label>
          <input v-model="bridgeForm.name" type="text" class="input" placeholder="bridge1" required />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="bridgeForm.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
        <div class="flex items-center">
          <input type="checkbox" v-model="bridgeForm.vlan_filtering" id="vlan-filtering" class="mr-2" />
          <label for="vlan-filtering">Activer le filtrage VLAN</label>
        </div>
      </form>

      <template #footer>
        <button @click="addBridge" class="btn btn-primary" :disabled="addingBridge">
          {{ addingBridge ? 'Ajout...' : 'Ajouter' }}
        </button>
        <button @click="showAddBridgeModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add Port Modal -->
    <Modal v-model="showAddPortModal" title="Ajouter un port au bridge" size="sm">
      <form @submit.prevent="addPort" class="space-y-4">
        <div>
          <label class="label">Bridge *</label>
          <select v-model="portForm.bridge" class="input" required>
            <option value="" disabled>Selectionner un bridge</option>
            <option v-for="br in bridges" :key="br.id" :value="br.name">{{ br.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Interface *</label>
          <input v-model="portForm.interface" type="text" class="input" placeholder="ether2" required />
        </div>
        <div>
          <label class="label">PVID</label>
          <input v-model.number="portForm.pvid" type="number" class="input" min="1" max="4094" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="portForm.comment" type="text" class="input" placeholder="Optionnel" />
        </div>
      </form>

      <template #footer>
        <button @click="addPort" class="btn btn-primary" :disabled="addingPort">
          {{ addingPort ? 'Ajout...' : 'Ajouter' }}
        </button>
        <button @click="showAddPortModal = false" class="btn btn-secondary mr-3">Annuler</button>
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

const bridges = ref([])
const bridgePorts = ref([])
const bridgeVlans = ref([])
const loadingBridges = ref(true)
const loadingPorts = ref(true)
const loadingVlans = ref(true)
const deletingBridge = ref(null)
const deletingPort = ref(null)
const showAddBridgeModal = ref(false)
const showAddPortModal = ref(false)
const addingBridge = ref(false)
const addingPort = ref(false)

const bridgeForm = reactive({
  name: '',
  comment: '',
  vlan_filtering: false
})

const portForm = reactive({
  bridge: '',
  interface: '',
  pvid: 1,
  comment: ''
})

const bridgeColumns = [
  { key: 'name', label: 'Nom' },
  { key: 'mac_address', label: 'MAC' },
  { key: 'mtu', label: 'MTU' },
  { key: 'protocol_mode', label: 'Mode' },
  { key: 'vlan_filtering', label: 'VLAN Filtering' },
  { key: 'running', label: 'Etat' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
]

const portColumns = [
  { key: 'bridge', label: 'Bridge' },
  { key: 'interface', label: 'Interface' },
  { key: 'pvid', label: 'PVID' },
  { key: 'hw', label: 'Offload' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
]

const vlanColumns = [
  { key: 'bridge', label: 'Bridge' },
  { key: 'vlan_ids', label: 'VLAN IDs' },
  { key: 'tagged', label: 'Tagged' },
  { key: 'untagged', label: 'Untagged' },
  { key: 'disabled', label: 'Status' }
]

async function fetchBridges() {
  loadingBridges.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/bridges`)
    bridges.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des bridges')
  } finally {
    loadingBridges.value = false
  }
}

async function fetchPorts() {
  loadingPorts.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/bridges/ports`)
    bridgePorts.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des ports')
  } finally {
    loadingPorts.value = false
  }
}

async function fetchVlans() {
  loadingVlans.value = true
  try {
    const response = await api.get(`/routers/${route.params.id}/bridges/vlans`)
    bridgeVlans.value = response.data
  } catch (error) {
    notifications.error('Erreur lors du chargement des VLANs')
  } finally {
    loadingVlans.value = false
  }
}

async function addBridge() {
  addingBridge.value = true
  try {
    await api.post(`/routers/${route.params.id}/bridges`, null, {
      params: {
        name: bridgeForm.name,
        comment: bridgeForm.comment,
        vlan_filtering: bridgeForm.vlan_filtering
      }
    })
    notifications.success('Bridge ajoute')
    showAddBridgeModal.value = false
    bridgeForm.name = ''
    bridgeForm.comment = ''
    bridgeForm.vlan_filtering = false
    await fetchBridges()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout du bridge')
  } finally {
    addingBridge.value = false
  }
}

async function addPort() {
  addingPort.value = true
  try {
    await api.post(`/routers/${route.params.id}/bridges/ports`, null, {
      params: {
        bridge: portForm.bridge,
        interface: portForm.interface,
        pvid: portForm.pvid,
        comment: portForm.comment
      }
    })
    notifications.success('Port ajoute au bridge')
    showAddPortModal.value = false
    portForm.bridge = ''
    portForm.interface = ''
    portForm.pvid = 1
    portForm.comment = ''
    await fetchPorts()
  } catch (error) {
    notifications.error('Erreur lors de l\'ajout du port')
  } finally {
    addingPort.value = false
  }
}

async function deleteBridge(bridge) {
  if (!confirm(`Supprimer le bridge "${bridge.name}" ?`)) return
  deletingBridge.value = bridge.id
  try {
    await api.delete(`/routers/${route.params.id}/bridges/${bridge.id}`)
    notifications.success('Bridge supprime')
    await fetchBridges()
    await fetchPorts()
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deletingBridge.value = null
  }
}

async function deletePort(port) {
  if (!confirm(`Retirer l'interface "${port.interface}" du bridge ?`)) return
  deletingPort.value = port.id
  try {
    await api.delete(`/routers/${route.params.id}/bridges/ports/${port.id}`)
    notifications.success('Port retire')
    await fetchPorts()
  } catch (error) {
    notifications.error('Erreur lors du retrait du port')
  } finally {
    deletingPort.value = null
  }
}

onMounted(() => {
  fetchBridges()
  fetchPorts()
  fetchVlans()
})
</script>
