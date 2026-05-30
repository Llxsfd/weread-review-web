import { apiClient } from './client'

export interface HighlightItem {
  id: number
  book: string
  author: string | null
  category: string | null
  chapter: string | null
  text: string
  next_review: string | null
  status: string
  weread_url?: string | null
}

export interface HighlightSearchResult {
  items: HighlightItem[]
  total: number
  page: number
  page_size: number
}

export interface HighlightSearchParams {
  q?: string
  book?: string
  author?: string
  category?: string
  chapter?: string
  page?: number
  page_size?: number
}

export async function fetchHighlights(params: HighlightSearchParams = {}): Promise<HighlightSearchResult> {
  const { data } = await apiClient.get<HighlightSearchResult>('/api/highlights', { params })
  return data
}
