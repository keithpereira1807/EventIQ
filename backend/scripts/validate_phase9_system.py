import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def http_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def http_post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def test_health():
    print("Testing /api/health...")
    status, data = http_get("/api/health")
    assert status == 200, f"Expected 200, got {status}"
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    print("✓ Health check passed.")

def test_events_count():
    print("Testing /api/events/count...")
    status, data = http_get("/api/events/count")
    assert status == 200
    assert data["event_count"] == 10000
    print(f"✓ Total event count: {data['event_count']}.")

def test_query_matrix():
    queries = [
        "machine learning events for students",
        "free technology workshops in Mumbai",
        "photography workshops for beginners",
        "career fairs in Delhi",
        "professional networking events in Pune",
    ]
    models = ["structured", "hybrid", "bm25", "tfidf", "semantic"]
    
    print("\n--- Testing 25 Query-Model Combinations ---")
    results_summary = {}

    for q in queries:
        results_summary[q] = {}
        for m in models:
            payload = {"query": q, "top_k": 10, "model": m}
            t0 = time.perf_counter()
            status, data = http_post("/api/search", payload)
            latency_ms = (time.perf_counter() - t0) * 1000
            
            assert status == 200, f"Query '{q}' with model '{m}' failed with status {status}"
            assert data["query"] == q
            assert data["model"] == m
            results = data["results"]
            assert len(results) == 10, f"Expected 10 results, got {len(results)}"
            
            # Check ranking stability and monotonicity
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True), f"Scores not descending for {m}: {scores}"
            ranks = [r["rank"] for r in results]
            assert ranks == list(range(1, 11)), f"Ranks not 1..10: {ranks}"
            
            # Check explainability for structured
            if m == "structured":
                for r in results:
                    assert "hybrid_score" in r and r["hybrid_score"] is not None
                    assert "structured_score" in r and r["structured_score"] is not None
                    assert "final_score" in r and r["final_score"] is not None
                    assert "matched_signals" in r
                    assert "signal_contributions" in r
                    expected_final = round(0.85 * r["hybrid_score"] + 0.15 * r["structured_score"], 4)
                    assert abs(r["final_score"] - expected_final) <= 0.0002, (
                        f"Decomposition mismatch: {r['final_score']} vs expected {expected_final}"
                    )
            elif m in ("bm25", "tfidf", "semantic"):
                for r in results:
                    assert r.get("structured_score") is None
                    assert r.get("matched_signals") is None
            
            results_summary[q][m] = {
                "top1_id": results[0]["event_id"],
                "top1_title": results[0]["title"],
                "top1_score": results[0]["score"],
                "latency_ms": round(latency_ms, 2)
            }
            print(f"✓ [{m:10s}] '{q[:30]}...' -> #{results[0]['rank']} {results[0]['title'][:25]} (score: {results[0]['score']:.4f}) in {latency_ms:.1f}ms")

    return results_summary

def test_edge_cases():
    print("\n--- Testing Search Edge Cases ---")
    
    # A. Normal query
    status, data = http_post("/api/search", {"query": "machine learning events", "top_k": 5, "model": "structured"})
    assert status == 200 and len(data["results"]) == 5
    print("✓ Normal query: 200 OK")
    
    # B. Empty query
    status, data = http_post("/api/search", {"query": "", "top_k": 5, "model": "structured"})
    assert status in (400, 422), f"Expected 400/422 for empty query, got {status}"
    print(f"✓ Empty query: correctly rejected with HTTP {status}")
    
    # C. Whitespace query
    status, data = http_post("/api/search", {"query": "     ", "top_k": 5, "model": "structured"})
    assert status in (400, 422), f"Expected 400/422 for whitespace query, got {status}"
    print(f"✓ Whitespace query: correctly rejected with HTTP {status}")
    
    # D. Very short query
    status, data = http_post("/api/search", {"query": "AI", "top_k": 5, "model": "structured"})
    assert status == 200 and len(data["results"]) == 5
    print("✓ Very short query ('AI'): 200 OK")
    
    # E. Longer query
    long_q = "I am looking for free technology workshops in Mumbai for students"
    status, data = http_post("/api/search", {"query": long_q, "top_k": 10, "model": "structured"})
    assert status == 200 and len(data["results"]) == 10
    print("✓ Long natural language query: 200 OK")
    
    # F. Unknown / non-matching query
    status, data = http_post("/api/search", {"query": "xyznonexistentgibberish9999", "top_k": 5, "model": "structured"})
    assert status == 200
    print(f"✓ Non-matching query: handled gracefully (returns {len(data['results'])} results with scores)")
    
    # G. Mixed case query
    status1, d_mixed = http_post("/api/search", {"query": "MaChInE LeArNiNg EvEnTs In MuMbAi", "top_k": 5, "model": "structured"})
    status2, d_lower = http_post("/api/search", {"query": "machine learning events in mumbai", "top_k": 5, "model": "structured"})
    assert status1 == 200 and status2 == 200
    assert d_mixed["results"][0]["event_id"] == d_lower["results"][0]["event_id"]
    print("✓ Mixed case handling: matches lowercase results identically")
    
    # H. Query with punctuation
    status, data = http_post("/api/search", {"query": "free, tech workshops! (in Mumbai)...", "top_k": 5, "model": "structured"})
    assert status == 200 and len(data["results"]) == 5
    print("✓ Query with punctuation: 200 OK")
    
    # I. top_k = 1
    status, data = http_post("/api/search", {"query": "technology conferences", "top_k": 1, "model": "structured"})
    assert status == 200 and len(data["results"]) == 1
    print("✓ top_k = 1: 200 OK")
    
    # J. top_k = 50
    status, data = http_post("/api/search", {"query": "technology conferences", "top_k": 50, "model": "structured"})
    assert status == 200 and len(data["results"]) == 50
    print("✓ top_k = 50: 200 OK")
    
    # K. invalid top_k
    status1, _ = http_post("/api/search", {"query": "technology conferences", "top_k": 0, "model": "structured"})
    assert status1 in (400, 422), f"Expected 400/422 for top_k=0, got {status1}"
    status2, _ = http_post("/api/search", {"query": "technology conferences", "top_k": 100, "model": "structured"})
    assert status2 in (400, 422), f"Expected 400/422 for top_k=100, got {status2}"
    print(f"✓ Invalid top_k (0, 100): rejected with HTTP {status1} / {status2}")
    
    # L. unsupported model
    status, _ = http_post("/api/search", {"query": "technology conferences", "top_k": 5, "model": "random_forest_retriever"})
    assert status in (400, 422), f"Expected 400/422 for unsupported model, got {status}"
    print(f"✓ Unsupported model: rejected with HTTP {status}")

def test_evaluation_consistency():
    print("\n--- Verifying Baseline Evaluation Consistency ---")
    status, api_eval = http_get("/api/evaluation")
    assert status == 200
    
    known_baselines = {
        "TF-IDF": {"precision_at_5": 0.3552, "precision_at_10": 0.2628, "recall_at_10": 0.1752, "f1": 0.2102, "mrr": 0.4820, "ndcg_at_10": 0.3101},
        "BM25": {"precision_at_5": 0.3860, "precision_at_10": 0.3250, "recall_at_10": 0.2167, "f1": 0.2600, "mrr": 0.4797, "ndcg_at_10": 0.3623},
        "Semantic (all-MiniLM-L6-v2)": {"precision_at_5": 0.2248, "precision_at_10": 0.1788, "recall_at_10": 0.1192, "f1": 0.1430, "mrr": 0.3729, "ndcg_at_10": 0.1955},
        "Hybrid (alpha=0.70)": {"precision_at_5": 0.3808, "precision_at_10": 0.3402, "recall_at_10": 0.2268, "f1": 0.2722, "mrr": 0.4915, "ndcg_at_10": 0.3689},
        "Structured Ranking (lambda=0.15)": {"precision_at_5": 0.3832, "precision_at_10": 0.3364, "recall_at_10": 0.2243, "f1": 0.2691, "mrr": 0.4991, "ndcg_at_10": 0.3731},
    }
    
    for row in api_eval["comparison"]:
        model_name = row["model"]
        assert model_name in known_baselines, f"Unexpected model {model_name}"
        expected = known_baselines[model_name]
        for metric, val in expected.items():
            actual = round(row[metric], 4)
            assert actual == val, f"Baseline mismatch for {model_name} on {metric}: actual {actual} != expected {val}"
            print(f"  ✓ {model_name} {metric}: {actual:.4f} == {val:.4f}")
    
    print("✓ All 5 model evaluation baselines are 100% consistent with recorded benchmarks.")

def test_performance():
    print("\n--- Measuring API Latency & Model Reuse ---")
    models = ["tfidf", "bm25", "semantic", "hybrid", "structured"]
    q = "machine learning conferences in Mumbai"
    
    for m in models:
        latencies = []
        for _ in range(5):
            t0 = time.perf_counter()
            status, data = http_post("/api/search", {"query": q, "top_k": 10, "model": m})
            assert status == 200
            lat = (time.perf_counter() - t0) * 1000
            latencies.append(lat)
        avg_lat = sum(latencies) / len(latencies)
        min_lat = min(latencies)
        max_lat = max(latencies)
        print(f"✓ Model {m:12s}: avg={avg_lat:.1f}ms, min={min_lat:.1f}ms, max={max_lat:.1f}ms (5 repeated requests)")

if __name__ == "__main__":
    test_health()
    test_events_count()
    test_query_matrix()
    test_edge_cases()
    test_evaluation_consistency()
    test_performance()
    print("\nAll Phase 9 validation tests passed successfully!")
