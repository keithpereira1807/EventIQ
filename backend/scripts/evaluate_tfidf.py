import os
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

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

    print("Loading datasets...")

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

    print("Building TF-IDF matrix...")

    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        min_df=2,
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        events["searchable_text"]
    )

    print(
        f"TF-IDF matrix: {tfidf_matrix.shape}"
    )

    # Create relevance lookup
    relevance_lookup = {}

    for query_id, group in relevance.groupby(
        "query_id"
    ):

        relevance_lookup[query_id] = {
            row["event_id"]: int(row["relevance"])
            for _, row in group.iterrows()
        }

    print()
    print("Evaluating TF-IDF...")
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

        query_vector = vectorizer.transform(
            [query_text]
        )

        scores = cosine_similarity(
            query_vector,
            tfidf_matrix
        ).flatten()

        top_indices = np.argsort(
            scores
        )[::-1][:10]

        retrieved = [
            event_ids[index]
            for index in top_indices
        ]

        p5 = precision_at_k(
            retrieved,
            relevant,
            5
        )

        p10 = precision_at_k(
            retrieved,
            relevant,
            10
        )

        r10 = recall_at_k(
            retrieved,
            relevant,
            10
        )

        f1 = f1_score(
            p10,
            r10
        )

        mrr = reciprocal_rank(
            retrieved,
            relevant
        )

        ndcg = ndcg_at_k(
            retrieved,
            relevance_dict,
            10
        )

        precision5_scores.append(p5)
        precision10_scores.append(p10)
        recall10_scores.append(r10)
        f1_scores.append(f1)
        mrr_scores.append(mrr)
        ndcg10_scores.append(ndcg)

        evaluated_queries += 1

    print("=" * 60)
    print("TF-IDF EVALUATION RESULTS")
    print("=" * 60)

    print(f"Queries evaluated: {evaluated_queries}")

    print(
        f"Precision@5:  "
        f"{np.mean(precision5_scores):.4f}"
    )

    print(
        f"Precision@10: "
        f"{np.mean(precision10_scores):.4f}"
    )

    print(
        f"Recall@10:    "
        f"{np.mean(recall10_scores):.4f}"
    )

    print(
        f"F1:           "
        f"{np.mean(f1_scores):.4f}"
    )

    print(
        f"MRR:          "
        f"{np.mean(mrr_scores):.4f}"
    )

    print(
        f"NDCG@10:      "
        f"{np.mean(ndcg10_scores):.4f}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()