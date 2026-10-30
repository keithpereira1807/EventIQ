import json
import os
import sys
import time

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.preprocessing import build_searchable_document


EVENTS_PATH = os.path.join(
    PROJECT_ROOT, "data", "events.csv"
)

QUERIES_PATH = os.path.join(
    PROJECT_ROOT, "data", "queries.csv"
)

RELEVANCE_PATH = os.path.join(
    PROJECT_ROOT, "data", "relevance.csv"
)

EMBEDDINGS_PATH = os.path.join(
    PROJECT_ROOT, "data", "event_embeddings.npy"
)

EVAL_OUTPUT_PATH = os.path.join(
    PROJECT_ROOT, "evaluation", "semantic_results.json"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def precision_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]

    if not retrieved_k:
        return 0.0

    relevant_count = sum(
        1 for event_id in retrieved_k
        if event_id in relevant
    )

    return relevant_count / k


def recall_at_k(retrieved, relevant, k):
    if not relevant:
        return 0.0

    retrieved_k = retrieved[:k]

    relevant_count = sum(
        1 for event_id in retrieved_k
        if event_id in relevant
    )

    return relevant_count / len(relevant)


def f1_score(precision, recall):
    if precision + recall == 0:
        return 0.0

    return (
        2 * precision * recall
        / (precision + recall)
    )


def reciprocal_rank(retrieved, relevant):
    for rank, event_id in enumerate(retrieved, start=1):
        if event_id in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(retrieved, relevance_dict, k):
    retrieved_k = retrieved[:k]

    dcg = 0.0

    for rank, event_id in enumerate(
        retrieved_k,
        start=1
    ):
        relevance = relevance_dict.get(
            event_id,
            0
        )

        dcg += (
            (2 ** relevance - 1)
            / np.log2(rank + 1)
        )

    ideal_relevances = sorted(
        relevance_dict.values(),
        reverse=True
    )[:k]

    idcg = 0.0

    for rank, relevance in enumerate(
        ideal_relevances,
        start=1
    ):
        idcg += (
            (2 ** relevance - 1)
            / np.log2(rank + 1)
        )

    if idcg == 0:
        return 0.0

    return dcg / idcg


def main():
    print("Loading datasets for Semantic evaluation...")

    events = pd.read_csv(EVENTS_PATH)
    queries = pd.read_csv(QUERIES_PATH)
    relevance = pd.read_csv(RELEVANCE_PATH)

    print(f"Events: {len(events)}")
    print(f"Queries: {len(queries)}")
    print(f"Relevance judgments: {len(relevance)}")

    print(f"Loading SentenceTransformer model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    if not os.path.exists(EMBEDDINGS_PATH):
        raise FileNotFoundError(
            f"Embeddings file {EMBEDDINGS_PATH} not found. Run generate_embeddings.py first."
        )

    print(f"Loading precomputed event embeddings from {EMBEDDINGS_PATH}...")
    embeddings = np.load(EMBEDDINGS_PATH)
    print(f"Embeddings matrix shape: {embeddings.shape}")

    # Create relevance lookup
    relevance_lookup = {}

    for query_id, group in relevance.groupby("query_id"):
        relevance_lookup[query_id] = {
            row["event_id"]: int(row["relevance"])
            for _, row in group.iterrows()
        }

    print()
    print("Encoding queries and evaluating Semantic Retrieval...")
    eval_start_time = time.time()

    precision5_scores = []
    precision10_scores = []
    recall10_scores = []
    f1_scores = []
    mrr_scores = []
    ndcg10_scores = []

    evaluated_queries = 0
    event_ids = events["event_id"].tolist()

    # Pre-encode all queries in batch for efficiency
    query_texts = queries["query"].tolist()
    query_embeddings = model.encode(
        query_texts,
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=True
    )

    similarity_matrix = cosine_similarity(query_embeddings, embeddings)

    for idx, query_row in queries.iterrows():
        query_id = query_row["query_id"]

        if query_id not in relevance_lookup:
            continue

        relevance_dict = relevance_lookup[query_id]

        # Only explicitly judged relevant documents
        relevant = {
            event_id
            for event_id, score in relevance_dict.items()
            if score > 0
        }

        if not relevant:
            continue

        scores = similarity_matrix[idx]
        top_indices = np.argsort(scores)[::-1][:10]

        retrieved = [
            event_ids[index]
            for index in top_indices
        ]

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

    eval_duration = time.time() - eval_start_time

    results = {
        "model": "Semantic (all-MiniLM-L6-v2)",
        "model_name": MODEL_NAME,
        "embedding_dimension": int(embeddings.shape[1]),
        "total_documents": int(embeddings.shape[0]),
        "queries_evaluated": evaluated_queries,
        "evaluation_duration_seconds": round(eval_duration, 2),
        "precision_at_5": round(float(np.mean(precision5_scores)), 4),
        "precision_at_10": round(float(np.mean(precision10_scores)), 4),
        "recall_at_10": round(float(np.mean(recall10_scores)), 4),
        "f1": round(float(np.mean(f1_scores)), 4),
        "mrr": round(float(np.mean(mrr_scores)), 4),
        "ndcg_at_10": round(float(np.mean(ndcg10_scores)), 4)
    }

    print()
    print("=" * 60)
    print("SEMANTIC EVALUATION RESULTS")
    print("=" * 60)
    print(f"Model: {results['model']}")
    print(f"Embedding Dimension: {results['embedding_dimension']}")
    print(f"Documents: {results['total_documents']}")
    print(f"Queries evaluated: {results['queries_evaluated']}")
    print(f"Evaluation duration: {results['evaluation_duration_seconds']}s")
    print(f"Precision@5:  {results['precision_at_5']:.4f}")
    print(f"Precision@10: {results['precision_at_10']:.4f}")
    print(f"Recall@10:    {results['recall_at_10']:.4f}")
    print(f"F1:           {results['f1']:.4f}")
    print(f"MRR:          {results['mrr']:.4f}")
    print(f"NDCG@10:      {results['ndcg_at_10']:.4f}")
    print("=" * 60)

    os.makedirs(os.path.dirname(EVAL_OUTPUT_PATH), exist_ok=True)
    with open(EVAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {EVAL_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

