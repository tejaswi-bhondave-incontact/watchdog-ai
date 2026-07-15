from typing import List, Dict
from datetime import datetime


SAMPLE_PIPELINE_DATA = {
    "flaky_tests": [
        {
            "test_name": "test_websocket_connection_timeout",
            "file": "tests/test_websocket.py",
            "pass_rate": 0.67,
            "last_10_runs": ["PASS", "FAIL", "PASS", "PASS", "FAIL", "PASS", "FAIL", "PASS", "PASS", "FAIL"],
            "avg_duration_ms": 4500,
        },
        {
            "test_name": "test_async_message_delivery",
            "file": "tests/test_messaging.py",
            "pass_rate": 0.80,
            "last_10_runs": ["PASS", "PASS", "FAIL", "PASS", "PASS", "PASS", "FAIL", "PASS", "PASS", "PASS"],
            "avg_duration_ms": 3200,
        },
    ],
    "never_run_tests": [
        {
            "test_name": "test_bulk_import_csv",
            "file": "tests/test_import.py",
            "last_run": "2026-03-15",
            "reason": "skipped_in_ci",
        },
        {
            "test_name": "test_data_migration_v2",
            "file": "tests/test_migration.py",
            "last_run": "2026-01-20",
            "reason": "excluded_from_pipeline",
        },
    ],
    "build_failures": [
        {
            "branch": "feature/payment-v2",
            "failure_count": 3,
            "last_failure": "2026-07-14",
            "error": "ModuleNotFoundError: No module named 'payment_gateway_v2'",
            "files_changed": ["src/payments/gateway.py", "src/payments/refund.py"],
        },
    ],
}


class CICDMonitor:
    def __init__(self):
        self.blindspots: List[Dict] = []

    def scan(self):
        self.blindspots = []
        self._analyze_flaky_tests()
        self._analyze_never_run_tests()
        self._analyze_build_failures()

    def _analyze_flaky_tests(self):
        for test in SAMPLE_PIPELINE_DATA["flaky_tests"]:
            if test["pass_rate"] < 0.85:
                self.blindspots.append({
                    "source": "cicd",
                    "category": "CI/CD Pipeline",
                    "endpoint": test["file"],
                    "scenario": f"flaky_{test['test_name']}",
                    "details": (
                        f"Test '{test['test_name']}' is flaky — passes only "
                        f"{int(test['pass_rate']*100)}% of the time. "
                        f"Last 10 runs: {' '.join(test['last_10_runs'])}. "
                        f"Needs a stability-focused replacement test."
                    ),
                    "severity": "high" if test["pass_rate"] < 0.7 else "medium",
                    "pass_rate": test["pass_rate"],
                    "detected_at": datetime.now().isoformat(),
                    "test_generated": False,
                })

    def _analyze_never_run_tests(self):
        for test in SAMPLE_PIPELINE_DATA["never_run_tests"]:
            self.blindspots.append({
                "source": "cicd",
                "category": "CI/CD Pipeline",
                "endpoint": test["file"],
                "scenario": f"stale_{test['test_name']}",
                "details": (
                    f"Test '{test['test_name']}' hasn't run since {test['last_run']} "
                    f"(reason: {test['reason']}). It may be outdated or broken. "
                    f"Need a fresh, runnable version."
                ),
                "severity": "medium",
                "last_run": test["last_run"],
                "detected_at": datetime.now().isoformat(),
                "test_generated": False,
            })

    def _analyze_build_failures(self):
        for failure in SAMPLE_PIPELINE_DATA["build_failures"]:
            if failure["failure_count"] >= 2:
                self.blindspots.append({
                    "source": "cicd",
                    "category": "CI/CD Pipeline",
                    "endpoint": failure["branch"],
                    "scenario": f"build_failure_{failure['branch'].replace('/', '_')}",
                    "details": (
                        f"Branch '{failure['branch']}' failed {failure['failure_count']} times. "
                        f"Error: {failure['error']}. "
                        f"Files: {', '.join(failure['files_changed'])}. "
                        f"Need import/dependency validation test."
                    ),
                    "severity": "high",
                    "detected_at": datetime.now().isoformat(),
                    "test_generated": False,
                })

    def get_blindspots(self) -> List[Dict]:
        return self.blindspots
