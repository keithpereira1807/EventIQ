import json
import os
import sys
import time

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.bm25 import tokenize
from backend.retrieval.preprocessing import build_searchable_document
from backend.retrieval.structured_ranking import QueryIntentParser, DEFAULT_SIGNAL_WEIGHTS, DEFAULT_LAMBDA

EVENTS_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")
QUERIES_PATH = os.path.join(PROJECT_ROOT, "data", "queries.csv")
RELEVANCE_PATH = os.path.join(PROJECT_ROOT, "data", "relevance.csv")
EMBEDDINGS_PATH = os.path.join(PROJECT_ROOT, "data", "event_embeddings.npy")
EVAL_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "evaluation", "structured_ranking_results.json")
HYBRID_RESULTS_PATH = os.path.join(PROJECT_ROOT, "evaluation", "hybrid_results.json")
MODEL_NAME = "all-MiniLM-L6-v2"
HYBRID_ALPHA = 0.70


def precision_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    if not retrieved_k:
        return 0.0
    relevant_count = sum(1 for event_id in retrieved_k if event_id in relevant)
    return relevant_count / k


def recall_at_k(retrieved, relevant, k):
    if not relevant:
        return 0.0
    retrieved_k = retrieved[:k]
    relevant_count = sum(1 for event_id in retrieved_k if event_id in relevant)
    return relevant_count / len(relevant)


def f1_score(precision, recall):
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def reciprocal_rank(retrieved, relevant):
    for rank, event_id in enumerate(retrieved, start=1):
        if event_id in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved, relevance_dict, k):
    retrieved_k = retrieved[:k]
    dcg = 0.0
    for rank, event_id in enumerate(retrieved_k, start=1):
        relevance = relevance_dict.get(event_id, 0)
        dcg += (2 ** relevance - 1) / np.log2(rank + 1)

    ideal_relevances = sorted(relevance_dict.values(), reverse=True)[:k]
    idcg = 0.0
    for rank, relevance in enumerate(ideal_relevances, start=1):
        idcg += (2 ** relevance - 1) / np.log2(rank + 1)

    if idcg == 0:
        return 0.0
    return dcg / idcg


def main():
    print("=" * 75)
    print("STRUCTURED EVENT RANKING EVALUATION (PHASE 6)")
    print("=" * 75)

    print("Loading datasets...")
    events = pd.read_csv(EVENTS_PATH)
    queries = pd.read_csv(QUERIES_PATH)
    relevance = pd.read_csv(RELEVANCE_PATH)

    print(f"Events: {len(events)}")
    print(f"Queries: {len(queries)}")
    print(f"Relevance judgments: {len(relevance)}")

    print("Initializing BM25 index...")
    events["searchable_text"] = events.apply(build_searchable_document, axis=1)
    tokenized_corpus = [tokenize(doc) for doc in events["searchable_text"]]
    bm25 = BM25Okapi(tokenized_corpus)

    print(f"Loading persistent embeddings from {EMBEDDINGS_PATH}...")
    embeddings = np.load(EMBEDDINGS_PATH)

    print(f"Loading SentenceTransformer model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print("Batch encoding 500 queries...")
    query_texts = queries["query"].tolist()
    query_embeddings = model.encode(
        query_texts,
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=True
    )
    all_semantic_similarities = query_embeddings @ embeddings.T

    relevance_lookup = {}
    for query_id, group in relevance.groupby("query_id"):
        relevance_lookup[query_id] = {
            row["event_id"]: int(row["relevance"])
            for _, row in group.iterrows()
        }

    intent_parser = QueryIntentParser(data_path=EVENTS_PATH)
    event_ids = events["event_id"].tolist()
    total_docs = len(event_ids)

    # Pre-extract numpy columns for high-speed metadata matching
    city_col = events["city"].to_numpy()
    cat_col = events["category"].to_numpy()
    subcat_col = events["subcategory"].to_numpy()
    is_free_col = events["is_free"].to_numpy(dtype=bool)
    event_type_col = events["event_type"].to_numpy()
    audience_series = events["audience"].fillna("").str.lower()

    precision5_scores = []
    precision10_scores = []
    recall10_scores = []
    f1_scores = []
    mrr_scores = []
    ndcg10_scores = []

    evaluated_queries = 0
    start_eval_time = time.time()

    print()
    print("Running Structured Ranking over all queries...")

    for idx, query_row in queries.iterrows():
        query_id = query_row["query_id"]
        query_text = query_row["query"]

        if query_id not in relevance_lookup:
            continue

        relevance_dict = relevance_lookup[query_id]
        relevant = {e for e, s in relevance_dict.items() if s > 0}
        if not relevant:
            continue

        # 1. Full-corpus BM25 scores
        query_tokens = tokenize(query_text)
        if not query_tokens:
            raw_bm25 = np.zeros(total_docs, dtype=np.float64)
        else:
            raw_bm25 = np.array(bm25.get_scores(query_tokens), dtype=np.float64)

        # Min-Max normalize BM25
        min_b = float(raw_bm25.min())
        max_b = float(raw_bm25.max())
        diff_b = max_b - min_b
        if diff_b < 1e-9:
            norm_bm25 = np.zeros_like(raw_bm25)
        else:
            norm_bm25 = (raw_bm25 - min_b) / diff_b

        # 2. Semantic similarity scores
        sem_scores = all_semantic_similarities[idx]

        # 3. Hybrid score (alpha = 0.70)
        hybrid_scores = HYBRID_ALPHA * norm_bm25 + (1.0 - HYBRID_ALPHA) * sem_scores

        # 4. Structured Score
        intents = intent_parser.parse(query_text)
        active_signals = [k for k in DEFAULT_SIGNAL_WEIGHTS if k in intents]
        total_active_weight = sum(DEFAULT_SIGNAL_WEIGHTS[k] for k in active_signals)

        if total_active_weight > 0:
            weighted_matches = np.zeros(total_docs, dtype=np.float64)

            if "city" in intents:
                city_match = (city_col == intents["city"]).astype(np.float64)
                weighted_matches += DEFAULT_SIGNAL_WEIGHTS["city"] * city_match

            if "category" in intents:
                cat_match = (cat_col == intents["category"])
                if "subcategory" in intents:
                    cat_match = cat_match | (subcat_col == intents["subcategory"])
                weighted_matches += DEFAULT_SIGNAL_WEIGHTS["category"] * cat_match.astype(np.float64)

            if "is_free" in intents:
                free_match = is_free_col.astype(np.float64)
                weighted_matches += DEFAULT_SIGNAL_WEIGHTS["is_free"] * free_match

            if "event_type" in intents:
                et_match = (event_type_col == intents["event_type"]).astype(np.float64)
                weighted_matches += DEFAULT_SIGNAL_WEIGHTS["event_type"] * et_match

            if "audience" in intents:
                target_aud = intents["audience"].lower()
                aud_match = audience_series.str.contains(target_aud, regex=False).to_numpy(dtype=np.float64)
                weighted_matches += DEFAULT_SIGNAL_WEIGHTS["audience"] * aud_match

            structured_scores = weighted_matches / total_active_weight
        else:
            structured_scores = np.zeros(total_docs, dtype=np.float64)

        # 5. Final Convex Fusion: 0.85 * Hybrid + 0.15 * Structured
        final_scores = (1.0 - DEFAULT_LAMBDA) * hybrid_scores + DEFAULT_LAMBDA * structured_scores

        # 6. Top-10 selection
        top_indices = np.argsort(final_scores)[::-1][:10]
        retrieved = [event_ids[i] for i in top_indices]

        p5 = precision_at_k(retrieved, relevant, 5)
        p10 = precision_at_k(retrieved, relevant, 10)
        r10 = recall_at_k(retrieved, relevant, 10)
        f1 = f1_score(p10, r10)
        mrr = reciprocal_rank(retrieved, relevant)
        ndcg = ndcg_at_k(retrieved, relevance_dict, 10)

        precision5_scores.append(p5)
        precision10_scores.append(p10)
        recall10_scores.append(r10)
        f1_scores.append(f1)
        mrr_scores.append(mrr)
        ndcg10_scores.append(ndcg)

        evaluated_queries += 1

    eval_duration = time.time() - start_eval_time

    # Load Hybrid baseline for direct A/B comparison
    with open(HYBRID_RESULTS_PATH, "r", encoding="utf-8") as f:
        hybrid_data = json.load(f)
    hybrid_baseline = hybrid_data["best_metrics"]

    current_metrics = {
        "precision_at_5": round(float(np.mean(precision5_scores)), 4),
        "precision_at_10": round(float(np.mean(precision10_scores)), 4),
        "recall_at_10": round(float(np.mean(recall10_scores)), 4),
        "f1": round(float(np.mean(f1_scores)), 4),
        "mrr": round(float(np.mean(mrr_scores)), 4),
        "ndcg_at_10": round(float(np.mean(ndcg10_scores)), 4)
    }

    print()
    print("=" * 75)
    print("STRUCTURED RANKING EVALUATION RESULTS (A/B COMPARISON)")
    print("=" * 75)
    print(f"Queries evaluated: {evaluated_queries} ({eval_duration:.2f}s)")
    print(f"Lambda weight: {DEFAULT_LAMBDA} (85% Hybrid + 15% Structured)")
    print(f"Signal weights: {DEFAULT_SIGNAL_WEIGHTS}")
    print("-" * 75)
    print(f"{'Metric':<16} {'Hybrid Baseline':<18} {'Structured Ranking':<20} {'Delta':<10}")
    print("-" * 75)

    delta_dict = {}
    for k in ["precision_at_5", "precision_at_10", "recall_at_10", "f1", "mrr", "ndcg_at_10"]:
        h_val = hybrid_baseline[k]
        s_val = current_metrics[k]
        diff = round(s_val - h_val, 4)
        delta_dict[k] = diff
        sign = "+" if diff >= 0 else ""
        print(f"{k:<16} {h_val:<18.4f} {s_val:<20.4f} {sign}{diff:<10.4f}")

    print("=" * 75)

    output = {
        "model": "Structured Event Ranking (Hybrid + Structured Intent Layer)",
        "base_model": "Hybrid (alpha=0.70)",
        "lambda_weight": DEFAULT_LAMBDA,
        "signal_weights": DEFAULT_SIGNAL_WEIGHTS,
        "queries_evaluated": evaluated_queries,
        "evaluation_duration_seconds": round(eval_duration, 2),
        "metrics": current_metrics,
        "hybrid_baseline": hybrid_baseline,
        "deltas_vs_hybrid": delta_dict
    }

    os.makedirs(os.path.dirname(EVAL_OUTPUT_PATH), exist_ok=True)
    with open(EVAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to {EVAL_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

