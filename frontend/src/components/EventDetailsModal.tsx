import React, { useEffect, useState } from 'react';
import { EventDetail } from '../types';
import { apiService } from '../services/api';
import { X, Calendar, MapPin, Tag, Users, Star, DollarSign, Building } from 'lucide-react';

interface EventDetailsModalProps {
  eventId: string | null;
  onClose: () => void;
}

export const EventDetailsModal: React.FC<EventDetailsModalProps> = ({ eventId, onClose }) => {
  const [event, setEvent] = useState<EventDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!eventId) return;

    let isMounted = true;
    setLoading(true);
    setError(null);

    apiService
      .getEventById(eventId)
      .then((data) => {
        if (isMounted) {
          setEvent(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load event details.');
          setLoading(false);
        }
      });

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      isMounted = false;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [eventId, onClose]);

  if (!eventId) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
              }}
            >
              EVENT ID: {eventId}
            </span>
            <h2>{loading ? 'Loading Event Details...' : event?.title}</h2>
          </div>
          <button className="modal-close-btn" onClick={onClose} title="Close modal">
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {loading && (
            <div className="loading-box" style={{ padding: '2rem' }}>
              <div className="spinner" />
              <p>Fetching full event schema from PostgreSQL...</p>
            </div>
          )}

          {error && (
            <div className="error-box">
              <p>{error}</p>
            </div>
          )}

          {event && !loading && (
            <>
              {event.description && (
                <div>
                  <h4
                    style={{
                      fontSize: '0.8125rem',
                      textTransform: 'uppercase',
                      color: 'var(--text-muted)',
                      marginBottom: '0.5rem',
                    }}
                  >
                    Description
                  </h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', lineHeight: 1.6 }}>
                    {event.description}
                  </p>
                </div>
              )}

              <div>
                <h4
                  style={{
                    fontSize: '0.8125rem',
                    textTransform: 'uppercase',
                    color: 'var(--text-muted)',
                    marginBottom: '0.75rem',
                  }}
                >
                  Event Specifications & Metadata
                </h4>
                <table className="modal-meta-table">
                  <tbody>
                    <tr>
                      <td>Category / Subcategory</td>
                      <td>
                        {event.category || 'N/A'} &gt; {event.subcategory || 'N/A'}
                      </td>
                    </tr>
                    <tr>
                      <td>Event Type</td>
                      <td>{event.event_type || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Tags</td>
                      <td>{event.tags || 'None'}</td>
                    </tr>
                    <tr>
                      <td>Location</td>
                      <td>
                        {[event.venue, event.address, event.city, event.state]
                          .filter(Boolean)
                          .join(', ') || 'N/A'}
                      </td>
                    </tr>
                    {(event.latitude !== undefined || event.longitude !== undefined) && (
                      <tr>
                        <td>Coordinates</td>
                        <td>
                          {event.latitude?.toFixed(4)}, {event.longitude?.toFixed(4)}
                        </td>
                      </tr>
                    )}
                    <tr>
                      <td>Date & Time</td>
                      <td>
                        {event.start_date || 'N/A'} {event.start_time || ''}
                        {event.end_date ? ` to ${event.end_date} ${event.end_time || ''}` : ''}
                      </td>
                    </tr>
                    <tr>
                      <td>Pricing</td>
                      <td>
                        {event.is_free
                          ? 'FREE'
                          : `${event.currency || 'INR'} ${event.price !== undefined ? event.price : 'N/A'}`}
                      </td>
                    </tr>
                    <tr>
                      <td>Organizer</td>
                      <td>{event.organizer || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Target Audience</td>
                      <td>{event.audience || 'General'}</td>
                    </tr>
                    <tr>
                      <td>Expected Attendees</td>
                      <td>
                        {event.expected_attendees ? event.expected_attendees.toLocaleString() : 'N/A'}
                      </td>
                    </tr>
                    <tr>
                      <td>Language</td>
                      <td>{event.language || 'English'}</td>
                    </tr>
                    <tr>
                      <td>Rating</td>
                      <td>{event.rating ? `${event.rating.toFixed(1)} / 5.0` : 'N/A'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

