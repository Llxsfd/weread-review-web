import { apiClient } from './client'

export interface CollectionItem {
  id: number
  name: string
  description: string | null
  highlight_count: number
}

export interface CollectionDetail {
  id: number
  name: string
  description: string | null
  highlights: Array<{
    id: number
    book: string
    author: string | null
    category: string | null
    chapter: string | null
    text: string
  }>
}

export async function fetchCollections(): Promise<CollectionItem[]> {
  const { data } = await apiClient.get<CollectionItem[]>('/api/collections')
  return data
}

export async function createCollection(name: string, description = ''): Promise<CollectionItem> {
  const { data } = await apiClient.post<CollectionItem>('/api/collections', { name, description })
  return data
}

export async function updateCollection(id: number, name: string, description = ''): Promise<CollectionItem> {
  const { data } = await apiClient.patch<CollectionItem>(`/api/collections/${id}`, { name, description })
  return data
}

export async function deleteCollection(id: number): Promise<{ ok: boolean }> {
  const { data } = await apiClient.delete<{ ok: boolean }>(`/api/collections/${id}`)
  return data
}

export async function addHighlightToCollection(collectionId: number, highlightId: number): Promise<{ ok: boolean }> {
  const { data } = await apiClient.post<{ ok: boolean }>(`/api/collections/${collectionId}/highlights`, {
    highlight_id: highlightId
  })
  return data
}

export async function fetchCollectionDetail(collectionId: number): Promise<CollectionDetail> {
  const { data } = await apiClient.get<CollectionDetail>(`/api/collections/${collectionId}`)
  return data
}

export async function exportCollectionMarkdown(collectionId: number): Promise<string> {
  const { data } = await apiClient.get<{ markdown: string }>(`/api/collections/${collectionId}/export/markdown`)
  return data.markdown
}
