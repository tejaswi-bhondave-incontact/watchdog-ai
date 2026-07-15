import os
import subprocess
import tempfile
import json
from typing import List, Dict
from datetime import datetime


class TestRunner:
    def __init__(self):
        self.results: List[Dict] = []
        self.generated_test_dir = tempfile.mkdtemp(prefix="watchdog_tests_")

    def run_all(self) -> List[Dict]:
        from ai_engine.generator import TestGenerator
        # Get all generated tests from the generator
        # This is called from app.py which has access to the generator instance
        return self.results

    def run_test(self, test_code: str, test_name: str) -> Dict:
        test_file = os.path.join(self.generated_test_dir, f"{test_name}.py")

        with open(test_file, "w") as f:
            f.write(test_code)

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_file, "-v", "--tb=short", "--no-header"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.generated_test_dir,
            )

            passed = result.returncode == 0
            output = result.stdout + result.stderr

            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "status": "PASSED" if passed else "FAILED",
                "output": output[:1000],
                "return_code": result.returncode,
                "executed_at": datetime.now().isoformat(),
                "bug_found": not passed,
            }

        except subprocess.TimeoutExpired:
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "status": "TIMEOUT",
                "output": "Test execution timed out after 30 seconds",
                "return_code": -1,
                "executed_at": datetime.now().isoformat(),
                "bug_found": True,
            }
        except Exception as e:
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "status": "ERROR",
                "output": str(e),
                "return_code": -1,
                "executed_at": datetime.now().isoformat(),
                "bug_found": True,
            }

        self.results.append(test_result)
        return test_result

    def run_generated_tests(self, generated_tests: List[Dict]) -> List[Dict]:
        self.results = []
        for test in generated_tests:
            result = self.run_test(test["test_code"], test["test_name"])
            self.results.append(result)
        return self.results

    def get_results(self) -> List[Dict]:
        return self.results
