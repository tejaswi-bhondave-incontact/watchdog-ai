"""Traffic Simulator — generates realistic production traffic
including edge cases that WatchDog AI will detect."""

import httpx
import time
from datetime import datetime

WATCHDOG_URL = "http://localhost:8000"
SAMPLE_APP_URL = "http://localhost:8001"

NORMAL_TRAFFIC = [
    {"method": "POST", "path": "/api/users", "body": {"name": "John Smith", "email": "john@example.com", "phone": "+1-555-0100"}},
    {"method": "POST", "path": "/api/users", "body": {"name": "Jane Doe", "email": "jane@example.com", "phone": "+1-555-0101"}},
    {"method": "GET", "path": "/api/products", "body": {}},
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "1", "product_id": "1", "quantity": 2}},
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "2", "product_id": "2", "quantity": 1, "discount_code": "SAVE20"}},
]

EDGE_CASE_TRAFFIC = [
    # Unicode/emoji names
    {"method": "POST", "path": "/api/users", "body": {"name": "José María 🇪🇸", "email": "jose@test.com"}},
    {"method": "POST", "path": "/api/users", "body": {"name": "田中太郎", "email": "tanaka@test.jp"}},
    # Empty fields
    {"method": "POST", "path": "/api/users", "body": {"name": "", "email": ""}},
    {"method": "POST", "path": "/api/users", "body": {"name": None, "email": "null@test.com"}},
    # Oversized input
    {"method": "POST", "path": "/api/users", "body": {"name": "A" * 500, "email": "long@test.com"}},
    # Injection attempts
    {"method": "POST", "path": "/api/users", "body": {"name": "<script>alert('xss')</script>", "email": "xss@test.com"}},
    {"method": "POST", "path": "/api/users", "body": {"name": "'; DROP TABLE users; --", "email": "sql@test.com"}},
    # Negative values
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "1", "product_id": "1", "quantity": -5}},
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "1", "product_id": "1", "quantity": 0}},
    # Huge values
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "1", "product_id": "1", "quantity": 99999999}},
    # Invalid references
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "nonexistent", "product_id": "999", "quantity": 1}},
    # Discount code edge cases
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "1", "product_id": "1", "quantity": 1, "discount_code": ""}},
    {"method": "POST", "path": "/api/orders", "body": {"user_id": "1", "product_id": "1", "quantity": 1, "discount_code": "INVALID_CODE_12345"}},
]

SAMPLE_LOGS = [
    {"level": "ERROR", "message": "NullPointerException in PaymentService.processRefund: refund_id is None", "source": "payment_service", "stack_trace": "File payment_service.py, line 47\n  refund.process()\nNullPointerException: refund_id cannot be None"},
    {"level": "ERROR", "message": "ConnectionError: Database connection pool exhausted after 30s timeout", "source": "db_connection_pool", "stack_trace": "File db_pool.py, line 112\n  connection = pool.acquire(timeout=30)\nConnectionError: Pool exhausted"},
    {"level": "ERROR", "message": "TypeError: cannot concatenate 'NoneType' to str in email_service.send_notification", "source": "email_service", "stack_trace": "File email_service.py, line 89\n  body = greeting + user.name\nTypeError: can only concatenate str to str"},
    {"level": "WARNING", "message": "Slow query detected: SELECT * FROM orders WHERE status='pending' took 3.2s", "source": "query_monitor"},
    {"level": "WARNING", "message": "Slow query detected: SELECT * FROM orders WHERE status='pending' took 2.8s", "source": "query_monitor"},
    {"level": "WARNING", "message": "Slow query detected: SELECT * FROM orders WHERE status='pending' took 4.1s", "source": "query_monitor"},
    {"level": "WARNING", "message": "Slow query detected: SELECT * FROM orders WHERE status='pending' took 3.5s", "source": "query_monitor"},
    {"level": "CRITICAL", "message": "OutOfMemoryError: heap space exceeded during bulk CSV import", "source": "import_service", "stack_trace": "File import_service.py, line 203\n  data = file.read()\njava.lang.OutOfMemoryError: Java heap space"},
]

SAMPLE_UI_CLICKS = [
    {"page": "checkout", "element": "submit_button", "timestamp": "2026-07-15T10:30:00", "session_id": "sess_001", "error": None},
    {"page": "checkout", "element": "submit_button", "timestamp": "2026-07-15T10:30:01", "session_id": "sess_001", "error": None},
    {"page": "checkout", "element": "submit_button", "timestamp": "2026-07-15T10:30:02", "session_id": "sess_001", "error": "Button unresponsive - timeout after 5s"},
    {"page": "profile", "element": "save_button", "timestamp": "2026-07-15T11:00:00", "session_id": "sess_002", "error": None},
    {"page": "profile", "element": "upload_avatar", "timestamp": "2026-07-15T11:00:05", "session_id": "sess_002", "error": "500 Internal Server Error on file upload"},
    {"page": "dashboard", "element": "export_csv", "timestamp": "2026-07-15T11:30:00", "session_id": "sess_003", "error": None},
    {"page": "dashboard", "element": "filter_date", "timestamp": "2026-07-15T11:30:02", "session_id": "sess_003", "error": None},
    {"page": "dashboard", "element": "export_csv", "timestamp": "2026-07-15T11:30:10", "session_id": "sess_003", "error": "Export failed: too many records"},
]


def simulate_api_traffic(client):
    print("\n[API Traffic Monitor] Sending production traffic...")
    all_traffic = NORMAL_TRAFFIC + EDGE_CASE_TRAFFIC
    for traffic in all_traffic:
        try:
            if traffic["method"] == "POST":
                resp = client.post(f"{SAMPLE_APP_URL}{traffic['path']}", json=traffic["body"])
            else:
                resp = client.get(f"{SAMPLE_APP_URL}{traffic['path']}")

            client.post(f"{WATCHDOG_URL}/api/traffic/ingest", json={
                "method": traffic["method"],
                "path": traffic["path"],
                "body": traffic["body"],
                "status_code": resp.status_code,
                "response": resp.text[:200],
            })
            status = "OK" if resp.status_code < 400 else "WARN" if resp.status_code < 500 else "ERR"
            print(f"  [{status}] {traffic['method']} {traffic['path']} -> {resp.status_code}")
        except Exception as e:
            print(f"  [ERR] {traffic['method']} {traffic['path']} -> {e}")
        time.sleep(0.1)


def simulate_log_ingestion(client):
    print("\n[Log Monitor] Ingesting application logs...")
    for log in SAMPLE_LOGS:
        client.post(f"{WATCHDOG_URL}/api/logs/ingest", json=log)
        print(f"  [{log['level']}] {log['message'][:80]}")
        time.sleep(0.05)


def simulate_ui_clicks(client):
    print("\n[UI Click Monitor] Ingesting user click events...")
    for click in SAMPLE_UI_CLICKS:
        client.post(f"{WATCHDOG_URL}/api/ui-clicks/ingest", json=click)
        err = f" -> {click['error']}" if click.get("error") else ""
        print(f"  {click['page']}/{click['element']}{err}")
        time.sleep(0.05)


def trigger_scans(client):
    print("\n[Scanners] Running Git, DB, CI/CD scans...")
    client.post(f"{WATCHDOG_URL}/api/git/scan")
    print("  Git Diff scan complete")
    client.post(f"{WATCHDOG_URL}/api/db/scan")
    print("  Database scan complete")
    client.post(f"{WATCHDOG_URL}/api/cicd/scan")
    print("  CI/CD Pipeline scan complete")


def generate_and_run_tests(client):
    print("\n[AI Engine] Generating tests from blind spots...")
    resp = client.post(f"{WATCHDOG_URL}/api/generate")
    data = resp.json()
    print(f"  Generated {data['count']} test cases")

    print("\n[Test Runner] Executing generated tests...")
    resp = client.post(f"{WATCHDOG_URL}/api/run-tests")
    results = resp.json().get("results", [])
    for r in results:
        status = "PASS" if r["status"] == "PASSED" else "FAIL"
        print(f"  [{status}] {r['test_name']}")


def main():
    print("=" * 60)
    print("  WatchDog AI - Traffic Simulator")
    print("=" * 60)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  WatchDog API: {WATCHDOG_URL}")
    print(f"  Sample App: {SAMPLE_APP_URL}")
    print("=" * 60)

    client = httpx.Client(timeout=30.0)
    try:
        simulate_api_traffic(client)
        simulate_log_ingestion(client)
        simulate_ui_clicks(client)
        trigger_scans(client)
        generate_and_run_tests(client)
    finally:
        client.close()

    print("\n" + "=" * 60)
    print("  Simulation complete! Open http://localhost:5173 for the dashboard.")
    print("=" * 60)


if __name__ == "__main__":
    main()
