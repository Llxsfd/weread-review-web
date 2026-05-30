import { apiClient } from './client'

export interface ReviewCard {
  id: number
  book_id: string
  book: string
  author: string | null
  chapter: string | null
  question: string
  text: string
  note: string
  due: string
  memory_level: number
  weread_url?: string | null
}

export interface ReviewDrawParams {
  mode?: 'random' | 'book' | 'category'
  book_id?: string
  category?: string
  exclude_book_id?: string
}

export interface TodayReviewedItem {
  id: number
  card_id: number
  book: string
  chapter: string | null
  text: string
  rating: string
  reviewed_at: string
}

export interface TodayReviewStats {
  reviewed_count: number
  reviewed_items: TodayReviewedItem[]
}

export async function fetchTodayReview(): Promise<ReviewCard[]> {
  const { data } = await apiClient.get<ReviewCard[]>('/api/review/today')
  return data
}

export async function fetchTodayReviewStats(): Promise<TodayReviewStats> {
  const { data } = await apiClient.get<TodayReviewStats>('/api/review/today/stats')
  return data
}

export async function fetchRandomReview(params: ReviewDrawParams = {}): Promise<ReviewCard | null> {
  const { data } = await apiClient.get<ReviewCard | null>('/api/review/random', {
    params
  })
  return data
}

export async function answerReviewCard(cardId: number, rating: string) {
  const { data } = await apiClient.post(`/api/review/cards/${cardId}/answer`, { rating })
  return data
}
