import React from 'react';
import { CategoryItem, LocationItem } from '../types';
import { Filter, RotateCcw } from 'lucide-react';

interface FiltersSidebarProps {
  categories: CategoryItem[];
  locations: LocationItem[];
  selectedCategory: string | null;
  onSelectCategory: (cat: string | null) => void;
  selectedCity: string | null;
  onSelectCity: (city: string | null) => void;
  priceFilter: 'all' | 'free' | 'paid';
  onSelectPriceFilter: (p: 'all' | 'free' | 'paid') => void;
  onReset: () => void;
}

export const FiltersSidebar: React.FC<FiltersSidebarProps> = ({
  categories,
  locations,
  selectedCategory,
  onSelectCategory,
  selectedCity,
  onSelectCity,
  priceFilter,
  onSelectPriceFilter,
  onReset,
}) => {
  const hasActiveFilters =
    selectedCategory !== null || selectedCity !== null || priceFilter !== 'all';

  return (
    <aside className="filters-sidebar">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem', fontWeight: 600 }}>
            <Filter size={14} color="#38bdf8" />
            <span>Facets & Filters</span>
          </span>
          <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', display: 'block', marginTop: '2px' }}>
            Applied over retrieved set
          </span>
        </div>
        {hasActiveFilters && (
          <button type="button" className="filter-reset-btn" onClick={onReset} title="Clear all filters">
            <RotateCcw size={11} style={{ marginRight: 3, display: 'inline' }} />
            Reset
          </button>
        )}
      </div>

      {/* Price Type */}
      <div>
        <div className="filter-section-title">Pricing</div>
        <div style={{ display: 'flex', gap: '0.35rem' }}>
          <button
            type="button"
            className={`model-pill ${priceFilter === 'all' ? 'active' : ''}`}
            onClick={() => onSelectPriceFilter('all')}
            style={{ flex: 1, justifyContent: 'center' }}
          >
            All
          </button>
          <button
            type="button"
            className={`model-pill ${priceFilter === 'free' ? 'active' : ''}`}
            onClick={() => onSelectPriceFilter('free')}
            style={{ flex: 1, justifyContent: 'center' }}
          >
            Free
          </button>
          <button
            type="button"
            className={`model-pill ${priceFilter === 'paid' ? 'active' : ''}`}
            onClick={() => onSelectPriceFilter('paid')}
            style={{ flex: 1, justifyContent: 'center' }}
          >
            Paid
          </button>
        </div>
      </div>

      {/* Categories */}
      <div>
        <div className="filter-section-title">
          <span>Categories</span>
          {selectedCategory && (
            <span
              style={{ fontSize: '0.7rem', color: '#38bdf8', cursor: 'pointer' }}
              onClick={() => onSelectCategory(null)}
            >
              Clear
            </span>
          )}
        </div>
        <div className="filter-chip-list">
          {categories.map((cat) => {
            const isActive = selectedCategory === cat.category;
            return (
              <button
                key={cat.category}
                type="button"
                className={`filter-item-btn ${isActive ? 'active' : ''}`}
                onClick={() => onSelectCategory(isActive ? null : cat.category)}
              >
                <span>{cat.category}</span>
                <span className="filter-count-badge">{cat.count}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Locations */}
      <div>
        <div className="filter-section-title">
          <span>Locations (Top Cities)</span>
          {selectedCity && (
            <span
              style={{ fontSize: '0.7rem', color: '#38bdf8', cursor: 'pointer' }}
              onClick={() => onSelectCity(null)}
            >
              Clear
            </span>
          )}
        </div>
        <div className="filter-chip-list">
          {locations.slice(0, 15).map((loc) => {
            const isActive = selectedCity === loc.city;
            return (
              <button
                key={loc.city}
                type="button"
                className={`filter-item-btn ${isActive ? 'active' : ''}`}
                onClick={() => onSelectCity(isActive ? null : loc.city)}
              >
                <span>{loc.city}</span>
                <span className="filter-count-badge">{loc.count}</span>
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
};

