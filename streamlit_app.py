import os
import sys
import json
import numpy as np
import pandas as pd
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="EventIQ — Intelligent Event Retrieval & Ranking",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")
EMBEDDINGS_PATH = os.path.join(PROJECT_ROOT, "data", "event_embeddings.npy")
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluation")

# Custom Dark Theme Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .event-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease;
    }
    .event-card:hover {
        border-color: #6366f1;
    }
    .badge-category {
        background-color: #0284c7;
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-city {
        background-color: #334155;
        color: #cbd5e1;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-free {
        background-color: #059669;
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-paid {
        background-color: #d97706;
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    .score-chip {
        float: right;
        font-family: monospace;
        font-size: 0.95rem;
        font-weight: 700;
        color: #38bdf8;
        background: #0f172a;
        padding: 4px 12px;
        border-radius: 8px;
        border: 1px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading 10,000 events corpus and AI retrieval models...")
def load_search_service():
    from backend.app.services.search_service import SearchService
    return SearchService.get_instance()


# App Header
st.markdown('<div class="main-header">EventIQ — Intelligent Event Retrieval & Ranking System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Evaluating Classical Lexical Matchers, Dense Neural Embeddings, Hybrid Convex Score Fusion, and Intent-Aware Re-ranking over a 10,000-Event Indian Corpus.</div>', unsafe_allow_html=True)

# Navigation Tabs
tab_search, tab_eval, tab_arch = st.tabs(["🔍 Search & Retrieval", "📊 Evaluation Benchmarks", "🏗️ System Architecture"])

service = load_search_service()

# ==============================================================================
# TAB 1: Search & Retrieval
# ==============================================================================
with tab_search:
    # Sidebar Filters
    with st.sidebar:
        st.header("⚙️ Retrieval Parameters")

        model_display_names = {
            "Structured Ranking (λ=0.15)": "structured",
            "Hybrid Fusion (α=0.70)": "hybrid",
            "BM25 Lexical (Okapi)": "bm25",
            "TF-IDF Baseline (Vector Space)": "tfidf",
            "Dense Semantic (all-MiniLM-L6-v2)": "semantic",
        }

        selected_model_label = st.selectbox(
            "Information Retrieval Model",
            options=list(model_display_names.keys()),
            index=0,
            help="Choose between lexical matching, dense sentence embeddings, convex hybrid fusion, or intent re-ranking.",
        )
        selected_model = model_display_names[selected_model_label]

        top_k = st.slider("Number of Results (Top-K)", min_value=3, max_value=25, value=10, step=1)

        st.markdown("---")
        st.subheader("💡 Example Queries")
        examples = [
            "free technology workshops in Mumbai for students",
            "machine learning and AI conferences in Bengaluru",
            "photography workshops for beginners in Pune",
            "startup pitching and venture capital events in Delhi",
            "music festivals and live concerts in Goa",
            "cybersecurity bootcamps in Hyderabad"
        ]
        example_choice = st.selectbox("Quick populate query:", ["Custom Query"] + examples)

        st.markdown("---")
        st.info("ℹ️ **Corpus Details:**\n- 10,000 Events\n- 20 Major Indian Cities\n- 384-dimensional Embeddings\n- Precomputed NPY Vectors")

    # Search Bar
    default_text = example_choice if example_choice != "Custom Query" else ""
    query_input = st.text_input(
        "Enter conversational event query:",
        value=default_text,
        placeholder="e.g. free technology workshops in Mumbai for students",
    )

    col_btn, col_clear = st.columns([1, 6])
    retrieve_clicked = col_btn.button("🔍 Retrieve Events", type="primary", use_container_width=True)

    active_query = query_input.strip()

    if active_query:
        with st.spinner(f"Running '{selected_model_label}' retrieval across 10,000 events..."):
            try:
                search_res = service.search(query=active_query, model_name=selected_model, top_k=top_k)
                results = search_res.get("results", [])

                st.markdown(f"### Found **{len(results)}** matching events for: *\"{active_query}\"*")
                st.caption(f"Architecture: **{selected_model_label}** | Ranking Metric: Relevance Score")

                if not results:
                    st.warning("No matching events found. Try expanding your search terms.")

                for idx, ev in enumerate(results, 1):
                    with st.container():
                        is_free = ev.get("is_free", False)
                        price = ev.get("price", 0)
                        currency = ev.get("currency", "INR")
                        price_str = "Free" if is_free or price == 0 else f"{currency} {price:,.0f}"
                        badge_price = "badge-free" if is_free or price == 0 else "badge-paid"

                        score_val = ev.get("score", 0.0)
                        title = ev.get("title", "Untitled Event")
                        city = ev.get("city", "India")
                        state = ev.get("state", "")
                        location_str = f"{city}, {state}" if state else city
                        category = ev.get("category", "General")
                        date_str = ev.get("start_date", "TBA")
                        organizer = ev.get("organizer", "Organizer")
                        venue = ev.get("venue", "Venue")
                        audience = ev.get("audience", "All Audiences")
                        rating = ev.get("rating")
                        rating_str = f"⭐ {rating:.1f}" if rating else ""
                        desc = ev.get("description", "No description available.")

                        st.markdown(f"""
                        <div class="event-card">
                            <span class="score-chip">Score: {score_val:.4f}</span>
                            <h4 style="margin: 0 0 0.5rem 0; color: #f8fafc;">#{idx}. {title}</h4>
                            <div style="margin-bottom: 0.6rem;">
                                <span class="badge-category">{category}</span>
                                <span class="badge-city">📍 {location_str}</span>
                                <span class="{badge_price}">🎟️ {price_str}</span>
                                <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">📅 {date_str}</span>
                                <span style="font-size: 0.8rem; color: #fbbf24; margin-left: 6px;">{rating_str}</span>
                            </div>
                            <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 0.5rem; line-height: 1.4;">{desc}</p>
                            <div style="font-size: 0.78rem; color: #64748b;">
                                🏢 <b>Organizer:</b> {organizer} &nbsp;|&nbsp; 📍 <b>Venue:</b> {venue} &nbsp;|&nbsp; 👥 <b>Target Audience:</b> {audience}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Explainability Expander for Structured Ranking
                        if selected_model == "structured" and "matched_signals" in ev:
                            with st.expander(f"🔎 Explainability & Score Decomposition for #{idx} ({title})"):
                                c1, c2, c3 = st.columns(3)
                                c1.metric("Final Combined Score", f"{ev.get('final_score', 0):.4f}")
                                c2.metric("Hybrid Content Score (85%)", f"{ev.get('hybrid_score', 0):.4f}")
                                c3.metric("Structured Intent Score (15%)", f"{ev.get('structured_score', 0):.4f}")

                                signals = ev.get("matched_signals", {})
                                active_sigs = [f"**{k.title()}**: `{v}`" for k, v in signals.items() if v is not None]
                                if active_sigs:
                                    st.markdown("🎯 **Detected Query Intent Signals:** " + " • ".join(active_sigs))

                                contribs = ev.get("signal_contributions", {})
                                if contribs:
                                    st.write("Signal Breakdown:")
                                    st.dataframe(
                                        pd.DataFrame([
                                            {"Signal": k.title(), "Match Contribution": f"{v:.4f}"}
                                            for k, v in contribs.items()
                                        ]),
                                        use_container_width=True,
                                        hide_index=True
                                    )

            except Exception as ex:
                st.error(f"Search execution failed: {ex}")
    else:
        st.info("👆 Type a natural-language query above or choose an example from the sidebar to retrieve events.")


# ==============================================================================
# TAB 2: Evaluation Benchmarks
# ==============================================================================
with tab_eval:
    st.markdown("### Reproducible Information Retrieval Benchmarks")
    st.markdown("""
    The EventIQ architectures were empirically evaluated across a standardized test suite of **500 ground-truth query topics** 
    and **7,500 graded relevance judgments** (graded 1–3) following standard TREC / Cranfield evaluation protocols.
    """)

    eval_data = service.get_evaluation()
    comparison_table = eval_data.get("comparison", [])

    if comparison_table:
        df_comp = pd.DataFrame(comparison_table)
        df_comp.columns = ["Model Architecture", "P@5", "P@10", "Recall@10", "F1 Score", "MRR", "NDCG@10"]
        st.dataframe(
            df_comp.style.highlight_max(subset=["P@5", "P@10", "Recall@10", "F1 Score", "MRR", "NDCG@10"], color="#1e3a8a"),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Model Performance Visual Comparison")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.caption("Precision@10 vs Recall@10")
            chart_df = df_comp.set_index("Model Architecture")[["P@10", "Recall@10"]]
            st.bar_chart(chart_df)

        with chart_col2:
            st.caption("Ranking Quality (MRR vs NDCG@10)")
            ranking_df = df_comp.set_index("Model Architecture")[["MRR", "NDCG@10"]]
            st.bar_chart(ranking_df)

        st.markdown(r"""
        #### Key Academic Insights & Trade-Offs:
        1. **Top-Rank Precision & Order**: **Structured Ranking ($\lambda=0.15$)** achieves the highest **NDCG@10 (0.3731)** and highest **MRR (0.4991)** by boosting events that satisfy detected constraints (e.g. specific city, free admission, target demographic).
        2. **Coverage & Robustness**: **Hybrid Fusion ($\alpha=0.70$)** achieves the highest **Recall@10 (0.2268)** and highest **F1 (0.2722)**, leveraging dense semantic embeddings to bridge vocabulary gaps where lexical matchers fail.
        3. **Immediate Precision**: **Okapi BM25** delivers the highest immediate **Precision@5 (0.3860)** due to exact query token saturation in short document listings.
        """)


# ==============================================================================
# TAB 3: System Architecture
# ==============================================================================
with tab_arch:
    st.markdown("### System Architecture & IR Formulations")

    st.markdown("""
    ```
    User Query (Natural Language)
             │
             ├──► 1. Lexical BM25 (Okapi Token Probabilities) ──┐
             │                                                  ├──► Hybrid Convex Score Fusion (α = 0.70)
             └──► 2. Dense Semantic Vector (all-MiniLM-L6-v2) ──┘            │
                                                                             ▼
    Structured Query Intent Signals (City, Free/Paid, Audience) ──► Structured Event Ranker (λ = 0.15)
                                                                             │
                                                                             ▼
                                                                 Ranked Event Output
    ```
    """)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 1. BM25 Lexical Retrieval")
        st.latex(r"\text{score}_{\text{BM25}}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}")
        st.markdown("*Parameters:* $k_1 = 1.5$, $b = 0.75$. Unsupervised exact lexical token matching normalized by corpus document length.")

        st.markdown("#### 2. Dense Semantic Retrieval")
        st.latex(r"\text{sim}_{\text{Semantic}}(q, d) = \frac{\mathbf{e}_q \cdot \mathbf{e}_d}{\|\mathbf{e}_q\|_2 \|\mathbf{e}_d\|_2}")
        st.markdown("*Encoder:* `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). Precomputed vector matrix stored in `data/event_embeddings.npy`.")

    with col_b:
        st.markdown("#### 3. Convex Hybrid Score Fusion")
        st.latex(r"\text{HybridScore}(d) = \alpha \cdot \text{BM25}_{\text{norm}}(d) + (1 - \alpha) \cdot \text{sim}_{\text{Semantic}}(q, d)")
        st.markdown("*Convex parameter:* $\alpha = 0.70$. Merges lexical probabilistic relevance with deep contextual semantics.")

        st.markdown("#### 4. Structured Intent Re-Ranking")
        st.latex(r"\text{FinalScore}(d) = (1 - \lambda) \cdot \text{HybridScore}(d) + \lambda \cdot \text{StructuredScore}(d)")
        st.markdown(r"*Soft blend:* $\lambda = 0.15$. Detects and extracts structured metadata constraints (city, admission, audience) from natural text.")
