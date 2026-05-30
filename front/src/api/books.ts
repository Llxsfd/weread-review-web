import { apiClient } from './client'

export interface BookItem {
  id: string
  title: string
  author: string | null
  category: string | null
  cover: string | null
  progress: number
  highlights: number
  due: number
}

export interface BookHighlightItem {
  id: number
  chapter: string | null
  text: string
  created_at: string | null
  next_review: string | null
  status: string
  weread_url?: string | null
}

export async function fetchBooks(q = ''): Promise<BookItem[]> {
  const { data } = await apiClient.get<BookItem[]>('/api/books', {
    params: q.trim() ? { q: q.trim() } : undefined
  })
  return data
}

export async function fetchBookHighlights(bookId: string): Promise<BookHighlightItem[]> {
  const { data } = await apiClient.get<BookHighlightItem[]>(`/api/books/${encodeURIComponent(bookId)}/highlights`)
  return data
}
