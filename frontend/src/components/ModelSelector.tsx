import React from 'react';
import { RetrievalModel } from '../types';
import { Sparkles, SlidersHorizontal, Cpu, Binary, Brain } from 'lucide-react';

interface ModelSelectorProps {
  selectedModel: RetrievalModel;
  onSelectModel: (model: RetrievalModel) => void;
  topK: number;
  onSelectTopK: (topK: number) => void;
  disabled?: boolean;
}

interface ModelOption {
  id: RetrievalModel;
  label: string;
  badge: string;
  icon: React.ReactNode;
}

const MODELS: ModelOption[] = [
  {
    id: 'structured',
    label: 'Structured Ranking',
    badge: 'λ = 0.15',
    icon: <Sparkles size={14} />,
  },
  {
    id: 'hybrid',
    label: 'Hybrid Fusion',
    badge: 'α = 0.70',
    icon: <SlidersHorizontal size={14} />,
  },
  {
    id: 'bm25',
    label: 'BM25 Lexical',
    badge: 'Probabilistic',
    icon: <Binary size={14} />,
  },
  {
    id: 'semantic',
    label: 'Semantic Vector',
    badge: 'MiniLM-L6-v2',
    icon: <Brain size={14} />,
  },
  {
    id: 'tfidf',
    label: 'TF-IDF Baseline',
    badge: 'Vector Space',
    icon: <Cpu size={14} />,
  },
];

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  selectedModel,
  onSelectModel,
  topK,
  onSelectTopK,
  disabled = false,
}) => {
  return (
    <div className="controls-bar">
      <div className="model-selector-group">
        <span className="control-label">Retriever:</span>
        {MODELS.map((m) => {
          const isActive = selectedModel === m.id;
          return (
            <button
              key={m.id}
              type="button"
              className={`model-pill ${isActive ? 'active' : ''}`}
              onClick={() => onSelectModel(m.id)}
              disabled={disabled}
              title={`Use ${m.label} retrieval engine`}
            >
              {m.icon}
              <span>{m.label}</span>
              <span
                style={{
                  fontSize: '0.6875rem',
                  opacity: 0.8,
                  fontFamily: 'var(--font-mono)',
                  marginLeft: '2px',
                }}
              >
                ({m.badge})
              </span>
            </button>
          );
        })}
      </div>

      <div className="topk-selector-group">
        <span className="control-label">Top-K:</span>
        <select
          className="select-dropdown"
          value={topK}
          onChange={(e) => onSelectTopK(Number(e.target.value))}
          disabled={disabled}
        >
          <option value={5}>Top 5</option>
          <option value={10}>Top 10 (Default)</option>
          <option value={15}>Top 15</option>
          <option value={20}>Top 20</option>
          <option value={25}>Top 25</option>
          <option value={50}>Top 50</option>
        </select>
      </div>
    </div>
  );
};

