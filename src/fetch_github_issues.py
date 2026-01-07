import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env")

OWNER = "apache"
REPO = "airflow"
MAX_ISSUES = 300  # enough to be real, not overwhelming

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def fetch_issues():
    all_issues = []
    page = 1

    while len(all_issues) < MAX_ISSUES:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
        params = {
            "state": "all",
            "per_page": 50,
            "page": page
        }

        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"GitHub API error: {resp.text}")

        issues = resp.json()

        if not issues:
            break

        for issue in issues:
            # skip PRs
            if "pull_request" in issue:
                continue

            all_issues.append({
                "ticket_id": f"GH-{issue['number']}",
                "created_date": issue["created_at"][:10],
                "due_date": "",  # GitHub doesn't have due dates
                "requester_role": "User",
                "system": f"{OWNER}/{REPO}",
                "title": issue["title"],
                "description": issue["body"] or ""
            })

            if len(all_issues) >= MAX_ISSUES:
                break

        page += 1
        time.sleep(1)  # be polite to API

    return pd.DataFrame(all_issues)

def main():
    df = fetch_issues()
    df.to_csv("data/github_issues_raw.csv", index=False)
    print(f"Saved data/github_issues_raw.csv ({len(df)} issues)")

if __name__ == "__main__":
    main()
