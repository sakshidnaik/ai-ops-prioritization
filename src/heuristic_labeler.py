import pandas as pd

INPUT = "data/github_issues_raw.csv"
OUTPUT = "data/github_issues_labeled_50.csv"

KEYWORDS = {
    "Outage/Incident": ["crash", "panic", "segfault", "outage", "down", "deadlock"],
    "Data Quality Fix": ["incorrect", "wrong", "null", "missing", "corrupt"],
    "Ops Backlog": ["cleanup", "refactor", "technical debt", "todo"],
    "Process/Workflow Change": ["proposal", "design", "improvement"],
    "Access/Permissions": ["permission", "access", "auth", "oauth"],
}

def classify(text: str):
    t = text.lower()
    for cat, words in KEYWORDS.items():
        if any(w in t for w in words):
            return cat
    return "Other"

def severity_from_text(text: str):
    t = text.lower()
    if any(w in t for w in ["crash", "data loss", "panic"]):
        return 5
    if any(w in t for w in ["broken", "fails", "error"]):
        return 4
    return 3

def time_sensitivity(text: str):
    t = text.lower()
    if any(w in t for w in ["urgent", "asap", "blocker"]):
        return "High"
    if any(w in t for w in ["soon", "important"]):
        return "Medium"
    return "Low"

def main():
    df = pd.read_csv(INPUT).head(50).copy()

    labels = []
    for _, row in df.iterrows():
        text = f"{row['title']} {row['description']}"
        labels.append({
            "llm_category": classify(text),
            "llm_severity": severity_from_text(text),
            "llm_time_sensitivity": time_sensitivity(text),
            "llm_reason": "Rule-based classification on issue text",
            "label_source": "heuristic"
        })

    out = pd.concat([df.reset_index(drop=True), pd.DataFrame(labels)], axis=1)
    out.to_csv(OUTPUT, index=False)
    print(f"Saved: {OUTPUT}")

if __name__ == "__main__":
    main()
