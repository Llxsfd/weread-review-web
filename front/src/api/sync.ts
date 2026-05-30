import { apiClient } from './client'

export interface SyncResult {
  job_id: number | null
  status: string
  books_synced: number
  highlights_synced: number
  message: string
  logs?: string[]
}

export interface SyncJob {
  id: number
  job_type: string
  status: string
  books_synced: number
  highlights_synced: number
  total_books?: number | null
  progress?: number
  message: string | null
  logs: string[]
  started_at: string | null
  finished_at: string | null
}

export async function runFullSync(): Promise<SyncResult> {
  const { data } = await apiClient.post<SyncResult>('/api/sync/full')
  return data
}

export async function runQuickSync(): Promise<SyncResult> {
  const { data } = await apiClient.post<SyncResult>('/api/sync/quick')
  return data
}

export async function fetchSyncJobs(): Promise<SyncJob[]> {
  const { data } = await apiClient.get<SyncJob[]>('/api/sync/jobs')
  return data
}

export async function fetchSyncJob(jobId: number): Promise<SyncJob> {
  const { data } = await apiClient.get<SyncJob>(`/api/sync/jobs/${jobId}`)
  return data
}

export async function cancelSyncJob(jobId: number): Promise<SyncJob> {
  const { data } = await apiClient.post<SyncJob>(`/api/sync/jobs/${jobId}/cancel`)
  return data
}
