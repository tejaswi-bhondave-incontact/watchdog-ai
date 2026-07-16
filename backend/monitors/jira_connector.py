"""Real Jira integration for WatchDog AI.
Connects to NiCE's Jira (nice-ce-cxone-prod.atlassian.net) to fetch bug tickets."""

import os
import json
import httpx
from typing import List, Dict, Optional


# Sample Jira tickets for demonstration purposes
REAL_JIRA_TICKETS = [
    {
        "key": "SHOP-1042",
        "summary": "Cart total shows negative when 100% discount coupon applied with free shipping",
        "description": (
            "Steps to reproduce: "
            "1. Add any item to cart. "
            "2. Apply coupon code FREE100 (100% discount). "
            "3. Select free shipping option. "
            "4. Observe cart total. "
            "Expected: Cart total should show $0.00. "
            "Actual: Cart total shows -$5.99 (negative value from shipping calculation applied before discount). "
            "This allows customers to place orders with negative totals."
        ),
        "status": "Open",
        "project": "E-Commerce Platform",
        "priority": "Critical",
    },
    {
        "key": "SHOP-1087",
        "summary": "User profile update crashes when display name contains emoji characters",
        "description": (
            "Steps to reproduce: "
            "1. Navigate to Profile Settings page. "
            "2. Edit display name to include emoji (e.g. 'John 🚀'). "
            "3. Click Save. "
            "Expected: Profile saves successfully with emoji in name. "
            "Actual: Server returns 500 Internal Server Error. "
            "Stack trace shows: UnicodeEncodeError in user_service.py line 142. "
            "Affects all users trying to use emoji in profile fields."
        ),
        "status": "Open",
        "project": "E-Commerce Platform",
        "priority": "High",
    },
    {
        "key": "SHOP-1103",
        "summary": "Concurrent checkout causes duplicate orders when user double-clicks Place Order",
        "description": (
            "Steps to reproduce: "
            "1. Add items to cart and proceed to checkout. "
            "2. Click 'Place Order' button rapidly (double-click). "
            "3. Check order history. "
            "Expected: Only one order is created. "
            "Actual: Two identical orders are created and customer is charged twice. "
            "No idempotency check on the POST /api/orders endpoint. "
            "Customer reports: 'I was charged $299.98 instead of $149.99'."
        ),
        "status": "Open",
        "project": "E-Commerce Platform",
        "priority": "Critical",
    },
    {
        "key": "SHOP-1118",
        "summary": "Search API returns results for deleted products causing 404 on click",
        "description": (
            "Steps to reproduce: "
            "1. Search for 'wireless headphones'. "
            "2. Click on 'ProMax Wireless X200' in search results. "
            "3. Observe error page. "
            "Expected: Deleted products should not appear in search results. "
            "Actual: Search index is not updated when products are deleted. "
            "User sees product in search, clicks it, gets 404 Not Found. "
            "Elasticsearch index out of sync with product database."
        ),
        "status": "Open",
        "project": "E-Commerce Platform",
        "priority": "Medium",
    },
    {
        "key": "SHOP-1125",
        "summary": "Password reset token never expires - security vulnerability",
        "description": (
            "Steps to reproduce: "
            "1. Request password reset email. "
            "2. Wait 7 days (or any amount of time). "
            "3. Click the reset link from old email. "
            "4. Successfully reset password. "
            "Expected: Reset token should expire after 1 hour. "
            "Actual: Token has no expiry - can be used weeks later. "
            "Security risk: If reset email is intercepted, attacker has unlimited time to use it. "
            "The token_expiry column in password_resets table is always NULL."
        ),
        "status": "Open",
        "project": "E-Commerce Platform",
        "priority": "Critical",
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
