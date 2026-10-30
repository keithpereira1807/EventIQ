import React from 'react';
import { Database, Cpu, Brain, SlidersHorizontal, Sparkles, Server } from 'lucide-react';

export const ArchitectureView: React.FC = () => {
  return (
    <div className="eval-view">
      <div>
        <h2 className="eval-header-title">EventIQ System Architecture & Methodology</h2>
        <p className="eval-header-desc">
          An end-to-end multi-stage Information Retrieval (IR) and Ranking engine designed for natural language event search over structured corpora.
        </p>
      </div>

      <div className="arch-grid">
        <div className="arch-card">
          <span className="arch-badge">DATASET & REPOSITORY</span>
          <h3 className="arch-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={16} color="#38bdf8" />
            10,000 Event Corpus
          </h3>
          <p className="arch-desc">
            Stored in PostgreSQL with full relational attributes: title, description, category, subcategory, tags, event type, city, state, venue, dates, pricing, organizer, audience, and rating. Searchable documents are formed by concatenating title, description, category, subcategory, and tags.
          </p>
        </div>

        <div className="arch-card">
          <span className="arch-badge">PHASE 2 & 3: LEXICAL RETRIEVAL</span>
          <h3 className="arch-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={16} color="#34d399" />
            TF-IDF & Okapi BM25
          </h3>
          <p className="arch-desc">
            Baseline lexical matchers operating on unigram/bigram tokenized text. BM25 employs document length normalization ($k_1=1.5, b=0.75$) to achieve high precision on exact term occurrences.
          </p>
        </div>

        <div className="arch-card">
          <span className="arch-badge">PHASE 4: DENSE RETRIEVAL</span>
          <h3 className="arch-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Brain size={16} color="#a855f7" />
            Semantic Sentence Embeddings
          </h3>
          <p className="arch-desc">
            Uses <code style={{ color: '#38bdf8' }}>all-MiniLM-L6-v2</code> to embed queries and events into a shared 384-dimensional continuous vector space. All 10,000 event embeddings are precomputed and cached in a persistent matrix artifact (<code style={{ color: '#94a3b8' }}>data/event_embeddings.npy</code>) for low-latency cosine retrieval.
          </p>
        </div>

        <div className="arch-card">
          <span className="arch-badge">PHASE 5: HYBRID FUSION</span>
          <h3 className="arch-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <SlidersHorizontal size={16} color="#f59e0b" />
            Score-Level Hybrid Fusion (α = 0.70)
          </h3>
          <p className="arch-desc">
            Applies per-query Min-Max normalization to BM25 scores and fuses with semantic cosine similarities across all 10,000 events before Top-K selection:
            <br />
            <code style={{ color: '#38bdf8', display: 'block', marginTop: '0.35rem' }}>
              HybridScore = α·BM25_norm + (1-α)·SemanticScore
            </code>
          </p>
        </div>

        <div className="arch-card">
          <span className="arch-badge">PHASE 6: STRUCTURED RERANKING</span>
          <h3 className="arch-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={16} color="#ec4899" />
            Explainable Intent Reranking (λ = 0.15)
          </h3>
          <p className="arch-desc">
            Extracts structured intent signals (city, category, free/paid, event type, audience) from the natural query using corpus vocabulary. Soft additive linear blending with active-signal normalization:
            <br />
            <code style={{ color: '#38bdf8', display: 'block', marginTop: '0.35rem' }}>
              FinalScore = (1-λ)·HybridScore + λ·StructuredScore
            </code>
          </p>
        </div>

        <div className="arch-card">
          <span className="arch-badge">PHASE 7 & 8: API & CLIENT</span>
          <h3 className="arch-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Server size={16} color="#38bdf8" />
            FastAPI Backend & React Frontend
          </h3>
          <p className="arch-desc">
            High-performance asynchronous FastAPI service exposing <code style={{ color: '#93c5fd' }}>/api/search</code>, <code style={{ color: '#93c5fd' }}>/api/events/&#123;id&#125;</code>, and <code style={{ color: '#93c5fd' }}>/api/evaluation</code>. Modern dark-theme React interface with Recharts analytics and explainability decomposition.
          </p>
        </div>
      </div>

      <div className="academic-callout" style={{ marginTop: '1rem' }}>
        <h4 style={{ color: '#f8fafc', marginBottom: '0.5rem' }}>
          Ground Truth IR Evaluation Benchmark Specifications
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <div style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Corpus Size</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.125rem', color: '#f8fafc', fontWeight: 600 }}>
              10,000 Documents
            </div>
          </div>
          <div>
            <div style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Test Queries</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.125rem', color: '#f8fafc', fontWeight: 600 }}>
              500 Natural Language Queries
            </div>
          </div>
          <div>
            <div style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Relevance Judgments</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.125rem', color: '#f8fafc', fontWeight: 600 }}>
              7,500 Graded Judgments (1-3)
            </div>
          </div>
          <div>
            <div style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Relevance Threshold</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.125rem', color: '#f8fafc', fontWeight: 600 }}>
              Relevance Label ≥ 2
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

