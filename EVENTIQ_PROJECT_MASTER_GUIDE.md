You are the lead software engineer, ML/IR engineer, backend engineer, frontend engineer, QA engineer, and technical project manager for my final-year academic project.

Your job is to take my existing project called:

EVENTIQ — An Intelligent Event Retrieval and Ranking System

and complete it from its CURRENT STATE to a fully working, demonstrable, academically defensible project.

IMPORTANT:
Do NOT blindly rebuild the project.
Do NOT replace working code unnecessarily.
Do NOT change the existing TF-IDF implementation unless there is a clear bug.
First inspect the existing project and understand what has already been implemented.

You are acting as the PROJECT HEAD.

============================================================
1. CURRENT PROJECT OBJECTIVE
============================================================

EventIQ is an Information Retrieval and Ranking System for discovering events using natural-language queries.

The system should allow a user to enter a query such as:

"machine learning events for students"

"AI workshops in Mumbai"

"free technology events in Pune"

"startup networking events in Bengaluru"

"photography workshops for beginners"

The system should retrieve relevant events and rank them intelligently.

The final system should demonstrate that different retrieval/ranking approaches can be compared and improved:

1. TF-IDF
2. BM25
3. Semantic retrieval
4. Hybrid retrieval/ranking

The project must also have a simple, professional frontend where a user can search events and see ranked results.

This is an academic/research project, so the implementation must be explainable and the evaluation must be reproducible.

============================================================
2. CRITICAL RULE
============================================================

BEFORE CHANGING ANYTHING:

Inspect the entire existing project.

Determine:

- existing folder structure
- existing Python files
- existing FastAPI files
- existing PostgreSQL configuration
- existing retrieval code
- existing evaluation code
- existing dataset
- existing requirements
- existing environment configuration
- existing Git configuration
- existing frontend, if any

Do not assume that something is missing just because it is not described below.

After inspecting the project, give me a short report:

A. What already works
B. What is partially implemented
C. What is missing
D. What you recommend doing next

Then proceed with implementation.

If you need information that cannot be determined from the project files, ASK ME.

Do not invent:
- credentials
- API keys
- database passwords
- deployment information
- user requirements
- academic requirements
- design requirements
- external services
- evaluation results

If something important is unknown, explicitly ask me.

============================================================
3. CURRENT PROJECT LOCATION
============================================================

The project is currently located approximately at:

C:\EventIQ

The project is being developed on Windows.

The backend uses Python.

The database is PostgreSQL.

The frontend will be React + Vite.

============================================================
4. CURRENT DATASET
============================================================

The project already has a synthetic Indian event dataset.

Files:

data/events.csv
data/queries.csv
data/relevance.csv
data/README.txt

Dataset:

10,000 synthetic events
500 queries
7,500 relevance judgments

The dataset is intended for Information Retrieval research.

Important:

The event listings are synthetic.

Do not present them as real-world events.

The dataset uses Indian context including:

- Indian cities
- Indian states
- INR pricing
- Indian venue names
- Indian event categories
- Indian audiences

The events contain fields such as:

event_id
title
description
category
subcategory
tags
event_type
city
state
venue
address
latitude
longitude
start_date
start_time
end_date
end_time
price
currency
is_free
organizer
expected_attendees
audience
language
rating

Queries contain:

query_id
query

Relevance judgments contain:

query_id
event_id
relevance

Relevance scale:

0 = not relevant
1 = partially relevant
2 = relevant
3 = highly relevant

There are only 7,500 explicit query-event judgments.

There are theoretically 5,000,000 possible query-event pairs.

DO NOT automatically claim every unjudged pair is irrelevant unless the evaluation methodology explicitly requires it.

============================================================
5. DATABASE
============================================================

PostgreSQL database:

Database name:

eventiq

Existing tables:

events
queries
relevance

Existing events schema:

CREATE TABLE events (
    event_id VARCHAR(20) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    tags TEXT,
    event_type VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    venue VARCHAR(255),
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    start_date DATE,
    start_time TIME,
    end_date DATE,
    end_time TIME,
    price INTEGER,
    currency VARCHAR(10),
    is_free BOOLEAN,
    organizer VARCHAR(255),
    expected_attendees INTEGER,
    audience TEXT,
    language VARCHAR(50),
    rating NUMERIC(2,1)
);

queries:

CREATE TABLE queries (
    query_id VARCHAR(20) PRIMARY KEY,
    query TEXT NOT NULL
);

relevance:

CREATE TABLE relevance (
    query_id VARCHAR(20) NOT NULL,
    event_id VARCHAR(20) NOT NULL,
    relevance INTEGER NOT NULL,
    PRIMARY KEY (query_id, event_id),
    FOREIGN KEY (query_id) REFERENCES queries(query_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

Existing indexes include:

idx_events_category
idx_events_subcategory
idx_events_city
idx_events_start_date
idx_events_event_type
idx_events_is_free

Verify these before adding duplicates.

============================================================
6. CURRENT FASTAPI BACKEND
============================================================

Existing backend structure is approximately:

backend/
    app/
        __init__.py
        config.py
        database.py
        main.py

Current database configuration uses:

DATABASE_URL

from .env

Do not expose the actual database password.

The .env file must remain ignored by Git.

.env.example must contain only placeholder credentials.

============================================================
7. CURRENT TF-IDF IMPLEMENTATION
============================================================

TF-IDF is ALREADY IMPLEMENTED.

Do not rewrite it unnecessarily.

Existing preprocessing file:

backend/retrieval/preprocessing.py

Current searchable fields:

title
description
category
subcategory
tags

Current preprocessing:

- lowercase
- remove non-alphanumeric characters
- normalize whitespace

Existing TF-IDF vectorizer:

TfidfVectorizer(
    max_features=20000,
    ngram_range=(1, 2),
    min_df=2,
    stop_words="english"
)

Current matrix:

10,000 documents

5,960 features

Shape:

(10000, 5960)

Existing retrieval method:

cosine similarity

Existing TF-IDF retriever:

backend/retrieval/tfidf.py

Existing evaluation:

backend/scripts/evaluate_tfidf.py

============================================================
8. CURRENT TF-IDF RESULTS
============================================================

These results are already obtained.

DO NOT modify them.

DO NOT rerun and overwrite them unless there is a clear bug in the evaluation implementation.

Baseline:

Queries evaluated: 500

Precision@5:
0.3552

Precision@10:
0.2628

Recall@10:
0.1752

F1:
0.2102

MRR:
0.4820

NDCG@10:
0.3101

These are the project's TF-IDF BASELINE RESULTS.

Preserve them.

The final project must compare future retrieval approaches against this baseline.

============================================================
9. PHASE 3 — BM25
============================================================

Continue from here.

Implement BM25.

Recommended library:

rank-bm25

Do not modify the TF-IDF implementation to make BM25 work.

Create:

backend/retrieval/bm25.py

Create:

backend/scripts/test_bm25_search.py

Test at least these queries:

1. AI workshops in Mumbai
2. machine learning events for students
3. startup networking events in Bengaluru
4. photography workshops for beginners
5. free technology events in Pune

Then create:

backend/scripts/evaluate_bm25.py

Use EXACTLY the same evaluation methodology as TF-IDF.

Evaluate:

Precision@5
Precision@10
Recall@10
F1
MRR
NDCG@10

Do not change the relevance dataset.

Do not change the evaluation methodology between models.

Store BM25 results separately.

For example:

evaluation/
    tfidf_results.json
    bm25_results.json

or an equivalent structured approach.

Ask me before introducing a major new evaluation format if necessary.

============================================================
10. PHASE 4 — SEMANTIC RETRIEVAL
============================================================

After BM25 is working and evaluated, implement semantic retrieval.

Recommended model:

sentence-transformers

Use a lightweight model suitable for local development.

Possible model:

all-MiniLM-L6-v2

BUT:

Before downloading a large model or requiring external services, verify my environment.

If the environment does not have the model:

tell me what will be installed and why.

Do not use an external paid API unless I explicitly approve it.

Generate embeddings for events.

Initially create embeddings for:

title
description
category
subcategory
tags

Use cosine similarity.

Create something similar to:

backend/retrieval/semantic.py

The semantic retriever should support:

search(query, top_k=10)

Evaluate using the SAME:

Precision@5
Precision@10
Recall@10
F1
MRR
NDCG@10

Do not compare models using different datasets or evaluation protocols.

============================================================
11. PHASE 5 — HYBRID RETRIEVAL
============================================================

After TF-IDF, BM25 and semantic retrieval are working, implement a hybrid approach.

The purpose is to combine:

lexical relevance

and

semantic relevance.

Start with a simple and explainable method.

For example:

hybrid_score =
    alpha * normalized_bm25_score
    +
    (1 - alpha) * semantic_score

Test multiple alpha values.

For example:

0.25
0.50
0.75

Determine which performs best on the evaluation dataset.

Do not simply choose a value because it "looks good."

Use the evaluation metrics.

The final report should show why the chosen alpha was selected.

If normalization is necessary, implement it properly.

Document the normalization method.

============================================================
12. PHASE 6 — STRUCTURED EVENT RANKING
============================================================

The system should eventually incorporate structured event information.

Potential signals:

text relevance
semantic relevance
location
category
subcategory
date
price
free/paid
audience
event type
rating
expected attendees

However:

DO NOT immediately create an overly complicated machine-learning ranking model.

Start with an explainable ranking layer.

For example:

final_score =
    text_score
    +
    semantic_score
    +
    structured relevance

But design this carefully.

Natural-language query interpretation should distinguish between:

"free technology events in Pune"

and

"technology events in Pune"

For example:

"free" should influence the free/price signal.

"Pune" should influence location.

"technology" should influence category.

"students" should influence audience.

"workshops" should influence event type.

Do not hard-code hundreds of special cases.

Build a clean query-processing approach.

If an NLP model is needed, explain why before adding it.

============================================================
13. PHASE 7 — SEARCH API
============================================================

Once the retrieval system is stable, expose it through FastAPI.

Create:

POST /api/search

Request example:

{
    "query": "machine learning events for students",
    "top_k": 10,
    "model": "hybrid"
}

Possible model values:

tfidf
bm25
semantic
hybrid

Response should be structured.

Example:

{
    "query": "...",
    "model": "hybrid",
    "results": [
        {
            "rank": 1,
            "event_id": "...",
            "title": "...",
            "category": "...",
            "city": "...",
            "date": "...",
            "price": 0,
            "is_free": true,
            "score": 0.87
        }
    ]
}

The API should NOT expose internal stack traces to the frontend.

Implement proper error handling.

Validate:

- empty queries
- invalid top_k
- invalid model
- database failures
- retrieval failures

============================================================
14. EXISTING API
============================================================

Preserve existing:

GET /api/health

GET /api/events/count

These currently verify:

database connectivity

and

event count.

Do not break them.

============================================================
15. ADDITIONAL BACKEND ENDPOINTS
============================================================

Add endpoints where useful:

GET /api/events/{event_id}

GET /api/categories

GET /api/locations

GET /api/search/history

GET /api/evaluation

Possibly:

POST /api/feedback

But only add feedback if it is actually useful and can be implemented cleanly.

Do not create unnecessary endpoints.

============================================================
16. SEARCH HISTORY
============================================================

A simple search history feature would be useful.

Initially it can be stored locally or in PostgreSQL.

Ask me if user authentication is expected.

IMPORTANT:

Do not introduce authentication unless necessary.

This is primarily an academic demonstration system.

Avoid unnecessary complexity.

============================================================
17. PHASE 8 — SIMPLE FRONTEND
============================================================

Create a SIMPLE, PROFESSIONAL frontend.

Do NOT create an overly complicated SaaS dashboard.

The frontend should demonstrate the research system clearly.

Technology:

React
Vite
JavaScript or TypeScript

Choose TypeScript if it does not complicate the existing setup.

Use a clean modern UI.

The user prefers a dark theme.

Use:

dark background
clean cards
good spacing
professional typography
subtle borders
clear buttons
simple animations only where useful

Do NOT make it look like an "AI-generated website".

Avoid:

huge gradients
excessive glassmorphism
unnecessary glowing effects
overloaded dashboards
excessive animations
fake statistics

============================================================
18. FRONTEND PAGE 1 — SEARCH
============================================================

Create a simple homepage.

Header:

EventIQ

Subtitle:

Intelligent Event Retrieval and Ranking System

Main search box:

"Search for events..."

Example queries:

AI workshops in Mumbai

machine learning events for students

free technology events in Pune

startup networking events in Bengaluru

Buttons:

Search

Possibly model selector:

TF-IDF
BM25
Semantic
Hybrid

Default:

Hybrid

Allow the user to change the model so the project demonstration can show differences between retrieval approaches.

============================================================
19. FRONTEND PAGE 2 — SEARCH RESULTS
============================================================

Display:

Query

Selected retrieval model

Number of results

Ranked event cards

Each card should show:

Rank

Event title

Category

Subcategory

City

Venue

Date

Price

Free/Paid

Rating

Relevance score

Use a clean card layout.

Example:

#1
Machine Learning Workshop

Technology
Machine Learning

Mumbai

12 Oct 2026

Free

Score: 0.842

============================================================
20. FILTERS
============================================================

Add simple filters if practical:

City
Category
Free only
Date

Do not allow filters to become more complicated than necessary.

The main purpose is to demonstrate the retrieval system.

============================================================
21. EVENT DETAILS
============================================================

When a user clicks an event:

show:

Title
Description
Category
Subcategory
Tags
City
State
Venue
Address
Date
Time
Price
Free/Paid
Organizer
Expected attendees
Audience
Language
Rating

Create:

/events/:eventId

============================================================
22. EVALUATION DASHBOARD
============================================================

This is important for the academic demonstration.

Create a simple evaluation page:

/evaluation

Show a comparison table:

Model | P@5 | P@10 | Recall@10 | F1 | MRR | NDCG@10

TF-IDF
BM25
Semantic
Hybrid

Use charts where useful.

Possible charts:

Precision@5 comparison
Precision@10 comparison
Recall@10 comparison
MRR comparison
NDCG@10 comparison

Do not fabricate results.

If a model has not yet been evaluated, display:

"Not evaluated"

rather than inventing a number.

The TF-IDF baseline values must be displayed accurately:

P@5 = 0.3552
P@10 = 0.2628
Recall@10 = 0.1752
F1 = 0.2102
MRR = 0.4820
NDCG@10 = 0.3101

============================================================
23. PROJECT ARCHITECTURE
============================================================

Keep the architecture clean.

Recommended structure:

EventIQ/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── schemas/
│   │
│   ├── retrieval/
│   │   ├── preprocessing.py
│   │   ├── tfidf.py
│   │   ├── bm25.py
│   │   ├── semantic.py
│   │   └── hybrid.py
│   │
│   ├── evaluation/
│   │
│   └── scripts/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   │
│   └── ...
│
├── data/
│
├── evaluation/
│
├── docs/
│
├── .env
├── .env.example
├── .gitignore
└── README.md

You may adapt this structure to the existing project.

Do not reorganize the entire repository unnecessarily.

============================================================
24. CODE QUALITY
============================================================

Write production-quality academic project code.

Requirements:

- modular
- readable
- maintainable
- meaningful variable names
- functions should have one clear responsibility
- avoid duplicated code
- avoid unnecessary abstraction
- avoid giant files
- avoid hard-coded absolute paths
- use environment variables for configuration
- use proper exception handling
- validate API inputs
- avoid leaking secrets
- avoid debug prints in production code

Comments should explain WHY something exists when necessary.

Do not comment every obvious line.

============================================================
25. PERFORMANCE
============================================================

Do not recompute everything on every API request.

For example:

Do NOT rebuild TF-IDF every time a user searches.

Do NOT rebuild BM25 every request.

Do NOT regenerate embeddings every request.

Load/build indexes once when appropriate.

If caching is useful, implement a simple solution.

However, don't over-engineer.

The dataset is only 10,000 events.

Keep the architecture appropriate for this scale.

============================================================
26. TESTING
============================================================

Test the system systematically.

Backend tests should cover:

GET /api/health

GET /api/events/count

GET /api/events/{event_id}

POST /api/search

Invalid search requests

Unknown event IDs

Unknown retrieval model

Empty query

Frontend should be tested manually for:

search
results
filters
event details
model switching
evaluation dashboard
API failure handling

============================================================
27. RETRIEVAL TEST QUERIES
============================================================

Use these as standard demonstration queries:

1. AI workshops in Mumbai

2. machine learning events for students

3. startup networking events in Bengaluru

4. photography workshops for beginners

5. free technology events in Pune

Also create additional queries that test:

location

category

audience

event type

price

free events

date

semantic similarity

mixed requirements

============================================================
28. IMPORTANT RESEARCH REQUIREMENT
============================================================

Do not make claims such as:

"Hybrid is better"

until it has actually been evaluated.

Do not fabricate metrics.

Do not alter relevance labels simply to improve a model.

Do not modify the test dataset after seeing results unless there is a documented data-quality problem.

The comparison must be scientifically defensible.

The project should clearly distinguish:

retrieval

ranking

evaluation

frontend presentation

============================================================
29. EVALUATION PIPELINE
============================================================

The final evaluation pipeline should be reproducible.

Ideally:

python backend/scripts/evaluate_tfidf.py

python backend/scripts/evaluate_bm25.py

python backend/scripts/evaluate_semantic.py

python backend/scripts/evaluate_hybrid.py

Then produce a combined result.

For example:

evaluation/results.csv

with columns:

model
precision_at_5
precision_at_10
recall_at_10
f1
mrr
ndcg_at_10

Also preserve individual model results if useful.

============================================================
30. DOCUMENTATION
============================================================

Create/update:

README.md

It should explain:

1. Project overview
2. Problem statement
3. Objectives
4. Architecture
5. Dataset
6. Database
7. Retrieval models
8. Ranking methodology
9. Evaluation methodology
10. API
11. Frontend
12. Installation
13. Running the backend
14. Running the frontend
15. Evaluation
16. Results
17. Limitations
18. Future work

Do not claim future components are implemented if they are not.

============================================================
31. ACADEMIC DOCUMENTATION
============================================================

Create a docs folder if appropriate.

Useful documents:

docs/
    architecture.md
    retrieval.md
    evaluation.md
    api.md

These documents should explain the system in language suitable for a final-year project presentation/viva.

Include explanations of:

TF-IDF

Cosine similarity

BM25

Semantic embeddings

Cosine similarity for embeddings

Hybrid retrieval

Precision

Recall

F1

MRR

NDCG

Explain why each method is used.

============================================================
32. ARCHITECTURE DIAGRAM
============================================================

Create a clean architecture diagram in documentation.

Conceptually:

User
  ↓
React Frontend
  ↓
FastAPI
  ↓
Query Processing
  ↓
Retrieval Layer
  ├── TF-IDF
  ├── BM25
  ├── Semantic
  └── Hybrid
  ↓
Ranking
  ↓
PostgreSQL
  ↓
Ranked Results
  ↓
React UI

Also show:

Evaluation Dataset
       ↓
Evaluation Pipeline
       ↓
Metrics
       ↓
Model Comparison

If possible, generate a Mermaid diagram in README/docs.

============================================================
33. DATABASE PERFORMANCE
============================================================

Use PostgreSQL appropriately.

Avoid retrieving the entire database unnecessarily for every search.

However, for a 10,000-event academic dataset, a reasonable in-memory retrieval index is acceptable.

If using PostgreSQL for filtering:

category
city
date
free status

should be handled efficiently.

============================================================
34. SECURITY
============================================================

Absolutely do NOT commit:

.env

database passwords

API keys

secret keys

private tokens

credentials

local virtual environments

cache files

temporary files

Use:

.env

.env.example

.gitignore

Verify Git status before commits.

============================================================
35. GIT WORKFLOW
============================================================

Do not make giant meaningless commits.

Use logical commits such as:

"Add BM25 retrieval baseline"

"Add semantic retrieval"

"Add hybrid ranking"

"Add search API"

"Add EventIQ frontend"

"Add evaluation dashboard"

Before each major commit:

run tests

check git diff

check git status

verify no secrets are staged

Do not push automatically unless I explicitly ask you to push.

============================================================
36. IMPORTANT: DO NOT DESTROY EXISTING WORK
============================================================

The existing TF-IDF implementation is part of the project.

The existing evaluation values are part of the project's baseline.

Do NOT:

delete TF-IDF

replace it with BM25

rename it unnecessarily

change its parameters without justification

change the relevance dataset

change its evaluation protocol

overwrite baseline results

The final project must be able to run all retrieval methods independently.

============================================================
37. HANDLING UNCERTAINTY
============================================================

If you encounter something where you need my decision:

STOP and ask me.

Examples:

- database password
- GitHub repository URL
- preferred deployment platform
- whether authentication is required
- whether external APIs are allowed
- whether a large model can be downloaded
- whether a specific frontend library should be used
- academic formatting requirements
- university-specific requirements

Do not make major assumptions.

For small implementation details, use sensible engineering judgment.

============================================================
38. HOW TO WORK
============================================================

Work incrementally.

Do not attempt to create the entire system in one uncontrolled operation.

Follow this sequence:

STEP 1
Inspect existing repository.

STEP 2
Report current state.

STEP 3
Verify Phase 1 and Phase 2.

STEP 4
Implement BM25.

STEP 5
Test BM25.

STEP 6
Evaluate BM25.

STEP 7
Compare TF-IDF vs BM25.

STEP 8
Implement semantic retrieval.

STEP 9
Evaluate semantic retrieval.

STEP 10
Implement hybrid retrieval.

STEP 11
Evaluate hybrid retrieval.

STEP 12
Implement structured ranking improvements if justified.

STEP 13
Build FastAPI search endpoints.

STEP 14
Build simple React frontend.

STEP 15
Connect frontend to backend.

STEP 16
Build event details.

STEP 17
Build evaluation dashboard.

STEP 18
Perform complete testing.

STEP 19
Update documentation.

STEP 20
Prepare final project structure and run instructions.

============================================================
39. AFTER EACH MAJOR PHASE
============================================================

After each phase, provide me with:

1. What was implemented
2. Files created
3. Files modified
4. Commands to run
5. Test results
6. Evaluation results, if applicable
7. Any problems encountered
8. What the next phase will be

Do not simply say "done."

Give concrete technical results.

============================================================
40. FINAL PROJECT ACCEPTANCE CRITERIA
============================================================

The project is considered complete only when:

[ ] PostgreSQL works

[ ] Dataset loads correctly

[ ] FastAPI works

[ ] Health endpoint works

[ ] Event count endpoint works

[ ] TF-IDF works

[ ] BM25 works

[ ] Semantic retrieval works

[ ] Hybrid retrieval works

[ ] Evaluation works

[ ] Metrics are reproducible

[ ] Model comparison works

[ ] Search API works

[ ] React frontend works

[ ] Search works from frontend

[ ] Retrieval model selection works

[ ] Results are displayed correctly

[ ] Event details work

[ ] Filters work

[ ] Evaluation dashboard works

[ ] No fabricated metrics

[ ] No secrets committed

[ ] README is complete

[ ] Architecture is documented

[ ] Project can be demonstrated locally

============================================================
41. FINAL DEMONSTRATION FLOW
============================================================

The finished project should support this demonstration:

1. Start PostgreSQL.

2. Start FastAPI.

3. Start React.

4. Open EventIQ.

5. Search:

"machine learning events for students"

6. Show ranked results.

7. Switch:

TF-IDF → BM25 → Semantic → Hybrid

8. Show how ranking changes.

9. Search:

"free technology events in Pune"

10. Demonstrate structured information such as:

city

category

free status

11. Open an event.

12. Open Evaluation Dashboard.

13. Show comparison:

TF-IDF
BM25
Semantic
Hybrid

14. Explain:

retrieval → ranking → evaluation.

============================================================
42. MOST IMPORTANT INSTRUCTION
============================================================

Treat this as a real academic software engineering project.

Prioritize:

correctness

reproducibility

explainability

clean architecture

simple UI

proper evaluation

maintainability

Do NOT prioritize flashy UI over the retrieval system.

Do NOT over-engineer.

Do NOT fabricate.

Do NOT break working components.

Do NOT ask me questions that can be answered by inspecting the repository.

ASK ME only when you genuinely need information that cannot be determined from the project.

============================================================
43. START NOW
============================================================

Start by inspecting the existing EventIQ repository.

Do NOT immediately write code.

First determine exactly what exists.

Then provide:

PROJECT STATUS

Completed:
...

Partially completed:
...

Missing:
...

Potential issues:
...

Recommended next action:
...

After that, if no clarification is required, begin Phase 3 — BM25.

If clarification is required, ask me the questions before making the relevant changes.

Remember:

The current TF-IDF implementation and its evaluation results are the baseline and must be preserved.