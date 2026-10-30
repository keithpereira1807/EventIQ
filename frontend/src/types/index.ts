export type RetrievalModel = 'structured' | 'hybrid' | 'bm25' | 'tfidf' | 'semantic';

export interface SearchResultItem {
  rank: number;
  event_id: string;
  title: string;
  description?: string;
  category?: string;
  subcategory?: string;
  city?: string;
  state?: string;
  venue?: string;
  start_date?: string;
  start_time?: string;
  price?: number;
  currency?: string;
  is_free?: boolean;
  organizer?: string;
  audience?: string;
  rating?: number;
  score: number;
  hybrid_score?: number;
  structured_score?: number;
  final_score?: number;
  matched_signals?: Record<string, any>;
  signal_contributions?: Record<string, number>;
}

export interface SearchResponse {
  query: string;
  model: string;
  total_results: number;
  results: SearchResultItem[];
}

export interface EventDetail {
  event_id: string;
  title: string;
  description?: string;
  category?: string;
  subcategory?: string;
  tags?: string;
  event_type?: string;
  city?: string;
  state?: string;
  venue?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  start_date?: string;
  start_time?: string;
  end_date?: string;
  end_time?: string;
  price?: number;
  currency?: string;
  is_free?: boolean;
  organizer?: string;
  expected_attendees?: number;
  audience?: string;
  language?: string;
  rating?: number;
}

export interface CategoryItem {
  category: string;
  count: number;
}

export interface LocationItem {
  city: string;
  state?: string;
  count: number;
}

export interface ModelMetrics {
  model: string;
  precision_at_5: number;
  precision_at_10: number;
  recall_at_10: number;
  f1: number;
  mrr: number;
  ndcg_at_10: number;
}

export interface EvaluationData {
  comparison: ModelMetrics[];
  raw_benchmarks: Record<string, any>;
}

export interface SystemHealth {
  status: string;
  database: string;
}

