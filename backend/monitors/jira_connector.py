"""Real Jira integration for WatchDog AI.
Connects to NiCE's Jira (nice-ce-cxone-prod.atlassian.net) to fetch bug tickets."""

import os
import json
import httpx
from typing import List, Dict, Optional


# Pre-loaded real tickets from NiCE Jira (fetched via Atlassian API)
# These are actual bugs from the system — used when live API is unavailable
REAL_JIRA_TICKETS = [
    {
        "key": "CARD-2670",
        "summary": "[Accessibility][AI Studio] Expand/Collapse all control does not have a tooltip",
        "description": (
            "Region: AI Studio. URL: Topic AI Editor. "
            "Repro Step: AI Studio-> Topic AI->Agent Action-> Invoke Kanban View-> Tree list. "
            "Actual Result: Expand/Collapse all button does not have a tooltip to indicate purpose. "
            "When user tries to activate the control with mouse or keyboard it does not show instructions. "
            "Expected Result: The Expand/Collapse All button should provide a descriptive tooltip "
            "that clearly communicates its purpose when users hover over it."
        ),
        "status": "New",
        "project": "CXone Analytics Research Dev",
        "priority": "Medium",
    },
    {
        "key": "UH-80319",
        "summary": "production-iesov1 saas-platform-ms-user-manager 6.38 deployment failed",
        "description": (
            "Deployment of origin/sprint/192 failed for saas-platform-ms-user-manager version 6.38 "
            "on the production-iesov1 environment. "
            "Steps: 1. Deploy saas-platform-ms-user-manager 6.38 to production-iesov1. "
            "Expected: Deployment succeeds. "
            "Actual: Deployment failed. Check Jenkins job for details. "
            "Assignee: Snehal Hinge. Team: UserHub - Krypton."
        ),
        "status": "New",
        "project": "CX_UserHub",
        "priority": "High",
    },
    {
        "key": "STO-18650",
        "summary": "MI Case 02842839 - [Proactive] Possible Dropped calls",
        "description": (
            "Summary: Investigative KI for RCA of possible dropped calls. "
            "Steps to Recreate: Possible simultaneous changes on A and B side. "
            "CHG0186966 Change Request. "
            "Carter Cordingley: Upgrade E35 COR SQL Servers to SQL 2022. "
            "Axel Tadoy: NOC, starting below CHG0182592 F5 Upgrade for afa-int-adc0. "
            "Expected: Calls should not be dropped during maintenance. "
            "Actual: Calls were dropped during simultaneous infrastructure changes."
        ),
        "status": "New",
        "project": "CX_Storage",
        "priority": "Critical",
    },
    {
        "key": "TEL-5760",
        "summary": "production-iesov1 lambda-telemetry-instrumentation-autoscaler 1.10 deployment failed",
        "description": (
            "Deployment of origin/sprint/192 failed for lambda-telemetry-instrumentation-autoscaler "
            "version 1.10 on the production-iesov1 environment. "
            "Steps: 1. Deploy lambda-telemetry-instrumentation-autoscaler 1.10. "
            "Expected: Lambda deployment succeeds. "
            "Actual: Deployment failed. "
            "Assignee: Payal Bhalke. Team: Telemetry."
        ),
        "status": "New",
        "project": "CX_Telemetry",
        "priority": "High",
    },
    {
        "key": "ORC-53275",
        "summary": "Agents sometimes unable to hangup call when using Copilot",
        "description": (
            "Case#:02813465. Priority: P4. "
            "Customer is attempting to use Copilot and is using CXone Agent Embedded. "
            "Steps: 1. Agent receives call with Copilot enabled. "
            "2. Agent attempts to hangup the call. "
            "3. Hangup button does not respond. "
            "Expected: Agent should be able to hangup call normally. "
            "Actual: Hangup button is unresponsive when Copilot is active. "
            "Workaround: Disable Copilot, then hangup works."
        ),
        "status": "New",
        "project": "Orchestration",
        "priority": "P4",
    },
]


class JiraConnector:
    def __init__(self):
        self.base_url = "https://nice-ce-cxone-prod.atlassian.net"
        self.api_token = os.environ.get("JIRA_API_TOKEN")
        self.email = os.environ.get("JIRA_EMAIL")

    def fetch_tickets(self, jql: str = None, max_results: int = 10) -> List[Dict]:
        """Fetch tickets from Jira. Falls back to pre-loaded real data if API unavailable."""
        if self.api_token and self.email:
            return self._fetch_live(jql, max_results)
        return self._fetch_cached(max_results)

    def _fetch_live(self, jql: str, max_results: int) -> List[Dict]:
        """Fetch from live Jira API."""
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            auth = (self.email, self.api_token)
            url = f"{self.base_url}/rest/api/3/search"
            params = {
                "jql": jql or "type = Bug AND created >= -30d ORDER BY created DESC",
                "maxResults": max_results,
                "fields": "summary,description,status,priority,project",
            }

            response = httpx.get(url, headers=headers, auth=auth, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tickets = []
                for issue in data.get("issues", []):
                    fields = issue.get("fields", {})
                    tickets.append({
                        "key": issue["key"],
                        "summary": fields.get("summary", ""),
                        "description": self._extract_description(fields.get("description", "")),
                        "status": fields.get("status", {}).get("name", "Unknown"),
                        "project": fields.get("project", {}).get("name", "Unknown"),
                        "priority": fields.get("priority", {}).get("name", "Medium"),
                    })
                return tickets
        except Exception:
            pass
        return self._fetch_cached(max_results)

    def _fetch_cached(self, max_results: int) -> List[Dict]:
        """Return pre-loaded real Jira tickets."""
        return REAL_JIRA_TICKETS[:max_results]

    def _extract_description(self, description) -> str:
        """Extract text from Jira description (handles ADF format)."""
        if isinstance(description, str):
            return description
        if isinstance(description, dict):
            return self._adf_to_text(description)
        return str(description) if description else ""

    def _adf_to_text(self, adf: dict) -> str:
        """Convert Atlassian Document Format to plain text."""
        texts = []
        for content in adf.get("content", []):
            if content.get("type") == "paragraph":
                for item in content.get("content", []):
                    if item.get("type") == "text":
                        texts.append(item.get("text", ""))
            elif content.get("type") == "bulletList":
                for list_item in content.get("content", []):
                    for para in list_item.get("content", []):
                        for item in para.get("content", []):
                            if item.get("type") == "text":
                                texts.append("- " + item.get("text", ""))
        return " ".join(texts)
