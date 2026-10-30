import os
import re
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.retrieval.hybrid import HybridRetriever

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")

# Predefined structured signal weights (as required by Phase 6 methodology)
DEFAULT_SIGNAL_WEIGHTS = {
    "city": 0.30,
    "category": 0.25,
    "is_free": 0.20,
    "event_type": 0.15,
    "audience": 0.10
}

DEFAULT_LAMBDA = 0.15


class QueryIntentParser:
    """
    Extracts structured intent from natural-language queries using
    the native vocabulary of the EventIQ dataset.
    """

    def __init__(self, data_path=None):
        path = data_path or DATA_PATH
        df = pd.read_csv(path)

        # 1. Cities: Canonical 20 cities, sorted by length descending so 'New Delhi' precedes 'Delhi'
        raw_cities = df["city"].dropna().unique().tolist()
        self.cities = sorted(raw_cities, key=lambda c: -len(c))

        # 2. Categories & Subcategories
        self.categories = sorted(df["category"].dropna().unique().tolist(), key=lambda c: -len(c))

        subcat_df = df[["subcategory", "category"]].dropna().drop_duplicates()
        self.subcat_to_cat = subcat_df.set_index("subcategory")["category"].to_dict()
        # Add explicit canonical acronym
        self.subcat_to_cat["AI"] = "Technology"

        # 3. Event Types (singular & plural forms)
        raw_types = df["event_type"].dropna().unique().tolist()
        self.event_types = sorted(raw_types, key=lambda e: -len(e))

        # 4. Audiences
        self.audiences = ["students", "beginners", "professionals"]

    def parse(self, query):
        """
        Parses query text and returns active structured intent signals.
        """
        if not query or not str(query).strip():
            return {}

        q_str = str(query).strip()
        intents = {}

        # City matching (word boundary, case-insensitive)
        for city in self.cities:
            pattern = r"\b" + re.escape(city) + r"\b"
            if re.search(pattern, q_str, re.IGNORECASE):
                intents["city"] = city
                break

        # Free intent
        if re.search(r"\bfree\b", q_str, re.IGNORECASE):
            intents["is_free"] = True

        # Audience matching
        for aud in self.audiences:
            pattern = r"\b" + re.escape(aud) + r"\b"
            if re.search(pattern, q_str, re.IGNORECASE):
                intents["audience"] = aud.capitalize()
                break

        # Event Type matching (supports singular and plural forms, e.g. workshop / workshops)
        for et in self.event_types:
            pattern = r"\b(" + re.escape(et) + r"|" + re.escape(et) + r"s)\b"
            if re.search(pattern, q_str, re.IGNORECASE):
                intents["event_type"] = et
                break

        # Category matching
        for cat in self.categories:
            pattern = r"\b" + re.escape(cat) + r"\b"
            if re.search(pattern, q_str, re.IGNORECASE):
                intents["category"] = cat
                break

        # If primary category wasn't found directly, search subcategories
        if "category" not in intents:
            for sub, parent_cat in sorted(self.subcat_to_cat.items(), key=lambda x: -len(x[0])):
                pattern = r"\b" + re.escape(sub) + r"\b"
                if re.search(pattern, q_str, re.IGNORECASE):
                    intents["category"] = parent_cat
                    intents["subcategory"] = sub
                    break

        return intents


class StructuredEventRanker:
    """
    Explainable structured ranking layer on top of HybridRetriever.
    
    Formula:
        FinalScore = (1 - lambda) * HybridScore + lambda * StructuredScore
    where:
        StructuredScore = (sum_{k in Active} w_k * Match_k) / (sum_{k in Active} w_k)
    """

    def __init__(
        self,
        hybrid_retriever=None,
        signal_weights=None,
        lambda_weight=DEFAULT_LAMBDA,
        data_path=None
    ):
        self.path = data_path or DATA_PATH
        self.hybrid_retriever = hybrid_retriever or HybridRetriever(alpha=0.70)
        self.signal_weights = signal_weights or DEFAULT_SIGNAL_WEIGHTS
        self.lambda_weight = float(lambda_weight)
        self.intent_parser = QueryIntentParser(data_path=self.path)
        self.df = self.hybrid_retriever.df

    def rank(self, query, top_k=10, lambda_weight=None):
        eff_lambda = self.lambda_weight if lambda_weight is None else float(lambda_weight)
        intents = self.intent_parser.parse(query)

        # 1. Retrieve hybrid scores across all 10,000 documents
        # Search returns top_k dataframe, but we need full-corpus hybrid scores for exact fusion
        q_str = "" if query is None else str(query).strip()
        if not q_str:
            empty_df = self.df.head(0).copy()
            empty_df["score"] = 0.0
            return empty_df

        # Get full-corpus normalized BM25
        query_tokens = [t for t in q_str.lower().split() if t]
        if not query_tokens:
            norm_bm25 = np.zeros(len(self.df), dtype=np.float64)
        else:
            raw_bm25 = np.array(
                self.hybrid_retriever.bm25_retriever.bm25.get_scores(query_tokens),
                dtype=np.float64
            )
            min_b = float(raw_bm25.min())
            max_b = float(raw_bm25.max())
            diff_b = max_b - min_b
            if diff_b < 1e-9:
                norm_bm25 = np.zeros_like(raw_bm25)
            else:
                norm_bm25 = (raw_bm25 - min_b) / diff_b

        # Get full-corpus semantic similarities
        query_emb = self.hybrid_retriever.semantic_retriever.model.encode(
            [q_str],
            normalize_embeddings=True
        )
        semantic_scores = (
            query_emb @ self.hybrid_retriever.semantic_retriever.embeddings.T
        ).flatten()

        # Hybrid scores (alpha = 0.70)
        alpha = self.hybrid_retriever.alpha
        hybrid_scores = alpha * norm_bm25 + (1.0 - alpha) * semantic_scores

        # 2. Evaluate active structured signals
        active_signals = [k for k in self.signal_weights if k in intents]
        total_active_weight = sum(self.signal_weights[k] for k in active_signals)

        num_events = len(self.df)
        match_arrays = {}

        if total_active_weight > 0:
            if "city" in intents:
                match_arrays["city"] = (self.df["city"] == intents["city"]).to_numpy(dtype=np.float64)
            if "category" in intents:
                cat_match = (self.df["category"] == intents["category"])
                if "subcategory" in intents:
                    cat_match = cat_match | (self.df["subcategory"] == intents["subcategory"])
                match_arrays["category"] = cat_match.to_numpy(dtype=np.float64)
            if "is_free" in intents:
                match_arrays["is_free"] = (self.df["is_free"] == True).to_numpy(dtype=np.float64)
            if "event_type" in intents:
                match_arrays["event_type"] = (self.df["event_type"] == intents["event_type"]).to_numpy(dtype=np.float64)
            if "audience" in intents:
                target_aud = intents["audience"].lower()
                match_arrays["audience"] = self.df["audience"].fillna("").str.lower().str.contains(
                    target_aud, regex=False
                ).to_numpy(dtype=np.float64)

            # Compute normalized structured score for each document
            weighted_match_sum = np.zeros(num_events, dtype=np.float64)
            for k in active_signals:
                weighted_match_sum += self.signal_weights[k] * match_arrays[k]

            structured_scores = weighted_match_sum / total_active_weight
        else:
            structured_scores = np.zeros(num_events, dtype=np.float64)

        # 3. Final convex combination
        final_scores = (1.0 - eff_lambda) * hybrid_scores + eff_lambda * structured_scores

        # 4. Extract Top-K
        top_indices = final_scores.argsort()[-top_k:][::-1]
        top_events = self.df.iloc[top_indices].copy()

        # 5. Build explainable breakdown for each result
        results = []
        for rank_pos, idx in enumerate(top_indices, start=1):
            row = self.df.iloc[idx]
            h_score = float(hybrid_scores[idx])
            s_score = float(structured_scores[idx])
            f_score = float(final_scores[idx])

            matched_dict = {}
            contrib_dict = {
                "hybrid_base": round((1.0 - eff_lambda) * h_score, 4)
            }

            if total_active_weight > 0:
                for k in active_signals:
                    is_match = bool(match_arrays[k][idx] > 0.5)
                    if is_match:
                        matched_dict[k] = intents[k]
                    signal_contrib = eff_lambda * (self.signal_weights[k] / total_active_weight) * float(match_arrays[k][idx])
                    contrib_dict[f"{k}_match"] = round(signal_contrib, 4)

            result_item = {
                "rank": rank_pos,
                "event_id": row["event_id"],
                "title": row["title"],
                "category": row["category"],
                "city": row["city"],
                "start_date": row["start_date"],
                "price": int(row["price"]),
                "is_free": bool(row["is_free"]),
                "final_score": round(f_score, 4),
                "hybrid_score": round(h_score, 4),
                "structured_score": round(s_score, 4),
                "matched_signals": matched_dict,
                "signal_contributions": contrib_dict
            }
            results.append(result_item)

        return results

