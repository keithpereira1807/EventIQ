import os
import sys

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Limit PyTorch threads to reduce container RAM usage
torch.set_num_threads(1)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.preprocessing import build_searchable_document

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")
EMBEDDINGS_PATH = os.path.join(PROJECT_ROOT, "data", "event_embeddings.npy")
MODEL_NAME = "all-MiniLM-L6-v2"


class SemanticRetriever:
    """
    Semantic event retrieval using sentence-transformers (all-MiniLM-L6-v2)
    and cosine similarity over dense vector embeddings.
    """

    def __init__(self, data_path=None, embeddings_path=None, model_name=MODEL_NAME, df=None):
        self.data_path = data_path or DATA_PATH
        self.embeddings_path = embeddings_path or EMBEDDINGS_PATH
        self.model_name = model_name

        if df is not None:
            self.df = df
        else:
            print("Loading EventIQ dataset for Semantic Retrieval...")
            self.df = pd.read_csv(self.data_path)

        if "searchable_text" not in self.df.columns:
            self.df["searchable_text"] = self.df.apply(
                build_searchable_document,
                axis=1
            )
        print(f"Loaded {len(self.df)} events.")

        print(f"Loading sentence-transformer model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)

        if os.path.exists(self.embeddings_path):
            print(f"Loading persistent event embeddings from {self.embeddings_path}...")
            self.embeddings = np.load(self.embeddings_path)
            print(f"Loaded embeddings matrix with shape: {self.embeddings.shape}")
        else:
            print("Persistent embeddings not found. Generating new embeddings...")
            self.embeddings = self._generate_and_save_embeddings()

    def _generate_and_save_embeddings(self, batch_size=64):
        documents = self.df["searchable_text"].tolist()
        print(f"Encoding {len(documents)} event documents in batches of {batch_size}...")
        embeddings = self.model.encode(
            documents,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        os.makedirs(os.path.dirname(self.embeddings_path), exist_ok=True)
        np.save(self.embeddings_path, embeddings)
        print(f"Saved {len(embeddings)} embeddings to {self.embeddings_path}")
        return embeddings

    def search(self, query, top_k=10):
        if not query or not str(query).strip():
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

        query_embedding = self.model.encode(
            [str(query).strip()],
            normalize_embeddings=True
        )

        similarity_scores = cosine_similarity(
            query_embedding,
            self.embeddings
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

