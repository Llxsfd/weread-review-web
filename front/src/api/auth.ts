import { apiClient } from './client'

export interface AuthUser {
  id: number
  email: string
  nickname: string | null
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/api/auth/login', { email, password })
  return data
}

export async function register(email: string, password: string, nickname: string): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/api/auth/register', { email, password, nickname })
  return data
}

