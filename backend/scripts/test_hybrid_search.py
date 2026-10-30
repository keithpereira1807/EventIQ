import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.hybrid import HybridRetriever


TEST_QUERIES = [
    "AI workshops in Mumbai",
    "machine learning events for students",
    "startup networking events in Bengaluru",
    "photography workshops for beginners",
    "free technology events in Pune"
]


def main():
    retriever = HybridRetriever(alpha=0.70)

    for query in TEST_QUERIES:
        print()
        print("=" * 70)
        print(f"QUERY: {query} (Hybrid alpha=0.70)")
        print("=" * 70)

        results = retriever.search(query, top_k=5)

        for rank, (index, row) in enumerate(results.iterrows(), start=1):
            print()
            print(f"Rank: {rank}")
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
