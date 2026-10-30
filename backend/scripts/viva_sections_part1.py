"""
Part 1 of EventIQ Viva Preparation Guide: Sections 1 to 10
Exhaustive Academic & Practical Explanations (Fully Expanded for Viva Mastery)
"""
from docx.shared import Pt, RGBColor
from viva_guide_builder import (
    add_heading_1, add_heading_2, add_heading_3,
    add_p, add_bullet, add_callout, add_formula_box,
    add_table_styled, add_diagram_box, add_code_box,
    ROYAL_BLUE, NAVY, TEXT_DARK, SLATE
)

def add_six_step_block(doc, concept_name, what_is_it, why_use_it, how_it_works, how_implemented, example_eventiq, teacher_speech):
    """Utility to render the 6-step explanation pattern requested by user."""
    add_heading_2(doc, f"Concept Deep Dive: {concept_name}")
    
    add_p(doc, what_is_it, bold_prefix="1. What is it? ")
    add_p(doc, why_use_it, bold_prefix="2. Why do we use it? ")
    add_p(doc, how_it_works, bold_prefix="3. How does it work? ")
    add_p(doc, how_implemented, bold_prefix="4. How is it implemented in EventIQ? ")
    add_p(doc, example_eventiq, bold_prefix="5. Concrete Example from EventIQ: ")
    
    add_callout(doc, f"What to Say to Your Teacher: {concept_name}", teacher_speech, "teacher")

def build_section_1(doc):
    add_heading_1(doc, "SECTION 1 — PROJECT OVERVIEW")
    
    add_heading_2(doc, "1.1 Project Title & Executive Summary")
    add_p(doc, "Project Title: EventIQ: An Intelligent Event Retrieval and Ranking System", bold_prefix="Official Title: ")
    add_p(doc, "EventIQ is an Information Retrieval (IR) and Ranking System engineered to accept conversational, natural-language event queries, retrieve the most relevant candidate events from a 10,000-document structured corpus, and rank them using multi-paradigm scoring algorithms. The project bridges classical lexical information retrieval with state-of-the-art dense semantic neural embeddings and explainable structured query-intent matching.")

    add_heading_2(doc, "1.2 The Problem Statement & Industry Motivation")
    add_p(doc, "Event discovery across modern digital platforms is fundamentally flawed due to two contrasting but equally problematic search paradigms:")
    add_bullet(doc, "Traditional database-driven event portals force users into rigid dropdown menus (e.g., Select City -> Select Category -> Select Date Range). If an event organizer categorizes an event under 'Education' instead of 'Technology', or if an introductory Python session is tagged under 'Data Science', the listing completely disappears from user view. Boolean SQL queries (WHERE city='Mumbai' AND category='Tech') treat relevance as a binary 0 or 1, completely failing to capture partial matches or rank candidate events by graded relevance.", bold_prefix="1. Rigid SQL & Faceted Filters: ")
    add_bullet(doc, "Basic keyword matchers (such as SQL LIKE '%machine learning%' or naive string matching) rely strictly on verbatim word overlap. If a student searches for 'beginner coding meetup', but the organizer titled their event 'introductory programming workshop', lexical string matching fails completely. This is formally known in Information Retrieval as the 'Vocabulary Mismatch Problem'.", bold_prefix="2. Naive Keyword Search: ")
    add_bullet(doc, "Commercial event aggregators often rely on opaque black-box machine learning models, ad-sponsored bidding algorithms, or collaborative filtering systems that cannot explain to the user why a specific event was recommended. Users cannot verify whether an event was returned because it truly matched their query or because an organizer paid for promotion.", bold_prefix="3. Lack of Algorithmic Explainability: ")

    add_heading_2(doc, "1.3 The Proposed Solution: Multi-Paradigm Retrieval & Ranking")
    add_p(doc, "EventIQ resolves these limitations by implementing an end-to-end, multi-stage Information Retrieval pipeline that accepts free-form natural language queries and evaluates five distinct retrieval paradigms:")
    add_bullet(doc, "Vector Space Model baseline using sublinear term frequencies and unigram/bigram tokenization.", bold_prefix="1. TF-IDF Baseline: ")
    add_bullet(doc, "Probabilistic model incorporating non-linear term frequency saturation and document length normalization (k1=1.5, b=0.75).", bold_prefix="2. Okapi BM25: ")
    add_bullet(doc, "Dense continuous vector representations via Sentence-Transformers (all-MiniLM-L6-v2) mapping query and event semantics into a shared 384-dimensional latent space.", bold_prefix="3. Dense Semantic Retrieval: ")
    add_bullet(doc, "Document-level convex score fusion combining Min-Max normalized BM25 scores (70%) with semantic cosine similarity (30%) across the full 10,000-event corpus.", bold_prefix="4. Hybrid Retrieval (α = 0.70): ")
    add_bullet(doc, "Soft additive re-ranking combining hybrid retrieval (85%) with rule-free, vocabulary-driven structured intent satisfaction (15%) across extracted city, category, admission, event type, and target audience constraints.", bold_prefix="5. Structured Intent Ranking (λ = 0.15): ")

    add_heading_2(doc, "1.4 Architectural Comparison of Search Paradigms")
    headers = ["Search Paradigm", "Mathematical Mechanism", "Core Strengths", "Core Weaknesses in Event Search"]
    rows = [
        ["Traditional Keyword", "Exact SQL substring match (`LIKE %term%`)", "Zero compute overhead; trivial index.", "No relevance ranking; binary 0/1 matching; acute vocabulary mismatch."],
        ["Information Retrieval", "Statistical term weighting (TF-IDF, BM25)", "Probabilistic relevance ranking; accounts for document length and term rarity.", "Cannot understand synonyms, conceptual semantics, or paraphrased user intent."],
        ["Semantic Retrieval", "Dense neural vector embeddings (all-MiniLM-L6-v2)", "Understands conceptual intent and synonyms across 384 continuous dimensions.", "Weaker exact keyword precision; misses specific named entities and exact city names."],
        ["Hybrid Retrieval", "Convex linear fusion of BM25 + Semantic (α = 0.70)", "Combines exact keyword precision with conceptual semantic recall.", "Ignores explicit structured query constraints (e.g. 'free admission', 'students')."],
        ["Structured Ranking", "Hybrid fusion + Normalized query intent re-ranking (λ = 0.15)", "Highest top-rank precision (NDCG@10, MRR); fully explainable score decomposition.", "Requires dynamic corpus vocabulary extraction layer."]
    ]
    add_table_styled(doc, headers, rows, [1.4, 1.8, 1.8, 1.8])

    add_heading_2(doc, "1.5 Concrete Query Decomposition Example")
    add_callout(doc, "How EventIQ Understands a User Query",
        "Input Query: 'free photography workshops for beginners in Mumbai'\n\n"
        "How EventIQ decomposes and executes this query:\n"
        "1. Lexical Layer (BM25): Tokenizes into ['free', 'photography', 'workshops', 'beginners', 'mumbai'] and searches all 10,000 documents using term frequency and IDF weighting.\n"
        "2. Semantic Layer (MiniLM): Encodes the full sentence into a 384-dimensional vector, matching concepts like 'camera training', 'photo editing', 'shutter speed basics'.\n"
        "3. Hybrid Fusion: Normalizes BM25 to [0,1] and computes: HybridScore = 0.70 * BM25_norm + 0.30 * SemanticScore.\n"
        "4. Intent Extraction: Detects City='Mumbai', Category='Photography', Free=True, EventType='Workshop', Audience='Beginners'.\n"
        "5. Structured Boost: Computes StructuredScore based on active constraints and produces FinalScore = 0.85 * Hybrid + 0.15 * Structured.\n"
        "Result: A beginner photography workshop in Mumbai with free entry is ranked #1, with a complete transparent breakdown displayed to the user.",
        "teacher"
    )

def build_section_2(doc):
    add_heading_1(doc, "SECTION 2 — PROJECT OBJECTIVES")
    add_p(doc, "The development of EventIQ was governed by eleven explicit academic and engineering objectives:")
    
    objectives = [
        ("1. Natural-Language Event Search", "Enable users to discover events through expressive conversational queries without manually navigating database filters."),
        ("2. Multi-Field Document Representation", "Formulate unified searchable document representations by concatenating structured and unstructured metadata (title, description, category, subcategory, tags)."),
        ("3. Baseline Lexical Retrieval (TF-IDF)", "Implement a vector space retrieval engine with sublinear term frequency scaling and n-gram extraction (1-2) as an empirical benchmark."),
        ("4. State-of-the-Art Lexical Retrieval (BM25)", "Implement the Okapi BM25 probabilistic model with document length normalization (k1=1.5, b=0.75) to achieve high immediate precision."),
        ("5. Dense Semantic Neural Retrieval", "Deploy Sentence-Transformers (all-MiniLM-L6-v2) to generate 384-dimensional dense vectors, precomputing a persistent 10,000-document embedding artifact."),
        ("6. Score-Level Hybrid Fusion", "Design and evaluate a convex linear combination strategy that fuses Min-Max normalized BM25 with semantic cosine similarity at α=0.70."),
        ("7. Explainable Structured Intent Ranking", "Build a vocabulary-driven intent extraction engine that detects query constraints and applies soft additive re-ranking at λ=0.15."),
        ("8. Transparent Score Decomposition", "Provide full mathematical explainability for ranked results, displaying final scores, hybrid scores, structured scores, and signal contribution progress bars."),
        ("9. Standardized IR Evaluation Framework", "Conduct reproducible Cranfield-style offline evaluation over 500 ground-truth query topics and 7,500 relevance judgments using P@5, P@10, R@10, F1, MRR, and NDCG@10."),
        ("10. High-Performance REST API", "Expose clean, sanitized asynchronous endpoints via FastAPI with in-memory singleton model reuse and strict Pydantic validation."),
        ("11. Professional Academic Frontend", "Develop a responsive React 19 + Vite interface featuring an interactive search experience, facet filtering over retrieved candidates, and live Recharts evaluation graphs.")
    ]
    for title, desc in objectives:
        add_bullet(doc, desc, bold_prefix=f"{title}: ")

    add_callout(doc, "What to Say to Your Teacher About Project Scope",
        "\"Our primary research goal was not merely to build another event directory website, but to conduct a rigorous, empirical comparison of five foundational Information Retrieval paradigms on a standardized benchmark, demonstrating why hybrid fusion and structured intent re-ranking outperform isolated keyword or semantic models.\"",
        "teacher"
    )

def build_section_3(doc):
    add_heading_1(doc, "SECTION 3 — TECHNOLOGY STACK & JUSTIFICATIONS")
    add_p(doc, "Every technology in EventIQ was deliberately chosen based on software engineering best practices, computational efficiency, and Information Retrieval requirements:")
    
    headers = ["Layer", "Technology", "Version", "Role in EventIQ", "Technical Justification & Alternative Rejected"]
    rows = [
        ["Frontend", "React", "19.3.0", "User Interface Library", "Component-based architecture, efficient virtual DOM reconciliation, and seamless declarative UI state management. Rejected Vanilla JS due to state management complexity."],
        ["Frontend", "Vite", "8.3.4", "Build Tool & Bundler", "Lightning-fast Hot Module Replacement (HMR) and optimized Rolldown/ESBuild production bundling. Rejected Webpack due to slow cold-start times."],
        ["Frontend", "TypeScript", "6.0.2", "Type Safety", "Eliminates runtime errors by enforcing strict schema alignment between backend FastAPI responses and UI props. Rejected untyped JavaScript to prevent runtime schema bugs."],
        ["Frontend", "Recharts", "3.10.1", "Data Visualization", "Declarative, responsive SVG charting library utilized for rendering evaluation benchmark graphs (NDCG, MRR, Precision, Recall). Rejected Chart.js due to imperative canvas lifecycle."],
        ["Backend", "Python", "3.12", "Core Programming Language", "Industry standard for Data Science and Information Retrieval with rich scientific libraries (NumPy, scikit-learn, PyTorch)."],
        ["Backend", "FastAPI", "0.141.1", "REST API Framework", "Asynchronous ASGI framework with native OpenAPI/Swagger generation and high throughput. Rejected Flask due to lack of native async and Pydantic integration."],
        ["Backend", "Pydantic", "2.13.5", "Data Validation", "Enforces request/response schemas, type coercion, and sanitizes input to prevent malformed queries. Rejected manual validation dictionaries."],
        ["Backend", "scikit-learn", "1.9.1", "Lexical Modeling", "Provides optimized C-accelerated TfidfVectorizer with sublinear scaling and cosine similarity metrics. Rejected custom TF-IDF due to lack of sparse matrix optimization."],
        ["Backend", "rank-bm25", "0.2.2", "Probabilistic IR", "Pure-Python, performant implementation of Okapi BM25 with customizable k1 and b hyperparameters. Rejected full Lucene/Java stack to keep the codebase Pythonic."],
        ["Backend", "sentence-transformers", "6.1.0", "Neural Semantic Search", "PyTorch-backed library providing pre-trained transformer embeddings optimized for sentence-level semantic similarity. Rejected raw HuggingFace BERT due to pooling overhead."],
        ["ML Model", "all-MiniLM-L6-v2", "N/A", "Embedding Model", "384-dimensional dense representations; exceptional speed-to-quality ratio (5x faster than BERT-base with 99% retained semantic quality). Rejected BERT-base due to 110M parameter CPU latency."],
        ["Database", "PostgreSQL", "14+", "Relational Storage", "Robust relational ACID database housing the 10,000 events, 500 queries, and 7,500 relevance rows with B-tree indexes. Rejected SQLite due to concurrent connection constraints."],
        ["Data Processing", "NumPy & pandas", "Latest", "Vector & Matrix Math", "Vectorized dot products, matrix manipulation, and Min-Max score scaling across 10,000 items."]
    ]
    add_table_styled(doc, headers, rows, [0.8, 1.2, 0.7, 1.6, 2.5])

    add_callout(doc, "Viva Tip: Why not Elasticsearch or Algolia?",
        "Examiners frequently ask: 'Why didn't you just install Elasticsearch?'\n"
        "Your answer: 'Elasticsearch is a black-box pre-packaged enterprise search engine that obscures the underlying mathematics. Our academic project required implementing, controlling, and benchmarking each retrieval layer from first principles—including BM25 token length normalization, dense neural vector mathematics, custom per-query Min-Max score fusion, and intent extraction. Implementing these layers directly in Python allows exact mathematical verification and reproducible academic defense.'",
        "tip"
    )

def build_section_4(doc):
    add_heading_1(doc, "SECTION 4 — COMPLETE SYSTEM ARCHITECTURE")
    add_p(doc, "EventIQ is organized into a clean decoupled three-tier architecture: the React Presentation Tier, the FastAPI Application Service Tier, and the PostgreSQL Data & Vector Persistence Tier.")
    
    diagram = (
        "+---------------------------------------------------------------------------------------+\n"
        "|                                CLIENT / PRESENTATION TIER                            |\n"
        "|   React 19 + Vite Frontend (Port 5173)                                                |\n"
        "|   [Search Bar & Query Chips]  [Model Selector (5 Models)]  [Facet Sidebar (Top-K)]   |\n"
        "|   [Ranked Event Cards]        [Score Explainability Panel] [Evaluation Dashboard]    |\n"
        "+-------------------------------------------+-------------------------------------------+\n"
        "                                            | HTTP REST / JSON (Fetch API)\n"
        "                                            v\n"
        "+---------------------------------------------------------------------------------------+\n"
        "|                              APPLICATION SERVICE TIER (FastAPI)                       |\n"
        "|   Backend REST Service (Port 8000)                                                    |\n"
        "|   ├── main.py (CORS Middleware, Pydantic Exception Handlers, Endpoints)              |\n"
        "|   ├── schemas.py (SearchRequest, SearchResponse, EventDetailResponse, etc.)           |\n"
        "|   └── services/search_service.py (Thread-Safe In-Memory Singleton Manager)            |\n"
        "|        │                                                                              |\n"
        "|        v                                                                              |\n"
        "|   +-------------------------------------------------------------------------------+   |\n"
        "|   |                        RETRIEVAL & RANKING SUBSYSTEM                          |   |\n"
        "|   |  1. TF-IDF Retriever: Sparse Vector Space Cosine Similarity                  |   |\n"
        "|   |  2. BM25 Retriever: Probabilistic Okapi BM25 (k1=1.5, b=0.75)                 |   |\n"
        "|   |  3. Semantic Retriever: all-MiniLM-L6-v2 (384-d Cosine Matrix Mult)          |   |\n"
        "|   |  4. Hybrid Retriever: Full-Corpus Min-Max Score Fusion (alpha = 0.70)         |   |\n"
        "|   |  5. Structured Ranker: Vocabulary Intent Matching (lambda = 0.15)             |   |\n"
        "|   +-------------------------------------------------------------------------------+   |\n"
        "+-------------------------------------------+-------------------------------------------+\n"
        "                                            | SQL & Binary Matrix Caching\n"
        "                                            v\n"
        "+---------------------------------------------------------------------------------------+\n"
        "|                                DATA & PERSISTENCE TIER                                |\n"
        "|   ├── PostgreSQL Database (Port 5432): events (10,000), queries (500), relevance (7.5k)|\n"
        "|   ├── Persistent Embeddings Matrix: data/event_embeddings.npy (10000 x 384 float32)  |\n"
        "|   └── Offline Benchmark Artifacts: evaluation/*.json (TREC Evaluation Results)         |\n"
        "+---------------------------------------------------------------------------------------+"
    )
    add_diagram_box(doc, "EventIQ End-to-End System Architecture", diagram)

    add_heading_2(doc, "4.1 Component Walkthrough")
    add_p(doc, "1. Presentation Tier (React): Captures user keystrokes, provides curated test queries, dispatches asynchronous HTTP POST requests, filters retrieved results locally by active facets, and visualizes score decomposition.")
    add_p(doc, "2. API Gateway & Validation (FastAPI): Validates query strings and top_k bounds using Pydantic models. Catches exceptions and maps them to clean HTTP 422/500 responses without exposing stack traces or server paths.")
    add_p(doc, "3. SearchService Singleton: The core engine manager. Loaded once on server boot (~17.4s), it holds the TF-IDF matrix, BM25 tokenized corpus, neural transformer model, and the 10,000-document embedding matrix permanently in RAM for microsecond query dispatch.")
    add_p(doc, "4. Multi-Paradigm Retrieval Layer: Implements the five standalone and composite retrieval engines.")
    add_p(doc, "5. Data & Vector Persistence Tier: Relational metadata stored in PostgreSQL; dense neural embeddings serialized as a contiguous binary NumPy matrix (`data/event_embeddings.npy`).")

def build_section_5(doc):
    add_heading_1(doc, "SECTION 5 — THE EVENTIQ DATASET")
    add_p(doc, "The dataset is the empirical foundation of EventIQ. It consists of 10,000 synthetic Indian event documents, 500 test query topics, and 7,500 expert relevance judgments designed specifically for Information Retrieval experimentation.")

    add_heading_2(doc, "5.1 Dataset Files Breakdown")
    headers = ["Filename", "Records", "Format", "Contents & Purpose in Project"]
    rows = [
        ["data/events.csv", "10,000 rows", "CSV (UTF-8)", "Complete corpus of event listings containing 25 metadata attributes per event."],
        ["data/queries.csv", "500 rows", "CSV (UTF-8)", "Ground-truth natural language query topics (query_id, query_text)."],
        ["data/relevance.csv", "7,500 rows", "CSV (UTF-8)", "Graded relevance assessments mapping (query_id, event_id, relevance_score)."],
        ["data/README.txt", "Text", "Markdown", "Dataset schema definitions, generation methodology, and distribution statistics."]
    ]
    add_table_styled(doc, headers, rows, [1.5, 1.0, 1.2, 3.1])

    add_heading_2(doc, "5.2 Event Schema Fields (25 Attributes)")
    add_p(doc, "Each event document possesses rich structural, temporal, spatial, and categorical metadata:")
    add_bullet(doc, "Unique alphanumeric identifier formatted as 'EVT' followed by 6 digits (e.g., 'EVT001305').", bold_prefix="event_id (PK): ")
    add_bullet(doc, "Event title (e.g., 'Machine Learning Meetup in Mumbai').", bold_prefix="title: ")
    add_bullet(doc, "Comprehensive 2-4 sentence summary outlining the syllabus, target participants, and activities.", bold_prefix="description: ")
    add_bullet(doc, "One of 20 high-level domains (e.g., Technology, Photography, Business, Health & Wellness).", bold_prefix="category: ")
    add_bullet(doc, "Specific niche discipline (e.g., Machine Learning, Portrait Photography, Web Development).", bold_prefix="subcategory: ")
    add_bullet(doc, "Comma-separated keywords (e.g., 'Python, Cloud, Data Science, AI').", bold_prefix="tags: ")
    add_bullet(doc, "Format: Workshop, Meetup, Conference, Seminar, Festival, Hackathon, Competition, Career Fair.", bold_prefix="event_type: ")
    add_bullet(doc, "Geographic location across 20 major Indian metro and tier-1 cities (Mumbai, Bengaluru, Delhi, Pune, Hyderabad, etc.).", bold_prefix="city & state: ")
    add_bullet(doc, "Realistic event premises (e.g., 'Bombay Exhibition Centre', 'Nehru Centre', 'Balgandharva Ranga Mandir').", bold_prefix="venue & address: ")
    add_bullet(doc, "Exact geographic coordinates for spatial queries.", bold_prefix="latitude & longitude: ")
    add_bullet(doc, "ISO-formatted temporal boundaries (YYYY-MM-DD and HH:MM:SS).", bold_prefix="start/end date & time: ")
    add_bullet(doc, "Admission cost in INR (currency='INR') and boolean flag is_free (True when price=0).", bold_prefix="price, currency, is_free: ")
    add_bullet(doc, "Name of the organizing institution or collective.", bold_prefix="organizer: ")
    add_bullet(doc, "Target participant demographic (e.g., Students, Beginners, Developers, Researchers, Professionals).", bold_prefix="audience: ")
    add_bullet(doc, "Language medium (predominantly English) and attendee volume (e.g., 50 to 1,500).", bold_prefix="language & expected_attendees: ")
    add_bullet(doc, "Historical attendee satisfaction rating on a 1.0 to 5.0 scale.", bold_prefix="rating: ")

    add_heading_2(doc, "5.3 Graded Relevance Judgments")
    add_p(doc, "In accordance with TREC (Text REtrieval Conference) standards, the 7,500 judgments in `data/relevance.csv` utilize a 4-tier graded scale:")
    add_bullet(doc, "The event has zero topical or spatial connection to the user's information need.", bold_prefix="0 = Not Relevant: ")
    add_bullet(doc, "The event matches some secondary aspects (e.g., general topic matches, but wrong city or wrong event type).", bold_prefix="1 = Marginally Relevant: ")
    add_bullet(doc, "The event satisfies the core criteria of the query (e.g., topic and city match).", bold_prefix="2 = Relevant: ")
    add_bullet(doc, "The event completely and specifically satisfies all query facets (topic, city, admission, target audience).", bold_prefix="3 = Highly Relevant: ")

    add_callout(doc, "CRITICAL ACADEMIC DISTINCTION: Synthetic vs. Real Data",
        "Examiners may ask: 'Is this real scraped data from BookMyShow or Meetup.com?'\n"
        "Your exact answer: 'No. The dataset is a synthetic benchmark created for Information Retrieval research. Scraped web data is noisy, unstructured, and lacks ground-truth relevance assessments. By utilizing a controlled 10,000-event synthetic Indian corpus with 500 standardized query topics and 7,500 explicit graded relevance judgments, we can conduct rigorous, reproducible Cranfield-style offline IR evaluation.'",
        "alert"
    )

def build_section_6(doc):
    add_heading_1(doc, "SECTION 6 — DATABASE ARCHITECTURE")
    add_p(doc, "EventIQ employs PostgreSQL 14+ for relational data persistence. The schema is organized into three normalized tables:")

    diagram = (
        "+-----------------------+          +-----------------------+          +-----------------------+\n"
        "|        queries        |          |       relevance       |          |        events         |\n"
        "+-----------------------+          +-----------------------+          +-----------------------+\n"
        "| query_id (PK, VARCHAR)|<---+     | id (PK, SERIAL)       |     +--->| event_id (PK, VARCHAR)|\n"
        "| query_text (TEXT)     |    +-----| query_id (FK, VARCHAR)|     |    | title (TEXT)          |\n"
        "| created_at (TIMESTAMP)|          | event_id (FK, VARCHAR)|-----+    | description (TEXT)    |\n"
        "+-----------------------+          | relevance_score (INT) |          | category (VARCHAR)    |\n"
        "                                   +-----------------------+          | city (VARCHAR)        |\n"
        "                                                                      | is_free (BOOLEAN)     |\n"
        "                                                                      | ... (25 attributes)   |\n"
        "                                                                      +-----------------------+"
    )
    add_diagram_box(doc, "PostgreSQL Relational ER Diagram", diagram)

    add_heading_2(doc, "6.1 Relational Schema & Indexes")
    add_p(doc, "1. `events`: Primary table holding all 10,000 event records. `event_id` is the primary key. B-tree indexes are established on `city`, `category`, `is_free`, `event_type`, and `audience` to support low-latency SQL lookups.")
    add_p(doc, "2. `queries`: Stores the 500 standardized test query topics. `query_id` is the primary key (e.g., 'Q001' to 'Q500').")
    add_p(doc, "3. `relevance`: Association table linking `query_id` and `event_id` with foreign key constraints. Forms the ground-truth evaluation matrix.")

    add_heading_2(doc, "6.2 Role in Search vs. Evaluation")
    add_p(doc, "In production search, PostgreSQL serves as the persistent catalog from which full event records are retrieved once the candidate event IDs have been ranked by the SearchService. In offline evaluation, PostgreSQL supplies the query set and relevance judgments to compute TREC metrics.")

def build_section_7(doc):
    add_heading_1(doc, "SECTION 7 — SEARCHABLE DOCUMENT CREATION")
    add_p(doc, "Events are rich multi-field entities. A fundamental challenge in event retrieval is that critical relevance signals are scattered across structured and unstructured fields. If a user searches for 'Python cloud coding', the word 'Python' may be in tags, 'cloud' in description, and 'coding' in subcategory.")

    add_heading_2(doc, "7.1 Multi-Field Concatenation Strategy")
    add_p(doc, "EventIQ constructs a single unified searchable document for each event by concatenating five descriptive fields with whitespace delimiters:")
    add_p(doc, "SearchableDocument = title + ' ' + description + ' ' + category + ' ' + subcategory + ' ' + tags", bold_prefix="Formulation: ")

    add_heading_2(doc, "7.2 Preprocessing Pipeline")
    add_p(doc, "Before text is ingested into lexical or semantic models, it undergoes standardized normalization:")
    add_bullet(doc, "All text is converted to lowercase to ensure case-insensitive matching.", bold_prefix="1. Lowercasing: ")
    add_bullet(doc, "Special characters, punctuation, and non-alphanumeric symbols are sanitized into single spaces.", bold_prefix="2. Punctuation Handling: ")
    add_bullet(doc, "Consecutive spaces, tabs, and newlines are collapsed to single whitespace characters.", bold_prefix="3. Whitespace Normalization: ")
    add_bullet(doc, "Standard English stopwords ('the', 'is', 'at', 'which', 'on') are removed during TF-IDF tokenization, but preserved in semantic retrieval where syntactic context is required by the transformer.", bold_prefix="4. Stopword Removal: ")

    add_callout(doc, "Concrete EventIQ Searchable Document Example",
        "Event ID: EVT001305\n"
        "• Title: Machine Learning Meetup in Mumbai\n"
        "• Description: Machine Learning Meetup in Mumbai is an English-language meetup focused on machine learning and related topics including Machine Learning, Cybersecurity, Cloud Computing, Python...\n"
        "• Category: Technology\n"
        "• Subcategory: Machine Learning\n"
        "• Tags: Machine Learning, Cybersecurity, Cloud Computing, Python\n\n"
        "Constructed Searchable Document:\n"
        "\"machine learning meetup in mumbai machine learning meetup in mumbai is an english-language meetup focused on machine learning and related topics including machine learning cybersecurity cloud computing python the programme is designed for researchers in and around mumbai technology machine learning machine learning cybersecurity cloud computing python\"",
        "tip"
    )

def build_section_8(doc):
    add_heading_1(doc, "SECTION 8 — PHASE 2: TF-IDF RETRIEVAL BASELINE")
    
    add_six_step_block(doc,
        "TF-IDF (Term Frequency-Inverse Document Frequency)",
        "TF-IDF is a statistical weighting mechanism used in the Vector Space Model of Information Retrieval. It evaluates how important a word is to a document within a collection.",
        "We use it as our baseline retrieval engine because it is the classic, benchmark information retrieval algorithm against which all modern IR models (BM25, Dense Embeddings) are compared.",
        "It computes two components: Term Frequency (tf) measures how often a word occurs in a document; Inverse Document Frequency (idf) measures how rare or informative the word is across all 10,000 documents. The document and query are converted into high-dimensional sparse vectors, and their similarity is measured using the cosine of the angle between them.",
        "Implemented in backend/retrieval/tfidf.py using scikit-learn's TfidfVectorizer with sublinear_tf=True, ngram_range=(1,2), max_features=20000, and English stopword filtering. The resulting document matrix has shape (10000, 5960).",
        "For query 'machine learning in Mumbai', words 'machine learning' and 'mumbai' get high IDF weights, while generic words get low weights. Candidate documents with matching terms receive positive cosine similarity scores.",
        "\"TF-IDF is our foundational Vector Space baseline. It uses sublinear term frequencies and unigram/bigram tokenization. While it achieved a respectable P@5 of 0.3552, it lacks term saturation and document length normalization, which led us directly to Phase 3: Okapi BM25.\""
    )

    add_formula_box(doc, "TF-IDF Weighting & Cosine Similarity",
        "w(t, d) = (1 + log(tf(t, d))) * log(N / df(t))\n"
        "sim(q, d) = (q · d) / (||q|| * ||d||) = sum(w(t, q) * w(t, d)) / (sqrt(sum(w(t, q)^2)) * sqrt(sum(w(t, d)^2)))",
        [
            ("tf(t, d)", "Sublinear Term Frequency: frequency of term t in document d"),
            ("N", "Total number of documents in corpus (10,000)"),
            ("df(t)", "Document Frequency: number of documents containing term t"),
            ("q · d", "Dot product of the query vector and document vector"),
            ("||q||, ||d||", "Euclidean (L2) norms ensuring length normalization")
        ]
    )

    add_code_box(doc, "TF-IDF Core Implementation (backend/retrieval/tfidf.py)",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n"
        "from sklearn.metrics.pairwise import cosine_similarity\n\n"
        "class TFIDFRetriever:\n"
        "    def __init__(self, corpus):\n"
        "        self.vectorizer = TfidfVectorizer(\n"
        "            sublinear_tf=True,\n"
        "            ngram_range=(1, 2),\n"
        "            max_features=20000,\n"
        "            stop_words='english'\n"
        "        )\n"
        "        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)\n\n"
        "    def search(self, query, top_k=10):\n"
        "        q_vec = self.vectorizer.transform([query])\n"
        "        sims = cosine_similarity(q_vec, self.tfidf_matrix).flatten()\n"
        "        top_indices = np.argsort(sims)[::-1][:top_k]\n"
        "        return top_indices, sims[top_indices]"
    )

    add_heading_2(doc, "8.3 Phase 2 Evaluation Results")
    headers = ["Model", "P@5", "P@10", "Recall@10", "F1", "MRR", "NDCG@10"]
    rows = [["TF-IDF Baseline", "0.3552", "0.2628", "0.1752", "0.2102", "0.4820", "0.3101"]]
    add_table_styled(doc, headers, rows, [1.6, 0.8, 0.8, 0.9, 0.8, 0.8, 0.9])

def build_section_9(doc):
    add_heading_1(doc, "SECTION 9 — PHASE 3: OKAPI BM25 RETRIEVAL")
    
    add_six_step_block(doc,
        "Okapi BM25 (Best Matching 25)",
        "BM25 is a probabilistic Information Retrieval algorithm that estimates the probability that a document is relevant to a query. It is widely considered the state-of-the-art classical lexical ranking function.",
        "TF-IDF has two fatal flaws: (1) it allows term frequency to scale without bound, and (2) it does not adequately penalize excessively verbose documents. BM25 solves both problems with term frequency saturation and document length normalization.",
        "It uses parameter k1 to govern non-linear term saturation (preventing term repetition abuse) and parameter b to normalize document length against the average corpus length (avgdl).",
        "Implemented in backend/retrieval/bm25.py using rank_bm25.BM25Okapi with k1=1.5 and b=0.75 across the pre-tokenized 10,000-document corpus. Evaluates all 10,000 items in vectorized NumPy operations.",
        "If an event mentions 'workshop' 30 times, BM25 caps the score contribution near the asymptotic limit governed by k1=1.5, preventing keyword-stuffed documents from stealing top ranks.",
        "\"BM25 is our probabilistic lexical engine. By introducing term saturation (k1=1.5) and length normalization (b=0.75), BM25 delivered an immediate +16.8% increase in NDCG@10 (0.3623) and achieved our project's highest Precision@5 of 0.3860.\""
    )

    add_formula_box(doc, "Okapi BM25 Scoring Formula",
        "Score_BM25(q, d) = sum_{t in q} IDF(t) * [ (f(t, d) * (k1 + 1)) / (f(t, d) + k1 * (1 - b + b * (|d| / avgdl))) ]\n"
        "where: IDF(t) = log( (N - n(t) + 0.5) / (n(t) + 0.5) + 1 )",
        [
            ("f(t, d)", "Raw term frequency of token t in event document d"),
            ("|d| / avgdl", "Document length ratio: length of document d divided by average corpus length"),
            ("k1 = 1.5", "Term frequency saturation parameter (controls non-linear scaling)"),
            ("b = 0.75", "Length normalization parameter (b=1 is full normalization; b=0 is none)"),
            ("N = 10,000", "Total corpus document count"),
            ("n(t)", "Number of documents containing token t")
        ]
    )

    add_code_box(doc, "BM25 Implementation (backend/retrieval/bm25.py)",
        "from rank_bm25 import BM25Okapi\n\n"
        "class BM25Retriever:\n"
        "    def __init__(self, tokenized_corpus):\n"
        "        self.bm25 = BM25Okapi(tokenized_corpus, k1=1.5, b=0.75)\n\n"
        "    def search(self, query_tokens, top_k=10):\n"
        "        scores = self.bm25.get_scores(query_tokens)\n"
        "        top_indices = np.argsort(scores)[::-1][:top_k]\n"
        "        return top_indices, scores[top_indices]"
    )

    add_heading_2(doc, "9.3 Phase 3 Evaluation Results (BM25 vs. TF-IDF)")
    headers = ["Model", "P@5", "P@10", "Recall@10", "F1", "MRR", "NDCG@10", "Gain over TF-IDF"]
    rows = [
        ["TF-IDF", "0.3552", "0.2628", "0.1752", "0.2102", "0.4820", "0.3101", "Baseline"],
        ["BM25", "0.3860", "0.3250", "0.2167", "0.2600", "0.4797", "0.3623", "+8.7% P@5, +16.8% NDCG@10"]
    ]
    add_table_styled(doc, headers, rows, [1.2, 0.7, 0.7, 0.8, 0.7, 0.7, 0.8, 1.4])

def build_section_10(doc):
    add_heading_1(doc, "SECTION 10 — PHASE 4: DENSE SEMANTIC RETRIEVAL")
    
    add_six_step_block(doc,
        "Dense Semantic Neural Retrieval",
        "Semantic retrieval is a neural search paradigm that represents text queries and documents as dense continuous vectors in high-dimensional latent space, computing relevance via vector angles rather than lexical token overlap.",
        "BM25 completely fails when a user uses synonyms or conceptual phrases (e.g. searching for 'AI networking' when the event says 'Machine Learning Meetup'). Semantic retrieval captures deep conceptual meaning.",
        "A transformer neural network (all-MiniLM-L6-v2) encodes text into 384 continuous dimensions. The dot product between the query vector and document vector represents their cosine similarity.",
        "Implemented in backend/retrieval/semantic.py using Sentence-Transformers. To eliminate query latency, all 10,000 event embeddings were precomputed into data/event_embeddings.npy (15.3MB float32). At query time, only the query is encoded, and matrix multiplication against the cached matrix takes ~30ms.",
        "Query: 'rock concert'. An event titled 'Indie Music Fest at Marine Lines' has zero words matching 'rock' or 'concert', yet MiniLM assigns it a high similarity score of 0.74 because both live in the same music domain vector cluster.",
        "\"Semantic retrieval maps text to 384-dimensional dense vectors using all-MiniLM-L6-v2. We precomputed a persistent 10,000-document embedding matrix to achieve 30ms latency. While standalone semantic search yields lower precision on exact keyword topics, it provides vital conceptual recall that powers our Phase 5 Hybrid engine.\""
    )

    add_code_box(doc, "Semantic Vector Retrieval (backend/retrieval/semantic.py)",
        "from sentence_transformers import SentenceTransformer\n"
        "import numpy as np\n\n"
        "class SemanticRetriever:\n"
        "    def __init__(self, embeddings_path='data/event_embeddings.npy'):\n"
        "        self.model = SentenceTransformer('all-MiniLM-L6-v2')\n"
        "        self.doc_embeddings = np.load(embeddings_path) # (10000, 384)\n"
        "        # Pre-normalize for fast cosine via dot product\n"
        "        self.norms = np.linalg.norm(self.doc_embeddings, axis=1, keepdims=True)\n"
        "        self.doc_embeddings = self.doc_embeddings / np.maximum(self.norms, 1e-9)\n\n"
        "    def search(self, query, top_k=10):\n"
        "        q_emb = self.model.encode(query, convert_to_numpy=True)\n"
        "        q_emb = q_emb / max(np.linalg.norm(q_emb), 1e-9)\n"
        "        sims = np.dot(self.doc_embeddings, q_emb)\n"
        "        top_indices = np.argsort(sims)[::-1][:top_k]\n"
        "        return top_indices, sims[top_indices]"
    )

    add_heading_2(doc, "10.3 Phase 4 Evaluation Results & Critical Academic Defense")
    headers = ["Model", "P@5", "P@10", "Recall@10", "F1", "MRR", "NDCG@10"]
    rows = [
        ["BM25 Lexical", "0.3860", "0.3250", "0.2167", "0.2600", "0.4797", "0.3623"],
        ["Semantic (all-MiniLM-L6-v2)", "0.2248", "0.1788", "0.1192", "0.1430", "0.3729", "0.1955"]
    ]
    add_table_styled(doc, headers, rows, [1.8, 0.8, 0.8, 0.9, 0.8, 0.8, 0.9])

    add_callout(doc, "Crucial Viva Defense: Why is Semantic Retrieval lower on this benchmark?",
        "Examiners will immediately ask: 'Why are your Semantic Retrieval numbers (NDCG=0.1955) lower than BM25 (NDCG=0.3623)? Does that mean neural embeddings failed?'\n\n"
        "Your rock-solid academic answer:\n"
        "1. Specificity & Named Entities: Event queries are heavily keyword-specific and location-bound (e.g., 'conferences in Mumbai', 'React developer meetup'). Semantic models project words into broad conceptual clusters—it knows Mumbai and Delhi are both Indian cities, but it might treat an event in Delhi as semantically similar to a query for Mumbai! BM25 strictly penalizes city mismatches.\n"
        "2. Short Event Titles vs. Long Descriptions: Dense vector averaging dilutes exact keywords over long multi-field text.\n"
        "3. The True Value of Semantic Retrieval: Standalone semantic search has lower precision on exact keyword topics, BUT it possesses unique associative recall that BM25 lacks. When combined in Phase 5 Hybrid Retrieval, the semantic model contributes vital conceptual matches, elevating overall system Recall@10 from 0.2167 to 0.2268!",
        "alert"
    )

