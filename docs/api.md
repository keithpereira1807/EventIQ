# EventIQ REST API Documentation

This document describes the REST API endpoints provided by the EventIQ FastAPI backend service.

---

## Base URL
```text
http://localhost:8000
```

Interactive documentation is available at:
* Swagger UI: `GET /docs`
* OpenAPI JSON specification: `GET /openapi.json`

---

## 1. System Health & Diagnostics

### `GET /api/health`
Verifies backend service operational status and PostgreSQL database connectivity.

* **Response Status**: `200 OK` (or `503 Service Unavailable` if database is disconnected)
* **Response Body**:
```json
{
  "status": "ok",
  "database": "connected"
}
```

---

### `GET /api/events/count`
Returns the total count of events currently indexed in the PostgreSQL database.

* **Response Status**: `200 OK`
* **Response Body**:
```json
{
  "event_count": 10000
}
```

---

## 2. Event Search & Retrieval

### `POST /api/search`
Retrieves and ranks events for a natural-language query using one of five information retrieval architectures.

* **Request Headers**: `Content-Type: application/json`
* **Request Body**:

| Field | Type | Default | Constraints | Description |
| :--- | :---: | :---: | :---: | :--- |
| `query` | `string` | *Required* | Non-empty, non-whitespace | Natural-language event query |
| `top_k` | `integer` | `10` | $1 \le \text{top\_k} \le 50$ | Number of ranked results to return |
| `model` | `string` | `"structured"` | One of supported models | Retrieval model identifier |

#### Supported Models:
* `tfidf`: Lexical retrieval using TF-IDF (n-grams 1–2) with Cosine Similarity.
* `bm25`: Lexical probabilistic retrieval using BM25Okapi.
* `semantic`: Dense semantic vector retrieval using Sentence-Transformers (`all-MiniLM-L6-v2`) with Cosine Similarity.
* `hybrid`: Document-level linear fusion of normalized BM25 ($70\%$) and semantic similarity ($30\%$).
* `structured` *(Default)*: Hybrid retrieval ($85\%$) combined with explainable structured query-intent matching ($15\%$).

#### Example Request:
```json
{
  "query": "free technology events in Pune",
  "top_k": 3,
  "model": "structured"
}
```

#### Example Response (`200 OK`):
```json
{
  "query": "free technology events in Pune",
  "model": "structured",
  "total_results": 3,
  "results": [
    {
      "rank": 1,
      "event_id": "EVT005707",
      "title": "Web Development Career Fair in Pune",
      "description": "Web Development Career Fair in Pune is an English-language career fair...",
      "category": "Technology",
      "subcategory": "Web Development",
      "city": "Pune",
      "state": "Maharashtra",
      "venue": "Balgandharva Ranga Mandir",
      "start_date": "2026-12-24",
      "start_time": "10:00:00",
      "price": 499,
      "currency": "INR",
      "is_free": false,
      "organizer": "Tech Innovators Hub",
      "audience": "Developers, Students",
      "rating": 4.6,
      "score": 0.8472,
      "hybrid_score": 0.8673,
      "structured_score": 0.7333,
      "final_score": 0.8472,
      "matched_signals": {
        "city": "Pune",
        "category": "Technology"
      },
      "signal_contributions": {
        "hybrid_base": 0.7372,
        "city_match": 0.06,
        "category_match": 0.05,
        "is_free_match": 0.0
      }
    }
  ]
}
```

#### Validation Error Responses (`422 Unprocessable Content`):
* **Empty query**:
```json
{
  "status": "error",
  "error_type": "validation_error",
  "message": "body.query: Value error, Query must not be empty or whitespace only."
}
```
* **Invalid model**:
```json
{
  "status": "error",
  "error_type": "validation_error",
  "message": "body.model: Value error, Unsupported model 'custom'. Supported models are: bm25, hybrid, semantic, structured, tfidf"
}
```
* **Invalid `top_k`**:
```json
{
  "status": "error",
  "error_type": "validation_error",
  "message": "body.top_k: Input should be less than or equal to 50"
}
```

---

## 3. Event Details

### `GET /api/events/{event_id}`
Retrieves complete database metadata for a specific event by its ID.

* **Path Parameters**: `event_id` (`string`, e.g. `"EVT000001"`)
* **Response Status**: `200 OK`
* **Example Response**:
```json
{
  "event_id": "EVT000001",
  "title": "Interactive Career Fair Exhibition",
  "description": "Interactive Career Fair Exhibition is an English-language exhibition focused on career fair...",
  "category": "Career & Jobs",
  "subcategory": "Career Fair",
  "tags": "Career Fair, Resume Building, Professional Development, Jobs",
  "event_type": "Exhibition",
  "city": "Ahmedabad",
  "state": "Gujarat",
  "venue": "Riverfront Event Centre",
  "address": "Riverfront Event Centre, Ahmedabad, Gujarat",
  "latitude": 23.029951,
  "longitude": 72.569326,
  "start_date": "2026-10-17",
  "start_time": "09:00:00",
  "end_date": "2026-10-17",
  "end_time": "10:00:00",
  "price": 1499,
  "currency": "INR",
  "is_free": false,
  "organizer": "Career Development Network",
  "expected_attendees": 241,
  "audience": "Professionals",
  "language": "English",
  "rating": 4.8
}
```

* **Error Response (`404 Not Found`)**:
```json
{
  "detail": "Event with ID 'EVT999999' was not found."
}
```

---

## 4. Metadata Catalogs

### `GET /api/categories`
Returns distinct event categories and their total event counts for frontend navigation and filtering.

* **Response Status**: `200 OK`
* **Response Body**:
```json
[
  { "category": "Photography", "count": 531 },
  { "category": "Gaming", "count": 520 },
  { "category": "Community", "count": 517 },
  { "category": "Technology", "count": 515 }
]
```

---

### `GET /api/locations`
Returns distinct event cities and their total event counts.

* **Response Status**: `200 OK`
* **Response Body**:
```json
[
  { "city": "Indore", "state": "Madhya Pradesh", "count": 537 },
  { "city": "Ahmedabad", "state": "Gujarat", "count": 515 },
  { "city": "New Delhi", "state": "Delhi", "count": 515 },
  { "city": "Pune", "state": "Maharashtra", "count": 508 }
]
```

---

## 5. Academic Evaluation

### `GET /api/evaluation`
Returns the standardized evaluation results comparing all 5 models across the 500 academic benchmark queries and 7,500 relevance judgments.

* **Response Status**: `200 OK`
* **Response Body**:
```json
{
  "comparison": [
    {
      "model": "TF-IDF",
      "precision_at_5": 0.3552,
      "precision_at_10": 0.2628,
      "recall_at_10": 0.1752,
      "f1": 0.2102,
      "mrr": 0.482,
      "ndcg_at_10": 0.3101
    },
    {
      "model": "BM25",
      "precision_at_5": 0.386,
      "precision_at_10": 0.325,
      "recall_at_10": 0.2167,
      "f1": 0.26,
      "mrr": 0.4797,
      "ndcg_at_10": 0.3623
    },
    {
      "model": "Semantic (all-MiniLM-L6-v2)",
      "precision_at_5": 0.2248,
      "precision_at_10": 0.1788,
      "recall_at_10": 0.1192,
      "f1": 0.143,
      "mrr": 0.3729,
      "ndcg_at_10": 0.1955
    },
    {
      "model": "Hybrid (alpha=0.70)",
      "precision_at_5": 0.3808,
      "precision_at_10": 0.3402,
      "recall_at_10": 0.2268,
      "f1": 0.2722,
      "mrr": 0.4915,
      "ndcg_at_10": 0.3689
    },
    {
      "model": "Structured Ranking (lambda=0.15)",
      "precision_at_5": 0.3832,
      "precision_at_10": 0.3364,
      "recall_at_10": 0.2243,
      "f1": 0.2691,
      "mrr": 0.4991,
      "ndcg_at_10": 0.3731
    }
  ],
  "raw_benchmarks": { ... }
}
```

