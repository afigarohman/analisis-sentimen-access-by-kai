import { api } from './client'

export interface DashboardStats {
  total_reviews: number
  total_positive: number
  total_neutral: number
  total_negative: number
  average_score: number
}

export interface SentimentDistributionItem {
  score: number
  total: number
}

export interface ReviewGrowthItem {
  date: string
  total: number
}

export interface SentimentTrendItem {
  date: string
  score: number
  total: number
}

export interface AspectDistributionItem {
  aspect: string
  total: number
}

export interface NegativeAspectInsightItem {
  aspect: string
  total: number
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>('/dashboard/stats')
  return data
}

export async function fetchSentimentDistribution(): Promise<
  SentimentDistributionItem[]
> {
  const { data } = await api.get<SentimentDistributionItem[]>(
    '/dashboard/sentiment-distribution',
  )
  return data
}

export async function fetchReviewGrowth(): Promise<ReviewGrowthItem[]> {
  const { data } = await api.get<ReviewGrowthItem[]>(
    '/dashboard/review-growth',
  )
  return data
}

export async function fetchSentimentTrend(): Promise<SentimentTrendItem[]> {
  const { data } = await api.get<SentimentTrendItem[]>(
    '/dashboard/sentiment-trend',
  )
  return data
}

export async function fetchAspectDistribution(): Promise<
  AspectDistributionItem[]
> {
  const { data } = await api.get<AspectDistributionItem[]>(
    '/dashboard/aspect-distribution',
  )
  return data
}

export async function fetchNegativeAspectInsights(): Promise<
  NegativeAspectInsightItem[]
> {
  const { data } = await api.get<NegativeAspectInsightItem[]>(
    '/dashboard/negative-aspect-insights',
  )
  return data
}
