from typing import List, Dict
from datetime import datetime


SAMPLE_SLOW_QUERIES = [
    {
        "query": "SELECT * FROM orders WHERE customer_id = ? AND status IN (?, ?) ORDER BY created_at DESC",
        "avg_time_ms": 2300,
        "table": "orders",
        "operation": "SELECT",
        "frequency": 450,
    },
    {
        "query": "UPDATE users SET last_login = ? WHERE email = ?",
        "avg_time_ms": 890,
        "table": "users",
        "operation": "UPDATE",
        "frequency": 1200,
    },
    {
        "query": "INSERT INTO audit_log (user_id, action, details) VALUES (?, ?, ?)",
        "avg_time_ms": 150,
        "table": "audit_log",
        "operation": "INSERT",
        "frequency": 5000,
        "null_results": 0,
    },
]

SAMPLE_NULL_RESULTS = [
    {
        "query": "SELECT config_value FROM settings WHERE key = ?",
        "params": ["notification_retry_count"],
        "table": "settings",
        "null_percentage": 35,
    },
    {
        "query": "SELECT manager_id FROM employees WHERE department = ?",
        "params": ["temp_contractors"],
        "table": "employees",
        "null_percentage": 100,
    },
]

EXISTING_DB_TESTS = [
    "test_orders_query_valid_customer",
    "test_users_update_last_login",
]


class DBMonitor:
    def __init__(self):
        self.blindspots: List[Dict] = []

    def scan(self):
        self.blindspots = []
        self._analyze_slow_queries()
        self._analyze_null_results()

    def _analyze_slow_queries(self):
        for query_info in SAMPLE_SLOW_QUERIES:
            if query_info["avg_time_ms"] > 1000:
                scenario = f"slow_query_{query_info['table']}_{query_info['operation'].lower()}"
                test_name = f"test_{query_info['table']}_query_performance"

                if test_name not in EXISTING_DB_TESTS:
                    self.blindspots.append({
                        "source": "database",
                        "category": "Database Queries",
                        "endpoint": f"{query_info['table']}.{query_info['operation']}",
                        "scenario": scenario,
                        "details": (
                            f"Query on '{query_info['table']}' takes {query_info['avg_time_ms']}ms avg "
                            f"({query_info['frequency']} calls/day). No performance test exists."
                        ),
                        "severity": "high" if query_info["avg_time_ms"] > 2000 else "medium",
                        "query": query_info["query"],
                        "avg_time_ms": query_info["avg_time_ms"],
                        "detected_at": datetime.now().isoformat(),
                        "test_generated": False,
                    })

    def _analyze_null_results(self):
        for null_info in SAMPLE_NULL_RESULTS:
            if null_info["null_percentage"] > 30:
                scenario = f"null_result_{null_info['table']}_{null_info['params'][0]}"
                self.blindspots.append({
                    "source": "database",
                    "category": "Database Queries",
                    "endpoint": f"{null_info['table']}.SELECT",
                    "scenario": scenario,
                    "details": (
                        f"Query on '{null_info['table']}' returns NULL {null_info['null_percentage']}% of the time "
                        f"for param '{null_info['params'][0]}'. No test validates null handling."
                    ),
                    "severity": "high" if null_info["null_percentage"] > 80 else "medium",
                    "query": null_info["query"],
                    "null_percentage": null_info["null_percentage"],
                    "detected_at": datetime.now().isoformat(),
                    "test_generated": False,
                })

    def get_blindspots(self) -> List[Dict]:
        return self.blindspots
