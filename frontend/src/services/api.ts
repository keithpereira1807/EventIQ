import {
  RetrievalModel,
  SearchResponse,
  EventDetail,
  CategoryItem,
  LocationItem,
  EvaluationData,
  SystemHealth,
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000/api' : '/api');

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMessage = `HTTP error ${res.status}`;
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        if (typeof errorJson.detail === 'string') {
          errorMessage = errorJson.detail;
        } else if (Array.isArray(errorJson.detail)) {
          errorMessage = errorJson.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
        }
      }
    } catch {
      // response wasn't JSON
    }
    throw new ApiError(errorMessage, res.status);
  }
  return res.json();
}

export const apiService = {
  async search(
    query: string,
    model: RetrievalModel = 'structured',
    top_k: number = 10
  ): Promise<SearchResponse> {
    const res = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query.trim(),
        model,
        top_k,
      }),
    });
    return handleResponse<SearchResponse>(res);
  },

  async getEventById(eventId: string): Promise<EventDetail> {
    const res = await fetch(`${API_BASE_URL}/events/${encodeURIComponent(eventId)}`);
    return handleResponse<EventDetail>(res);
  },

  async getCategories(): Promise<CategoryItem[]> {
    const res = await fetch(`${API_BASE_URL}/categories`);
    return handleResponse<CategoryItem[]>(res);
  },

  async getLocations(): Promise<LocationItem[]> {
    const res = await fetch(`${API_BASE_URL}/locations`);
    return handleResponse<LocationItem[]>(res);
  },

  async getEvaluation(): Promise<EvaluationData> {
    const res = await fetch(`${API_BASE_URL}/evaluation`);
    return handleResponse<EvaluationData>(res);
  },

  async getHealth(): Promise<SystemHealth> {
    const res = await fetch(`${API_BASE_URL}/health`);
    return handleResponse<SystemHealth>(res);
  },

  async getEventsCount(): Promise<{ total_events: number; event_count: number }> {
    const res = await fetch(`${API_BASE_URL}/events/count`);
    const data = await handleResponse<any>(res);
    const count = data.event_count ?? data.total_events ?? 0;
    return { total_events: count, event_count: count };
  },
};
