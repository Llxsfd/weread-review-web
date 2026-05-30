import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchSettingsStatus, type SettingsStatus } from '../api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const status = ref<SettingsStatus | null>(null)
  const loading = ref(false)
  const initialized = ref(false)

  async function fetchStatus() {
    if (loading.value) return
    loading.value = true
    try {
      status.value = await fetchSettingsStatus()
      initialized.value = true
    } catch (e) {
      console.error('Failed to fetch settings status', e)
    } finally {
      loading.value = false
    }
  }

  function updateStatus(newStatus: SettingsStatus) {
    status.value = newStatus
  }

  return {
    status,
    loading,
    initialized,
    fetchStatus,
    updateStatus
  }
})
