import time
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath("."))

print("Starting latency measurement...")
t0 = time.perf_counter()
from backend.app.services.search_service import SearchService
s = SearchService.get_instance()
t1 = time.perf_counter()
cold_start_ms = (t1 - t0) * 1000
print(f"SearchService Cold Start: {cold_start_ms:.1f}ms")

# First search (Cold query)
t0 = time.perf_counter()
res1 = s.search("free machine learning workshops in Mumbai", top_k=10, model_name="structured")
t1 = time.perf_counter()
first_search_ms = (t1 - t0) * 1000
print(f"First Search (Cold query): {first_search_ms:.1f}ms")

# Warm search (10 iterations)
times = []
for _ in range(10):
    t0 = time.perf_counter()
    res = s.search("free machine learning workshops in Mumbai", top_k=10, model_name="structured")
    times.append((time.perf_counter() - t0) * 1000)

avg_warm = sum(times) / len(times)
min_warm = min(times)
max_warm = max(times)
print(f"Warm Searches (10 iterations): avg={avg_warm:.1f}ms, min={min_warm:.1f}ms, max={max_warm:.1f}ms")

for m in ["tfidf", "bm25", "semantic", "hybrid", "structured"]:
    m_times = []
    for _ in range(5):
        t0 = time.perf_counter()
        r = s.search("career fairs in Delhi", top_k=10, model_name=m)
        m_times.append((time.perf_counter() - t0) * 1000)
    print(f"Model {m:12s}: avg={sum(m_times)/len(m_times):.1f}ms (min={min(m_times):.1f}ms, max={max(m_times):.1f}ms)")
