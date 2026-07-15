# 🐕 WatchDog AI

**Auto-generates test cases by learning from real production traffic.**

Sparkathon 2026 | Team: Tejaswi Bhondave & Priyanka

---

## What It Does

WatchDog AI monitors **7 sources** in real-time, identifies coverage gaps, and uses AI to automatically generate the missing test cases.

| # | Monitor | What It Catches |
|---|---------|----------------|
| 1 | API Traffic | Edge cases, unexpected inputs, error patterns |
| 2 | Application Logs | Errors, exceptions, repeated warnings |
| 3 | Jira Tickets | Bug descriptions → instant regression tests |
| 4 | Git Diffs | Modified code without test coverage |
| 5 | Database Queries | Slow queries, null results |
| 6 | CI/CD Pipeline | Flaky tests, stale tests, build failures |
| 7 | UI Click Paths | User paths that lead to errors |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip

### 1. Start the Backend (WatchDog API)

```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend runs on http://localhost:8000

### 2. Start the Sample App (what WatchDog monitors)

```bash
cd sample_app
pip install fastapi uvicorn
python app.py
```
Sample app runs on http://localhost:8001

### 3. Start the Frontend Dashboard

```bash
cd frontend
npm install
npm start
```
Dashboard runs on http://localhost:3000

### 4. Run the Traffic Simulator

```bash
cd backend
python traffic_simulator.py
```

This simulates production traffic, ingests logs, triggers all 7 monitors, generates tests, and runs them.

---

## Demo Walkthrough

1. **Start all 3 services** (backend, sample_app, frontend)
2. **Run traffic simulator** — watch the terminal as it sends edge-case traffic
3. **Open dashboard** at http://localhost:3000
4. **See blind spots** — WatchDog found coverage gaps across all 7 categories
5. **See generated tests** — AI wrote test code automatically
6. **See test results** — some tests FAIL = bugs discovered!
7. **Try Jira input** — paste a bug description, get a test instantly

---

## Architecture

```
┌───────────────┐     ┌───────────────┐     ┌──────────────┐
│  Sample API   │────▶│ Traffic Logger │────▶│   Analyzer   │
│  (port 8001)  │     │               │     │ (7 monitors) │
└───────────────┘     └───────────────┘     └──────┬───────┘
                                                    │
                                                    ▼
┌───────────────┐     ┌───────────────┐     ┌──────────────┐
│  Dashboard    │◀────│  Test Runner  │◀────│  AI Engine   │
│  (port 3000)  │     │  (pytest)     │     │  (Bedrock)   │
└───────────────┘     └───────────────┘     └──────────────┘
```

---

## Tech Stack

- **Backend:** Python, FastAPI, boto3
- **AI Engine:** AWS Bedrock (Claude) with template fallback
- **Test Runner:** pytest
- **Frontend:** React, Tailwind CSS
- **Sample App:** FastAPI

---

## Environment Variables

```bash
# Optional — falls back to template-based generation if not set
export USE_BEDROCK=true
export AWS_REGION=us-east-1
```

---

## Team

- **Tejaswi Bhondave** — Backend, AI Engine, Monitors
- **Priyanka** — Frontend Dashboard, UI Click Tracker, Jira Integration
