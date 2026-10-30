import json
import os
import sys
import time

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.bm25 import tokenize
from backend.retrieval.preprocessing import build_searchable_document


EVENTS_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")
QUERIES_PATH = os.path.join(PROJECT_ROOT, "data", "queries.csv")
RELEVANCE_PATH = os.path.join(PROJECT_ROOT, "data", "relevance.csv")
EMBEDDINGS_PATH = os.path.join(PROJECT_ROOT, "data", "event_embeddings.npy")
EVAL_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "evaluation", "hybrid_results.json")
MODEL_NAME = "all-MiniLM-L6-v2"

ALPHAS_TO_EVALUATE = [0.25, 0.50, 0.60, 0.70, 0.75]


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
    print("=" * 70)
    print("HYBRID RETRIEVAL EVALUATION PIPELINE")
    print("=" * 70)

    print("Loading datasets...")
    events = pd.read_csv(EVENTS_PATH)
    queries = pd.read_csv(QUERIES_PATH)
    relevance = pd.read_csv(RELEVANCE_PATH)

    print(f"Events: {len(events)}")
    print(f"Queries: {len(queries)}")
    print(f"Relevance judgments: {len(relevance)}")

    print("Building searchable text and BM25 index...")
    events["searchable_text"] = events.apply(build_searchable_document, axis=1)
    tokenized_corpus = [tokenize(doc) for doc in events["searchable_text"]]
    bm25 = BM25Okapi(tokenized_corpus)

    print(f"Loading persistent embeddings from {EMBEDDINGS_PATH}...")
    embeddings = np.load(EMBEDDINGS_PATH)
    print(f"Embeddings shape: {embeddings.shape}")

    print(f"Loading SentenceTransformer model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    # Encode all 500 queries in batch
    print("Batch encoding 500 queries...")
    query_texts = queries["query"].tolist()
    query_embeddings = model.encode(
        query_texts,
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=True
    )
    # Cosine similarity matrix: (500, 10000)
    all_semantic_similarities = query_embeddings @ embeddings.T

    # Relevance lookup
    relevance_lookup = {}
    for query_id, group in relevance.groupby("query_id"):
        relevance_lookup[query_id] = {
            row["event_id"]: int(row["relevance"])
            for _, row in group.iterrows()
        }

    event_ids = events["event_id"].tolist()
    total_docs = len(event_ids)

    # Metric accumulators per alpha
    alpha_metrics = {
        alpha: {
            "p5": [], "p10": [], "r10": [], "f1": [], "mrr": [], "ndcg10": []
        }
        for alpha in ALPHAS_TO_EVALUATE
    }

    evaluated_queries = 0
    start_eval_time = time.time()

    print()
    print("Running Full-Corpus Document-Level Hybrid Fusion across queries...")

    for idx, query_row in queries.iterrows():
        query_id = query_row["query_id"]
        query_text = query_row["query"]

        if query_id not in relevance_lookup:
            continue

        relevance_dict = relevance_lookup[query_id]
        relevant = {e for e, s in relevance_dict.items() if s > 0}
        if not relevant:
            continue

        # 1. BM25 raw scores for all 10,000 events
        query_tokens = tokenize(query_text)
        if not query_tokens:
            raw_bm25 = np.zeros(total_docs, dtype=np.float64)
        else:
            raw_bm25 = np.array(bm25.get_scores(query_tokens), dtype=np.float64)

        # 2. Min-Max normalization per query
        min_b = float(raw_bm25.min())
        max_b = float(raw_bm25.max())
        diff_b = max_b - min_b
        if diff_b < 1e-9:
            norm_bm25 = np.zeros_like(raw_bm25)
        else:
            norm_bm25 = (raw_bm25 - min_b) / diff_b

        # 3. Semantic scores for all 10,000 events
        sem_scores = all_semantic_similarities[idx]

        # 4. Evaluate each alpha
        for alpha in ALPHAS_TO_EVALUATE:
            hybrid_scores = alpha * norm_bm25 + (1.0 - alpha) * sem_scores

            # Top-10 selection after full-corpus fusion
            top_indices = np.argsort(hybrid_scores)[::-1][:10]
            retrieved = [event_ids[i] for i in top_indices]

            p5 = precision_at_k(retrieved, relevant, 5)
            p10 = precision_at_k(retrieved, relevant, 10)
            r10 = recall_at_k(retrieved, relevant, 10)
            f1 = f1_score(p10, r10)
            mrr = reciprocal_rank(retrieved, relevant)
            ndcg = ndcg_at_k(retrieved, relevance_dict, 10)

            alpha_metrics[alpha]["p5"].append(p5)
            alpha_metrics[alpha]["p10"].append(p10)
            alpha_metrics[alpha]["r10"].append(r10)
            alpha_metrics[alpha]["f1"].append(f1)
            alpha_metrics[alpha]["mrr"].append(mrr)
            alpha_metrics[alpha]["ndcg10"].append(ndcg)

        evaluated_queries += 1

    eval_duration = time.time() - start_eval_time

    # Summarize results
    results_by_alpha = {}
    best_alpha = None
    best_ndcg = -1.0

    print()
    print("=" * 80)
    print(f"HYBRID EVALUATION RESULTS ACROSS ALPHAS ({evaluated_queries} queries, {eval_duration:.2f}s)")
    print("=" * 80)
    print(f"{'Alpha':<8} {'P@5':<10} {'P@10':<10} {'Recall@10':<12} {'F1':<10} {'MRR':<10} {'NDCG@10':<10}")
    print("-" * 80)

    for alpha in ALPHAS_TO_EVALUATE:
        m = alpha_metrics[alpha]
        summary = {
            "alpha": float(alpha),
            "precision_at_5": round(float(np.mean(m["p5"])), 4),
            "precision_at_10": round(float(np.mean(m["p10"])), 4),
            "recall_at_10": round(float(np.mean(m["r10"])), 4),
            "f1": round(float(np.mean(m["f1"])), 4),
            "mrr": round(float(np.mean(m["mrr"])), 4),
            "ndcg_at_10": round(float(np.mean(m["ndcg10"])), 4)
        }
        results_by_alpha[f"alpha_{alpha:.2f}"] = summary

        print(
            f"{alpha:<8.2f} "
            f"{summary['precision_at_5']:<10.4f} "
            f"{summary['precision_at_10']:<10.4f} "
            f"{summary['recall_at_10']:<12.4f} "
            f"{summary['f1']:<10.4f} "
            f"{summary['mrr']:<10.4f} "
            f"{summary['ndcg_at_10']:<10.4f}"
        )

        if summary["ndcg_at_10"] > best_ndcg:
            best_ndcg = summary["ndcg_at_10"]
            best_alpha = alpha

    print("=" * 80)
    print(f"Optimal Alpha Selected: {best_alpha:.2f} (Highest NDCG@10: {best_ndcg:.4f})")
    print("=" * 80)

    final_output = {
        "model": "Hybrid (BM25 + all-MiniLM-L6-v2)",
        "fusion_strategy": "Full-corpus convex linear combination with per-query Min-Max normalized BM25",
        "formula": "hybrid_score = alpha * normalized_bm25 + (1 - alpha) * semantic_score",
        "selected_alpha": float(best_alpha),
        "queries_evaluated": evaluated_queries,
        "evaluation_duration_seconds": round(eval_duration, 2),
        "best_metrics": results_by_alpha[f"alpha_{best_alpha:.2f}"],
        "all_alphas_evaluated": results_by_alpha
    }

    os.makedirs(os.path.dirname(EVAL_OUTPUT_PATH), exist_ok=True)
    with open(EVAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)

    print(f"Results successfully saved to {EVAL_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

