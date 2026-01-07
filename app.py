import streamlit as st
import pandas as pd
from pathlib import Path

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="AI Ops Prioritization", layout="wide")
st.title("🧠 AI Ops Prioritization & Risk Scoring System")
st.caption("Real dataset: GitHub Issues → heuristic labeling → priority scoring → dashboard")

DATA_FILE = Path("data/github_issues_scored_50.csv")

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        st.error(f"Missing file: {DATA_FILE}. Run:\n\n1) python src/local_label.py\n2) python src/scoring.py")
        st.stop()
    df = pd.read_csv(DATA_FILE)

    # Safety defaults if columns are missing
    if "priority_score" not in df.columns:
        df["priority_score"] = 0
    if "risk_level" not in df.columns:
        df["risk_level"] = "Low"
    if "llm_category" not in df.columns:
        df["llm_category"] = "Other"
    if "llm_severity" not in df.columns:
        df["llm_severity"] = 3
    if "llm_time_sensitivity" not in df.columns:
        df["llm_time_sensitivity"] = "Medium"
    if "llm_reason" not in df.columns:
        df["llm_reason"] = ""
    if "score_breakdown" not in df.columns:
        df["score_breakdown"] = ""
    if "title" not in df.columns:
        df["title"] = ""
    if "description" not in df.columns:
        df["description"] = ""

    return df

df = load_data()

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

category_filter = st.sidebar.multiselect(
    "Category",
    options=sorted(df["llm_category"].dropna().unique()),
    default=list(sorted(df["llm_category"].dropna().unique()))
)

risk_filter = st.sidebar.multiselect(
    "Risk Level",
    options=["High", "Medium", "Low"],
    default=["High", "Medium", "Low"]
)

min_score = st.sidebar.slider(
    "Minimum Priority Score",
    min_value=0,
    max_value=100,
    value=0,
    step=5
)

filtered = df[
    (df["llm_category"].isin(category_filter)) &
    (df["risk_level"].isin(risk_filter)) &
    (df["priority_score"] >= min_score)
].copy()

# ----------------------------
# KPIs
# ----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Issues", len(filtered))
col2.metric("High Risk", int((filtered["risk_level"] == "High").sum()))
col3.metric("Avg Priority Score", int(filtered["priority_score"].mean()) if len(filtered) else 0)
col4.metric("Max Priority Score", int(filtered["priority_score"].max()) if len(filtered) else 0)

st.divider()

# ----------------------------
# Top 10 high risk block
# ----------------------------
st.markdown("### 🚨 Top 10 High-Risk Issues")
top_high = filtered[filtered["risk_level"] == "High"].sort_values("priority_score", ascending=False).head(10)

top_cols = [c for c in ["ticket_id", "title", "llm_category", "priority_score", "llm_reason"] if c in top_high.columns]
if len(top_high):
    st.dataframe(top_high[top_cols], use_container_width=True, hide_index=True)
else:
    st.info("No High-Risk issues match the current filters.")

st.divider()

# ----------------------------
# Overview charts
# ----------------------------
st.markdown("### 📊 Overview")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Issues by Category")
    st.bar_chart(filtered["llm_category"].value_counts())

with c2:
    st.subheader("Issues by Risk Level")
    st.bar_chart(filtered["risk_level"].value_counts())

st.divider()

# ----------------------------
# Main table
# ----------------------------
st.markdown("### 🔥 Prioritized Issue List")

show_cols = [
    "ticket_id",
    "title",
    "llm_category",
    "llm_severity",
    "llm_time_sensitivity",
    "priority_score",
    "risk_level",
    "llm_reason",
]
show_cols = [c for c in show_cols if c in df.columns]

table = filtered[show_cols].sort_values("priority_score", ascending=False).reset_index(drop=True)

selected = st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
    selection_mode="single-row",
    on_select="rerun"
)

# ----------------------------
# Details panel
# ----------------------------
if selected and selected.get("selection", {}).get("rows"):
    row_idx = selected["selection"]["rows"][0]
    ticket_id = table.loc[row_idx, "ticket_id"] if "ticket_id" in table.columns else None

    st.markdown("### 🧾 Issue Details")

    # pull the full row from filtered (so it matches what user sees)
    if ticket_id is not None and "ticket_id" in filtered.columns:
        full_row = filtered[filtered["ticket_id"] == ticket_id].iloc[0]
    else:
        full_row = filtered.iloc[row_idx]

    left, right = st.columns([2, 1])

    with left:
        st.write("**Issue ID:**", full_row.get("ticket_id", ""))
        st.write("**Title:**", full_row.get("title", ""))
        st.write("**Description:**", full_row.get("description", ""))

    with right:
        st.write("**Category:**", full_row.get("llm_category", "Other"))
        st.write("**Severity:**", full_row.get("llm_severity", 3))
        st.write("**Time Sensitivity:**", full_row.get("llm_time_sensitivity", "Medium"))
        st.write("**Priority Score:**", full_row.get("priority_score", 0))
        st.write("**Risk Level:**", full_row.get("risk_level", "Low"))

    st.markdown("### 🧠 Why this score?")
    st.write("**AI/Logic Reason:**", full_row.get("llm_reason", ""))

    breakdown = full_row.get("score_breakdown", "")
    if isinstance(breakdown, str) and breakdown.strip():
        st.code(breakdown)
    else:
        st.caption("No score breakdown found (add `score_breakdown` in scoring.py for explainability).")
