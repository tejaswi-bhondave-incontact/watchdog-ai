"""WatchDog AI — Full Demo Script"""
import subprocess, sys, time, os, json
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Start backend
os.chdir('C:/Users/tbhondave/watchdog-ai/backend')
proc1 = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(4)

# Start sample app
os.chdir('C:/Users/tbhondave/watchdog-ai/sample_app')
proc2 = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8001'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(4)
os.chdir('C:/Users/tbhondave/watchdog-ai/backend')

import httpx

print('=' * 60)
print('  WATCHDOG AI - LIVE DEMO')
print('=' * 60)
print('  Backend (8000): RUNNING')
print('  Sample App (8001): RUNNING')
print('=' * 60)

# Phase 1: API Traffic
print('\n[PHASE 1] API Traffic Monitor')
print('-' * 40)
traffic = [
    {'method': 'POST', 'path': '/api/users', 'body': {'name': 'John Smith', 'email': 'john@test.com'}, 'status_code': 201},
    {'method': 'POST', 'path': '/api/users', 'body': {'name': '', 'email': ''}, 'status_code': 400},
    {'method': 'POST', 'path': '/api/users', 'body': {'name': None, 'email': 'null@test.com'}, 'status_code': 400},
    {'method': 'POST', 'path': '/api/users', 'body': {'name': '<script>alert(1)</script>', 'email': 'xss@t.com'}, 'status_code': 201},
    {'method': 'POST', 'path': '/api/orders', 'body': {'user_id': '1', 'product_id': '1', 'quantity': -5}, 'status_code': 201},
    {'method': 'POST', 'path': '/api/orders', 'body': {'user_id': '1', 'product_id': '1', 'quantity': 99999999}, 'status_code': 201},
    {'method': 'POST', 'path': '/api/users', 'body': {'name': 'A'*500, 'email': 'long@t.com'}, 'status_code': 201},
]
for t in traffic:
    httpx.post('http://localhost:8000/api/traffic/ingest', json=t)
r = httpx.get('http://localhost:8000/api/blindspots')
api_bs = [b for b in r.json()['blindspots'] if b['source'] == 'api_traffic']
print(f'  Sent {len(traffic)} requests (normal + edge cases)')
print(f'  BLIND SPOTS FOUND: {len(api_bs)}')
for b in api_bs:
    print(f'    - {b["scenario"]}')

# Phase 2: Log Monitor
print('\n[PHASE 2] Application Log Monitor')
print('-' * 40)
logs = [
    {'level': 'ERROR', 'message': 'NullPointerException in PaymentService.processRefund', 'source': 'payment_service', 'stack_trace': 'NullPointerException at line 47'},
    {'level': 'ERROR', 'message': 'TypeError cannot concatenate NoneType to str', 'source': 'email_service', 'stack_trace': 'TypeError at line 89'},
    {'level': 'CRITICAL', 'message': 'OutOfMemoryError heap space exceeded', 'source': 'import_service', 'stack_trace': 'OutOfMemoryError'},
]
for l in logs:
    httpx.post('http://localhost:8000/api/logs/ingest', json=l)
r = httpx.get('http://localhost:8000/api/blindspots')
log_bs = [b for b in r.json()['blindspots'] if b['source'] == 'logs']
print(f'  Ingested {len(logs)} error logs')
print(f'  BLIND SPOTS FOUND: {len(log_bs)}')
for b in log_bs:
    print(f'    - {b["scenario"]}')

# Phase 3: UI Clicks
print('\n[PHASE 3] UI Click Path Monitor')
print('-' * 40)
clicks = [
    {'page': 'checkout', 'element': 'submit_btn', 'timestamp': '2026-07-15T10:00:00', 'session_id': 's1', 'error': None},
    {'page': 'checkout', 'element': 'submit_btn', 'timestamp': '2026-07-15T10:00:01', 'session_id': 's1', 'error': None},
    {'page': 'checkout', 'element': 'submit_btn', 'timestamp': '2026-07-15T10:00:02', 'session_id': 's1', 'error': 'Button unresponsive'},
    {'page': 'profile', 'element': 'upload_avatar', 'timestamp': '2026-07-15T11:00:00', 'session_id': 's2', 'error': '500 Internal Server Error'},
]
for c in clicks:
    httpx.post('http://localhost:8000/api/ui-clicks/ingest', json=c)
r = httpx.get('http://localhost:8000/api/blindspots')
ui_bs = [b for b in r.json()['blindspots'] if b['source'] == 'ui_clicks']
print(f'  Tracked {len(clicks)} click events')
print(f'  BLIND SPOTS FOUND: {len(ui_bs)}')
for b in ui_bs:
    print(f'    - {b["scenario"]}')

# Phase 4: Scans
print('\n[PHASE 4] Git + Database + CI/CD Scans')
print('-' * 40)
httpx.post('http://localhost:8000/api/git/scan')
httpx.post('http://localhost:8000/api/db/scan')
httpx.post('http://localhost:8000/api/cicd/scan')
r = httpx.get('http://localhost:8000/api/blindspots')
all_bs = r.json()['blindspots']
git_bs = [b for b in all_bs if b['source'] == 'git_diff']
db_bs = [b for b in all_bs if b['source'] == 'database']
cicd_bs = [b for b in all_bs if b['source'] == 'cicd']
print(f'  Git Diffs: {len(git_bs)} uncovered functions')
print(f'  Database: {len(db_bs)} slow/null queries')
print(f'  CI/CD: {len(cicd_bs)} flaky/stale tests')

# Phase 5: Jira
print('\n[PHASE 5] Jira Ticket Analysis')
print('-' * 40)
jira_text = 'When user tries to checkout with 2 items and applies coupon SAVE20, the total shows negative. Steps: 1. Add 2 items 2. Apply SAVE20 3. Click checkout. Expected: correct total. Actual: shows -50 dollars.'
r = httpx.post('http://localhost:8000/api/jira-analyze', json={'ticket_text': jira_text, 'ticket_id': 'BUG-1234'})
result = r.json()
print(f'  Ticket: BUG-1234')
print(f'  Blind spot detected: {result["blindspot"]["scenario"]}')
print(f'  Test auto-generated: YES')

# Phase 6: Generate ALL tests
print('\n[PHASE 6] AI Test Generation')
print('-' * 40)
r = httpx.post('http://localhost:8000/api/generate')
data = r.json()
print(f'  Tests generated from all blind spots: {data["count"]}')

# Show sample
r = httpx.get('http://localhost:8000/api/generated-tests')
tests = r.json()['tests']
if tests:
    print(f'\n  --- Sample Test ({tests[0]["scenario"]}) ---')
    for line in tests[0]['test_code'].split('\n')[:10]:
        print(f'  {line}')
    print('  ...')

# Final
print('\n' + '=' * 60)
print('  FINAL RESULTS')
print('=' * 60)
r = httpx.get('http://localhost:8000/api/overview')
ov = r.json()
print(f'  Blind Spots Found:  {ov["total_blindspots"]}')
print(f'  Tests Generated:    {ov["tests_generated"]}')
print(f'  Bugs Discovered:    {ov["bugs_found"]}')
print(f'  Coverage Increase:  {ov["coverage_increase"]}')
print(f'  Monitors Active:    {ov["monitors_active"]}')
print('=' * 60)
print('  DEMO COMPLETE!')
print('  Open http://localhost:5173 for the dashboard')
print('=' * 60)

proc1.terminate()
proc2.terminate()
