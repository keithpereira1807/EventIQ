import json
import os
import sys
from typing import Any, Dict, List, Optional
import pandas as pd

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.app.database import get_connection
from backend.retrieval.tfidf import TFIDFRetriever
from backend.retrieval.bm25 import BM25Retriever
from backend.retrieval.semantic import SemanticRetriever
from backend.retrieval.hybrid import HybridRetriever
from backend.retrieval.structured_ranking import StructuredEventRanker

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluation")


class SearchService:
    """
    Singleton service managing in-memory retrieval models and database queries.
    Models and persistent embeddings are loaded once and reused across API requests.
    """

    _instance = None

    def __init__(self):
        print("Initializing SearchService and pre-loading retrieval models...")
        self.df = pd.read_csv(DATA_PATH)
        self.df_by_id = self.df.set_index("event_id").to_dict(orient="index")

        print("Loading TF-IDF model...")
        self.tfidf_retriever = TFIDFRetriever()

        print("Loading BM25 model...")
        self.bm25_retriever = BM25Retriever()

        print("Loading Semantic model...")
        self.semantic_retriever = SemanticRetriever()

        print("Loading Hybrid model (alpha=0.70)...")
        self.hybrid_retriever = HybridRetriever(
            alpha=0.70,
            bm25_retriever=self.bm25_retriever,
            semantic_retriever=self.semantic_retriever
        )

        print("Loading Structured Ranker (lambda=0.15)...")
        self.structured_ranker = StructuredEventRanker(
            hybrid_retriever=self.hybrid_retriever,
            lambda_weight=0.15
        )
        print("All retrieval models successfully loaded into SearchService.")

    @classmethod
    def get_instance(cls) -> "SearchService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def search(self, query: str, model_name: str = "structured", top_k: int = 10) -> Dict[str, Any]:
        """
        Executes query search using the specified retrieval model.
        """
        m = model_name.lower().strip()

        if m == "structured":
            structured_results = self.structured_ranker.rank(query, top_k=top_k)
            formatted = []
            for item in structured_results:
                e_id = item["event_id"]
                full_event = self.df_by_id.get(e_id, {})

                formatted.append({
                    "rank": item["rank"],
                    "event_id": e_id,
                    "title": item["title"],
                    "description": full_event.get("description"),
                    "category": item["category"],
                    "subcategory": full_event.get("subcategory"),
                    "city": item["city"],
                    "state": full_event.get("state"),
                    "venue": full_event.get("venue"),
                    "start_date": item["start_date"],
                    "start_time": full_event.get("start_time"),
                    "price": item["price"],
                    "currency": full_event.get("currency", "INR"),
                    "is_free": item["is_free"],
                    "organizer": full_event.get("organizer"),
                    "audience": full_event.get("audience"),
                    "rating": float(full_event.get("rating")) if full_event.get("rating") is not None else None,
                    "score": item["final_score"],
                    "hybrid_score": item["hybrid_score"],
                    "structured_score": item["structured_score"],
                    "final_score": item["final_score"],
                    "matched_signals": item["matched_signals"],
                    "signal_contributions": item["signal_contributions"]
                })

            return {
                "query": query,
                "model": m,
                "total_results": len(formatted),
                "results": formatted
            }

        # Otherwise: tfidf, bm25, semantic, hybrid
        if m == "tfidf":
            df_res = self.tfidf_retriever.search(query, top_k=top_k)
        elif m == "bm25":
            df_res = self.bm25_retriever.search(query, top_k=top_k)
        elif m == "semantic":
            df_res = self.semantic_retriever.search(query, top_k=top_k)
        elif m == "hybrid":
            df_res = self.hybrid_retriever.search(query, top_k=top_k, alpha=0.70)
        else:
            raise ValueError(f"Unknown model: {model_name}")

        formatted = []
        for rank_idx, (index, row) in enumerate(df_res.iterrows(), start=1):
            e_id = row["event_id"]
            full_event = self.df_by_id.get(e_id, {})
            score_val = round(float(row["score"]), 4)

            formatted.append({
                "rank": rank_idx,
                "event_id": e_id,
                "title": row["title"],
                "description": full_event.get("description"),
                "category": row["category"],
                "subcategory": full_event.get("subcategory"),
                "city": row["city"],
                "state": full_event.get("state"),
                "venue": full_event.get("venue"),
                "start_date": str(row["start_date"]),
                "start_time": full_event.get("start_time"),
                "price": int(row["price"]) if pd.notnull(row["price"]) else 0,
                "currency": full_event.get("currency", "INR"),
                "is_free": bool(row["is_free"]),
                "organizer": full_event.get("organizer"),
                "audience": full_event.get("audience"),
                "rating": float(full_event.get("rating")) if pd.notnull(full_event.get("rating")) else None,
                "score": score_val
            })

        return {
            "query": query,
            "model": m,
            "total_results": len(formatted),
            "results": formatted
        }

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single event by event_id from PostgreSQL, with in-memory fallback.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT event_id, title, description, category, subcategory, tags,
                       event_type, city, state, venue, address, latitude, longitude,
                       start_date, start_time, end_date, end_time, price, currency,
                       is_free, organizer, expected_attendees, audience, language, rating
                FROM events
                WHERE event_id = %s
                """,
                (event_id,)
            )
            row = cur.fetchone()
            cur.close()
            conn.close()

            if row:
                return {
                    "event_id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "category": row[3],
                    "subcategory": row[4],
                    "tags": row[5],
                    "event_type": row[6],
                    "city": row[7],
                    "state": row[8],
                    "venue": row[9],
                    "address": row[10],
                    "latitude": row[11],
                    "longitude": row[12],
                    "start_date": str(row[13]) if row[13] is not None else None,
                    "start_time": str(row[14]) if row[14] is not None else None,
                    "end_date": str(row[15]) if row[15] is not None else None,
                    "end_time": str(row[16]) if row[16] is not None else None,
                    "price": row[17],
                    "currency": row[18],
                    "is_free": row[19],
                    "organizer": row[20],
                    "expected_attendees": row[21],
                    "audience": row[22],
                    "language": row[23],
                    "rating": float(row[24]) if row[24] is not None else None
                }
        except Exception as e:
            print(f"PostgreSQL fetch failed for {event_id}: {e}")

        # Fallback to in-memory DataFrame
        if event_id in self.df_by_id:
            raw = self.df_by_id[event_id].copy()
            raw["event_id"] = event_id
            for date_col in ["start_date", "start_time", "end_date", "end_time"]:
                if date_col in raw and pd.notnull(raw[date_col]):
                    raw[date_col] = str(raw[date_col])
            if "rating" in raw and pd.notnull(raw["rating"]):
                raw["rating"] = float(raw["rating"])
            return raw

        return None

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Retrieves all categories and their event counts.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT category, COUNT(*) as cnt
                FROM events
                GROUP BY category
                ORDER BY cnt DESC
                """
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [{"category": r[0], "count": r[1]} for r in rows]
        except Exception:
            series = self.df["category"].value_counts()
            return [{"category": cat, "count": int(cnt)} for cat, cnt in series.items()]

    def get_locations(self) -> List[Dict[str, Any]]:
        """
        Retrieves all city locations and their event counts.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT city, state, COUNT(*) as cnt
                FROM events
                GROUP BY city, state
                ORDER BY cnt DESC
                """
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [{"city": r[0], "state": r[1], "count": r[2]} for r in rows]
        except Exception:
            grouped = self.df.groupby(["city", "state"]).size().reset_index(name="count")
            grouped = grouped.sort_values(by="count", ascending=False)
            return grouped.to_dict(orient="records")

    def get_evaluation(self) -> Dict[str, Any]:
        """
        Loads saved academic evaluation benchmarks from the evaluation/ directory.
        """
        eval_files = {
            "tfidf": "tfidf_results.json",
            "bm25": "bm25_results.json",
            "semantic": "semantic_results.json",
            "hybrid": "hybrid_results.json",
            "structured": "structured_ranking_results.json"
        }

        data = {}
        for key, fname in eval_files.items():
            fpath = os.path.join(EVAL_DIR, fname)
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    data[key] = json.load(f)
            else:
                data[key] = None

        # Build clean comparison table list for UI display
        comparison = []
        if data.get("tfidf"):
            d = data["tfidf"]
            comparison.append({
                "model": "TF-IDF",
                "precision_at_5": d.get("precision_at_5"),
                "precision_at_10": d.get("precision_at_10"),
                "recall_at_10": d.get("recall_at_10"),
                "f1": d.get("f1"),
                "mrr": d.get("mrr"),
                "ndcg_at_10": d.get("ndcg_at_10")
            })
        if data.get("bm25"):
            d = data["bm25"]
            comparison.append({
                "model": "BM25",
                "precision_at_5": d.get("precision_at_5"),
                "precision_at_10": d.get("precision_at_10"),
                "recall_at_10": d.get("recall_at_10"),
                "f1": d.get("f1"),
                "mrr": d.get("mrr"),
                "ndcg_at_10": d.get("ndcg_at_10")
            })
        if data.get("semantic"):
            d = data["semantic"]
            comparison.append({
                "model": "Semantic (all-MiniLM-L6-v2)",
                "precision_at_5": d.get("precision_at_5"),
                "precision_at_10": d.get("precision_at_10"),
                "recall_at_10": d.get("recall_at_10"),
                "f1": d.get("f1"),
                "mrr": d.get("mrr"),
                "ndcg_at_10": d.get("ndcg_at_10")
            })
        if data.get("hybrid") and "best_metrics" in data["hybrid"]:
            d = data["hybrid"]["best_metrics"]
            comparison.append({
                "model": "Hybrid (alpha=0.70)",
                "precision_at_5": d.get("precision_at_5"),
                "precision_at_10": d.get("precision_at_10"),
                "recall_at_10": d.get("recall_at_10"),
                "f1": d.get("f1"),
                "mrr": d.get("mrr"),
                "ndcg_at_10": d.get("ndcg_at_10")
            })
        if data.get("structured") and "metrics" in data["structured"]:
            d = data["structured"]["metrics"]
            comparison.append({
                "model": "Structured Ranking (lambda=0.15)",
                "precision_at_5": d.get("precision_at_5"),
                "precision_at_10": d.get("precision_at_10"),
                "recall_at_10": d.get("recall_at_10"),
                "f1": d.get("f1"),
                "mrr": d.get("mrr"),
                "ndcg_at_10": d.get("ndcg_at_10")
            })

        return {
            "comparison": comparison,
            "raw_benchmarks": data
        }

