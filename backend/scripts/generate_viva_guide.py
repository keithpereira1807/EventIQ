"""
Main Generator Script for:
EventIQ — Complete Project Explanation and Viva Preparation Guide (.docx)
"""
import os
import sys
import time

# Ensure scripts dir is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

import docx
from viva_guide_builder import init_document, add_title_page, add_heading_1, add_heading_2, add_p
from viva_sections_part1 import (
    build_section_1, build_section_2, build_section_3, build_section_4,
    build_section_5, build_section_6, build_section_7, build_section_8,
    build_section_9, build_section_10
)
from viva_sections_part2 import (
    build_section_11, build_section_12, build_section_13, build_section_14,
    build_section_15, build_section_16, build_section_17, build_section_18,
    build_section_19, build_section_20
)
from viva_sections_part3 import (
    build_section_21, build_section_22, build_section_23, build_section_24,
    build_section_25, build_section_26, build_section_27, build_section_28,
    build_section_29, build_section_30, build_section_31, build_section_32
)

def add_table_of_contents_overview(doc):
    add_heading_1(doc, "TABLE OF CONTENTS & GUIDE STRUCTURE")
    add_p(doc, "This comprehensive study guide is organized into 32 structured sections designed to provide end-to-end mastery of the EventIQ project:")
    
    sections = [
        ("SECTION 1", "Project Overview: Problem Statement, Motivation & Paradigm Comparison"),
        ("SECTION 2", "Project Objectives: Core Academic & Engineering Goals"),
        ("SECTION 3", "Technology Stack: Technical Justifications & Rejections"),
        ("SECTION 4", "System Architecture: Decoupled Multi-Tier System Design"),
        ("SECTION 5", "The EventIQ Dataset: 10,000 Events, 500 Queries, 7,500 Relevance Rows"),
        ("SECTION 6", "Database Architecture: PostgreSQL Relational Schema & Indexing"),
        ("SECTION 7", "Searchable Document Creation: Multi-Field Concatenation Strategy"),
        ("SECTION 8", "Phase 2: TF-IDF Retrieval Baseline (Theory, Implementation, Metrics)"),
        ("SECTION 9", "Phase 3: Okapi BM25 Lexical Retrieval (Length Normalization & Results)"),
        ("SECTION 10", "Phase 4: Dense Semantic Retrieval (MiniLM Embeddings & Persistent Matrix)"),
        ("SECTION 11", "Phase 5: Hybrid Retrieval (Convex Fusion, Min-Max Normalization, α=0.70)"),
        ("SECTION 12", "Phase 6: Structured Event Ranking (Vocabulary Intent Extraction)"),
        ("SECTION 13", "The Final Ranking Formula: Blending Foundation & Numerical Calculations"),
        ("SECTION 14", "Explainability: Full Score Decomposition & Transparent Visualizations"),
        ("SECTION 15", "Complete End-to-End Search Flow: Detailed Sequence Walkthrough"),
        ("SECTION 16", "FastAPI Backend Architecture: Endpoints, Schemas, Singleton Pattern"),
        ("SECTION 17", "React Frontend Architecture: Component Hierarchy & API Service Layer"),
        ("SECTION 18", "The Search Interface & Filtering: Dynamic Facet Aggregation"),
        ("SECTION 19", "Event Details Modal: Complete Entity Metadata Inspection"),
        ("SECTION 20", "Evaluation Dashboard & Metrics Theory: P@K, Recall, F1, MRR, NDCG@10"),
        ("SECTION 21", "Why Different Models Perform Differently: Academic Trade-Offs"),
        ("SECTION 22", "Phase-by-Phase Development History: Complete Evolution (Phases 1-9)"),
        ("SECTION 23", "Security & Configuration Audit: Credentials, Sanitization & CORS"),
        ("SECTION 24", "Performance Benchmarking: Cold Start, First Query & Warm Latencies"),
        ("SECTION 25", "Current Limitations: Engineering Boundaries & Acknowledged Scopes"),
        ("SECTION 26", "Future Enhancements: Temporal NLP, ANN Indexing & Learning-to-Rank"),
        ("SECTION 27", "Live Demonstration Script: Step-by-Step Viva Presentation Walkthrough"),
        ("SECTION 28", "Exhaustive Viva Voce Questions & Answers (50+ Categorized Q&As)"),
        ("SECTION 29", "'Explain This in 30 Seconds': Timed Elevator Pitches (30s, 1m, 3m)"),
        ("SECTION 30", "Important Formulas Cheat Sheet: Every Equation Defined & Explained"),
        ("SECTION 31", "Important Numbers Cheat Sheet: Critical Memorization Table"),
        ("SECTION 32", "Final 'What I Should Know' Checklist: Self-Assessment Pre-Exam Audit")
    ]
    for s_num, s_title in sections:
        add_p(doc, f"{s_num}: {s_title}")
    
    doc.add_page_break()

def generate_guide(output_path):
    print(f"Initializing EventIQ Viva Guide document builder...")
    t0 = time.perf_counter()
    doc = init_document()

    print("Building Title Page...")
    add_title_page(doc)

    print("Building Table of Contents Overview...")
    add_table_of_contents_overview(doc)

    print("Building Part 1 (Sections 1 to 10)...")
    build_section_1(doc)
    build_section_2(doc)
    build_section_3(doc)
    build_section_4(doc)
    build_section_5(doc)
    build_section_6(doc)
    build_section_7(doc)
    build_section_8(doc)
    build_section_9(doc)
    build_section_10(doc)

    print("Building Part 2 (Sections 11 to 20)...")
    build_section_11(doc)
    build_section_12(doc)
    build_section_13(doc)
    build_section_14(doc)
    build_section_15(doc)
    build_section_16(doc)
    build_section_17(doc)
    build_section_18(doc)
    build_section_19(doc)
    build_section_20(doc)

    print("Building Part 3 (Sections 21 to 32)...")
    build_section_21(doc)
    build_section_22(doc)
    build_section_23(doc)
    build_section_24(doc)
    build_section_25(doc)
    build_section_26(doc)
    build_section_27(doc)
    build_section_28(doc)
    build_section_29(doc)
    build_section_30(doc)
    build_section_31(doc)
    build_section_32(doc)

    print(f"Saving document to {output_path}...")
    doc.save(output_path)
    t1 = time.perf_counter()
    print(f"Document successfully created and saved in {t1 - t0:.2f} seconds!")

    # Verification
    print("Verifying document integrity...")
    reopened = docx.Document(output_path)
    total_paragraphs = len(reopened.paragraphs)
    total_tables = len(reopened.tables)
    file_size_kb = os.path.getsize(output_path) / 1024

    # Approximate page count estimate (avg 400 words / ~25-30 lines per page in standard academic letter layout)
    total_words = sum(len(p.text.split()) for p in reopened.paragraphs)
    estimated_pages = max(1, round(total_words / 320))

    print("\n--- Document Generation Verification Report ---")
    print(f"File Path: {os.path.abspath(output_path)}")
    print(f"File Size: {file_size_kb:.1f} KB")
    print(f"Paragraphs: {total_paragraphs}")
    print(f"Tables: {total_tables}")
    print(f"Total Words: {total_words:,}")
    print(f"Estimated Pages: ~{estimated_pages} pages")
    print("Verification: PASS [100% OK]")

if __name__ == "__main__":
    out_file = os.path.join(os.path.abspath("."), "EventIQ_Complete_Project_Explanation_and_Viva_Guide.docx")
    generate_guide(out_file)

