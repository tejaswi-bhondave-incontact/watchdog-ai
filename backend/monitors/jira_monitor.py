import re
from typing import List, Dict, Optional
from datetime import datetime


class JiraMonitor:
    def __init__(self):
        self.blindspots: List[Dict] = []

    def analyze_ticket(self, ticket_text: str, ticket_id: Optional[str] = None) -> Dict:
        steps = self._extract_steps_to_reproduce(ticket_text)
        expected = self._extract_expected_behavior(ticket_text)
        actual = self._extract_actual_behavior(ticket_text)
        affected_area = self._extract_affected_area(ticket_text)

        blindspot = {
            "source": "jira",
            "category": "Jira Tickets",
            "endpoint": affected_area,
            "scenario": f"regression_{ticket_id or 'manual'}",
            "details": ticket_text[:300],
            "severity": "high",
            "ticket_id": ticket_id,
            "steps_to_reproduce": steps,
            "expected_behavior": expected,
            "actual_behavior": actual,
            "affected_area": affected_area,
            "detected_at": datetime.now().isoformat(),
            "test_generated": False,
        }

        if not any(b["scenario"] == blindspot["scenario"] for b in self.blindspots):
            self.blindspots.append(blindspot)

        return blindspot

    def _extract_steps_to_reproduce(self, text: str) -> List[str]:
        steps = []
        patterns = [
            r'steps?\s*(?:to\s*reproduce)?[:\n]+(.*?)(?=expected|actual|$)',
            r'(?:1\.|step 1)[:\s]+(.*?)(?=expected|actual|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                raw = match.group(1)
                lines = [l.strip() for l in raw.split('\n') if l.strip()]
                steps = [re.sub(r'^\d+[\.\)]\s*', '', l) for l in lines[:10]]
                break

        if not steps:
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
            steps = sentences[:5]

        return steps

    def _extract_expected_behavior(self, text: str) -> str:
        patterns = [
            r'expected\s*(?:behavior|result|outcome)?[:\s]+(.*?)(?=actual|steps|$)',
            r'should\s+(.*?)(?:\.|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:200]
        return "System should handle this case without errors"

    def _extract_actual_behavior(self, text: str) -> str:
        patterns = [
            r'actual\s*(?:behavior|result|outcome)?[:\s]+(.*?)(?=expected|steps|$)',
            r'(?:instead|but)\s+(.*?)(?:\.|$)',
            r'error[:\s]+(.*?)(?:\.|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:200]
        return "System crashes or returns unexpected result"

    def _extract_affected_area(self, text: str) -> str:
        api_match = re.search(r'((?:GET|POST|PUT|DELETE|PATCH)\s+/[^\s]+)', text)
        if api_match:
            return api_match.group(1)

        module_patterns = [
            r'(?:in|on|at)\s+(?:the\s+)?(\w+\s*(?:page|module|service|component|screen))',
            r'(\w+(?:Service|Controller|Handler|Manager|Module))',
        ]
        for pattern in module_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return "unknown_module"

    def get_blindspots(self) -> List[Dict]:
        return self.blindspots
