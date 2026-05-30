import { apiClient } from './client'

export interface ChartDatum {
  label: string
  value: number
}

export interface DataCenterSummary {
  book_count: number
  highlight_count: number
  reviewed_highlight_count: number
  avg_highlights_per_book: number
}

export interface DataCenterBook {
  title: string
  author: string | null
  category?: string | null
  cover: string | null
  highlight_count: number
}

export interface DataCenterStats {
  summary: DataCenterSummary
  review_funnel: ChartDatum[]
  category_distribution: ChartDatum[]
  category_review_effect: Array<{
    label: string
    highlights: number
    reviewed: number
    mastered: number
    forgot_or_hard: number
  }>
  author_distribution: ChartDatum[]
  top_highlight_books: DataCenterBook[]
  reading_progress: ChartDatum[]
  memory_distribution: ChartDatum[]
  review_trend: ChartDatum[]
  stale_highlights: ChartDatum[]
}

export async function fetchDataCenter(): Promise<DataCenterStats> {
  const { data } = await apiClient.get<DataCenterStats>('/api/data-center')
  return data
}

export type DataCenterDistributions = Pick<
  DataCenterStats,
  'category_distribution' | 'author_distribution' | 'reading_progress' | 'memory_distribution'
>

export type DataCenterReviewStats = Pick<
  DataCenterStats,
  'review_funnel' | 'category_review_effect' | 'review_trend' | 'stale_highlights'
>

export type DataCenterBookStats = Pick<DataCenterStats, 'top_highlight_books'>

export async function fetchDataCenterSummary(): Promise<DataCenterSummary> {
  const { data } = await apiClient.get<DataCenterSummary>('/api/data-center/summary')
  return data
}

export async function fetchDataCenterDistributions(): Promise<DataCenterDistributions> {
  const { data } = await apiClient.get<DataCenterDistributions>('/api/data-center/distributions')
  return data
}

export async function fetchDataCenterReview(): Promise<DataCenterReviewStats> {
  const { data } = await apiClient.get<DataCenterReviewStats>('/api/data-center/review')
  return data
}

export async function fetchDataCenterBooks(): Promise<DataCenterBookStats> {
  const { data } = await apiClient.get<DataCenterBookStats>('/api/data-center/books')
  return data
}
