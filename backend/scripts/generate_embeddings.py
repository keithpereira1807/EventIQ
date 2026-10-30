import os
import sys
import time
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.preprocessing import build_searchable_document

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")
EMBEDDINGS_PATH = os.path.join(PROJECT_ROOT, "data", "event_embeddings.npy")
MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"Total events: {len(df)}")

    print("Building searchable documents...")
    df["searchable_text"] = df.apply(build_searchable_document, axis=1)

    print(f"Loading SentenceTransformer model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    documents = df["searchable_text"].tolist()
    print(f"Generating embeddings for {len(documents)} documents...")
    start_time = time.time()

    embeddings = model.encode(
        documents,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    elapsed = time.time() - start_time

    os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)

    print()
    print("=" * 60)
    print("EMBEDDINGS GENERATION COMPLETE")
    print("=" * 60)
    print(f"Model: {MODEL_NAME}")
    print(f"Documents encoded: {len(embeddings)}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"Matrix shape: {embeddings.shape}")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"File size on disk: {os.path.getsize(EMBEDDINGS_PATH) / (1024 * 1024):.2f} MB")
    print(f"Saved to: {EMBEDDINGS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()

