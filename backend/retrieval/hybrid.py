import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.bm25 import BM25Retriever, tokenize
from backend.retrieval.semantic import SemanticRetriever


class HybridRetriever:
    """
    Hybrid event retrieval fusing BM25 lexical scores and Sentence-Transformers
    dense semantic embeddings at the document level over the entire corpus.
    
    Formula:
        hybrid_score = alpha * normalized_bm25 + (1 - alpha) * semantic_score
    """

    def __init__(self, alpha=0.70, bm25_retriever=None, semantic_retriever=None):
        self.alpha = float(alpha)
        print("Initializing HybridRetriever...")
        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.semantic_retriever = semantic_retriever or SemanticRetriever()
        self.df = self.bm25_retriever.df
        print(f"HybridRetriever initialized with default alpha={self.alpha:.2f}.")

    def search(self, query, top_k=10, alpha=None):
        eff_alpha = self.alpha if alpha is None else float(alpha)
        q_str = "" if query is None else str(query).strip()

        if not q_str:
            empty_df = self.df.head(0).copy()
            empty_df["score"] = 0.0
            return empty_df[
                [
                    "event_id",
                    "title",
                    "category",
                    "city",
                    "start_date",
                    "price",
                    "is_free",
                    "score"
                ]
            ]

        # 1. Full-corpus BM25 scores
        query_tokens = tokenize(q_str)
        if not query_tokens:
            raw_bm25 = np.zeros(len(self.df), dtype=np.float64)
        else:
            raw_bm25 = np.array(
                self.bm25_retriever.bm25.get_scores(query_tokens),
                dtype=np.float64
            )

        # 2. Per-query Min-Max normalization for BM25
        min_b = float(raw_bm25.min())
        max_b = float(raw_bm25.max())
        range_b = max_b - min_b

        if range_b < 1e-9:
            norm_bm25 = np.zeros_like(raw_bm25)
        else:
            norm_bm25 = (raw_bm25 - min_b) / range_b

        # 3. Full-corpus Semantic cosine similarities
        query_emb = self.semantic_retriever.model.encode(
            [q_str],
            normalize_embeddings=True
        )
        semantic_scores = (
            query_emb @ self.semantic_retriever.embeddings.T
        ).flatten()

        # 4. Document-level convex fusion across all 10,000 events
        hybrid_scores = (
            eff_alpha * norm_bm25
            + (1.0 - eff_alpha) * semantic_scores
        )

        # 5. Extract top-k events from full-corpus fused scores
        top_indices = hybrid_scores.argsort()[-top_k:][::-1]

        results = self.df.iloc[top_indices].copy()
        results["score"] = hybrid_scores[top_indices]

        return results[
            [
                "event_id",
                "title",
                "category",
                "city",
                "start_date",
                "price",
                "is_free",
                "score"
            ]
        ]
