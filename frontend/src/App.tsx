import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { SearchView } from './components/SearchView';
import { EvaluationView } from './components/EvaluationView';
import { ArchitectureView } from './components/ArchitectureView';
import { EventDetailsModal } from './components/EventDetailsModal';
import { SystemHealth } from './types';
import { apiService } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'evaluation' | 'architecture'>('search');
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [totalEvents, setTotalEvents] = useState<number | null>(null);
  const [activeEventId, setActiveEventId] = useState<string | null>(null);

  useEffect(() => {
    // Health check
    apiService
      .getHealth()
      .then((h) => setHealth(h))
      .catch(() => setHealth({ status: 'error', database: 'disconnected' }));

    // Total events count
    apiService
      .getEventsCount()
      .then((c) => setTotalEvents(c.total_events))
      .catch(() => {});
  }, []);

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        health={health}
        totalEvents={totalEvents}
      />

      <div className="content-wrapper">
        {activeTab === 'search' && (
          <SearchView onOpenDetail={(id) => setActiveEventId(id)} />
        )}
        {activeTab === 'evaluation' && <EvaluationView />}
        {activeTab === 'architecture' && <ArchitectureView />}
      </div>

      <EventDetailsModal
        eventId={activeEventId}
        onClose={() => setActiveEventId(null)}
      />

      <footer
        style={{
          borderTop: '1px solid var(--border-subtle)',
          padding: '1.5rem',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          marginTop: 'auto',
          backgroundColor: 'var(--bg-secondary)',
        }}
      >
        <p>
          EventIQ — Information Retrieval & Ranking System | 10,000 Event Corpus | Evaluated on 500 Queries (TREC standard)
        </p>
        <p style={{ marginTop: '0.25rem', fontFamily: 'var(--font-mono)' }}>
          Backend: Python FastAPI &bull; Vector Space / BM25 / Sentence-Transformers &bull; Frontend: React + Vite + TypeScript
        </p>
      </footer>
    </div>
  );
};

