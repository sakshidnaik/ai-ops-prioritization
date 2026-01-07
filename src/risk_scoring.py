import pandas as pd

INPUT = "data/github_issues_labeled_50.csv"
OUTPUT = "data/github_issues_scored_50.csv"

CRITICAL_WORDS = [
    "blocker", "regression", "crash", "data loss", "security",
    "panic", "outage", "incident", "sev0", "sev1", "p0", "p1", "urgent"
]

HIGH_WORDS = [
    "broken", "fails", "failure", "error", "timeout", "exception",
    "cannot", "can't", "stuck", "deadlock", "corrupt", "leak"
]

CATEGORY_BOOST = {
    "Outage/Incident": 15,
    "Data Quality Fix": 10,
    "Data/Reporting": 8,
    "Access/Permissions": 6,
    "Process/Workflow Change": 4,
    "Ops Backlog": 3,
    "KPI Definition": 2,
    "Other": 0,
}

TIME_SENSITIVITY_BOOST = {
    "High": 12,
    "Medium": 6,
    "Low": 0,
}

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, int(x)))

def risk_bucket(score: int) -> str:
    if score >= 80:
        return "High"
    if score >= 55:
        return "Medium"
    return "Low"

def keyword_boost(text: str) -> int:
    t = (text or "").lower()
    boost = 0
    if any(w in t for w in CRITICAL_WORDS):
        boost += 18
    if any(w in t for w in HIGH_WORDS):
        boost += 10
    return boost

def compute_priority(row) -> tuple[int, str]:
    # base severity (1–5)
    sev = row.get("llm_severity", 3)
    try:
        sev = int(sev)
    except:
        sev = 3

    # Score severity strongly (max 60)
    severity_pts = sev * 12  # 1->12, 5->60

    # Time sensitivity boost
    ts = str(row.get("llm_time_sensitivity", "Medium")).strip().title()
    ts_pts = TIME_SENSITIVITY_BOOST.get(ts, 6)

    # Category boost
    cat = str(row.get("llm_category", "Other")).strip()
    cat_pts = CATEGORY_BOOST.get(cat, 0)

    # Keywords from title + description
    text = f"{row.get('title','')} {row.get('description','')}"
    kw_pts = keyword_boost(text)

    # Optional: closed issues are less urgent if your dataset has 'state'
    # (If your fetch script didn’t include it, this safely does nothing.)
    state = str(row.get("state", "")).lower()
    state_penalty = -10 if state == "closed" else 0

    raw = severity_pts + ts_pts + cat_pts + kw_pts + state_penalty
    score = clamp(raw)

    breakdown = (
        f"severity({severity_pts}) + time({ts_pts}) + category({cat_pts}) "
        f"+ keywords({kw_pts}) + state({state_penalty}) = {score}"
    )
    return score, breakdown

def main():
    df = pd.read_csv(INPUT)

    scores = df.apply(lambda r: compute_priority(r), axis=1)
    df["priority_score"] = [s[0] for s in scores]
    df["score_breakdown"] = [s[1] for s in scores]
    df["risk_level"] = df["priority_score"].apply(risk_bucket)

    df = df.sort_values("priority_score", ascending=False)
    df.to_csv(OUTPUT, index=False)

    print(f"Saved: {OUTPUT}")
    print("\nTop 10:")
    cols = ["ticket_id", "llm_category", "llm_severity", "llm_time_sensitivity", "priority_score", "risk_level"]
    cols = [c for c in cols if c in df.columns]
    print(df[cols].head(10).to_string(index=False))

if __name__ == "__main__":
    main()
