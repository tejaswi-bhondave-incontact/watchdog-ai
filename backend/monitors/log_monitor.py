import re
from typing import List, Dict
from datetime import datetime


class LogMonitor:
    def __init__(self):
        self.logs: List[Dict] = []
        self.blindspots: List[Dict] = []

    def ingest(self, log_entry: Dict):
        self.logs.append({
            **log_entry,
            "ingested_at": datetime.now().isoformat()
        })
        self._analyze(log_entry)

    def _analyze(self, log_entry: Dict):
        level = log_entry.get("level", "INFO").upper()
        message = log_entry.get("message", "")
        source = log_entry.get("source", "unknown")
        stack_trace = log_entry.get("stack_trace", "")

        if level in ["ERROR", "CRITICAL", "FATAL"]:
            error_type = self._extract_error_type(message, stack_trace)
            scenario = f"reproduce_{error_type}"

            if not any(b["scenario"] == scenario for b in self.blindspots):
                self.blindspots.append({
                    "source": "logs",
                    "category": "Application Logs",
                    "endpoint": source,
                    "scenario": scenario,
                    "details": f"Error in {source}: {message[:200]}",
                    "severity": "critical" if level in ["CRITICAL", "FATAL"] else "high",
                    "error_type": error_type,
                    "stack_trace": stack_trace[:500] if stack_trace else None,
                    "detected_at": datetime.now().isoformat(),
                    "test_generated": False,
                })

        if level == "WARNING" and self._is_repeated_warning(message):
            scenario = f"warning_pattern_{self._hash_message(message)}"
            if not any(b["scenario"] == scenario for b in self.blindspots):
                self.blindspots.append({
                    "source": "logs",
                    "category": "Application Logs",
                    "endpoint": source,
                    "scenario": scenario,
                    "details": f"Repeated warning in {source}: {message[:200]}",
                    "severity": "medium",
                    "detected_at": datetime.now().isoformat(),
                    "test_generated": False,
                })

    def _extract_error_type(self, message: str, stack_trace: str) -> str:
        patterns = [
            r'(NullPointerException|TypeError|ValueError|KeyError|IndexError|AttributeError)',
            r'(ConnectionError|TimeoutError|HTTPError)',
            r'(DatabaseError|IntegrityError|OperationalError)',
            r'(PermissionError|AuthenticationError|ForbiddenError)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message + " " + stack_trace)
            if match:
                return match.group(1).lower()
        return "unknown_error"

    def _is_repeated_warning(self, message: str) -> bool:
        similar_count = sum(
            1 for log in self.logs[-50:]
            if log.get("level", "").upper() == "WARNING"
            and self._similarity(log.get("message", ""), message) > 0.7
        )
        return similar_count >= 3

    def _similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / len(words_a | words_b)

    def _hash_message(self, message: str) -> str:
        return str(abs(hash(message[:50])))[:8]

    def get_blindspots(self) -> List[Dict]:
        return self.blindspots
