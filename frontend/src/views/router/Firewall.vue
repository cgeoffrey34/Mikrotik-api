<template>
  <div class="space-y-6">
    <!-- Tab navigation -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-4 overflow-x-auto" aria-label="Firewall tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            activeTab === tab.key
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-3 px-4 border-b-2 font-medium text-sm cursor-pointer'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- ==================== FILTER ==================== -->
    <div v-if="activeTab === 'filter'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Regles de filtrage ({{ filteredFilterRules.length }}/{{ filterRules.length }})</h3>
          <button @click="showFilterModal = true" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" /> Ajouter une regle
          </button>
        </div>

        <!-- Filters -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50 flex flex-wrap gap-4" v-if="filterChains.length > 1 || filterActions.length > 1">
          <div v-if="filterChains.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Chaine:</span>
            <button @click="filterChainFilter = ''" :class="[!filterChainFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="chain in filterChains" :key="chain" @click="filterChainFilter = chain" :class="[filterChainFilter === chain ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ chain }}</button>
          </div>
          <div v-if="filterActions.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Action:</span>
            <button @click="filterActionFilter = ''" :class="[!filterActionFilter ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="action in filterActions" :key="action" @click="filterActionFilter = action" :class="[filterActionFilter === action ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ action }}</button>
          </div>
        </div>

        <DataTable :columns="filterColumns" :data="filteredFilterRules" :loading="loadingFilter" empty-message="Aucune regle de filtrage">
          <template #cell-chain="{ row }"><span class="badge badge-info">{{ row.chain }}</span></template>
          <template #cell-action="{ row }"><span :class="[getActionClass(row.action), 'badge']">{{ row.action }}</span></template>
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">{{ row.disabled ? 'Desactivee' : 'Active' }}</span>
          </template>
          <template #cell-stats="{ row }">
            <div class="text-sm text-gray-500">{{ formatNumber(row.packets) }} pkt / {{ formatBytes(row.bytes) }}</div>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="toggleRule('filter', row)" :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']" :disabled="togglingId === row.id">
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button @click="deleteRule('filter', row)" class="text-red-600 hover:text-red-800" :disabled="deletingId === row.id">Supprimer</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== NAT ==================== -->
    <div v-if="activeTab === 'nat'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Regles NAT ({{ filteredNatRules.length }}/{{ natRules.length }})</h3>
          <button @click="showNatModal = true" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" /> Ajouter une regle NAT
          </button>
        </div>

        <!-- Filters -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50 flex flex-wrap gap-4" v-if="natChains.length > 1 || natActions.length > 1">
          <div v-if="natChains.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Chaine:</span>
            <button @click="natChainFilter = ''" :class="[!natChainFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="chain in natChains" :key="chain" @click="natChainFilter = chain" :class="[natChainFilter === chain ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ chain }}</button>
          </div>
          <div v-if="natActions.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Action:</span>
            <button @click="natActionFilter = ''" :class="[!natActionFilter ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="action in natActions" :key="action" @click="natActionFilter = action" :class="[natActionFilter === action ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ action }}</button>
          </div>
        </div>

        <DataTable :columns="natColumns" :data="filteredNatRules" :loading="loadingNat" empty-message="Aucune regle NAT">
          <template #cell-chain="{ row }"><span class="badge badge-info">{{ row.chain }}</span></template>
          <template #cell-action="{ row }"><span :class="[getNatActionClass(row.action), 'badge']">{{ row.action }}</span></template>
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">{{ row.disabled ? 'Desactivee' : 'Active' }}</span>
          </template>
          <template #cell-stats="{ row }">
            <div class="text-sm text-gray-500">{{ formatNumber(row.packets) }} pkt / {{ formatBytes(row.bytes) }}</div>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="toggleRule('nat', row)" :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']" :disabled="togglingId === row.id">
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button @click="deleteRule('nat', row)" class="text-red-600 hover:text-red-800" :disabled="deletingId === row.id">Supprimer</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== MANGLE ==================== -->
    <div v-if="activeTab === 'mangle'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Regles Mangle ({{ filteredMangleRules.length }}/{{ mangleRules.length }})</h3>
          <button @click="showMangleModal = true" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" /> Ajouter une regle Mangle
          </button>
        </div>

        <!-- Filters -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50 flex flex-wrap gap-4" v-if="mangleChains.length > 1 || mangleActions.length > 1">
          <div v-if="mangleChains.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Chaine:</span>
            <button @click="mangleChainFilter = ''" :class="[!mangleChainFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="chain in mangleChains" :key="chain" @click="mangleChainFilter = chain" :class="[mangleChainFilter === chain ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ chain }}</button>
          </div>
          <div v-if="mangleActions.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Action:</span>
            <button @click="mangleActionFilter = ''" :class="[!mangleActionFilter ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="action in mangleActions" :key="action" @click="mangleActionFilter = action" :class="[mangleActionFilter === action ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ action }}</button>
          </div>
        </div>

        <DataTable :columns="mangleColumns" :data="filteredMangleRules" :loading="loadingMangle" empty-message="Aucune regle Mangle">
          <template #cell-chain="{ row }"><span class="badge badge-info">{{ row.chain }}</span></template>
          <template #cell-action="{ row }"><span :class="[getMangleActionClass(row.action), 'badge']">{{ row.action }}</span></template>
          <template #cell-marks="{ row }">
            <div class="text-xs space-y-0.5">
              <div v-if="row.new_packet_mark"><span class="text-gray-500">pkt:</span> {{ row.new_packet_mark }}</div>
              <div v-if="row.new_connection_mark"><span class="text-gray-500">conn:</span> {{ row.new_connection_mark }}</div>
              <div v-if="row.new_routing_mark"><span class="text-gray-500">route:</span> {{ row.new_routing_mark }}</div>
            </div>
          </template>
          <template #cell-passthrough="{ row }">
            <span :class="[row.passthrough ? 'badge-success' : 'badge-warning', 'badge']">{{ row.passthrough ? 'Oui' : 'Non' }}</span>
          </template>
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">{{ row.disabled ? 'Desactivee' : 'Active' }}</span>
          </template>
          <template #cell-stats="{ row }">
            <div class="text-sm text-gray-500">{{ formatNumber(row.packets) }} pkt / {{ formatBytes(row.bytes) }}</div>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="toggleRule('mangle', row)" :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']" :disabled="togglingId === row.id">
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button @click="deleteRule('mangle', row)" class="text-red-600 hover:text-red-800" :disabled="deletingId === row.id">Supprimer</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== RAW ==================== -->
    <div v-if="activeTab === 'raw'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Regles RAW ({{ filteredRawRules.length }}/{{ rawRules.length }})</h3>
          <button @click="showRawModal = true" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" /> Ajouter une regle RAW
          </button>
        </div>

        <!-- Filters -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50 flex flex-wrap gap-4" v-if="rawChains.length > 1 || rawActions.length > 1">
          <div v-if="rawChains.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Chaine:</span>
            <button @click="rawChainFilter = ''" :class="[!rawChainFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="chain in rawChains" :key="chain" @click="rawChainFilter = chain" :class="[rawChainFilter === chain ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ chain }}</button>
          </div>
          <div v-if="rawActions.length > 1" class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-600">Action:</span>
            <button @click="rawActionFilter = ''" :class="[!rawActionFilter ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">Toutes</button>
            <button v-for="action in rawActions" :key="action" @click="rawActionFilter = action" :class="[rawActionFilter === action ? 'bg-green-100 text-green-800 border-green-300' : 'bg-white text-gray-600 border-gray-300', 'px-2 py-1 rounded text-xs font-medium border']">{{ action }}</button>
          </div>
        </div>

        <DataTable :columns="rawColumns" :data="filteredRawRules" :loading="loadingRaw" empty-message="Aucune regle RAW">
          <template #cell-chain="{ row }"><span class="badge badge-info">{{ row.chain }}</span></template>
          <template #cell-action="{ row }"><span :class="[getRawActionClass(row.action), 'badge']">{{ row.action }}</span></template>
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">{{ row.disabled ? 'Desactivee' : 'Active' }}</span>
          </template>
          <template #cell-stats="{ row }">
            <div class="text-sm text-gray-500">{{ formatNumber(row.packets) }} pkt / {{ formatBytes(row.bytes) }}</div>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="toggleRule('raw', row)" :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']" :disabled="togglingId === row.id">
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button @click="deleteRule('raw', row)" class="text-red-600 hover:text-red-800" :disabled="deletingId === row.id">Supprimer</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== SERVICE PORTS ==================== -->
    <div v-if="activeTab === 'service-ports'">
      <div class="card">
        <div class="p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Service Ports (ALG)</h3>
        </div>
        <DataTable :columns="servicePortColumns" :data="servicePorts" :loading="loadingServicePorts" empty-message="Aucun service port">
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">{{ row.disabled ? 'Desactive' : 'Actif' }}</span>
          </template>
          <template #actions="{ row }">
            <button @click="toggleServicePort(row)" :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']" :disabled="togglingId === row.id">
              {{ row.disabled ? 'Activer' : 'Desactiver' }}
            </button>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== CONNECTIONS ==================== -->
    <div v-if="activeTab === 'connections'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Connexions actives ({{ connections.length }})</h3>
          <button @click="fetchConnections" class="btn btn-secondary text-sm">
            <ArrowPathIcon class="w-4 h-4 mr-1" /> Rafraichir
          </button>
        </div>
        <DataTable :columns="connectionColumns" :data="connections" :loading="loadingConnections" empty-message="Aucune connexion active">
          <template #cell-protocol="{ row }">
            <span class="badge badge-info">{{ row.protocol }}</span>
          </template>
          <template #cell-tcp_state="{ row }">
            <span v-if="row.tcp_state" :class="[getTcpStateClass(row.tcp_state), 'badge']">{{ row.tcp_state }}</span>
          </template>
          <template #cell-flags="{ row }">
            <div class="flex gap-1 flex-wrap">
              <span v-if="row.assured" class="badge badge-success text-xs">assured</span>
              <span v-if="row.fasttrack" class="badge badge-info text-xs">fasttrack</span>
              <span v-if="row.dying" class="badge badge-warning text-xs">dying</span>
            </div>
          </template>
          <template #cell-traffic="{ row }">
            <div class="text-xs text-gray-500">
              <div>TX: {{ formatBytes(row.orig_bytes) }} ({{ formatNumber(row.orig_packets) }} pkt)</div>
              <div>RX: {{ formatBytes(row.repl_bytes) }} ({{ formatNumber(row.repl_packets) }} pkt)</div>
            </div>
          </template>
          <template #actions="{ row }">
            <button @click="removeConnection(row)" class="text-red-600 hover:text-red-800" :disabled="deletingId === row.id">Supprimer</button>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== ADDRESS LISTS ==================== -->
    <div v-if="activeTab === 'address-lists'">
      <div class="card">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Address Lists</h3>
          <button @click="showAddressListModal = true" class="btn btn-primary text-sm">
            <PlusIcon class="w-4 h-4 mr-1" /> Ajouter une entree
          </button>
        </div>

        <!-- Filter by list name -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50" v-if="addressListNames.length > 1">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-sm font-medium text-gray-600">Liste :</span>
            <button
              @click="addressListFilter = ''"
              :class="[!addressListFilter ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-3 py-1 rounded-full text-xs font-medium border']"
            >
              Toutes ({{ addressListEntries.length }})
            </button>
            <button
              v-for="name in addressListNames"
              :key="name"
              @click="addressListFilter = name"
              :class="[addressListFilter === name ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-600 border-gray-300', 'px-3 py-1 rounded-full text-xs font-medium border']"
            >
              {{ name }} ({{ addressListEntries.filter(e => e.list === name).length }})
            </button>
          </div>
        </div>

        <DataTable :columns="addressListColumns" :data="filteredAddressListEntries" :loading="loadingAddressLists" empty-message="Aucune entree">
          <template #cell-list="{ row }"><span class="badge badge-info">{{ row.list }}</span></template>
          <template #cell-dynamic="{ row }">
            <span :class="[row.dynamic ? 'badge-purple' : 'badge-success', 'badge']">{{ row.dynamic ? 'Dynamique' : 'Statique' }}</span>
          </template>
          <template #cell-disabled="{ row }">
            <span :class="[row.disabled ? 'badge-warning' : 'badge-success', 'badge']">{{ row.disabled ? 'Desactivee' : 'Active' }}</span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-2">
              <button @click="toggleAddressListEntry(row)" :class="[row.disabled ? 'text-green-600 hover:text-green-800' : 'text-yellow-600 hover:text-yellow-800']" :disabled="togglingId === row.id">
                {{ row.disabled ? 'Activer' : 'Desactiver' }}
              </button>
              <button v-if="!row.dynamic" @click="deleteAddressListEntry(row)" class="text-red-600 hover:text-red-800" :disabled="deletingId === row.id">Supprimer</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- ==================== MODALS ==================== -->

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
              <option value="fasttrack-connection">fasttrack-connection</option>
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
        <button @click="addFilterRule" class="btn btn-primary" :disabled="adding">{{ adding ? 'Ajout...' : 'Ajouter' }}</button>
        <button @click="showFilterModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add NAT Rule Modal -->
    <Modal v-model="showNatModal" title="Ajouter une regle NAT" size="lg">
      <form @submit.prevent="addNatRule" class="space-y-4">
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
        <button @click="addNatRule" class="btn btn-primary" :disabled="adding">{{ adding ? 'Ajout...' : 'Ajouter' }}</button>
        <button @click="showNatModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add Mangle Rule Modal -->
    <Modal v-model="showMangleModal" title="Ajouter une regle Mangle" size="lg">
      <form @submit.prevent="addMangleRule" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Chaine *</label>
            <select v-model="mangleForm.chain" class="input" required>
              <option value="prerouting">prerouting</option>
              <option value="input">input</option>
              <option value="forward">forward</option>
              <option value="output">output</option>
              <option value="postrouting">postrouting</option>
            </select>
          </div>
          <div>
            <label class="label">Action *</label>
            <select v-model="mangleForm.action" class="input" required>
              <option value="mark-packet">mark-packet</option>
              <option value="mark-connection">mark-connection</option>
              <option value="mark-routing">mark-routing</option>
              <option value="change-mss">change-mss</option>
              <option value="change-ttl">change-ttl</option>
              <option value="change-dscp">change-dscp</option>
              <option value="accept">accept</option>
              <option value="drop">drop</option>
              <option value="log">log</option>
              <option value="passthrough">passthrough</option>
              <option value="jump">jump</option>
              <option value="return">return</option>
              <option value="fasttrack-connection">fasttrack-connection</option>
              <option value="sniff-tzsp">sniff-tzsp</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Adresse source</label>
            <input v-model="mangleForm.src_address" type="text" class="input" placeholder="0.0.0.0/0" />
          </div>
          <div>
            <label class="label">Adresse destination</label>
            <input v-model="mangleForm.dst_address" type="text" class="input" placeholder="0.0.0.0/0" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Protocole</label>
            <select v-model="mangleForm.protocol" class="input">
              <option value="">Tous</option>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
              <option value="icmp">ICMP</option>
              <option value="gre">GRE</option>
            </select>
          </div>
          <div>
            <label class="label">Port source</label>
            <input v-model="mangleForm.src_port" type="text" class="input" />
          </div>
          <div>
            <label class="label">Port destination</label>
            <input v-model="mangleForm.dst_port" type="text" class="input" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Interface entree</label>
            <input v-model="mangleForm.in_interface" type="text" class="input" />
          </div>
          <div>
            <label class="label">Interface sortie</label>
            <input v-model="mangleForm.out_interface" type="text" class="input" />
          </div>
        </div>
        <div>
          <label class="label">Etat de connexion</label>
          <input v-model="mangleForm.connection_state" type="text" class="input" placeholder="established,related,new" />
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">New Packet Mark</label>
            <input v-model="mangleForm.new_packet_mark" type="text" class="input" />
          </div>
          <div>
            <label class="label">New Connection Mark</label>
            <input v-model="mangleForm.new_connection_mark" type="text" class="input" />
          </div>
          <div>
            <label class="label">New Routing Mark</label>
            <input v-model="mangleForm.new_routing_mark" type="text" class="input" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Src Address List</label>
            <input v-model="mangleForm.src_address_list" type="text" class="input" />
          </div>
          <div>
            <label class="label">Dst Address List</label>
            <input v-model="mangleForm.dst_address_list" type="text" class="input" />
          </div>
        </div>
        <div class="flex items-center gap-6">
          <div class="flex items-center">
            <input type="checkbox" v-model="mangleForm.passthrough" id="mangle-passthrough" class="mr-2" />
            <label for="mangle-passthrough">Passthrough</label>
          </div>
          <div class="flex items-center">
            <input type="checkbox" v-model="mangleForm.disabled" id="mangle-disabled" class="mr-2" />
            <label for="mangle-disabled">Creer desactivee</label>
          </div>
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="mangleForm.comment" type="text" class="input" />
        </div>
      </form>
      <template #footer>
        <button @click="addMangleRule" class="btn btn-primary" :disabled="adding">{{ adding ? 'Ajout...' : 'Ajouter' }}</button>
        <button @click="showMangleModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add RAW Rule Modal -->
    <Modal v-model="showRawModal" title="Ajouter une regle RAW" size="lg">
      <form @submit.prevent="addRawRule" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Chaine *</label>
            <select v-model="rawForm.chain" class="input" required>
              <option value="prerouting">prerouting</option>
              <option value="output">output</option>
            </select>
          </div>
          <div>
            <label class="label">Action *</label>
            <select v-model="rawForm.action" class="input" required>
              <option value="accept">accept</option>
              <option value="drop">drop</option>
              <option value="notrack">notrack</option>
              <option value="log">log</option>
              <option value="jump">jump</option>
              <option value="return">return</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Adresse source</label>
            <input v-model="rawForm.src_address" type="text" class="input" placeholder="0.0.0.0/0" />
          </div>
          <div>
            <label class="label">Adresse destination</label>
            <input v-model="rawForm.dst_address" type="text" class="input" placeholder="0.0.0.0/0" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="label">Protocole</label>
            <select v-model="rawForm.protocol" class="input">
              <option value="">Tous</option>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
              <option value="icmp">ICMP</option>
            </select>
          </div>
          <div>
            <label class="label">Port source</label>
            <input v-model="rawForm.src_port" type="text" class="input" />
          </div>
          <div>
            <label class="label">Port destination</label>
            <input v-model="rawForm.dst_port" type="text" class="input" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Interface entree</label>
            <input v-model="rawForm.in_interface" type="text" class="input" />
          </div>
          <div>
            <label class="label">Interface sortie</label>
            <input v-model="rawForm.out_interface" type="text" class="input" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Src Address List</label>
            <input v-model="rawForm.src_address_list" type="text" class="input" />
          </div>
          <div>
            <label class="label">Dst Address List</label>
            <input v-model="rawForm.dst_address_list" type="text" class="input" />
          </div>
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="rawForm.comment" type="text" class="input" />
        </div>
        <div class="flex items-center">
          <input type="checkbox" v-model="rawForm.disabled" id="raw-disabled" class="mr-2" />
          <label for="raw-disabled">Creer desactivee</label>
        </div>
      </form>
      <template #footer>
        <button @click="addRawRule" class="btn btn-primary" :disabled="adding">{{ adding ? 'Ajout...' : 'Ajouter' }}</button>
        <button @click="showRawModal = false" class="btn btn-secondary mr-3">Annuler</button>
      </template>
    </Modal>

    <!-- Add Address List Entry Modal -->
    <Modal v-model="showAddressListModal" title="Ajouter une entree Address List" size="md">
      <form @submit.prevent="addAddressListEntry" class="space-y-4">
        <div>
          <label class="label">Nom de la liste *</label>
          <input v-model="addressListForm.list" type="text" class="input" required placeholder="blacklist" />
        </div>
        <div>
          <label class="label">Adresse *</label>
          <input v-model="addressListForm.address" type="text" class="input" required placeholder="192.168.1.0/24 ou domaine.com" />
        </div>
        <div>
          <label class="label">Timeout</label>
          <input v-model="addressListForm.timeout" type="text" class="input" placeholder="1d (vide = permanent)" />
        </div>
        <div>
          <label class="label">Commentaire</label>
          <input v-model="addressListForm.comment" type="text" class="input" />
        </div>
        <div class="flex items-center">
          <input type="checkbox" v-model="addressListForm.disabled" id="al-disabled" class="mr-2" />
          <label for="al-disabled">Creer desactivee</label>
        </div>
      </form>
      <template #footer>
        <button @click="addAddressListEntry" class="btn btn-primary" :disabled="adding">{{ adding ? 'Ajout...' : 'Ajouter' }}</button>
        <button @click="showAddressListModal = false" class="btn btn-secondary mr-3">Annuler</button>
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
import { PlusIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const notifications = useNotificationStore()
const routerId = route.params.id

// ==================== State ====================

const activeTab = ref('filter')
const tabs = [
  { key: 'filter', label: 'Filter' },
  { key: 'nat', label: 'NAT' },
  { key: 'mangle', label: 'Mangle' },
  { key: 'raw', label: 'RAW' },
  { key: 'service-ports', label: 'Service Ports' },
  { key: 'connections', label: 'Connections' },
  { key: 'address-lists', label: 'Address Lists' }
]

const filterRules = ref([])
const natRules = ref([])
const mangleRules = ref([])
const rawRules = ref([])
const servicePorts = ref([])
const connections = ref([])
const addressListEntries = ref([])
const addressListFilter = ref('')

// Chain and action filters for each section
const filterChainFilter = ref('')
const filterActionFilter = ref('')
const natChainFilter = ref('')
const natActionFilter = ref('')
const mangleChainFilter = ref('')
const mangleActionFilter = ref('')
const rawChainFilter = ref('')
const rawActionFilter = ref('')

const loadingFilter = ref(false)
const loadingNat = ref(false)
const loadingMangle = ref(false)
const loadingRaw = ref(false)
const loadingServicePorts = ref(false)
const loadingConnections = ref(false)
const loadingAddressLists = ref(false)

const togglingId = ref(null)
const deletingId = ref(null)
const adding = ref(false)

const showFilterModal = ref(false)
const showNatModal = ref(false)
const showMangleModal = ref(false)
const showRawModal = ref(false)
const showAddressListModal = ref(false)

// ==================== Forms ====================

const filterForm = reactive({
  chain: 'forward', action: 'accept', src_address: '', dst_address: '',
  protocol: '', src_port: '', dst_port: '', in_interface: '', out_interface: '',
  connection_state: '', comment: '', disabled: false
})

const natForm = reactive({
  chain: 'srcnat', action: 'masquerade', src_address: '', dst_address: '',
  protocol: '', src_port: '', dst_port: '', to_addresses: '', to_ports: '',
  in_interface: '', out_interface: '', comment: '', disabled: false
})

const mangleForm = reactive({
  chain: 'prerouting', action: 'mark-packet', src_address: '', dst_address: '',
  src_address_list: '', dst_address_list: '', protocol: '', src_port: '', dst_port: '',
  in_interface: '', out_interface: '', connection_state: '',
  new_packet_mark: '', new_connection_mark: '', new_routing_mark: '',
  passthrough: true, comment: '', disabled: false
})

const rawForm = reactive({
  chain: 'prerouting', action: 'drop', src_address: '', dst_address: '',
  src_address_list: '', dst_address_list: '', protocol: '', src_port: '', dst_port: '',
  in_interface: '', out_interface: '', connection_state: '', comment: '', disabled: false
})

const addressListForm = reactive({
  list: '', address: '', timeout: '', comment: '', disabled: false
})

// ==================== Columns ====================

const filterColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Proto' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'dst_port', label: 'Port' },
  { key: 'in_interface', label: 'In' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Stats' },
  { key: 'comment', label: 'Commentaire' }
]

const natColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Proto' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'to_addresses', label: 'Vers IP' },
  { key: 'to_ports', label: 'Vers Port' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Stats' },
  { key: 'comment', label: 'Commentaire' }
]

const mangleColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Proto' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'marks', label: 'Marks' },
  { key: 'passthrough', label: 'Passthrough' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Stats' },
  { key: 'comment', label: 'Commentaire' }
]

const rawColumns = [
  { key: 'chain', label: 'Chaine' },
  { key: 'action', label: 'Action' },
  { key: 'protocol', label: 'Proto' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'in_interface', label: 'In' },
  { key: 'disabled', label: 'Status' },
  { key: 'stats', label: 'Stats' },
  { key: 'comment', label: 'Commentaire' }
]

const servicePortColumns = [
  { key: 'name', label: 'Service' },
  { key: 'ports', label: 'Ports' },
  { key: 'disabled', label: 'Status' }
]

const connectionColumns = [
  { key: 'protocol', label: 'Proto' },
  { key: 'src_address', label: 'Source' },
  { key: 'dst_address', label: 'Destination' },
  { key: 'reply_src_address', label: 'Reply Src' },
  { key: 'reply_dst_address', label: 'Reply Dst' },
  { key: 'tcp_state', label: 'TCP State' },
  { key: 'timeout', label: 'Timeout' },
  { key: 'flags', label: 'Flags' },
  { key: 'traffic', label: 'Trafic' }
]

const addressListColumns = [
  { key: 'list', label: 'Liste' },
  { key: 'address', label: 'Adresse' },
  { key: 'timeout', label: 'Timeout' },
  { key: 'creation_time', label: 'Creation' },
  { key: 'dynamic', label: 'Type' },
  { key: 'disabled', label: 'Status' },
  { key: 'comment', label: 'Commentaire' }
]

// ==================== Computed ====================

// Filter rules - unique values and filtered data
const filterChains = computed(() => [...new Set(filterRules.value.map(r => r.chain).filter(Boolean))].sort())
const filterActions = computed(() => [...new Set(filterRules.value.map(r => r.action).filter(Boolean))].sort())
const filteredFilterRules = computed(() => {
  let rules = filterRules.value
  if (filterChainFilter.value) rules = rules.filter(r => r.chain === filterChainFilter.value)
  if (filterActionFilter.value) rules = rules.filter(r => r.action === filterActionFilter.value)
  return rules
})

// NAT rules - unique values and filtered data
const natChains = computed(() => [...new Set(natRules.value.map(r => r.chain).filter(Boolean))].sort())
const natActions = computed(() => [...new Set(natRules.value.map(r => r.action).filter(Boolean))].sort())
const filteredNatRules = computed(() => {
  let rules = natRules.value
  if (natChainFilter.value) rules = rules.filter(r => r.chain === natChainFilter.value)
  if (natActionFilter.value) rules = rules.filter(r => r.action === natActionFilter.value)
  return rules
})

// Mangle rules - unique values and filtered data
const mangleChains = computed(() => [...new Set(mangleRules.value.map(r => r.chain).filter(Boolean))].sort())
const mangleActions = computed(() => [...new Set(mangleRules.value.map(r => r.action).filter(Boolean))].sort())
const filteredMangleRules = computed(() => {
  let rules = mangleRules.value
  if (mangleChainFilter.value) rules = rules.filter(r => r.chain === mangleChainFilter.value)
  if (mangleActionFilter.value) rules = rules.filter(r => r.action === mangleActionFilter.value)
  return rules
})

// RAW rules - unique values and filtered data
const rawChains = computed(() => [...new Set(rawRules.value.map(r => r.chain).filter(Boolean))].sort())
const rawActions = computed(() => [...new Set(rawRules.value.map(r => r.action).filter(Boolean))].sort())
const filteredRawRules = computed(() => {
  let rules = rawRules.value
  if (rawChainFilter.value) rules = rules.filter(r => r.chain === rawChainFilter.value)
  if (rawActionFilter.value) rules = rules.filter(r => r.action === rawActionFilter.value)
  return rules
})

// Address list unique names
const addressListNames = computed(() => {
  const names = [...new Set(addressListEntries.value.map(e => e.list))]
  return names.sort()
})

const filteredAddressListEntries = computed(() => {
  if (!addressListFilter.value) return addressListEntries.value
  return addressListEntries.value.filter(e => e.list === addressListFilter.value)
})

// ==================== Helpers ====================

function getActionClass(action) {
  return { 'accept': 'badge-success', 'drop': 'badge-danger', 'reject': 'badge-danger', 'log': 'badge-warning', 'jump': 'badge-info', 'fasttrack-connection': 'badge-purple', 'passthrough': 'badge-info' }[action] || 'badge-info'
}
function getNatActionClass(action) {
  return { 'masquerade': 'badge-success', 'src-nat': 'badge-info', 'dst-nat': 'badge-purple', 'redirect': 'badge-warning', 'accept': 'badge-success', 'netmap': 'badge-info' }[action] || 'badge-info'
}
function getMangleActionClass(action) {
  return { 'mark-packet': 'badge-purple', 'mark-connection': 'badge-info', 'mark-routing': 'badge-teal', 'change-mss': 'badge-warning', 'accept': 'badge-success', 'drop': 'badge-danger', 'passthrough': 'badge-info', 'fasttrack-connection': 'badge-purple', 'log': 'badge-warning' }[action] || 'badge-info'
}
function getRawActionClass(action) {
  return { 'accept': 'badge-success', 'drop': 'badge-danger', 'notrack': 'badge-purple', 'log': 'badge-warning', 'jump': 'badge-info' }[action] || 'badge-info'
}
function getTcpStateClass(state) {
  return { 'established': 'badge-success', 'time-wait': 'badge-warning', 'close-wait': 'badge-warning', 'close': 'badge-danger' }[state] || 'badge-info'
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

function buildPayload(form, fields) {
  const payload = {}
  for (const key of fields) {
    const val = form[key]
    if (val !== '' && val !== null && val !== undefined) {
      payload[key] = val
    }
  }
  return payload
}

// ==================== Fetch ====================

async function fetchFilterRules() {
  loadingFilter.value = true
  try {
    const r = await api.get(`/routers/${routerId}/firewall/filter`)
    filterRules.value = r.data
  } catch { notifications.error('Erreur chargement regles de filtrage') }
  finally { loadingFilter.value = false }
}

async function fetchNatRules() {
  loadingNat.value = true
  try {
    const r = await api.get(`/routers/${routerId}/firewall/nat`)
    natRules.value = r.data
  } catch { notifications.error('Erreur chargement regles NAT') }
  finally { loadingNat.value = false }
}

async function fetchMangleRules() {
  loadingMangle.value = true
  try {
    const r = await api.get(`/routers/${routerId}/firewall/mangle`)
    mangleRules.value = r.data
  } catch { notifications.error('Erreur chargement regles Mangle') }
  finally { loadingMangle.value = false }
}

async function fetchRawRules() {
  loadingRaw.value = true
  try {
    const r = await api.get(`/routers/${routerId}/firewall/raw`)
    rawRules.value = r.data
  } catch { notifications.error('Erreur chargement regles RAW') }
  finally { loadingRaw.value = false }
}

async function fetchServicePorts() {
  loadingServicePorts.value = true
  try {
    const r = await api.get(`/routers/${routerId}/firewall/service-ports`)
    servicePorts.value = r.data
  } catch { notifications.error('Erreur chargement service ports') }
  finally { loadingServicePorts.value = false }
}

async function fetchConnections() {
  loadingConnections.value = true
  try {
    const r = await api.get(`/routers/${routerId}/firewall/connections`)
    connections.value = r.data
  } catch { notifications.error('Erreur chargement connexions') }
  finally { loadingConnections.value = false }
}

async function fetchAddressLists() {
  loadingAddressLists.value = true
  try {
    const r = await api.get(`/routers/${routerId}/firewall/address-lists`)
    addressListEntries.value = r.data
  } catch { notifications.error('Erreur chargement address lists') }
  finally { loadingAddressLists.value = false }
}

// ==================== Toggle / Delete generics ====================

async function toggleRule(section, rule) {
  togglingId.value = rule.id
  try {
    await api.post(`/routers/${routerId}/firewall/${section}/${rule.id}/toggle`, null, {
      params: { enable: rule.disabled }
    })
    notifications.success(`Regle ${rule.disabled ? 'activee' : 'desactivee'}`)
    await fetchTab(section)
  } catch { notifications.error('Erreur lors du changement d\'etat') }
  finally { togglingId.value = null }
}

async function deleteRule(section, rule) {
  if (!confirm('Supprimer cette regle ?')) return
  deletingId.value = rule.id
  try {
    await api.delete(`/routers/${routerId}/firewall/${section}/${rule.id}`)
    notifications.success('Regle supprimee')
    await fetchTab(section)
  } catch { notifications.error('Erreur lors de la suppression') }
  finally { deletingId.value = null }
}

async function toggleServicePort(port) {
  togglingId.value = port.id
  try {
    await api.post(`/routers/${routerId}/firewall/service-ports/${port.id}/toggle`, null, {
      params: { enable: port.disabled }
    })
    notifications.success(`Service port ${port.disabled ? 'active' : 'desactive'}`)
    await fetchServicePorts()
  } catch { notifications.error('Erreur lors du changement d\'etat') }
  finally { togglingId.value = null }
}

async function removeConnection(conn) {
  if (!confirm('Supprimer cette connexion ?')) return
  deletingId.value = conn.id
  try {
    await api.delete(`/routers/${routerId}/firewall/connections/${conn.id}`)
    notifications.success('Connexion supprimee')
    await fetchConnections()
  } catch { notifications.error('Erreur lors de la suppression') }
  finally { deletingId.value = null }
}

async function toggleAddressListEntry(entry) {
  togglingId.value = entry.id
  try {
    await api.post(`/routers/${routerId}/firewall/address-lists/${entry.id}/toggle`, null, {
      params: { enable: entry.disabled }
    })
    notifications.success(`Entree ${entry.disabled ? 'activee' : 'desactivee'}`)
    await fetchAddressLists()
  } catch { notifications.error('Erreur lors du changement d\'etat') }
  finally { togglingId.value = null }
}

async function deleteAddressListEntry(entry) {
  if (!confirm('Supprimer cette entree ?')) return
  deletingId.value = entry.id
  try {
    await api.delete(`/routers/${routerId}/firewall/address-lists/${entry.id}`)
    notifications.success('Entree supprimee')
    await fetchAddressLists()
  } catch { notifications.error('Erreur lors de la suppression') }
  finally { deletingId.value = null }
}

// ==================== Add rules ====================

async function addFilterRule() {
  adding.value = true
  try {
    const payload = buildPayload(filterForm, ['chain', 'action', 'src_address', 'dst_address', 'protocol', 'src_port', 'dst_port', 'in_interface', 'out_interface', 'connection_state', 'comment', 'disabled'])
    await api.post(`/routers/${routerId}/firewall/filter`, payload)
    notifications.success('Regle de filtrage ajoutee')
    showFilterModal.value = false
    Object.assign(filterForm, { chain: 'forward', action: 'accept', src_address: '', dst_address: '', protocol: '', src_port: '', dst_port: '', in_interface: '', out_interface: '', connection_state: '', comment: '', disabled: false })
    await fetchFilterRules()
  } catch { notifications.error('Erreur lors de l\'ajout') }
  finally { adding.value = false }
}

async function addNatRule() {
  adding.value = true
  try {
    const payload = buildPayload(natForm, ['chain', 'action', 'src_address', 'dst_address', 'protocol', 'src_port', 'dst_port', 'to_addresses', 'to_ports', 'in_interface', 'out_interface', 'comment', 'disabled'])
    await api.post(`/routers/${routerId}/firewall/nat`, payload)
    notifications.success('Regle NAT ajoutee')
    showNatModal.value = false
    Object.assign(natForm, { chain: 'srcnat', action: 'masquerade', src_address: '', dst_address: '', protocol: '', src_port: '', dst_port: '', to_addresses: '', to_ports: '', in_interface: '', out_interface: '', comment: '', disabled: false })
    await fetchNatRules()
  } catch { notifications.error('Erreur lors de l\'ajout') }
  finally { adding.value = false }
}

async function addMangleRule() {
  adding.value = true
  try {
    const payload = buildPayload(mangleForm, ['chain', 'action', 'src_address', 'dst_address', 'src_address_list', 'dst_address_list', 'protocol', 'src_port', 'dst_port', 'in_interface', 'out_interface', 'connection_state', 'new_packet_mark', 'new_connection_mark', 'new_routing_mark', 'passthrough', 'comment', 'disabled'])
    await api.post(`/routers/${routerId}/firewall/mangle`, payload)
    notifications.success('Regle Mangle ajoutee')
    showMangleModal.value = false
    Object.assign(mangleForm, { chain: 'prerouting', action: 'mark-packet', src_address: '', dst_address: '', src_address_list: '', dst_address_list: '', protocol: '', src_port: '', dst_port: '', in_interface: '', out_interface: '', connection_state: '', new_packet_mark: '', new_connection_mark: '', new_routing_mark: '', passthrough: true, comment: '', disabled: false })
    await fetchMangleRules()
  } catch { notifications.error('Erreur lors de l\'ajout') }
  finally { adding.value = false }
}

async function addRawRule() {
  adding.value = true
  try {
    const payload = buildPayload(rawForm, ['chain', 'action', 'src_address', 'dst_address', 'src_address_list', 'dst_address_list', 'protocol', 'src_port', 'dst_port', 'in_interface', 'out_interface', 'connection_state', 'comment', 'disabled'])
    await api.post(`/routers/${routerId}/firewall/raw`, payload)
    notifications.success('Regle RAW ajoutee')
    showRawModal.value = false
    Object.assign(rawForm, { chain: 'prerouting', action: 'drop', src_address: '', dst_address: '', src_address_list: '', dst_address_list: '', protocol: '', src_port: '', dst_port: '', in_interface: '', out_interface: '', connection_state: '', comment: '', disabled: false })
    await fetchRawRules()
  } catch { notifications.error('Erreur lors de l\'ajout') }
  finally { adding.value = false }
}

async function addAddressListEntry() {
  adding.value = true
  try {
    const payload = buildPayload(addressListForm, ['list', 'address', 'timeout', 'comment', 'disabled'])
    await api.post(`/routers/${routerId}/firewall/address-lists`, payload)
    notifications.success('Entree ajoutee')
    showAddressListModal.value = false
    Object.assign(addressListForm, { list: '', address: '', timeout: '', comment: '', disabled: false })
    await fetchAddressLists()
  } catch { notifications.error('Erreur lors de l\'ajout') }
  finally { adding.value = false }
}

// ==================== Tab loading ====================

const fetchMap = {
  filter: fetchFilterRules,
  nat: fetchNatRules,
  mangle: fetchMangleRules,
  raw: fetchRawRules,
  'service-ports': fetchServicePorts,
  connections: fetchConnections,
  'address-lists': fetchAddressLists
}

const loaded = reactive({})

async function fetchTab(tab) {
  if (fetchMap[tab]) await fetchMap[tab]()
}

watch(activeTab, (tab) => {
  if (!loaded[tab]) {
    loaded[tab] = true
    fetchTab(tab)
  }
})

onMounted(() => {
  loaded.filter = true
  fetchFilterRules()
})
</script>
