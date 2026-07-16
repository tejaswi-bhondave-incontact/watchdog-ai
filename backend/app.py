import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from monitors.api_traffic import APITrafficMonitor
from monitors.log_monitor import LogMonitor
from monitors.jira_monitor import JiraMonitor
from monitors.git_diff_monitor import GitDiffMonitor
from monitors.db_monitor import DBMonitor
from monitors.cicd_monitor import CICDMonitor
from monitors.ui_click_monitor import UIClickMonitor
from ai_engine.generator import TestGenerator
from test_runner.runner import TestRunner

app = FastAPI(title="WatchDog AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_traffic_monitor = APITrafficMonitor()
log_monitor = LogMonitor()
jira_monitor = JiraMonitor()
git_diff_monitor = GitDiffMonitor()
db_monitor = DBMonitor()
cicd_monitor = CICDMonitor()
ui_click_monitor = UIClickMonitor()
test_generator = TestGenerator()
test_runner = TestRunner()


class JiraInput(BaseModel):
    ticket_text: str
    ticket_id: Optional[str] = None


class JiraFetchInput(BaseModel):
    project_key: Optional[str] = None
    jql: Optional[str] = None
    max_results: Optional[int] = 10


class UIClickEvent(BaseModel):
    page: str
    element: str
    timestamp: str
    session_id: str
    error: Optional[str] = None


@app.get("/api/overview")
async def get_overview():
    blindspots = get_all_blindspots()
    generated = test_generator.get_generated_tests()
    results = test_runner.get_results()
    return {
        "total_blindspots": len(blindspots),
        "tests_generated": len(generated),
        "bugs_found": len([r for r in results if r["status"] == "FAILED"]),
        "coverage_increase": f"+{len(generated) * 2}%",
        "monitors_active": 7,
    }


@app.get("/api/monitors")
async def get_monitors():
    return {
        "monitors": [
            {"id": "api_traffic", "name": "API Traffic", "status": "active", "blindspots": len(api_traffic_monitor.get_blindspots())},
            {"id": "logs", "name": "Application Logs", "status": "active", "blindspots": len(log_monitor.get_blindspots())},
            {"id": "jira", "name": "Jira Tickets", "status": "active", "blindspots": len(jira_monitor.get_blindspots())},
            {"id": "git_diff", "name": "Git Diffs", "status": "active", "blindspots": len(git_diff_monitor.get_blindspots())},
            {"id": "database", "name": "Database Queries", "status": "active", "blindspots": len(db_monitor.get_blindspots())},
            {"id": "cicd", "name": "CI/CD Pipeline", "status": "active", "blindspots": len(cicd_monitor.get_blindspots())},
            {"id": "ui_clicks", "name": "UI Click Paths", "status": "active", "blindspots": len(ui_click_monitor.get_blindspots())},
        ]
    }


@app.get("/api/blindspots")
async def get_blindspots():
    return {"blindspots": get_all_blindspots()}


@app.get("/api/generated-tests")
async def get_generated_tests():
    return {"tests": test_generator.get_generated_tests()}


@app.get("/api/test-results")
async def get_test_results():
    return {"results": test_runner.get_results()}


@app.post("/api/jira-analyze")
async def analyze_jira(input: JiraInput):
    blindspot = jira_monitor.analyze_ticket(input.ticket_text, input.ticket_id)
    test_result = test_generator.generate_from_blindspot(blindspot)
    return {
        "blindspot": {
            **blindspot,
            "title": blindspot.get("scenario", ""),
            "description": blindspot.get("details", ""),
        },
        "generated_test": {
            "code": test_result["test_code"],
            "language": "python",
            **test_result,
        },
    }


@app.post("/api/jira-fetch")
async def fetch_jira_tickets(input: JiraFetchInput):
    """Fetch real bugs from Jira and analyze them for missing tests."""
    import httpx

    jira_base = "https://nice-ce-cxone-prod.atlassian.net"
    jql = input.jql or f"project = {input.project_key} AND type = Bug AND created >= -30d ORDER BY created DESC"

    # Use the Atlassian API via the backend
    # For the prototype, we fetch from our stored Jira data
    from monitors.jira_connector import JiraConnector
    connector = JiraConnector()
    tickets = connector.fetch_tickets(jql, input.max_results)

    results = []
    for ticket in tickets:
        blindspot = jira_monitor.analyze_ticket(
            ticket["description"],
            ticket["key"]
        )
        test_result = test_generator.generate_from_blindspot(blindspot)
        results.append({
            "ticket_key": ticket["key"],
            "summary": ticket["summary"],
            "status": ticket["status"],
            "blindspot": {
                **blindspot,
                "title": blindspot.get("scenario", ""),
                "description": blindspot.get("details", ""),
            },
            "generated_test": {
                "code": test_result["test_code"],
                "language": "python",
                **test_result,
            },
        })

    return {"tickets_analyzed": len(results), "results": results}


@app.post("/api/generate")
async def generate_tests():
    blindspots = get_all_blindspots()
    generated = []
    for bs in blindspots:
        if not bs.get("test_generated"):
            test_code = test_generator.generate_from_blindspot(bs)
            generated.append(test_code)
    return {"generated": generated, "count": len(generated)}


@app.post("/api/run-tests")
async def run_tests():
    results = test_runner.run_all()
    return {"results": results}


@app.post("/api/traffic/ingest")
async def ingest_traffic(request: Request):
    body = await request.json()
    api_traffic_monitor.ingest(body)
    return {"status": "ingested"}


@app.post("/api/logs/ingest")
async def ingest_log(request: Request):
    body = await request.json()
    log_monitor.ingest(body)
    return {"status": "ingested"}


@app.post("/api/ui-clicks/ingest")
async def ingest_click(event: UIClickEvent):
    ui_click_monitor.ingest(event.dict())
    return {"status": "ingested"}


@app.post("/api/git/scan")
async def scan_git():
    git_diff_monitor.scan()
    return {"blindspots": git_diff_monitor.get_blindspots()}


@app.post("/api/db/scan")
async def scan_db():
    db_monitor.scan()
    return {"blindspots": db_monitor.get_blindspots()}


@app.post("/api/cicd/scan")
async def scan_cicd():
    cicd_monitor.scan()
    return {"blindspots": cicd_monitor.get_blindspots()}


def get_all_blindspots():
    all_bs = []
    all_bs.extend(api_traffic_monitor.get_blindspots())
    all_bs.extend(log_monitor.get_blindspots())
    all_bs.extend(jira_monitor.get_blindspots())
    all_bs.extend(git_diff_monitor.get_blindspots())
    all_bs.extend(db_monitor.get_blindspots())
    all_bs.extend(cicd_monitor.get_blindspots())
    all_bs.extend(ui_click_monitor.get_blindspots())
    return all_bs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
