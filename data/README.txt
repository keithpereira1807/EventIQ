# EventIQ Indian Event Retrieval Dataset

This is a SYNTHETIC RESEARCH DATASET created for the EventIQ academic project.
It is designed to model realistic Indian event metadata in English.
Individual event listings, organizer associations, attendance figures, ratings,
and descriptions should NOT be interpreted as real-world event listings.

Files:
- events.csv: 10,000 synthetic event records
- queries.csv: 500 search queries
- relevance.csv: 7,500 synthetic relevance judgments

Relevance scale:
3 = highly relevant
2 = relevant
1 = partially relevant
0 = not relevant (unlisted pairs can be treated as non-relevant only if the
evaluation protocol explicitly permits that assumption).

The dataset uses real Indian city/state names, publicly known venue names, and
real geographic city coordinates as contextual metadata, while the event
listings themselves are synthetic.

Recommended EventIQ experiments:
1. TF-IDF + cosine similarity
2. BM25
3. Sentence-embedding semantic retrieval
4. Hybrid ranking using text, semantic similarity, category, location, date,
   price/free status and audience
5. Precision@K, Recall@K, MRR and NDCG@K
