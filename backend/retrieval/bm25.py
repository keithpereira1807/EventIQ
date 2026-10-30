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

from backend.retrieval.preprocessing import build_searchable_document, clean_text

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "events.csv"
)


def tokenize(text):
    """
    Split cleaned text into tokens.
    """
    cleaned = clean_text(text)
    return cleaned.split() if cleaned else []


class BM25Retriever:
    """
    BM25 lexical retrieval model using rank-bm25 (BM25Okapi).
    """

    def __init__(self, data_path=None):
        path = data_path or DATA_PATH
        print("Loading EventIQ dataset for BM25...")

        self.df = pd.read_csv(path)

        self.df["searchable_text"] = self.df.apply(
            build_searchable_document,
            axis=1
        )

        print(f"Loaded {len(self.df)} events.")

        print("Tokenizing corpus...")
        self.tokenized_corpus = [
            tokenize(doc) for doc in self.df["searchable_text"]
        ]

        print("Building BM25 index...")
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print("BM25 index built successfully.")

    def search(self, query, top_k=10):
        query_tokens = tokenize(query)

        if not query_tokens:
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

        scores = np.array(self.bm25.get_scores(query_tokens))

        top_indices = scores.argsort()[-top_k:][::-1]

        results = self.df.iloc[top_indices].copy()
        results["score"] = scores[top_indices]

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

