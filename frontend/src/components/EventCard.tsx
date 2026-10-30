import React, { useState } from 'react';
import { SearchResultItem } from '../types';
import { ExplainabilityPanel } from './ExplainabilityPanel';
import {
  Calendar,
  Clock,
  MapPin,
  Tag,
  Star,
  Users,
  ChevronDown,
  ChevronUp,
  ExternalLink,
} from 'lucide-react';

interface EventCardProps {
  item: SearchResultItem;
  model: string;
  onOpenDetail: (eventId: string) => void;
}

export const EventCard: React.FC<EventCardProps> = ({ item, model, onOpenDetail }) => {
  const [showExplain, setShowExplain] = useState<boolean>(false);

  const displayScore = (item.final_score ?? item.score).toFixed(4);

  return (
    <article className="event-card">
      <div className="event-card-header">
        <div className="event-rank-title-group">
          <span className="rank-badge">#{item.rank}</span>
          <div>
            <h3
              className="event-title"
              onClick={() => onOpenDetail(item.event_id)}
              title="View full event details"
            >
              {item.title}
            </h3>
          </div>
        </div>

        <div className="score-badge-container">
          <div className="score-badge">{displayScore}</div>
          <span className="score-label">
            {model === 'structured' ? 'Final Score' : 'Score'}
          </span>
        </div>
      </div>

      <div className="event-tags-row">
        {item.category && (
          <span className="tag-chip tag-category">
            <Tag size={10} style={{ marginRight: 3, display: 'inline' }} />
            {item.category}
          </span>
        )}
        {item.subcategory && (
          <span className="tag-chip tag-subcategory">{item.subcategory}</span>
        )}
        {item.is_free ? (
          <span className="tag-chip tag-free">FREE</span>
        ) : (
          <span className="tag-chip tag-paid">
            {item.currency ? item.currency : '₹'}
            {item.price ?? 'Paid'}
          </span>
        )}
        {item.audience && (
          <span className="tag-chip tag-audience">
            <Users size={10} style={{ marginRight: 3, display: 'inline' }} />
            {item.audience}
          </span>
        )}
        {item.rating && (
          <span
            className="tag-chip"
            style={{
              background: 'rgba(234, 179, 8, 0.12)',
              border: '1px solid rgba(234, 179, 8, 0.3)',
              color: '#facc15',
            }}
          >
            <Star size={10} style={{ marginRight: 3, display: 'inline' }} />
            {item.rating.toFixed(1)}
          </span>
        )}
      </div>

      {item.description && (
        <p className="event-description">{item.description}</p>
      )}

      <div className="event-meta-grid">
        {(item.city || item.state) && (
          <div className="meta-item">
            <MapPin size={13} />
            <span>
              {[item.venue, item.city, item.state].filter(Boolean).join(', ')}
            </span>
          </div>
        )}
        {item.start_date && (
          <div className="meta-item">
            <Calendar size={13} />
            <span>
              {item.start_date}
              {item.start_time ? ` at ${item.start_time}` : ''}
            </span>
          </div>
        )}
        {item.organizer && (
          <div className="meta-item">
            <span style={{ color: 'var(--text-muted)' }}>Organizer:</span>
            <span>{item.organizer}</span>
          </div>
        )}
      </div>

      <div className="event-actions-row">
        <button
          type="button"
          className="btn-explain"
          onClick={() => setShowExplain(!showExplain)}
        >
          {showExplain ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          <span>{showExplain ? 'Hide Score Breakdown' : 'Explain Score'}</span>
        </button>

        <button
          type="button"
          className="btn-secondary"
          onClick={() => onOpenDetail(item.event_id)}
        >
          <span>View Details</span>
          <ExternalLink size={12} />
        </button>
      </div>

      {showExplain && <ExplainabilityPanel item={item} model={model} />}
    </article>
  );
};

