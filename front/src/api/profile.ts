import { apiClient } from './client'

export interface UserProfile {
  id: number
  email: string
  nickname: string | null
  created_at: string | null
}

export async function fetchProfile(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>('/api/profile')
  return data
}

export async function updateProfile(nickname: string): Promise<UserProfile> {
  const { data } = await apiClient.patch<UserProfile>('/api/profile', { nickname })
  return data
}

export async function updatePassword(oldPassword: string, newPassword: string): Promise<{ password_changed: boolean }> {
  const { data } = await apiClient.patch<{ password_changed: boolean }>('/api/profile/password', {
    old_password: oldPassword,
    new_password: newPassword
  })
  return data
}

