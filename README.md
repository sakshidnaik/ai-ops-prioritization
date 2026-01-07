# Operational Risk Prioritization for Ops Backlogs

A hybrid AI + heuristic system to prioritize operational issues by business risk using real GitHub issue data.  
Designed to be explainable, reliable under constraints, and suitable for real-world operations teams.

---

## Overview

Operations teams often manage large backlogs of issues without a consistent way to determine which items pose the highest operational risk. Manual triage is time-consuming, subjective, and does not scale.

This project demonstrates an end-to-end **operational risk prioritization system** that:
- Classifies issues into operational categories
- Assigns severity and time sensitivity
- Computes an explainable priority score
- Surfaces high-risk issues through an interactive dashboard

The system is designed with real-world constraints in mind, including API rate limits, cost considerations, and the need for transparency in decision-making.

---

## Problem Statement

In high-volume operational environments, critical issues such as outages or data risks can be buried among low-impact tasks like UI tweaks or documentation updates.

Without a structured prioritization framework:
- High-risk issues may not receive timely attention
- Decision-making becomes inconsistent across analysts
- Operational reliability is negatively impacted

The goal of this project is to support **faster, safer, and more consistent triage decisions**.

---

## Dataset

- **Source:** Public GitHub Issues from the Apache Airflow repository
- **Why GitHub Issues:**  
  GitHub issue trackers closely resemble real operational backlogs, containing bug reports, incidents, enhancements, and maintenance tasks written by real users and engineers.
- **Dataset Size:**  
  - 50 issues for system demonstration  
  - 20 randomly sampled issues for manual validation

Using public data ensures transparency and avoids reliance on synthetic examples.

---

## Approach

The system follows a simple, explainable pipeline:

GitHub Issues
↓
Heuristic Labeling (category, severity, time sensitivity)
↓
Risk Scoring Logic (weighted, explainable rules)
↓
Prioritized Backlog
↓
Streamlit Dashboard


Each step is designed to be interpretable and adjustable based on operational needs.

---

## Why Hybrid (AI + Heuristics)

Large Language Models (LLMs) can be useful for classification but introduce challenges in production environments:
- API rate limits
- Cost at scale
- Reduced transparency

This system is intentionally designed as **hybrid**:
- Heuristics provide reliability, explainability, and low cost
- LLM-based labeling can be enabled selectively for ambiguous cases
- The system continues functioning even when external services are unavailable

This tradeoff prioritizes operational stability over model sophistication.

---

## Validation

To validate the prioritization logic, 20 issues were randomly sampled and manually reviewed to simulate analyst triage.

**Validation results:**
- ~50% alignment between system-generated and manual risk levels
- No critical outage or failure issues were incorrectly classified as Low risk
- Most mismatches occurred between Medium vs Low risk judgments on UI, documentation, or cleanup tasks

This indicates the system is **directionally correct and conservative**, favoring safety over under-prioritization.

---

## Dashboard

The Streamlit dashboard allows users to:
- Filter issues by category, risk level, and priority score
- Quickly identify top high-risk issues
- Inspect individual issues with full explainability

### Dashboard Overview
![Dashboard Overview](assets/dashboard_overview.png)

### Top High-Risk Issues
![Top High Risk Issues](assets/top_risk_issues.png)

### Issue Details & Explainability
![Issue Details](assets/issue_details.png)

---

## Business Impact

This system helps operations teams:
- Reduce time spent on manual triage
- Consistently surface high-risk issues
- Improve transparency in prioritization decisions
- Support faster response to operational risks

The output is advisory and designed to complement, not replace, human judgment.

---

## Limitations & Next Steps

**Current limitations:**
- Heuristic rules may underweight UI or documentation-related risks
- Risk prioritization remains subjective by nature
- Dataset size is intentionally limited for demonstration

**Future improvements:**
- Tune heuristics using analyst feedback
- Add human override workflows
- Selectively re-enable LLM-based labeling for ambiguous cases
- Expand dataset size for broader evaluation

---

## How to Run

```bash
pip install -r requirements.txt
python src/fetch_github_issues.py
python src/heuristic_labeler.py
python src/risk_scoring.py
streamlit run app.py


