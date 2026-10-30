import React from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  query: string;
  onChangeQuery: (query: string) => void;
  onSearch: (overrideQuery?: string) => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  'free machine learning workshops in Mumbai',
  'react developer meetups in Bangalore',
  'cybersecurity conferences in Delhi',
  'startup pitching events in Pune',
  'music festivals in Goa',
  'blockchain hackathons for students in Hyderabad',
];

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  onChangeQuery,
  onSearch,
  isLoading,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch();
    }
  };

  const handleChipClick = (example: string) => {
    onChangeQuery(example);
    onSearch(example);
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="search-input-row">
        <div className="search-input-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search events using natural language (e.g. 'free tech workshops in Mumbai')..."
            value={query}
            onChange={(e) => onChangeQuery(e.target.value)}
            disabled={isLoading}
          />
          {query && !isLoading && (
            <button
              type="button"
              className="clear-search-btn"
              onClick={() => onChangeQuery('')}
              title="Clear input"
            >
              <X size={16} />
            </button>
          )}
        </div>
        <button
          type="submit"
          className="submit-search-btn"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? (
            <>
              <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
              <span>Retrieving...</span>
            </>
          ) : (
            <>
              <Search size={16} />
              <span>Retrieve</span>
            </>
          )}
        </button>
      </form>

      <div className="example-queries">
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Examples:</span>
        {EXAMPLE_QUERIES.map((eq) => (
          <button
            key={eq}
            type="button"
            className="query-chip"
            onClick={() => handleChipClick(eq)}
            disabled={isLoading}
          >
            {eq}
          </button>
        ))}
      </div>
    </div>
  );
};

