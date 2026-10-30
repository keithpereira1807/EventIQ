# EventIQ: An Intelligent Event Retrieval and Ranking System

EventIQ is an Information Retrieval (IR) and Ranking System designed to retrieve and rank events from natural-language queries. The system evaluates and compares multiple Information Retrieval paradigms—from classical lexical matchers to dense neural vector search, score-level hybrid fusion, and explainable query-aware structured ranking.

#Live Demo: https://eventiq-exe.streamlit.app/

---

## 1. Project Objective

Traditional event discovery platforms rely heavily on rigid database filters (SQL `WHERE` clauses) or simple keyword matching, which fails when users express intent in conversational natural language (e.g., *"free technology workshops in Mumbai for students"*). 

The primary objectives of EventIQ are:
1. Accept conversational natural-language event queries.
2. Formulate searchable representations across multiple structured and unstructured event fields (`title`, `description`, `category`, `subcategory`, `tags`).
3. Implement and benchmark five distinct Information Retrieval paradigms:
   - **TF-IDF** (Vector Space Model Baseline)
   - **Okapi BM25** (Probabilistic Lexical Retrieval)
   - **Dense Semantic Retrieval** (`all-MiniLM-L6-v2` Sentence Embeddings)
   - **Hybrid Retrieval** (Document-Level Convex Score Fusion at $\alpha = 0.70$)
   - **Structured Event Ranking** (Intent-Aware Re-ranking at $\lambda = 0.15$)
4. Empirically evaluate all retrieval architectures against a standardized ground-truth benchmark using standard TREC IR metrics ($P@5, P@10, R@10, F_1, MRR, NDCG@10$).
5. Provide a production-grade FastAPI REST service and an academic dark-theme React frontend featuring score decomposition and interactive Recharts visualizations.

---

## 2. Dataset Specification

* **Corpus Size**: 10,000 synthetic event records situated in an Indian context (20 major cities, Indian states, INR pricing, realistic venues, categories, and target audiences).
* **Test Queries**: 500 ground-truth natural-language query topics (`data/queries.csv`).
* **Relevance Judgments**: 7,500 graded relevance labels on a 1–3 scale (`data/relevance.csv`).
* **Evaluation Threshold**: Graded relevance $\ge 2$ is treated as relevant for binary metrics ($P@K, R@K, F_1, MRR$), while graded values (1, 2, 3) are utilized for $NDCG@10$.
* *Note on Academic Terminology*: The event listings are synthetic representations created for Information Retrieval research. Unjudged query-document pairs are treated as unjudged per standard Cranfield/TREC pooling evaluation assumptions.

---

## 3. Retrieval Paradigms & Mathematical Formulations

### 1. TF-IDF (Vector Space Model)
- Unigram and bigram extraction with sublinear term frequency scaling ($1 + \log(tf)$).
- Cosine similarity between query vector $\vec{q}$ and document vectors $\vec{d}$:
  $$\text{sim}_{\text{TF-IDF}}(q, d) = \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\| \|\vec{d}\|}$$

### 2. Okapi BM25 (Probabilistic Model)
- Token-level probabilistic scoring with document length normalization ($k_1 = 1.5, b = 0.75$):
  $$\text{score}_{\text{BM25}}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}$$

### 3. Dense Semantic Retrieval
- 384-dimensional dense semantic representations computed via Sentence-Transformers (`all-MiniLM-L6-v2`).
- Embeddings for all 10,000 corpus documents are precomputed and cached in `data/event_embeddings.npy` to eliminate redundant inference overhead during search.
- Cosine similarity over normalized embedding vectors:
  $$\text{sim}_{\text{Semantic}}(q, d) = \frac{\mathbf{e}_q \cdot \mathbf{e}_d}{\|\mathbf{e}_q\|_2 \|\mathbf{e}_d\|_2}$$

### 4. Hybrid Retrieval (Score Fusion)
- Per-query Min-Max normalization is applied to BM25 scores across all 10,000 corpus documents before combination:
  $$\text{BM25}_{\text{norm}}(d) = \frac{\text{BM25}(d) - \min_j \text{BM25}(j)}{\max_j \text{BM25}(j) - \min_j \text{BM25}(j)}$$
- Convex linear combination evaluated at $\alpha = 0.70$:
  $$\text{HybridScore}(d) = \alpha \cdot \text{BM25}_{\text{norm}}(d) + (1 - \alpha) \cdot \text{sim}_{\text{Semantic}}(q, d)$$

### 5. Structured Event Ranking (Intent-Aware Re-ranking)
- Extracts structured intent signals from natural language queries matching the dataset vocabulary:
  - **City** (weight = 0.30)
  - **Category** (weight = 0.25)
  - **Free / Paid** (weight = 0.20)
  - **Event Type** (weight = 0.15)
  - **Audience** (weight = 0.10)
- The structured score is normalized dynamically by the sum of weights of *active* detected query signals.
- Combined via soft linear blending at $\lambda = 0.15$:
  $$\text{FinalScore}(d) = (1 - \lambda) \cdot \text{HybridScore}(d) + \lambda \cdot \text{StructuredScore}(d)$$

---

## 4. Empirical Evaluation Results

Evaluated offline across all 500 test queries and 7,500 relevance judgments:

| Model Architecture | Precision@5 | Precision@10 | Recall@10 | F1 Score | MRR | NDCG@10 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TF-IDF Baseline** | 0.3552 | 0.2628 | 0.1752 | 0.2102 | 0.4820 | 0.3101 |
| **BM25 Lexical** | **0.3860** | 0.3250 | 0.2167 | 0.2600 | 0.4797 | 0.3623 |
| **Semantic (`all-MiniLM-L6-v2`)** | 0.2248 | 0.1788 | 0.1192 | 0.1430 | 0.3729 | 0.1955 |
| **Hybrid ($\alpha=0.70$)** | 0.3808 | **0.3402** | **0.2268** | **0.2722** | 0.4915 | 0.3689 |
| **Structured Ranking ($\lambda=0.15$)** | 0.3832 | 0.3364 | 0.2243 | 0.2691 | **0.4991** | **0.3731** |

### Academic Findings & Trade-Offs
1. **Top-Rank Quality**: Structured Ranking achieves the highest $NDCG@10$ (0.3731) and highest $MRR$ (0.4991). Promoting events that satisfy explicit constraints (city, free admission, target audience) significantly elevates relevant items to the top ranks.
2. **Corpus Coverage**: Hybrid Retrieval achieves the highest $Recall@10$ (0.2268) and highest $F_1$ (0.2722). Dense semantic matching retrieves relevant items lacking exact query tokens, while BM25 anchors lexical precision.
3. **Immediate Precision**: BM25 achieves the highest $Precision@5$ (0.3860) due to sharp probabilistic reward for exact query token occurrences in short listings.
4. **Dense Semantic**: While standalone semantic retrieval yields lower lexical precision on keyword-specific queries, it provides vital conceptual recall when query and event listings share zero lexical overlap.

---

## 5. System Architecture

```
User (Browser)
       │
       ▼
React 19 + Vite Frontend (Port 5173)
  ├── Search Interface & Model Selector
  ├── Explainability Decomposition
  ├── Faceted Sidebar (Client-side over retrieved Top-K)
  └── Evaluation Dashboard (Recharts Visualizations)
       │
       ▼ (HTTP / JSON)
FastAPI Backend Service (Port 8000)
  ├── main.py (Endpoints & Error Handlers)
  ├── schemas.py (Pydantic Models)
  └── SearchService (Singleton Manager)
       ├── tfidf_retriever (scikit-learn)
       ├── bm25_retriever (rank-bm25)
       ├── semantic_retriever (sentence-transformers)
       ├── hybrid_retriever (Min-Max score fusion)
       └── structured_ranker (Query Intent Extractor)
             │
             ├── PostgreSQL Database (Port 5432)
             │     └── events (10,000 rows, B-tree indexes)
             └── Persistent Embeddings
                   └── data/event_embeddings.npy (10000 x 384 matrix)
```

---

## 6. Setup & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (tested on Node v22.14.0)
- PostgreSQL 14+ running locally on port 5432

### Backend Setup
1. Clone the repository and enter the directory:
   ```bash
   cd c:\EventIQ
   ```
2. Activate or create the Python virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Configure database credentials in `.env`:
   ```bash
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/eventiq
   ```
5. Initialize the database schema and populate the 10,000 events:
   ```powershell
   python -m backend.database.setup_db
   ```

### Frontend Setup
1. Navigate to the `frontend/` directory:
   ```powershell
   cd frontend
   ```
2. Install frontend packages:
   ```powershell
   npm install
   ```
3. Build the production bundle to verify types:
   ```powershell
   npm run build
   ```

---

## 7. Running the Complete System

### Terminal 1 — Start FastAPI Backend:
```powershell
cd c:\EventIQ
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- Swagger UI Documentation: `http://127.0.0.1:8000/docs`

### Terminal 2 — Start React Frontend:
```powershell
cd c:\EventIQ\frontend
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

## 8. REST API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/health` | GET | Operational health and database connectivity check. |
| `/api/events/count` | GET | Returns the total count of indexed events (`10,000`). |
| `/api/categories` | GET | List of distinct event categories with occurrence counts. |
| `/api/locations` | GET | List of distinct event cities with occurrence counts. |
| `/api/evaluation` | GET | Reproducible benchmark comparison table and raw metrics. |
| `/api/events/{id}` | GET | Complete metadata record for an individual event. |
| `/api/search` | POST | Dispatches search query across one of five retrieval models. |

For detailed request and response payload schemas, see [`docs/api.md`](docs/api.md).

