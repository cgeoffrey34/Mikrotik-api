<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Routeurs</h1>
        <p class="text-gray-600">Gestion de vos routeurs Mikrotik</p>
      </div>
      <button @click="showAddModal = true" class="btn btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        Ajouter un routeur
      </button>
    </div>

    <!-- Routers grid -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-flex items-center">
        <svg class="animate-spin h-8 w-8 text-mikrotik-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        Chargement des routeurs...
      </div>
    </div>

    <div v-else-if="routers.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="router in routers" :key="router.id" class="card overflow-hidden">
        <div :class="[router.is_online ? 'bg-green-500' : 'bg-red-500', 'h-1']"></div>
        <div class="p-6">
          <div class="flex items-start justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ router.name }}</h3>
              <p class="text-sm text-gray-500">{{ router.ip_address }}:{{ router.api_port }}</p>
            </div>
            <span :class="[router.is_online ? 'badge-success' : 'badge-danger', 'badge']">
              {{ router.is_online ? 'En ligne' : 'Hors ligne' }}
            </span>
          </div>

          <div class="mt-4 space-y-2">
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-24">Modele:</span>
              <span class="text-gray-900">{{ router.model || 'N/A' }}</span>
            </div>
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-24">Version:</span>
              <span class="text-gray-900">{{ router.ros_version || 'N/A' }}</span>
            </div>
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-24">Emplacement:</span>
              <span class="text-gray-900">{{ router.location || 'Non defini' }}</span>
            </div>
          </div>

          <div class="mt-6 flex items-center justify-between">
            <router-link :to="`/routers/${router.id}`" class="btn btn-primary text-sm">
              Gerer
            </router-link>
            <div class="flex space-x-2">
              <button @click="testRouter(router.id)" class="p-2 text-gray-400 hover:text-mikrotik-600" title="Tester">
                <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': testingId === router.id }" />
              </button>
              <button @click="editRouter(router)" class="p-2 text-gray-400 hover:text-mikrotik-600" title="Modifier">
                <PencilIcon class="w-5 h-5" />
              </button>
              <button @click="confirmDelete(router)" class="p-2 text-gray-400 hover:text-red-600" title="Supprimer">
                <TrashIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card p-12 text-center">
      <ServerStackIcon class="h-16 w-16 mx-auto text-gray-300 mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">Aucun routeur enregistre</h3>
      <p class="text-gray-500 mb-6">Commencez par ajouter votre premier routeur Mikrotik</p>
      <button @click="showAddModal = true" class="btn btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        Ajouter un routeur
      </button>
    </div>

    <!-- Add/Edit Modal -->
    <Modal v-model="showAddModal" :title="editingRouter ? 'Modifier le routeur' : 'Ajouter un routeur'" size="md">
      <form @submit.prevent="saveRouter" class="space-y-4">
        <div>
          <label class="label">Nom</label>
          <input v-model="form.name" type="text" class="input" placeholder="Ex: Routeur Principal" required />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Adresse IP</label>
            <input v-model="form.ip_address" type="text" class="input" placeholder="192.168.1.1" required />
          </div>
          <div>
            <label class="label">Port API</label>
            <input v-model.number="form.api_port" type="number" class="input" placeholder="8728" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Utilisateur</label>
            <input v-model="form.username" type="text" class="input" placeholder="admin" required />
          </div>
          <div>
            <label class="label">Mot de passe</label>
            <input v-model="form.password" type="password" class="input" :placeholder="editingRouter ? '(inchange)' : 'Mot de passe'" :required="!editingRouter" />
          </div>
        </div>

        <div>
          <label class="label">Emplacement</label>
          <input v-model="form.location" type="text" class="input" placeholder="Ex: Salle serveur" />
        </div>

        <div>
          <label class="label">Notes</label>
          <textarea v-model="form.notes" rows="3" class="input" placeholder="Notes additionnelles..."></textarea>
        </div>

        <div class="flex items-center">
          <input v-model="form.use_ssl" type="checkbox" id="use_ssl" class="mr-2" />
          <label for="use_ssl" class="text-sm text-gray-700">Utiliser SSL (port 8729)</label>
        </div>
      </form>

      <template #footer>
        <button @click="saveRouter" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Enregistrement...' : (editingRouter ? 'Modifier' : 'Ajouter') }}
        </button>
        <button @click="closeModal" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Delete confirmation -->
    <Modal v-model="showDeleteModal" title="Confirmer la suppression" size="sm">
      <p class="text-gray-600">
        Etes-vous sur de vouloir supprimer le routeur <strong>{{ routerToDelete?.name }}</strong> ?
        Cette action est irreversible.
      </p>

      <template #footer>
        <button @click="deleteRouterConfirmed" class="btn btn-danger" :disabled="deleting">
          {{ deleting ? 'Suppression...' : 'Supprimer' }}
        </button>
        <button @click="showDeleteModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoutersStore } from '../stores/routers'
import { useNotificationStore } from '../stores/notifications'
import Modal from '../components/Modal.vue'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ArrowPathIcon,
  ServerStackIcon
} from '@heroicons/vue/24/outline'

const store = useRoutersStore()
const notifications = useNotificationStore()
const { routers, loading } = storeToRefs(store)

const showAddModal = ref(false)
const showDeleteModal = ref(false)
const editingRouter = ref(null)
const routerToDelete = ref(null)
const testingId = ref(null)
const saving = ref(false)
const deleting = ref(false)

const form = reactive({
  name: '',
  ip_address: '',
  api_port: 8728,
  username: 'admin',
  password: '',
  location: '',
  notes: '',
  use_ssl: false
})

function resetForm() {
  form.name = ''
  form.ip_address = ''
  form.api_port = 8728
  form.username = 'admin'
  form.password = ''
  form.location = ''
  form.notes = ''
  form.use_ssl = false
}

function editRouter(router) {
  editingRouter.value = router
  form.name = router.name
  form.ip_address = router.ip_address
  form.api_port = router.api_port
  form.username = router.username
  form.password = ''
  form.location = router.location || ''
  form.notes = router.notes || ''
  form.use_ssl = router.use_ssl
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  editingRouter.value = null
  resetForm()
}

async function saveRouter() {
  saving.value = true
  try {
    const data = { ...form }
    if (editingRouter.value && !data.password) {
      delete data.password
    }

    if (editingRouter.value) {
      await store.updateRouter(editingRouter.value.id, data)
      notifications.success('Routeur mis a jour avec succes')
    } else {
      await store.addRouter(data)
      notifications.success('Routeur ajoute avec succes')
    }
    closeModal()
  } catch (error) {
    notifications.error(error.response?.data?.detail || 'Erreur lors de l\'enregistrement')
  } finally {
    saving.value = false
  }
}

function confirmDelete(router) {
  routerToDelete.value = router
  showDeleteModal.value = true
}

async function deleteRouterConfirmed() {
  deleting.value = true
  try {
    await store.deleteRouter(routerToDelete.value.id)
    notifications.success('Routeur supprime avec succes')
    showDeleteModal.value = false
    routerToDelete.value = null
  } catch (error) {
    notifications.error('Erreur lors de la suppression')
  } finally {
    deleting.value = false
  }
}

async function testRouter(id) {
  testingId.value = id
  try {
    const result = await store.testConnection(id)
    if (result.success) {
      notifications.success('Connexion reussie')
    } else {
      notifications.error(result.error || 'Connexion echouee')
    }
  } catch (error) {
    notifications.error('Erreur lors du test de connexion')
  } finally {
    testingId.value = null
  }
}

onMounted(() => {
  store.fetchRouters()
})
</script>
