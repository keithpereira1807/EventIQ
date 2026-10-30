import os
import sys

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Add project root to Python path
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


def main():

    print("Loading EventIQ dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Total events: {len(df)}")

    # Build searchable documents
    df["searchable_text"] = df.apply(
        build_searchable_document,
        axis=1
    )

    print("Searchable documents created.")

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        min_df=2,
        stop_words="english"
    )

    # Convert documents into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(
        df["searchable_text"]
    )

    print()
    print("TF-IDF model created successfully.")
    print(f"Documents: {tfidf_matrix.shape[0]}")
    print(f"Features: {tfidf_matrix.shape[1]}")

    # Show sample document
    print()
    print("Sample searchable document:")
    print(df.loc[0, "searchable_text"])

    # Show some learned vocabulary
    print()
    print("Sample TF-IDF vocabulary:")

    vocabulary = vectorizer.get_feature_names_out()

    print(vocabulary[:30])


if __name__ == "__main__":
    main()