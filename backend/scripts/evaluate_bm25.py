import json
import os
import sys

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.bm25 import tokenize
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

EVAL_OUTPUT_PATH = os.path.join(
    PROJECT_ROOT, "evaluation", "bm25_results.json"
)


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
    print("Loading datasets for BM25 evaluation...")

    events = pd.read_csv(EVENTS_PATH)
    queries = pd.read_csv(QUERIES_PATH)
    relevance = pd.read_csv(RELEVANCE_PATH)

    print(f"Events: {len(events)}")
    print(f"Queries: {len(queries)}")
    print(f"Relevance judgments: {len(relevance)}")

    print()
    print("Building searchable documents...")

    events["searchable_text"] = events.apply(
        build_searchable_document,
        axis=1
    )

    print("Tokenizing corpus...")
    tokenized_corpus = [
        tokenize(doc) for doc in events["searchable_text"]
    ]

    print("Building BM25 index...")
    bm25 = BM25Okapi(tokenized_corpus)

    # Create relevance lookup
    relevance_lookup = {}

    for query_id, group in relevance.groupby("query_id"):
        relevance_lookup[query_id] = {
            row["event_id"]: int(row["relevance"])
            for _, row in group.iterrows()
        }

    print()
    print("Evaluating BM25...")
    print()

    precision5_scores = []
    precision10_scores = []
    recall10_scores = []
    f1_scores = []
    mrr_scores = []
    ndcg10_scores = []

    evaluated_queries = 0

    event_ids = events["event_id"].tolist()

    for _, query_row in queries.iterrows():
        query_id = query_row["query_id"]
        query_text = query_row["query"]

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

        query_tokens = tokenize(query_text)

        if not query_tokens:
            scores = np.zeros(len(event_ids))
        else:
            scores = np.array(bm25.get_scores(query_tokens))

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

    results = {
        "model": "BM25",
        "queries_evaluated": evaluated_queries,
        "precision_at_5": round(float(np.mean(precision5_scores)), 4),
        "precision_at_10": round(float(np.mean(precision10_scores)), 4),
        "recall_at_10": round(float(np.mean(recall10_scores)), 4),
        "f1": round(float(np.mean(f1_scores)), 4),
        "mrr": round(float(np.mean(mrr_scores)), 4),
        "ndcg_at_10": round(float(np.mean(ndcg10_scores)), 4)
    }

    print("=" * 60)
    print("BM25 EVALUATION RESULTS")
    print("=" * 60)
    print(f"Queries evaluated: {results['queries_evaluated']}")
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

