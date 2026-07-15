import re
import os
from typing import List, Dict
from datetime import datetime


SAMPLE_DIFFS = [
    {
        "file": "src/services/payment_service.py",
        "function": "process_refund",
        "lines_changed": 15,
        "commit": "abc1234",
        "author": "dev@nice.com",
        "message": "Add refund retry logic for failed transactions",
    },
    {
        "file": "src/api/user_controller.py",
        "function": "update_profile",
        "lines_changed": 8,
        "commit": "def5678",
        "author": "dev2@nice.com",
        "message": "Allow special characters in display name",
    },
    {
        "file": "src/services/notification_service.py",
        "function": "send_email",
        "lines_changed": 22,
        "commit": "ghi9012",
        "author": "dev3@nice.com",
        "message": "Handle email bounce-back with retry queue",
    },
]

EXISTING_TEST_FILES = [
    "tests/test_payment_service.py::test_process_payment",
    "tests/test_payment_service.py::test_payment_validation",
    "tests/test_user_controller.py::test_create_user",
    "tests/test_user_controller.py::test_get_user",
    "tests/test_notification_service.py::test_send_sms",
]


class GitDiffMonitor:
    def __init__(self):
        self.blindspots: List[Dict] = []

    def scan(self, repo_path: str = None):
        self.blindspots = []
        diffs = self._get_recent_diffs(repo_path)

        for diff in diffs:
            file_name = diff["file"]
            function_name = diff["function"]
            test_file = self._expected_test_file(file_name)
            test_function = f"test_{function_name}"

            if not self._test_exists(test_file, test_function):
                self.blindspots.append({
                    "source": "git_diff",
                    "category": "Git Diffs",
                    "endpoint": f"{file_name}::{function_name}",
                    "scenario": f"missing_test_for_{function_name}",
                    "details": (
                        f"Function '{function_name}' in {file_name} was modified "
                        f"(commit {diff['commit']}: {diff['message']}) "
                        f"but no test '{test_function}' exists in {test_file}"
                    ),
                    "severity": "high" if diff["lines_changed"] > 10 else "medium",
                    "commit": diff["commit"],
                    "author": diff["author"],
                    "detected_at": datetime.now().isoformat(),
                    "test_generated": False,
                })

    def _get_recent_diffs(self, repo_path: str = None) -> List[Dict]:
        if repo_path and os.path.exists(repo_path):
            try:
                import git
                repo = git.Repo(repo_path)
                diffs = []
                for commit in list(repo.iter_commits(max_count=5)):
                    for diff in commit.diff(commit.parents[0] if commit.parents else None):
                        if diff.a_path and diff.a_path.endswith('.py'):
                            functions = self._extract_functions_from_diff(diff)
                            for func in functions:
                                diffs.append({
                                    "file": diff.a_path,
                                    "function": func,
                                    "lines_changed": 10,
                                    "commit": str(commit)[:7],
                                    "author": commit.author.email,
                                    "message": commit.message.strip()[:100],
                                })
                return diffs if diffs else SAMPLE_DIFFS
            except Exception:
                return SAMPLE_DIFFS
        return SAMPLE_DIFFS

    def _extract_functions_from_diff(self, diff) -> List[str]:
        functions = []
        try:
            if diff.diff:
                content = diff.diff.decode('utf-8', errors='ignore')
                matches = re.findall(r'def\s+(\w+)\s*\(', content)
                functions.extend(matches)
        except Exception:
            pass
        return functions if functions else ["unknown_function"]

    def _expected_test_file(self, source_file: str) -> str:
        base = os.path.basename(source_file).replace('.py', '')
        return f"tests/test_{base}.py"

    def _test_exists(self, test_file: str, test_function: str) -> bool:
        full_path = f"{test_file}::{test_function}"
        return any(full_path in existing for existing in EXISTING_TEST_FILES)

    def get_blindspots(self) -> List[Dict]:
        return self.blindspots
