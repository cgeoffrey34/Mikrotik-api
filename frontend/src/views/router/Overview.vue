<template>
  <div>
    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatsCard
        title="CPU"
        :value="stats?.cpu_load || 0"
        suffix="%"
        :icon="CpuChipIcon"
        color="blue"
        :progress="stats?.cpu_load || 0"
        progress-label="Utilisation"
      />
      <StatsCard
        title="Memoire"
        :value="formatBytes(stats?.memory_used || 0)"
        :suffix="`/ ${formatBytes(stats?.memory_total || 0)}`"
        :icon="CircleStackIcon"
        color="purple"
        :progress="stats?.memory_percent || 0"
        progress-label="Utilisation"
      />
      <StatsCard
        title="Disque"
        :value="formatBytes(stats?.disk_used || 0)"
        :suffix="`/ ${formatBytes(stats?.disk_total || 0)}`"
        :icon="ServerIcon"
        color="indigo"
        :progress="stats?.disk_percent || 0"
        progress-label="Utilisation"
      />
      <StatsCard
        title="Uptime"
        :value="stats?.uptime || 'N/A'"
        :icon="ClockIcon"
        color="green"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <StatsCard
        title="Clients WiFi"
        :value="stats?.wifi_clients || 0"
        :icon="WifiIcon"
        color="yellow"
      />
      <StatsCard
        title="Baux DHCP"
        :value="stats?.dhcp_leases || 0"
        :icon="ComputerDesktopIcon"
        color="blue"
      />
      <StatsCard
        title="Connexions actives"
        :value="stats?.active_connections || 0"
        :icon="ArrowsRightLeftIcon"
        color="green"
      />
    </div>

    <!-- Router info -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Informations</h3>
        <dl class="space-y-3">
          <div class="flex justify-between">
            <dt class="text-gray-500">Nom</dt>
            <dd class="text-gray-900 font-medium">{{ router.name }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Adresse IP</dt>
            <dd class="text-gray-900">{{ router.ip_address }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Port API</dt>
            <dd class="text-gray-900">{{ router.api_port }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Modele</dt>
            <dd class="text-gray-900">{{ router.model || 'N/A' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">N serie</dt>
            <dd class="text-gray-900">{{ router.serial_number || 'N/A' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Version RouterOS</dt>
            <dd class="text-gray-900">{{ router.ros_version || 'N/A' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Firmware</dt>
            <dd class="text-gray-900">{{ router.firmware_version || 'N/A' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Emplacement</dt>
            <dd class="text-gray-900">{{ router.location || 'Non defini' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">SSL</dt>
            <dd class="text-gray-900">{{ router.use_ssl ? 'Oui' : 'Non' }}</dd>
          </div>
        </dl>
      </div>

      <div class="card p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Notes</h3>
        <p class="text-gray-600">{{ router.notes || 'Aucune note' }}</p>

        <h3 class="text-lg font-medium text-gray-900 mt-6 mb-4">Dates</h3>
        <dl class="space-y-3">
          <div class="flex justify-between">
            <dt class="text-gray-500">Ajoute le</dt>
            <dd class="text-gray-900">{{ formatDate(router.created_at) }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Derniere connexion</dt>
            <dd class="text-gray-900">{{ router.last_seen ? formatDate(router.last_seen) : 'Jamais' }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatsCard from '../../components/StatsCard.vue'
import {
  CpuChipIcon,
  CircleStackIcon,
  ServerIcon,
  ClockIcon,
  WifiIcon,
  ComputerDesktopIcon,
  ArrowsRightLeftIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  router: Object,
  stats: Object
})

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString('fr-FR')
}
</script>
