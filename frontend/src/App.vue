<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Sidebar -->
    <aside class="fixed inset-y-0 left-0 w-64 bg-white shadow-lg z-30">
      <div class="flex items-center justify-center h-16 bg-mikrotik-600">
        <h1 class="text-xl font-bold text-white">Mikrotik Manager</h1>
      </div>

      <nav class="mt-6">
        <router-link
          to="/"
          class="flex items-center px-6 py-3 text-gray-700 hover:bg-mikrotik-50 hover:text-mikrotik-600 transition-colors"
          :class="{ 'bg-mikrotik-50 text-mikrotik-600 border-r-4 border-mikrotik-600': $route.path === '/' }"
        >
          <HomeIcon class="w-5 h-5 mr-3" />
          Dashboard
        </router-link>

        <router-link
          to="/routers"
          class="flex items-center px-6 py-3 text-gray-700 hover:bg-mikrotik-50 hover:text-mikrotik-600 transition-colors"
          :class="{ 'bg-mikrotik-50 text-mikrotik-600 border-r-4 border-mikrotik-600': $route.path.startsWith('/routers') }"
        >
          <ServerIcon class="w-5 h-5 mr-3" />
          Routeurs
        </router-link>
      </nav>
    </aside>

    <!-- Main content -->
    <main class="ml-64 min-h-screen">
      <header class="bg-white shadow-sm h-16 flex items-center px-6">
        <h2 class="text-lg font-semibold text-gray-800">{{ $route.name }}</h2>
      </header>

      <div class="p-6">
        <router-view />
      </div>
    </main>

    <!-- Notifications -->
    <NotificationToast />
  </div>
</template>

<script setup>
import { HomeIcon, ServerIcon } from '@heroicons/vue/24/outline'
import NotificationToast from './components/NotificationToast.vue'
</script>
