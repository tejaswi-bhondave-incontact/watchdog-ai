import json
from typing import List, Dict
from datetime import datetime


EXISTING_TESTS = [
    {"endpoint": "POST /api/users", "scenarios": ["valid_user", "duplicate_email"]},
    {"endpoint": "GET /api/users/{id}", "scenarios": ["valid_id", "not_found"]},
    {"endpoint": "POST /api/orders", "scenarios": ["valid_order"]},
    {"endpoint": "GET /api/products", "scenarios": ["list_all"]},
]


class APITrafficMonitor:
    def __init__(self):
        self.traffic_log: List[Dict] = []
        self.blindspots: List[Dict] = []

    def ingest(self, traffic_data: Dict):
        self.traffic_log.append({
            **traffic_data,
            "timestamp": datetime.now().isoformat()
        })
        self._analyze(traffic_data)

    def _analyze(self, traffic_data: Dict):
        endpoint = f"{traffic_data.get('method', 'GET')} {traffic_data.get('path', '')}"
        body = traffic_data.get("body", {})
        status_code = traffic_data.get("status_code", 200)

        for field, value in body.items():
            if self._is_edge_case(field, value):
                scenario = self._describe_edge_case(field, value)
                if not self._test_exists(endpoint, scenario):
                    blindspot = {
                        "source": "api_traffic",
                        "category": "API Traffic",
                        "endpoint": endpoint,
                        "scenario": scenario,
                        "details": f"Field '{field}' received value '{value}' — no test covers this",
                        "severity": "high" if status_code >= 500 else "medium",
                        "detected_at": datetime.now().isoformat(),
                        "test_generated": False,
                    }
                    if not any(b["scenario"] == scenario and b["endpoint"] == endpoint for b in self.blindspots):
                        self.blindspots.append(blindspot)

        if status_code >= 400:
            scenario = f"error_response_{status_code}"
            if not self._test_exists(endpoint, scenario):
                blindspot = {
                    "source": "api_traffic",
                    "category": "API Traffic",
                    "endpoint": endpoint,
                    "scenario": scenario,
                    "details": f"Endpoint returned {status_code} but no test validates this error path",
                    "severity": "high",
                    "detected_at": datetime.now().isoformat(),
                    "test_generated": False,
                }
                if not any(b["scenario"] == scenario and b["endpoint"] == endpoint for b in self.blindspots):
                    self.blindspots.append(blindspot)

    def _is_edge_case(self, field: str, value) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            if len(value) == 0:
                return True
            if len(value) > 200:
                return True
            if any(c in value for c in ['<', '>', '"', "'", ';', '--', '🎉', '🇪🇸', 'é', 'ñ', 'ü']):
                return True
        if isinstance(value, (int, float)):
            if value < 0:
                return True
            if value > 1000000:
                return True
        return False

    def _describe_edge_case(self, field: str, value) -> str:
        if value is None:
            return f"null_{field}"
        if isinstance(value, str):
            if len(value) == 0:
                return f"empty_{field}"
            if len(value) > 200:
                return f"oversized_{field}"
            if any(ord(c) > 127 for c in value):
                return f"unicode_{field}"
            if any(c in value for c in ['<', '>', '"', "'", ';', '--']):
                return f"injection_attempt_{field}"
        if isinstance(value, (int, float)) and value < 0:
            return f"negative_{field}"
        return f"unusual_{field}"

    def _test_exists(self, endpoint: str, scenario: str) -> bool:
        for test in EXISTING_TESTS:
            if test["endpoint"] == endpoint and scenario in test["scenarios"]:
                return True
        return False

    def get_blindspots(self) -> List[Dict]:
        return self.blindspots

    def get_traffic_log(self) -> List[Dict]:
        return self.traffic_log[-100:]
