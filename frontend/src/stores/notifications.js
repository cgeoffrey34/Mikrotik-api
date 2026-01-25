import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref([])
  let nextId = 0

  function addNotification({ type = 'info', title, message, timeout = 5000 }) {
    const id = nextId++
    notifications.value.push({ id, type, title, message })

    if (timeout > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, timeout)
    }

    return id
  }

  function removeNotification(id) {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  function success(message, title = 'Succès') {
    return addNotification({ type: 'success', title, message })
  }

  function error(message, title = 'Erreur') {
    return addNotification({ type: 'error', title, message, timeout: 8000 })
  }

  function warning(message, title = 'Attention') {
    return addNotification({ type: 'warning', title, message })
  }

  function info(message, title = 'Information') {
    return addNotification({ type: 'info', title, message })
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info
  }
})
