"""
Part 3 of EventIQ Viva Preparation Guide: Sections 21 to 32
Exhaustive Academic & Practical Explanations
"""
from docx.shared import Pt, RGBColor
from viva_guide_builder import (
    add_heading_1, add_heading_2, add_heading_3,
    add_p, add_bullet, add_callout, add_formula_box,
    add_table_styled, add_diagram_box,
    ROYAL_BLUE, NAVY, TEXT_DARK, SLATE
)

def build_section_21(doc):
    add_heading_1(doc, "SECTION 21 — WHY DIFFERENT MODELS PERFORM DIFFERENTLY")
    add_p(doc, "A critical requirement for an academic thesis defense is proving an understanding of WHY the retrieval models behave differently across the benchmark:")

    add_heading_2(doc, "21.1 The Theoretical Trade-Offs")
    add_bullet(doc, "Probabilistic term saturation and document length normalization make BM25 the strongest model for immediate top-5 lexical accuracy. When a user enters precise keywords, BM25 ensures exact-match documents are placed in slots #1 to #5.", bold_prefix="1. Why BM25 achieves the highest Precision@5 (0.3860): ")
    add_bullet(doc, "Min-Max score normalization allows dense vector semantics to rescue relevant documents that lack exact query terms. By evaluating across the full 10,000 documents, Hybrid Retrieval expands coverage, capturing more total relevant items in the top-10 slots than any other architecture.", bold_prefix="2. Why Hybrid Retrieval achieves highest Recall@10 (0.2268) & F1 (0.2722): ")
    add_bullet(doc, "Top-heavy metrics like NDCG@10 and MRR severely penalize systems when relevant items appear at ranks 6–10 instead of 1–3. Structured ranking detects exact constraint satisfaction (e.g. matching city='Mumbai' and admission='free') and applies a soft additive boost that pushes these perfect matches directly into Rank #1 and #2. This dramatically boosts reciprocal rank and graded logarithmic gain.", bold_prefix="3. Why Structured Ranking achieves highest MRR (0.4991) & NDCG@10 (0.3731): ")
    add_bullet(doc, "Promoting events based on structured signals (e.g. city and admission) occasionally pushes a broad topical match from rank 10 down to rank 11. Consequently, P@10 drops negligibly from 0.3402 to 0.3364 (-0.0038), while top-rank quality metrics jump significantly (+1.5% MRR, +1.1% NDCG). In Information Retrieval, this is a well-known, highly desirable trade-off: users rarely inspect items beyond rank 3, making MRR and NDCG far more critical for user satisfaction than raw 10th-position precision.", bold_prefix="4. Why Structured Ranking has slightly lower P@10 than Hybrid: ")

    add_callout(doc, "Golden Rule for Viva Defense",
        "Never say 'Structured Ranking is better in everything.'\n"
        "Examiners will immediately challenge you. The correct statement is: 'No single model dominates every metric. BM25 leads in immediate P@5. Hybrid retrieval leads in full-corpus Recall@10 and balanced F1. Structured ranking optimizes top-rank satisfaction, leading in MRR and NDCG@10. This demonstrates the classic trade-off between lexical precision, semantic recall, and intent-aware re-ranking.'",
        "teacher"
    )

def build_section_22(doc):
    add_heading_1(doc, "SECTION 22 — PHASE-BY-PHASE DEVELOPMENT HISTORY")
    add_p(doc, "EventIQ was built incrementally across nine rigorous development phases:")

    phases = [
        ("Phase 1: Dataset & PostgreSQL Foundation", "Loaded 10,000 synthetic events into PostgreSQL, created normalized relational schemas and B-tree indexes, verified database connectivity."),
        ("Phase 2: TF-IDF Retrieval Baseline", "Built searchable multi-field document representation, trained scikit-learn TfidfVectorizer (n-grams 1-2, sublinear tf), established baseline evaluation metrics (P@5=0.3552, NDCG=0.3101)."),
        ("Phase 3: Okapi BM25 Retrieval", "Implemented rank-bm25 BM25Okapi (k1=1.5, b=0.75), tokenized 10,000 documents, achieved +16.8% gain in NDCG@10 (0.3623) and superior P@5 (0.3860)."),
        ("Phase 4: Dense Semantic Retrieval", "Integrated Sentence-Transformers (all-MiniLM-L6-v2), precomputed 10,000 document embeddings into persistent binary artifact `data/event_embeddings.npy` (15.3MB), implemented vectorized cosine similarity."),
        ("Phase 5: Hybrid Score-Level Fusion", "Aligned BM25 and semantic scores, implemented per-query Min-Max normalization, executed grid search across alpha values [0.25, 0.50, 0.60, 0.70, 0.75], identified alpha=0.70 as optimal for Recall@10 (0.2268) and F1 (0.2722)."),
        ("Phase 6: Structured Intent Ranking", "Constructed vocabulary-driven intent extraction engine across city, category, admission, event type, and audience; implemented soft additive re-ranking at lambda=0.15, achieving peak MRR (0.4991) and NDCG@10 (0.3731)."),
        ("Phase 7: FastAPI Search & Event API", "Built high-performance asynchronous REST API, implemented Pydantic input/output schemas, singleton SearchService in-memory caching, and comprehensive error sanitization."),
        ("Phase 8: React + Vite Frontend", "Developed modern academic dark-theme user interface, interactive multi-model search, inline score explainability panels, dynamic faceted sidebar, and Recharts evaluation dashboard."),
        ("Phase 9: Final Integration & Hardening", "Executed comprehensive 25 query-model benchmark verification, edge-case testing, latency profiling, baseline invariance checks, dynamic facet hardening, and complete documentation packaging.")
    ]
    for p_name, p_desc in phases:
        add_bullet(doc, p_desc, bold_prefix=f"{p_name}: ")

def build_section_23(doc):
    add_heading_1(doc, "SECTION 23 — SECURITY & CONFIGURATION AUDIT")
    add_p(doc, "EventIQ was subjected to strict security review during Phase 9:")
    add_bullet(doc, "Database credentials reside exclusively in `.env` and are never committed to version control. The repository tracks only `.env.example` with placeholder credentials.", bold_prefix="1. Zero Hardcoded Credentials: ")
    add_bullet(doc, "FastAPI global exception handlers intercept all validation and unexpected runtime errors, returning sanitized JSON payloads without revealing server directory structures, database queries, or stack traces.", bold_prefix="2. Stack Trace Sanitization: ")
    add_bullet(doc, "Permissive `allow_origins=['*']` is enabled for local inter-port communication between Vite (5173) and FastAPI (8000). Production deployment would restrict origins to specific domain names.", bold_prefix="3. CORS Configuration: ")
    add_bullet(doc, "The React build artifact contains zero API secrets, database passwords, or private environment variables.", bold_prefix="4. Frontend Build Security: ")

def build_section_24(doc):
    add_heading_1(doc, "SECTION 24 — PERFORMANCE BENCHMARKING")
    add_p(doc, "Latency benchmarks were recorded in a local development environment (Python 3.12, Windows, CPU inference):")
    
    headers = ["Component / Operation", "Measured Latency", "Operational Nature", "Technical Notes"]
    rows = [
        ["SearchService Cold Start", "17.4 seconds", "One-time boot operation", "Loads TF-IDF vectorizer, builds BM25 index, loads transformer neural weights, memory-maps 10k embeddings."],
        ["First Search (Cold Query)", "50.3 ms", "First request", "Initial query encoding and index traversal."],
        ["Warm Search (10 iterations)", "33.1 ms average", "Steady-state runtime", "Min: 30.0ms, Max: 35.3ms across repeated requests."],
        ["TF-IDF Search", "22.6 ms average", "Lexical retrieval", "Sparse dot product via scikit-learn."],
        ["BM25 Search", "15.7 ms average", "Probabilistic retrieval", "Fastest standalone engine; pure NumPy token scoring."],
        ["Semantic Search", "30.9 ms average", "Dense neural retrieval", "Query encoding via MiniLM + matrix multiplication."],
        ["Hybrid Fusion", "27.7 ms average", "Composite retrieval", "Min-Max normalization + convex combination."],
        ["Structured Ranking", "29.2 ms average", "Full re-ranking pipeline", "Hybrid search + vocabulary intent boost."],
        ["Vite Frontend Boot", "534 ms", "Local client dev server", "Instant ES module serving."]
    ]
    add_table_styled(doc, headers, rows, [1.5, 1.1, 1.4, 2.8])

def build_section_25(doc):
    add_heading_1(doc, "SECTION 25 — CURRENT LIMITATIONS")
    add_p(doc, "A mature academic project acknowledges its real engineering boundaries:")
    add_bullet(doc, "EventIQ detects categorical and spatial intent but does not parse complex temporal expressions (e.g., 'next weekend', 'in March', 'tomorrow'). Dates must currently be filtered post-retrieval.", bold_prefix="1. Absence of Temporal NLP Parsing: ")
    add_bullet(doc, "The 10,000 document embeddings are held in RAM as a float32 NumPy matrix (15.3MB). While optimal for 10k documents (~30ms), scaling to 10 million events would exhaust memory and require Approximate Nearest Neighbor (ANN) indexers.", bold_prefix="2. In-Memory Dense Matrix Scaling: ")
    add_bullet(doc, "The 10,000 events are synthetic representations. While carefully modeled on Indian metros, they lack the messy, unstructured colloquialisms found in real-world user-generated event listings.", bold_prefix="3. Synthetic Benchmark Scope: ")

def build_section_26(doc):
    add_heading_1(doc, "SECTION 26 — FUTURE ENHANCEMENTS")
    add_p(doc, "The following enhancements represent natural extensions of the EventIQ architecture:")
    add_bullet(doc, "Integrate spaCy or Duckling to parse relative temporal expressions ('this Saturday', 'first week of November') and map them to ISO SQL timestamp ranges.", bold_prefix="1. Temporal Query Understanding: ")
    add_bullet(doc, "Migrate the in-memory embedding matrix to PostgreSQL pgvector using HNSW (Hierarchical Navigable Small World) indexing or FAISS for sub-millisecond retrieval across millions of vectors.", bold_prefix="2. Scalable ANN Vector Indexing: ")
    add_bullet(doc, "Replace manual linear blending (λ=0.15) with an ML-trained ranking model (e.g. LambdaMART, XGBoost Ranker) trained on user click-through and dwell-time logs.", bold_prefix="3. Learning-to-Rank (LTR): ")
    add_bullet(doc, "Incorporate user past attendance, preferences, and geolocation into the scoring equation.", bold_prefix="4. User Personalization: ")
    add_bullet(doc, "Deploy multilingual sentence transformers (e.g. `paraphrase-multilingual-MiniLM-L12-v2`) to support event discovery in Hindi, Marathi, and Tamil.", bold_prefix="5. Multilingual Event Discovery: ")

def build_section_27(doc):
    add_heading_1(doc, "SECTION 27 — COMPLETE LIVE DEMONSTRATION SCRIPT")
    add_p(doc, "Follow this exact step-by-step walkthrough during your viva presentation:")

    steps = [
        ("Step 1: System Boot & Verification",
         "CLICK: Open browser at http://localhost:5173.\n"
         "SHOW: Point to top-right header showing '● API Online | 10,000 Events'.\n"
         "SAY: 'EventIQ is connected live to our FastAPI backend and PostgreSQL database containing 10,000 indexed event listings.'"),
        ("Step 2: Enter Primary Demonstration Query",
         "CLICK: Type 'free technology workshops in Mumbai' or click the query chip.\n"
         "SHOW: The 10 ranked result cards rendered in under 40 milliseconds.\n"
         "SAY: 'Notice that our default engine is Structured Ranking. The top results are technology workshops located in Mumbai with free admission.'"),
        ("Step 3: Demonstrate Score Explainability",
         "CLICK: Click 'Explain Score' on Result #1.\n"
         "SHOW: The mathematical formula, decomposed scores, active matched signals, and green contribution bars.\n"
         "SAY: 'Unlike black-box search engines, EventIQ provides complete explainability. You can see the Final Score decomposed into 85% Hybrid Score and 15% Structured Score, with exact points awarded for matching city, category, free admission, and event type.'"),
        ("Step 4: Demonstrate Model Comparisons",
         "CLICK: Click 'BM25 Lexical', then 'Semantic Vector', then 'Hybrid Fusion'.\n"
         "SHOW: How rankings shift based on the underlying scoring logic.\n"
         "SAY: 'When switching to BM25, exact keyword tokens govern rank. Switching to Semantic captures conceptual relevance. Hybrid fusion at alpha=0.70 combines the strengths of both.'"),
        ("Step 5: Present the Evaluation Dashboard",
         "CLICK: Navigate to 'Evaluation Benchmarks' tab.\n"
         "SHOW: The academic comparison table and three Recharts graphs.\n"
         "SAY: 'We evaluated all five models across 500 test queries. Notice that Structured Ranking achieves the highest NDCG@10 (0.3731) and MRR (0.4991), while Hybrid achieves the highest Recall@10 (0.2268) and F1 (0.2722), and BM25 achieves peak Precision@5 (0.3860).'"),
        ("Step 6: Show System Architecture",
         "CLICK: Navigate to 'System Architecture' tab.\n"
         "SHOW: The multi-stage pipeline cards and ground-truth dataset specifications.\n"
         "SAY: 'Our system adheres to standard TREC Cranfield evaluation methodology over 7,500 graded relevance judgments.'")
    ]
    for title, script in steps:
        add_callout(doc, title, script, "tip")

    add_heading_2(doc, "27.1 Recommended Backup Demonstration Queries")
    add_bullet(doc, "Tests category ('Photography'), audience ('Beginners'), and city intent.", bold_prefix="1. 'photography workshops for beginners in Mumbai': ")
    add_bullet(doc, "Tests event type ('Career Fair') and city intent.", bold_prefix="2. 'career fairs in Delhi': ")
    add_bullet(doc, "Tests audience ('Developers', 'Students') and location intent.", bold_prefix="3. 'blockchain hackathons for students in Hyderabad': ")
    add_bullet(doc, "Tests leisure category and regional venue retrieval.", bold_prefix="4. 'music festivals in Goa': ")

def build_section_28(doc):
    add_heading_1(doc, "SECTION 28 — EXHAUSTIVE VIVA VOCE QUESTIONS & ANSWERS (60+ QUESTIONS)")
    add_p(doc, "The following 60+ questions cover every major theoretical, technical, and architectural topic likely to be raised by university examiners.")

    qas = [
        # Category A: Basic Project Questions
        ("Q1. What is EventIQ in one sentence?",
         "EventIQ is an Intelligent Information Retrieval and Ranking System that accepts conversational event queries and ranks events using lexical, semantic, hybrid, and structured intent algorithms."),
        ("Q2. Why is event search harder than standard web search?",
         "Event queries have strict multi-faceted constraints—spatial location, temporal dates, price, audience, and category. A web page matching 'tech conference' is relevant anywhere; an event matching 'tech conference' in Delhi is useless to someone in Mumbai."),
        ("Q3. What is the difference between search and recommendation?",
         "Search is query-driven information retrieval satisfying an explicit user information need. Recommendation is preference-driven matching based on user history without an active search query."),
        
        # Category B: Information Retrieval Fundamentals
        ("Q4. What is the Cranfield Evaluation Paradigm?",
         "A standardized methodology in Information Retrieval consisting of three components: a document corpus, a set of test queries, and human/expert ground-truth relevance assessments. EventIQ follows this with 10k events, 500 queries, and 7,500 judgments."),
        ("Q5. What is the Vocabulary Mismatch Problem?",
         "The phenomenon where users express a concept using different words than the document author (e.g. 'coding' vs 'programming'). Lexical search fails on mismatch; semantic search resolves it."),
        ("Q6. What is a Searchable Document?",
         "A concatenated textual representation combining multiple metadata fields (title, description, category, subcategory, tags) into a single unified text string for indexing."),

        # Category C: TF-IDF
        ("Q7. What does TF-IDF stand for and what is its intuition?",
         "Term Frequency-Inverse Document Frequency. Words frequent in a specific document get high weight, but words frequent across the entire corpus get discounted because they lack discriminative power."),
        ("Q8. Why did you use Sublinear Term Frequency?",
         "Because a document mentioning a term 20 times is not 20 times more relevant than one mentioning it once. 1 + log(tf) dampens the impact of repetitive words."),
        ("Q9. Why did you use n-grams (1, 2)?",
         "To capture compound terminology like 'machine learning' and 'data science' as distinct bigram tokens alongside unigrams."),

        # Category D: BM25
        ("Q10. Why is BM25 better than TF-IDF?",
         "BM25 incorporates term frequency saturation (preventing term repetition abuse) and document length normalization (penalizing excessively verbose documents)."),
        ("Q11. What do k1 and b represent in BM25?",
         "k1 (1.5) controls term frequency saturation non-linearity. b (0.75) controls the strength of document length normalization."),
        ("Q12. What was the exact gain of BM25 over TF-IDF in EventIQ?",
         "BM25 improved P@5 from 0.3552 to 0.3860 (+8.7%) and improved NDCG@10 from 0.3101 to 0.3623 (+16.8%)."),

        # Category E: Semantic Retrieval
        ("Q13. How does Sentence-Transformers work?",
         "It uses a Siamese neural network architecture based on BERT to generate fixed-length dense vector embeddings where semantically similar texts have high cosine similarity."),
        ("Q14. What model did you use and what is its vector dimension?",
         "We used all-MiniLM-L6-v2 which produces 384-dimensional dense floating-point vector embeddings."),
        ("Q15. Why didn't you re-compute embeddings on every search?",
         "Embedding 10,000 documents takes ~2.5 minutes on CPU. We precomputed the (10000, 384) matrix once into data/event_embeddings.npy and load it into RAM in 50ms."),

        # Category F: Hybrid Retrieval
        ("Q16. Why do you combine BM25 and Semantic Retrieval?",
         "BM25 provides exact keyword and named entity precision, while semantic retrieval provides conceptual synonym recall. Hybrid fusion combines both strengths."),
        ("Q17. Why is Min-Max normalization necessary before score fusion?",
         "BM25 scores are unbounded positive numbers (e.g. 0 to 18), while semantic scores are bounded in [-1, 1]. Without normalization, BM25 would completely dominate semantic scores."),
        ("Q18. What is the hybrid fusion formula in EventIQ?",
         "HybridScore = α * BM25_norm + (1 - α) * SemanticScore, with α = 0.70."),
        ("Q19. Why was α = 0.70 chosen?",
         "Empirical grid search across alphas [0.25, 0.50, 0.60, 0.70, 0.75] proved α=0.70 yields the highest P@10 (0.3402), highest Recall@10 (0.2268), and highest F1 (0.2722)."),

        # Category G: Structured Ranking
        ("Q20. What is Structured Ranking?",
         "A query-aware re-ranking layer that extracts structured constraints (city, category, admission, event type, audience) from the query and applies an explainable boost."),
        ("Q21. How are intent signals extracted without hardcoded rules?",
         "By checking candidate query tokens dynamically against the vocabulary stored in the PostgreSQL database (events.city, events.category)."),
        ("Q22. What is the final ranking formula?",
         "FinalScore = 0.85 * HybridScore + 0.15 * StructuredScore, using λ = 0.15."),
        ("Q23. Why is λ only 0.15 instead of 0.50?",
         "Because topical relevance (Hybrid) must remain the primary ranking foundation. A high λ would rank irrelevant events high simply because they matched the city or were free."),

        # Category H: FastAPI Backend
        ("Q24. Why did you choose FastAPI over Flask or Django?",
         "FastAPI provides native asynchronous execution, automatic Swagger UI documentation, and high-performance validation via Pydantic."),
        ("Q25. How do you prevent reloading models on every request?",
         "We implemented the SearchService Singleton pattern. Models are instantiated once on server boot and cached permanently in memory."),
        ("Q26. How are errors handled in the API?",
         "FastAPI exception handlers intercept RequestValidationError and return clean JSON payloads (HTTP 422/500) without stack traces."),

        # Category I: React Frontend
        ("Q27. Why React and Vite?",
         "React provides component-based UI state management. Vite provides ultra-fast development builds and efficient ES module bundling."),
        ("Q28. Is any ranking logic implemented in React?",
         "No. The frontend is strictly an API consumer. All retrieval, normalization, fusion, and ranking calculations occur exclusively on the backend."),
        ("Q29. How does facet filtering work in the UI?",
         "Facet filters aggregate categories, cities, and pricing across the currently retrieved candidate set and filter them client-side."),

        # Category J: PostgreSQL Database
        ("Q30. What tables exist in PostgreSQL?",
         "Three tables: events (10,000 listings), queries (500 query topics), and relevance (7,500 graded relevance judgments)."),
        ("Q31. What indexes are created?",
         "B-tree indexes on city, category, is_free, event_type, and audience to accelerate candidate filtering."),

        # Category K: Evaluation Metrics
        ("Q32. What is NDCG@10 and why is it important?",
         "Normalized Discounted Cumulative Gain at rank 10. It accounts for graded relevance (0-3) and penalizes systems when relevant items appear at lower ranks using logarithmic decay."),
        ("Q33. What is MRR?",
         "Mean Reciprocal Rank: average of 1 / rank of the first relevant document. Measures how fast the user encounters a good result."),
        ("Q34. What is the difference between Precision and Recall?",
         "Precision is the fraction of retrieved items that are relevant. Recall is the fraction of all relevant items in the corpus that were retrieved."),

        # Category L: Security & Quality
        ("Q35. How are database credentials protected?",
         "Stored in .env which is excluded by .gitignore. Only .env.example with placeholder strings is tracked."),
        ("Q36. Are stack traces exposed in API errors?",
         "No. All endpoints catch exceptions and return sanitized error descriptions."),

        # Category M: Performance
        ("Q37. What is the warm search latency of EventIQ?",
         "Approximately 33.1 milliseconds on standard CPU hardware."),
        ("Q38. Why does the server take 17.4 seconds to start?",
         "Because it preloads the TF-IDF matrix, builds the BM25 index, loads transformer neural weights, and memory-maps 10,000 dense embeddings."),

        # Category N: Limitations & Future Work
        ("Q39. What is a key limitation of EventIQ?",
         "It does not parse temporal expressions like 'next weekend' or 'tomorrow'."),
        ("Q40. How would you scale this to 10 million events?",
         "By deploying pgvector with HNSW indexing or FAISS for Approximate Nearest Neighbor vector search."),

        # Category O: Academic Invariance
        ("Q41. Did you fabricate or modify any evaluation results?",
         "No. All evaluation numbers are mathematically computed over 500 queries and 7,500 relevance judgments and persisted in reproducible JSON artifacts."),
        ("Q42. Which model achieves the highest NDCG@10?",
         "Structured Ranking at 0.3731."),
        ("Q43. Which model achieves the highest MRR?",
         "Structured Ranking at 0.4991."),
        ("Q44. Which model achieves the highest Recall@10?",
         "Hybrid Retrieval at 0.2268."),
        ("Q45. Which model achieves the highest F1 Score?",
         "Hybrid Retrieval at 0.2722."),
        ("Q46. Which model achieves the highest Precision@5?",
         "BM25 at 0.3860."),
        ("Q47. Does Semantic Retrieval outperform BM25 on this dataset?",
         "No. Standalone Semantic Retrieval achieves NDCG of 0.1955 vs BM25's 0.3623, but it provides vital conceptual recall when combined in Hybrid retrieval."),
        ("Q48. What is the relevance threshold used for binary metrics?",
         "Relevance score >= 2 (relevant and highly relevant)."),
        ("Q49. What Python version is used?",
         "Python 3.12 running in a dedicated virtual environment."),
        ("Q50. How is explainability rendered in the UI?",
         "Via the ExplainabilityPanel component showing formula decomposition, active intent chips, and signal contribution bars."),
        ("Q51. What happens if a user submits an empty query?",
         "FastAPI intercepts the request via Pydantic and returns HTTP 422 Unprocessable Content with a clean validation message."),
        ("Q52. How does EventIQ handle punctuation in queries?",
         "Non-alphanumeric characters are converted to single spaces during normalization, preventing regex parsing errors."),
        ("Q53. Why are unjudged documents not assumed to be non-relevant?",
         "Under standard Cranfield pooling assumptions, unjudged documents are treated as unassessed rather than automatically negative to avoid evaluation bias."),
        ("Q54. Why are stopwords removed in TF-IDF but kept in Semantic?",
         "TF-IDF treats words as an unordered bag-of-words where high-frequency stopwords add noise. Semantic transformers use self-attention across the whole sentence, where syntax and prepositions ('in Mumbai', 'for students') convey essential grammatical meaning."),
        ("Q55. What is the embedding storage format?",
         "A contiguous binary NumPy matrix (.npy) with shape (10000, 384) in float32 precision, occupying 15.3 MB."),
        ("Q56. What happens if top_k is set to 100?",
         "Pydantic validation rejects it with HTTP 422 because top_k is strictly bounded between 1 and 50."),
        ("Q57. How do you calculate F1 Score?",
         "Harmonic mean: 2 * (Precision * Recall) / (Precision + Recall)."),
        ("Q58. Can Structured Ranking handle queries with no intent signals?",
         "Yes. If no intent signals are detected, StructuredScore is 0.0 or not active, and the ranking defaults to the Hybrid score."),
        ("Q59. What is cosine similarity mathematically?",
         "The dot product of two normalized vectors, equivalent to the cosine of the angle between them in high-dimensional space."),
        ("Q60. Why is this project academically defensible?",
         "Because all claims are supported by standardized offline evaluations across 500 queries, with reproducible code, transparent mathematics, and verifiable trade-offs.")
    ]

    for q, a in qas:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        r_q = p.add_run(f"{q}\n")
        r_q.font.bold = True
        r_q.font.color.rgb = ROYAL_BLUE
        r_a = p.add_run(f"Answer: {a}")
        r_a.font.color.rgb = TEXT_DARK

def build_section_29(doc):
    add_heading_1(doc, "SECTION 29 — 'EXPLAIN THIS IN 30 SECONDS' (PITCH CHEAT SHEET)")
    add_p(doc, "Use these timed elevator pitches depending on how much time your examiner gives you:")

    add_callout(doc, "30-Second Elevator Pitch",
        "\"EventIQ is an Intelligent Information Retrieval and Ranking System for natural language event search over a 10,000-event corpus. Instead of rigid SQL filters or keyword search, it combines Okapi BM25 for lexical precision, Sentence-Transformers for semantic recall, and an explainable structured intent re-ranking layer. On our standardized 500-query benchmark, our structured model achieves peak NDCG@10 of 0.3731 and MRR of 0.4991, with complete mathematical score transparency.\"",
        "teacher"
    )

    add_callout(doc, "1-Minute Technical Pitch",
        "\"Traditional event search suffers from the vocabulary mismatch problem and opaque recommendation black boxes. In EventIQ, we designed a multi-stage Information Retrieval pipeline across 10,000 Indian event listings. We benchmarked five architectures: TF-IDF, BM25, MiniLM dense embeddings, Hybrid score fusion, and Structured Ranking. We solved score incommensurability by applying per-query Min-Max normalization to BM25 before fusing it with semantic cosine similarity at alpha=0.70. Then, we extracted query intents like city, category, admission, and audience, re-ranking candidates at lambda=0.15. This boosts NDCG@10 to 0.3731 and MRR to 0.4991. The complete system is served via a FastAPI backend and a React dashboard featuring live Recharts evaluation graphs and score decomposition.\"",
        "teacher"
    )

    add_callout(doc, "3-Minute In-Depth Academic Pitch",
        "\"Good morning. The core problem EventIQ addresses is intelligent event discovery from conversational natural language. Event listings are multi-field entities where relevance signals are scattered across titles, descriptions, categories, and tags. Furthermore, event queries involve strict real-world constraints—such as locations and ticket prices.\n\n"
        "To solve this, we implemented five retrieval paradigms from first principles. First, our TF-IDF baseline established initial scores. In Phase 3, we implemented Okapi BM25 with document length normalization (k1=1.5, b=0.75), which improved NDCG@10 by 16.8% and achieved peak P@5 of 0.3860. In Phase 4, we precomputed 384-dimensional dense vectors for all 10,000 events using all-MiniLM-L6-v2 into a persistent matrix to capture conceptual semantics.\n\n"
        "In Phase 5, we addressed score incommensurability: BM25 is unbounded, while semantic cosine similarity is bounded in [0, 1]. We implemented per-query Min-Max normalization and discovered that alpha=0.70 delivers peak Recall@10 (0.2268) and F1 (0.2722). In Phase 6, we created a vocabulary-driven intent extraction layer that detects active constraints and blends them at lambda=0.15. This soft boost pushes exact city, free admission, and audience matches into top rank positions, achieving our highest NDCG@10 of 0.3731 and MRR of 0.4991.\n\n"
        "Our backend is built on asynchronous FastAPI using a singleton SearchService to achieve 33ms search latencies. The frontend is built in React 19, allowing users to compare all five models, inspect mathematical explainability progress bars, and analyze live benchmark metrics. All results are completely reproducible across our 500 test queries and 7,500 relevance judgments.\"",
        "teacher"
    )

def build_section_30(doc):
    add_heading_1(doc, "SECTION 30 — IMPORTANT FORMULAS CHEAT SHEET")
    add_p(doc, "Memorize these exact mathematical formulations for your viva examination:")

    formulas = [
        ("TF-IDF Weight", "w(t, d) = (1 + log(tf(t, d))) * log(N / df(t))", "Sublinear term frequency multiplied by inverse document frequency."),
        ("Cosine Similarity", "cos(u, v) = (u · v) / (||u|| * ||v||)", "Dot product of vectors divided by product of their Euclidean L2 norms."),
        ("Okapi BM25", "Score = sum IDF(t) * [ (f(t,d)*(k1+1)) / (f(t,d) + k1*(1 - b + b*(|d|/avgdl))) ]", "Probabilistic scoring with k1=1.5 saturation and b=0.75 length normalization."),
        ("Min-Max BM25 Norm", "BM25_norm(d) = (BM25(d) - min_BM25) / (max_BM25 - min_BM25)", "Normalizes unbounded BM25 scores to [0.0, 1.0] across all 10k documents per query."),
        ("Hybrid Score (α=0.70)", "HybridScore = 0.70 * BM25_norm + 0.30 * SemanticScore", "Convex linear combination balancing 70% lexical precision and 30% semantic recall."),
        ("Structured Score", "StructuredScore = [ sum weight(s) * match(s, d) ] / [ sum active_weights ]", "Normalized binary constraint satisfaction across active query signals."),
        ("Final Ranking (λ=0.15)", "FinalScore = 0.85 * HybridScore + 0.15 * StructuredScore", "Soft linear blend giving 85% relevance foundation and 15% intent compliance boost."),
        ("Precision@K", "P@K = (Relevant retrieved items in top K) / K", "Fraction of top-K results that are relevant."),
        ("Recall@K", "R@K = (Relevant retrieved items in top K) / (Total relevant items in corpus)", "Fraction of total corpus relevant items captured in top-K."),
        ("F1 Score", "F1 = 2 * (P@10 * R@10) / (P@10 + R@10)", "Balanced harmonic mean of Precision@10 and Recall@10."),
        ("Mean Reciprocal Rank", "MRR = (1 / |Q|) * sum (1 / rank_first_relevant)", "Average reciprocal rank of the first relevant retrieved document."),
        ("NDCG@K", "NDCG@K = DCG@K / IDCG@K, where DCG@K = sum (2^{rel_i} - 1) / log2(i + 1)", "Normalized Discounted Cumulative Gain considering graded relevance (0-3).")
    ]
    for name, form, desc in formulas:
        add_p(doc, f"{desc}\n    Formula: {form}", bold_prefix=f"{name}: ")

def build_section_31(doc):
    add_heading_1(doc, "SECTION 31 — IMPORTANT NUMBERS CHEAT SHEET")
    add_p(doc, "Memorize these exact numerical figures for rapid recall during viva questioning:")

    headers = ["Parameter / Metric", "Exact Value", "Significance in Project"]
    rows = [
        ["Total Event Corpus Size", "10,000 events", "Relational database scale in PostgreSQL."],
        ["Test Query Topics", "500 queries", "Standardized test suite in data/queries.csv."],
        ["Relevance Judgments", "7,500 judgments", "Graded assessments (0-3) in data/relevance.csv."],
        ["Number of Metro Cities", "20 cities", "Indian metro & tier-1 cities (Mumbai, Bengaluru, Delhi, etc.)."],
        ["Number of High-Level Categories", "20 categories", "Technology, Photography, Business, etc."],
        ["MiniLM Embedding Dimension", "384 dimensions", "Dense vector size generated by all-MiniLM-L6-v2."],
        ["Persistent Embedding Matrix", "10,000 x 384", "Serialized binary NumPy matrix (15.3 MB float32)."],
        ["BM25 Parameters", "k1 = 1.5, b = 0.75", "Standard TREC probabilistic hyperparameters."],
        ["Optimal Alpha (α)", "0.70 (70% BM25)", "Selected via grid search; maximizes Recall@10 and F1."],
        ["Optimal Lambda (λ)", "0.15 (15% Structured)", "Selected re-ranking blend; maximizes MRR and NDCG@10."],
        ["Default Top-K", "10 results", "Default search result page size (configurable 1 to 50)."],
        ["Relevance Threshold", "Score >= 2", "Threshold for binary metrics (relevant & highly relevant)."],
        ["SearchService Cold Start", "17.4 seconds", "One-time memory preloading duration."],
        ["Average Warm Search Latency", "33.1 milliseconds", "Steady-state query response time on CPU."],
        ["BM25 Precision@5", "0.3860", "HIGHEST P@5 among all standalone models."],
        ["Hybrid Recall@10", "0.2268", "HIGHEST Recall@10 across all models."],
        ["Hybrid F1 Score", "0.2722", "HIGHEST F1 across all models."],
        ["Structured Ranking MRR", "0.4991", "HIGHEST MRR across all models."],
        ["Structured Ranking NDCG@10", "0.3731", "HIGHEST NDCG@10 across all models."]
    ]
    add_table_styled(doc, headers, rows, [1.8, 1.4, 3.6])

def build_section_32(doc):
    add_heading_1(doc, "SECTION 32 — FINAL 'WHAT I SHOULD KNOW' CHECKLIST")
    add_p(doc, "Before walking into your viva voce defense, verify that you can explain each item without notes:")

    checklist = [
        "I can state the exact problem EventIQ solves (rigid SQL vs keyword vs semantic).",
        "I can explain why the dataset has 10,000 events, 500 queries, and 7,500 relevance rows.",
        "I can explain that the dataset is synthetic and why synthetic benchmarks are used.",
        "I can explain why 5 event fields are concatenated into a single searchable document.",
        "I can write the TF-IDF formula and explain sublinear term frequency scaling.",
        "I can write the BM25 formula and explain why k1=1.5 and b=0.75 outperform TF-IDF.",
        "I can explain how all-MiniLM-L6-v2 maps text into 384-dimensional vector space.",
        "I can explain why persistent embeddings are cached in data/event_embeddings.npy.",
        "I can explain score incommensurability and why Min-Max normalization is necessary.",
        "I can explain why alpha = 0.70 was chosen and cite its peak Recall (0.2268) and F1 (0.2722).",
        "I can explain how intent signals (city, category, admission, type, audience) are extracted.",
        "I can explain why active weights normalization is used in the structured score.",
        "I can write the final ranking formula: FinalScore = 0.85 * Hybrid + 0.15 * Structured.",
        "I can compute a step-by-step numerical example of the final score.",
        "I can explain how explainability is displayed in the React frontend.",
        "I can explain the FastAPI architecture, schemas.py, and the SearchService Singleton.",
        "I can explain why models are preloaded in memory and achieve 33ms search latency.",
        "I can explain the React 19 component structure and that React contains zero ranking logic.",
        "I can explain that sidebar filters operate client-side over retrieved Top-K candidates.",
        "I can define all six evaluation metrics: P@5, P@10, Recall@10, F1, MRR, and NDCG@10.",
        "I can explain why no single model wins every metric and defend the academic trade-offs.",
        "I can state the exact limitations (no temporal parsing, in-memory embeddings, synthetic data).",
        "I can outline realistic future work (temporal NLP, pgvector HNSW indexing, Learning-to-Rank).",
        "I can deliver the 30-second, 1-minute, and 3-minute elevator pitches confidently."
    ]
    for item in checklist:
        add_p(doc, f"[  ]  {item}")

