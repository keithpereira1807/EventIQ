import json
import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.structured_ranking import StructuredEventRanker


TEST_QUERIES = [
    "AI workshops in Mumbai",
    "machine learning events for students",
    "startup networking events in Bengaluru",
    "photography workshops for beginners",
    "free technology events in Pune"
]


def main():
    ranker = StructuredEventRanker()

    for query in TEST_QUERIES:
        print()
        print("=" * 80)
        print(f"QUERY: {query}")
        intents = ranker.intent_parser.parse(query)
        print(f"EXTRACTED INTENTS: {intents}")
        print("=" * 80)

        results = ranker.rank(query, top_k=5)

        for res in results:
            print()
            print(f"Rank {res['rank']}: [{res['event_id']}] {res['title']}")
            print(f"  Category: {res['category']} | City: {res['city']} | Date: {res['start_date']} | Free: {res['is_free']}")
            print(f"  Scores: Final={res['final_score']} (Hybrid={res['hybrid_score']}, Structured={res['structured_score']})")
            print(f"  Matched Signals: {res['matched_signals']}")
            print(f"  Contributions: {res['signal_contributions']}")


if __name__ == "__main__":
    main()

