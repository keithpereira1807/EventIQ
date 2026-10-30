import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.app.main import app


def run_tests():
    print("=" * 80)
    print("EVENTIQ API ENDPOINT VERIFICATION SUITE")
    print("=" * 80)

    client = TestClient(app)

    # 1. /api/health
    print("\n[1] Testing GET /api/health...")
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    print("  Status:", resp.status_code, "| Response:", data)
    assert data["status"] == "ok" and data["database"] == "connected"

    # 2. /api/events/count
    print("\n[2] Testing GET /api/events/count...")
    resp = client.get("/api/events/count")
    assert resp.status_code == 200
    data = resp.json()
    print("  Status:", resp.status_code, "| Response:", data)
    assert data["event_count"] == 10000

    # 3. /api/search across all 5 models
    models = ["tfidf", "bm25", "semantic", "hybrid", "structured"]
    query = "free technology events in Pune"

    for m in models:
        print(f"\n[3-{m}] Testing POST /api/search with model='{m}'...")
        payload = {"query": query, "model": m, "top_k": 3}
        resp = client.post("/api/search", json=payload)
        assert resp.status_code == 200, f"Search failed for {m}: {resp.text}"
        data = resp.json()
        print(f"  Model: {data['model']}, Results Count: {data['total_results']}")
        top1 = data["results"][0]
        print(f"  Rank 1: [{top1['event_id']}] {top1['title']} (Score: {top1['score']})")
        if m == "structured":
            assert "structured_score" in top1 and "signal_contributions" in top1
            print(f"  Structured Breakdown: Final={top1['final_score']}, Hybrid={top1['hybrid_score']}, Struct={top1['structured_score']}")
            print(f"  Matched signals: {top1['matched_signals']}")

    # 4. Default search behavior (omitting model & top_k)
    print("\n[4] Testing POST /api/search default parameters (no model, no top_k)...")
    resp = client.post("/api/search", json={"query": "AI workshops in Mumbai"})
    assert resp.status_code == 200
    data = resp.json()
    print(f"  Default model used: {data['model']}, Default count: {data['total_results']}")
    assert data["model"] == "structured"
    assert data["total_results"] == 10

    # 5. Different top_k values
    print("\n[5] Testing POST /api/search with top_k=5 and top_k=25...")
    for k in [5, 25]:
        resp = client.post("/api/search", json={"query": "startup networking events", "top_k": k})
        assert resp.status_code == 200
        assert resp.json()["total_results"] == k
        print(f"  Requested top_k={k} -> Returned count={resp.json()['total_results']}")

    # 6. Validation error: Empty query
    print("\n[6] Testing validation: Empty query...")
    resp = client.post("/api/search", json={"query": "   ", "model": "structured"})
    print("  Status:", resp.status_code, "| Response:", resp.json())
    assert resp.status_code == 422

    # 7. Validation error: Invalid model
    print("\n[7] Testing validation: Invalid model...")
    resp = client.post("/api/search", json={"query": "test query", "model": "unsupported_model"})
    print("  Status:", resp.status_code, "| Response:", resp.json())
    assert resp.status_code == 422

    # 8. Validation error: Invalid top_k (< 1 and > 50)
    print("\n[8] Testing validation: top_k=0 and top_k=100...")
    resp0 = client.post("/api/search", json={"query": "test", "top_k": 0})
    assert resp0.status_code == 422
    resp100 = client.post("/api/search", json={"query": "test", "top_k": 100})
    assert resp100.status_code == 422
    print("  top_k=0 status:", resp0.status_code, "| top_k=100 status:", resp100.status_code)

    # 9. GET /api/events/{event_id} (Valid)
    print("\n[9] Testing GET /api/events/EVT000001...")
    resp = client.get("/api/events/EVT000001")
    assert resp.status_code == 200
    data = resp.json()
    print(f"  Status: {resp.status_code} | Event ID: {data['event_id']} | Title: {data['title']}")
    print(f"  City: {data['city']}, Price: {data['price']}, Rating: {data['rating']}")

    # 10. GET /api/events/{event_id} (Nonexistent)
    print("\n[10] Testing GET /api/events/EVT999999 (Nonexistent)...")
    resp = client.get("/api/events/EVT999999")
    print("  Status:", resp.status_code, "| Detail:", resp.json())
    assert resp.status_code == 404

    # 11. GET /api/categories
    print("\n[11] Testing GET /api/categories...")
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    cats = resp.json()
    print(f"  Categories count: {len(cats)} | Top 3 categories: {cats[:3]}")
    assert len(cats) >= 20

    # 12. GET /api/locations
    print("\n[12] Testing GET /api/locations...")
    resp = client.get("/api/locations")
    assert resp.status_code == 200
    locs = resp.json()
    print(f"  Locations count: {len(locs)} | Top 3 locations: {locs[:3]}")
    assert len(locs) >= 20

    # 13. GET /api/evaluation
    print("\n[13] Testing GET /api/evaluation...")
    resp = client.get("/api/evaluation")
    assert resp.status_code == 200
    eval_data = resp.json()
    print(f"  Comparison rows: {len(eval_data['comparison'])}")
    for row in eval_data["comparison"]:
        print(f"    - {row['model']:<35} NDCG@10: {row['ndcg_at_10']}, MRR: {row['mrr']}")
    assert len(eval_data["comparison"]) == 5

    # 14. GET /docs and /openapi.json
    print("\n[14] Testing Swagger /docs and OpenAPI /openapi.json...")
    docs_resp = client.get("/docs")
    openapi_resp = client.get("/openapi.json")
    assert docs_resp.status_code == 200
    assert openapi_resp.status_code == 200
    print(f"  /docs status: {docs_resp.status_code} | /openapi.json status: {openapi_resp.status_code}")
    openapi_json = openapi_resp.json()
    print(f"  OpenAPI version: {openapi_json['openapi']} | App title: {openapi_json['info']['title']}")

    print("\n" + "=" * 80)
    print("ALL API ENDPOINT TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()

