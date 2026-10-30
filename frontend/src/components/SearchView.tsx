import React, { useState, useEffect, useMemo } from 'react';
import {
  RetrievalModel,
  SearchResultItem,
  SearchResponse,
  CategoryItem,
  LocationItem,
} from '../types';
import { apiService } from '../services/api';
import { SearchBar } from './SearchBar';
import { ModelSelector } from './ModelSelector';
import { EventCard } from './EventCard';
import { FiltersSidebar } from './FiltersSidebar';
import { ArrowUpDown, AlertCircle, Info, Layers } from 'lucide-react';

interface SearchViewProps {
  onOpenDetail: (eventId: string) => void;
}

export const SearchView: React.FC<SearchViewProps> = ({ onOpenDetail }) => {
  const [query, setQuery] = useState<string>('free machine learning workshops in Mumbai');
  const [model, setModel] = useState<RetrievalModel>('structured');
  const [topK, setTopK] = useState<number>(10);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Facet data from API
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [locations, setLocations] = useState<LocationItem[]>([]);

  // Client-side facet filtering over retrieved Top-K
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<string | null>(null);
  const [priceFilter, setPriceFilter] = useState<'all' | 'free' | 'paid'>('all');
  const [sortBy, setSortBy] = useState<'rank' | 'rating' | 'price' | 'date'>('rank');

  useEffect(() => {
    // Load category and location facets from backend
    apiService.getCategories().then(setCategories).catch(() => {});
    apiService.getLocations().then(setLocations).catch(() => {});
  }, []);

  const handleSearch = async (overrideQuery?: string) => {
    const q = (overrideQuery !== undefined ? overrideQuery : query).trim();
    if (!q) return;

    setIsLoading(true);
    setError(null);

    try {
      const resp = await apiService.search(q, model, topK);
      setSearchResponse(resp);
      // Reset active filters on new query
      setSelectedCategory(null);
      setSelectedCity(null);
      setPriceFilter('all');
    } catch (err: any) {
      setError(err.message || 'An error occurred during search retrieval.');
    } finally {
      setIsLoading(false);
    }
  };

  // Facet data: compute from current search results so users see the actual categories & cities retrieved
  const dynamicCategories = useMemo(() => {
    if (!searchResponse || searchResponse.results.length === 0) return categories;
    const countMap: Record<string, number> = {};
    for (const r of searchResponse.results) {
      if (r.category) {
        countMap[r.category] = (countMap[r.category] || 0) + 1;
      }
    }
    return Object.entries(countMap)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count);
  }, [searchResponse, categories]);

  const dynamicLocations = useMemo(() => {
    if (!searchResponse || searchResponse.results.length === 0) return locations;
    const countMap: Record<string, { count: number; state?: string }> = {};
    for (const r of searchResponse.results) {
      if (r.city) {
        if (!countMap[r.city]) {
          countMap[r.city] = { count: 0, state: r.state };
        }
        countMap[r.city].count += 1;
      }
    }
    return Object.entries(countMap)
      .map(([city, info]) => ({ city, state: info.state, count: info.count }))
      .sort((a, b) => b.count - a.count);
  }, [searchResponse, locations]);

  // Filter and sort the retrieved results
  const filteredResults = useMemo(() => {
    if (!searchResponse) return [];
    let items = [...searchResponse.results];

    if (selectedCategory) {
      items = items.filter(
        (it) => it.category?.toLowerCase() === selectedCategory.toLowerCase()
      );
    }

    if (selectedCity) {
      items = items.filter(
        (it) => it.city?.toLowerCase() === selectedCity.toLowerCase()
      );
    }

    if (priceFilter === 'free') {
      items = items.filter((it) => it.is_free);
    } else if (priceFilter === 'paid') {
      items = items.filter((it) => !it.is_free);
    }

    if (sortBy === 'rating') {
      items.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0));
    } else if (sortBy === 'price') {
      items.sort((a, b) => (a.price ?? 0) - (b.price ?? 0));
    } else if (sortBy === 'date') {
      items.sort((a, b) => (a.start_date ?? '').localeCompare(b.start_date ?? ''));
    } else {
      // Default to rank
      items.sort((a, b) => a.rank - b.rank);
    }

    return items;
  }, [searchResponse, selectedCategory, selectedCity, priceFilter, sortBy]);

  const handleResetFilters = () => {
    setSelectedCategory(null);
    setSelectedCity(null);
    setPriceFilter('all');
    setSortBy('rank');
  };

  return (
    <div>
      <div className="search-hero">
        <h2 className="search-hero-title">Information Retrieval & Ranking Engine</h2>
        <p className="search-hero-desc">
          Query the 10,000-event knowledge base using exact lexical matchers, dense semantic embeddings, hybrid fusion, or query-aware explainable structured ranking.
        </p>
      </div>

      <div className="search-box-card">
        <SearchBar
          query={query}
          onChangeQuery={setQuery}
          onSearch={handleSearch}
          isLoading={isLoading}
        />
        <ModelSelector
          selectedModel={model}
          onSelectModel={setModel}
          topK={topK}
          onSelectTopK={setTopK}
          disabled={isLoading}
        />
      </div>

      {isLoading && (
        <div className="loading-box">
          <div className="spinner" />
          <p>
            Executing <strong>{model.toUpperCase()}</strong> retrieval over 10,000 event documents...
          </p>
        </div>
      )}

      {error && (
        <div className="error-box">
          <AlertCircle size={24} />
          <p>{error}</p>
        </div>
      )}

      {!isLoading && !error && searchResponse && (
        <div className="results-layout">
          <FiltersSidebar
            categories={dynamicCategories}
            locations={dynamicLocations}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
            selectedCity={selectedCity}
            onSelectCity={setSelectedCity}
            priceFilter={priceFilter}
            onSelectPriceFilter={setPriceFilter}
            onReset={handleResetFilters}
          />

          <main>
            <div className="results-header">
              <div className="results-meta">
                Showing <strong>{filteredResults.length}</strong> of{' '}
                <strong>{searchResponse.total_results}</strong> retrieved events for query:{' '}
                <em style={{ color: '#38bdf8' }}>"{searchResponse.query}"</em>
                <span
                  style={{
                    marginLeft: '0.5rem',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                  }}
                >
                  [{searchResponse.model.toUpperCase()}]
                </span>
              </div>

              <div className="results-sort">
                <ArrowUpDown size={14} />
                <label htmlFor="sort-select">Sort:</label>
                <select
                  id="sort-select"
                  className="select-dropdown"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                >
                  <option value="rank">Original Rank</option>
                  <option value="rating">Rating (High to Low)</option>
                  <option value="price">Price (Low to High)</option>
                  <option value="date">Date (Ascending)</option>
                </select>
              </div>
            </div>

            {filteredResults.length === 0 ? (
              <div className="empty-box">
                <Info size={28} color="#94a3b8" />
                <p>No retrieved events match the active facets.</p>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleResetFilters}
                >
                  Reset Active Filters
                </button>
              </div>
            ) : (
              <div className="event-card-list">
                {filteredResults.map((item) => (
                  <EventCard
                    key={item.event_id}
                    item={item}
                    model={searchResponse.model}
                    onOpenDetail={onOpenDetail}
                  />
                ))}
              </div>
            )}
          </main>
        </div>
      )}

      {!isLoading && !error && !searchResponse && (
        <div className="empty-box">
          <Layers size={32} color="#38bdf8" />
          <h3 style={{ fontSize: '1.125rem', color: 'var(--text-primary)' }}>
            Ready to Search EventIQ Corpus
          </h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: 540 }}>
            Enter a query above or click any of the curated query chips to test the retrieval pipeline.
            Compare rankings across TF-IDF, BM25, Semantic, Hybrid, and Structured Ranking.
          </p>
        </div>
      )}
    </div>
  );
};

