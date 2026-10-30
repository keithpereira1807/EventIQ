import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

sys.path.append(PROJECT_ROOT)

from backend.retrieval.tfidf import TFIDFRetriever


def main():

    retriever = TFIDFRetriever()

    query = "free technology events in Pune"

    print()
    print("=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    results = retriever.search(
        query,
        top_k=10
    )

    print()

    for index, row in results.iterrows():

        print()
        print(f"Rank: {list(results.index).index(index) + 1}")
        print(f"Event ID: {row['event_id']}")
        print(f"Title: {row['title']}")
        print(f"Category: {row['category']}")
        print(f"City: {row['city']}")
        print(f"Date: {row['start_date']}")
        print(f"Price: {row['price']}")
        print(f"Free: {row['is_free']}")
        print(f"Score: {row['score']:.4f}")


if __name__ == "__main__":
    main()