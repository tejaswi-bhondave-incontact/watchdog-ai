"""Traffic Simulator — generates realistic production traffic
including edge cases that WatchDog AI will detect."""

import httpx
import asyncio
import random
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


async def simulate_api_traffic(client: httpx.AsyncClient):
    print("\n🔍 [API Traffic Monitor] Sending production traffic...")
    all_traffic = NORMAL_TRAFFIC + EDGE_CASE_TRAFFIC
    for traffic in all_traffic:
        try:
            # Hit the sample app
            if traffic["method"] == "POST":
                resp = await client.post(f"{SAMPLE_APP_URL}{traffic['path']}", json=traffic["body"])
            else:
                resp = await client.get(f"{SAMPLE_APP_URL}{traffic['path']}")

            # Report to WatchDog
            await client.post(f"{WATCHDOG_URL}/api/traffic/ingest", json={
                "method": traffic["method"],
                "path": traffic["path"],
                "body": traffic["body"],
                "status_code": resp.status_code,
                "response": resp.text[:200],
            })
            status_icon = "✅" if resp.status_code < 400 else "⚠️" if resp.status_code < 500 else "❌"
            print(f"  {status_icon} {traffic['method']} {traffic['path']} → {resp.status_code}")
        except Exception as e:
            print(f"  ❌ {traffic['method']} {traffic['path']} → Error: {e}")
        await asyncio.sleep(0.2)


async def simulate_log_ingestion(client: httpx.AsyncClient):
    print("\n📋 [Log Monitor] Ingesting application logs...")
    for log in SAMPLE_LOGS:
        await client.post(f"{WATCHDOG_URL}/api/logs/ingest", json=log)
        icon = "🔴" if log["level"] == "ERROR" else "🟡" if log["level"] == "WARNING" else "🔥"
        print(f"  {icon} [{log['level']}] {log['message'][:80]}")
        await asyncio.sleep(0.1)


async def simulate_ui_clicks(client: httpx.AsyncClient):
    print("\n🖱️  [UI Click Monitor] Ingesting user click events...")
    for click in SAMPLE_UI_CLICKS:
        await client.post(f"{WATCHDOG_URL}/api/ui-clicks/ingest", json=click)
        icon = "❌" if click.get("error") else "✅"
        print(f"  {icon} {click['page']}/{click['element']} {'→ ' + click['error'] if click.get('error') else ''}")
        await asyncio.sleep(0.1)


async def trigger_scans(client: httpx.AsyncClient):
    print("\n🔎 [Scanners] Running Git, DB, CI/CD scans...")
    await client.post(f"{WATCHDOG_URL}/api/git/scan")
    print("  ✅ Git Diff scan complete")
    await client.post(f"{WATCHDOG_URL}/api/db/scan")
    print("  ✅ Database scan complete")
    await client.post(f"{WATCHDOG_URL}/api/cicd/scan")
    print("  ✅ CI/CD Pipeline scan complete")


async def generate_and_run_tests(client: httpx.AsyncClient):
    print("\n🤖 [AI Engine] Generating tests from blind spots...")
    resp = await client.post(f"{WATCHDOG_URL}/api/generate")
    data = resp.json()
    print(f"  ✅ Generated {data['count']} test cases")

    print("\n🧪 [Test Runner] Executing generated tests...")
    resp = await client.post(f"{WATCHDOG_URL}/api/run-tests")
    results = resp.json().get("results", [])
    for r in results:
        icon = "✅" if r["status"] == "PASSED" else "❌"
        print(f"  {icon} {r['test_name']} → {r['status']}")


async def main():
    print("=" * 60)
    print("🐕 WatchDog AI — Traffic Simulator")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"WatchDog API: {WATCHDOG_URL}")
    print(f"Sample App: {SAMPLE_APP_URL}")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        await simulate_api_traffic(client)
        await simulate_log_ingestion(client)
        await simulate_ui_clicks(client)
        await trigger_scans(client)
        await generate_and_run_tests(client)

    print("\n" + "=" * 60)
    print("✅ Simulation complete! Open http://localhost:3000 to see the dashboard.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
