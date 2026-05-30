import { apiClient } from './client'

export interface DashboardStats {
  book_count: number
  finished_book_count: number
  reading_book_count: number
  highlight_count: number
  user_note_count: number
  review_card_count: number
  due_today_count: number
  overdue_count: number
  reviewed_today_count: number
  latest_sync_at: string | null
  note_composition: ChartDatum[]
  review_status: ChartDatum[]
  category_distribution: ChartDatum[]
  top_highlight_books: TopHighlightBook[]
}

export interface ChartDatum {
  label: string
  value: number
}

export interface TopHighlightBook {
  title: string
  author: string | null
  category: string | null
  cover: string | null
  highlight_count: number
}

export async function fetchDashboard(): Promise<DashboardStats> {
  const { data } = await apiClient.get<DashboardStats>('/api/dashboard')
  return data
}
