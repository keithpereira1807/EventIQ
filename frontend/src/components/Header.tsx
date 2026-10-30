import React from 'react';
import { Search, BarChart3, Database, Layers } from 'lucide-react';
import { SystemHealth } from '../types';

interface HeaderProps {
  activeTab: 'search' | 'evaluation' | 'architecture';
  onSelectTab: (tab: 'search' | 'evaluation' | 'architecture') => void;
  health: SystemHealth | null;
  totalEvents: number | null;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onSelectTab,
  health,
  totalEvents,
}) => {
  const isHealthy = health?.status === 'ok';

  return (
    <header className="header-bar">
      <div className="header-inner">
        <div className="header-brand" onClick={() => onSelectTab('search')}>
          <span className="brand-badge">IR-EVAL</span>
          <div className="brand-title-group">
            <h1>EventIQ</h1>
            <p>Intelligent Event Information Retrieval & Ranking System</p>
          </div>
        </div>

        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => onSelectTab('search')}
          >
            <Search size={15} />
            <span>Search & Retrieval</span>
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'evaluation' ? 'active' : ''}`}
            onClick={() => onSelectTab('evaluation')}
          >
            <BarChart3 size={15} />
            <span>Evaluation Benchmarks</span>
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'architecture' ? 'active' : ''}`}
            onClick={() => onSelectTab('architecture')}
          >
            <Layers size={15} />
            <span>System Architecture</span>
          </button>
        </nav>

        <div className="system-status-indicator">
          <div className={`status-dot ${isHealthy ? 'online' : 'offline'}`} />
          <span>{isHealthy ? 'API Online' : 'API Connecting...'}</span>
          {totalEvents !== null && (
            <span style={{ color: '#64748b' }}>| {totalEvents.toLocaleString()} Events</span>
          )}
        </div>
      </div>
    </header>
  );
};

