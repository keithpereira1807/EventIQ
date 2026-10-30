import React from 'react';
import { SearchResultItem } from '../types';
import { SlidersHorizontal, Sparkles, Check } from 'lucide-react';

interface ExplainabilityPanelProps {
  item: SearchResultItem;
  model: string;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({ item, model }) => {
  const isStructured = model === 'structured' && item.structured_score !== undefined;
  const isHybrid = model === 'hybrid' || (model === 'structured' && item.hybrid_score !== undefined);

  return (
    <div className="explain-panel">
      <div className="explain-header">
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Sparkles size={13} color="#38bdf8" />
          <strong>Ranking Explainability & Score Decomposition</strong>
        </span>
        <span>Model: {model.toUpperCase()}</span>
      </div>

      {isStructured && (
        <>
          <div className="formula-display">
            FinalScore = 0.85 × HybridScore ({item.hybrid_score?.toFixed(4)}) + 0.15 × StructuredScore ({item.structured_score?.toFixed(4)})
          </div>

          <div className="scores-breakdown-grid">
            <div className="score-cell">
              <div className="score-cell-label">Final Rank Score</div>
              <div className="score-cell-val" style={{ color: '#38bdf8' }}>
                {(item.final_score ?? item.score).toFixed(4)}
              </div>
            </div>
            <div className="score-cell">
              <div className="score-cell-label">Hybrid Score (0.85)</div>
              <div className="score-cell-val">
                {item.hybrid_score !== undefined ? item.hybrid_score.toFixed(4) : 'N/A'}
              </div>
            </div>
            <div className="score-cell">
              <div className="score-cell-label">Structured Score (0.15)</div>
              <div className="score-cell-val" style={{ color: '#34d399' }}>
                {item.structured_score !== undefined ? item.structured_score.toFixed(4) : '0.0000'}
              </div>
            </div>
          </div>

          {item.matched_signals && Object.keys(item.matched_signals).length > 0 && (
            <div className="signals-breakdown">
              <div className="signals-title">Active Query Intent Matches:</div>
              <div className="signals-chips">
                {Object.entries(item.matched_signals).map(([key, value]) => (
                  <span key={key} className="signal-chip matched">
                    <Check size={11} style={{ marginRight: 3, display: 'inline' }} />
                    {key}: <strong>{String(value)}</strong>
                  </span>
                ))}
              </div>
            </div>
          )}

          {item.signal_contributions && Object.keys(item.signal_contributions).length > 0 && (
            <div className="signals-breakdown" style={{ marginTop: '0.625rem' }}>
              <div className="signals-title">Signal Contribution Decomposition:</div>
              <div className="contributions-bars">
                {Object.entries(item.signal_contributions).map(([sig, contrib]) => {
                  const pct = Math.min(100, Math.max(0, contrib * 100));
                  return (
                    <div key={sig} className="contrib-row">
                      <span className="contrib-name">{sig}</span>
                      <div className="contrib-bar-wrapper">
                        <div className="contrib-bar-fill" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="contrib-val">+{contrib.toFixed(3)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}

      {!isStructured && isHybrid && (
        <>
          <div className="formula-display">
            HybridScore = 0.70 × BM25(Min-Max) + 0.30 × Semantic(Cosine)
          </div>
          <div className="scores-breakdown-grid">
            <div className="score-cell">
              <div className="score-cell-label">Fused Hybrid Score</div>
              <div className="score-cell-val" style={{ color: '#38bdf8' }}>
                {item.score.toFixed(4)}
              </div>
            </div>
          </div>
        </>
      )}

      {!isStructured && !isHybrid && (
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>
          {model === 'bm25' && (
            <span>Raw Okapi BM25 score based on term frequency, inverse document frequency, and document length normalization across searchable tokens.</span>
          )}
          {model === 'tfidf' && (
            <span>Cosine similarity between query TF-IDF vector and event document TF-IDF vector in sublinear-scaled unigram/bigram space.</span>
          )}
          {model === 'semantic' && (
            <span>Dense cosine similarity between query embedding and 384-dimensional event embedding generated via sentence-transformers (<code style={{ color: '#38bdf8' }}>all-MiniLM-L6-v2</code>).</span>
          )}
        </div>
      )}
    </div>
  );
};

