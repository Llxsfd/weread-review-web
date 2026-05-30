import { apiClient } from './client'

export interface SettingsStatus {
  weread_key_configured: boolean
  ai_key_configured: boolean
}

export async function fetchSettingsStatus(): Promise<SettingsStatus> {
  const { data } = await apiClient.get<SettingsStatus>('/api/settings')
  return data
}

export async function fetchWeReadKey(): Promise<{ api_key: string; configured: boolean }> {
  const { data } = await apiClient.get<{ api_key: string; configured: boolean }>('/api/settings/weread-key')
  return data
}

export async function saveWeReadKey(apiKey: string): Promise<{ configured: boolean }> {
  const { data } = await apiClient.put<{ configured: boolean }>('/api/settings/weread-key', {
    api_key: apiKey
  })
  return data
}
