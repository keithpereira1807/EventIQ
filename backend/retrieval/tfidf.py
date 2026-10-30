import os
import sys

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

sys.path.append(PROJECT_ROOT)

from backend.retrieval.preprocessing import build_searchable_document


DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "events.csv"
)


class TFIDFRetriever:

    def __init__(self):
        print("Loading EventIQ dataset...")

        self.df = pd.read_csv(DATA_PATH)

        self.df["searchable_text"] = self.df.apply(
            build_searchable_document,
            axis=1
        )

        print(f"Loaded {len(self.df)} events.")

        self.vectorizer = TfidfVectorizer(
            max_features=20000,
            ngram_range=(1, 2),
            min_df=2,
            stop_words="english"
        )

        print("Building TF-IDF matrix...")

        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.df["searchable_text"]
        )

        print(
            f"TF-IDF matrix shape: {self.tfidf_matrix.shape}"
        )

    def search(self, query, top_k=10):

        query_vector = self.vectorizer.transform([query])

        similarity_scores = cosine_similarity(
            query_vector,
            self.tfidf_matrix
        ).flatten()

        top_indices = similarity_scores.argsort()[-top_k:][::-1]

        results = self.df.iloc[top_indices].copy()

        results["score"] = similarity_scores[top_indices]

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