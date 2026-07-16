export const mockData = {
  '/api/overview': {
    blindSpots: 23,
    testsGenerated: 156,
    bugsFound: 12,
    coveragePct: 67,
  },

  '/api/monitors': [
    { name: 'API', status: 'active', lastChecked: '2 min ago', message: 'Tracking 48 endpoints, 1.2k req/min' },
    { name: 'Logs', status: 'active', lastChecked: '1 min ago', message: 'Processing 3.4k log entries/min' },
    { name: 'Jira', status: 'active', lastChecked: '5 min ago', message: '14 new bugs synced today' },
    { name: 'Git', status: 'degraded', lastChecked: '10 min ago', message: 'Rate limited — retrying in 2 min' },
    { name: 'DB', status: 'active', lastChecked: '30 sec ago', message: 'Monitoring 12 tables, 890 queries/min' },
    { name: 'CI/CD', status: 'active', lastChecked: '3 min ago', message: 'Last pipeline: build #4821 passed' },
    { name: 'UI Clicks', status: 'down', lastChecked: '15 min ago', message: 'Tracker disconnected — check agent' },
  ],

  '/api/blindspots': [
    { flow: 'Password Reset Flow', severity: 'high', category: 'Auth', description: 'No tests cover token expiry edge case' },
    { flow: 'Bulk Contact Import', severity: 'high', category: 'Data', description: 'CSV parsing with special characters untested' },
    { flow: 'Agent Transfer', severity: 'medium', category: 'Routing', description: 'Multi-skill transfer path has no coverage' },
    { flow: 'Webhook Retry Logic', severity: 'medium', category: 'Integration', description: 'Exponential backoff not validated' },
    { flow: 'Session Timeout', severity: 'low', category: 'Auth', description: 'Grace period behavior undocumented and untested' },
    { flow: 'Report Export PDF', severity: 'high', category: 'Export', description: 'Large dataset pagination not tested' },
    { flow: 'Real-time Dashboard WS', severity: 'medium', category: 'UI', description: 'Reconnection after network drop untested' },
    { flow: 'Skill Assignment Rules', severity: 'low', category: 'Config', description: 'Priority conflict resolution not covered' },
  ],

  '/api/generated-tests': [
    {
      name: 'test_password_reset_expiry.py',
      language: 'python',
      code: `import pytest
from datetime import datetime, timedelta
from app.auth import PasswordResetToken

class TestPasswordResetExpiry:
    def test_token_expires_after_24_hours(self):
        token = PasswordResetToken.create(user_id=42)
        token.created_at = datetime.now() - timedelta(hours=25)
        assert token.is_expired() is True

    def test_token_valid_within_window(self):
        token = PasswordResetToken.create(user_id=42)
        assert token.is_expired() is False

    def test_used_token_cannot_be_reused(self):
        token = PasswordResetToken.create(user_id=42)
        token.consume()
        with pytest.raises(TokenAlreadyUsedError):
            token.consume()`,
    },
    {
      name: 'test_bulk_import_csv.py',
      language: 'python',
      code: `import pytest
from app.contacts import BulkImporter

class TestBulkImportCSV:
    def test_handles_unicode_names(self):
        csv_data = "name,email\\nJose Martinez,jose@example.com"
        result = BulkImporter.process(csv_data)
        assert result.success_count == 1

    def test_rejects_malformed_rows(self):
        csv_data = "name,email\\n,missing@name.com\\nNoEmail,"
        result = BulkImporter.process(csv_data)
        assert result.error_count == 2

    def test_large_file_batching(self):
        csv_data = generate_csv(rows=10000)
        result = BulkImporter.process(csv_data)
        assert result.batch_count == 10`,
    },
    {
      name: 'test_agent_transfer.js',
      language: 'javascript',
      code: `const { AgentRouter } = require('../src/routing');

describe('Agent Transfer', () => {
  it('should transfer to agent with matching skill', async () => {
    const router = new AgentRouter();
    const result = await router.transfer({
      contactId: 'c-001',
      targetSkill: 'billing',
    });
    expect(result.assignedAgent).toBeDefined();
    expect(result.assignedAgent.skills).toContain('billing');
  });

  it('should queue when no agents available', async () => {
    const router = new AgentRouter({ availableAgents: [] });
    const result = await router.transfer({
      contactId: 'c-002',
      targetSkill: 'technical',
    });
    expect(result.queued).toBe(true);
  });
});`,
    },
  ],

  '/api/test-results': [
    { name: 'test_password_reset_expiry.py', status: 'pass', duration: '1.2s', error: null },
    { name: 'test_bulk_import_csv.py', status: 'fail', duration: '3.8s', error: 'AssertionError: expected error_count == 2, got 1. Row with empty name was accepted instead of rejected.' },
    { name: 'test_agent_transfer.js', status: 'pass', duration: '0.9s', error: null },
    { name: 'test_webhook_retry.py', status: 'fail', duration: '12.1s', error: 'TimeoutError: Retry backoff exceeded max wait. 5th retry took 45s instead of expected 32s.' },
    { name: 'test_session_timeout.py', status: 'pass', duration: '2.1s', error: null },
  ],

  '/api/jira-analyze': {
    blindspot: { title: 'Report Export Pagination', description: 'Large dataset pagination not tested for PDF export' },
    generated_test: {
      code: `import pytest
from app.export import ReportExporter

class TestReportExportPagination:
    def test_large_dataset_paginates_correctly(self):
        exporter = ReportExporter(page_size=100)
        data = generate_report_data(rows=1500)
        pdf = exporter.export_pdf(data)
        assert pdf.page_count == 15

    def test_empty_dataset_returns_single_page(self):
        exporter = ReportExporter(page_size=100)
        pdf = exporter.export_pdf([])
        assert pdf.page_count == 1`,
      language: 'python',
    },
  },

  '/api/jira-fetch': {
    tickets_analyzed: 5,
    results: [
      {
        ticket_key: 'CARD-2670',
        summary: 'Contact card fails to load when agent has special characters in name',
        status: 'Open',
        blindspot: { title: 'Contact Card Special Chars', description: 'No test covers agent names with special characters in contact card rendering' },
        generated_test: { code: `import pytest\nfrom app.contact_card import ContactCard\n\nclass TestContactCardSpecialChars:\n    def test_renders_agent_name_with_unicode(self):\n        card = ContactCard(agent_name="José García")\n        assert card.render() is not None\n\n    def test_renders_agent_name_with_apostrophe(self):\n        card = ContactCard(agent_name="O'Brien")\n        assert "O'Brien" in card.render()`, language: 'python' },
      },
      {
        ticket_key: 'UH-80319',
        summary: 'User hub session expires without warning during active editing',
        status: 'Open',
        blindspot: { title: 'Session Expiry Warning', description: 'No test validates session expiry warning appears before timeout during active user interaction' },
        generated_test: { code: `import pytest\nfrom unittest.mock import patch\nfrom app.session import SessionManager\n\nclass TestSessionExpiryWarning:\n    def test_warning_shown_before_expiry(self):\n        session = SessionManager(timeout=3600)\n        session.advance_time(3300)  # 5 min before expiry\n        assert session.should_show_warning() is True\n\n    def test_active_editing_extends_session(self):\n        session = SessionManager(timeout=3600)\n        session.advance_time(3500)\n        session.record_activity()\n        assert session.is_expired() is False`, language: 'python' },
      },
      {
        ticket_key: 'ORC-53275',
        summary: 'Orchestration fails when concurrent transfers exceed pool limit',
        status: 'In Progress',
        blindspot: { title: 'Concurrent Transfer Limit', description: 'No test validates behavior when concurrent agent transfers exceed the configured pool limit' },
        generated_test: { code: `import pytest\nfrom app.orchestration import TransferPool\n\nclass TestConcurrentTransferLimit:\n    def test_rejects_transfer_over_pool_limit(self):\n        pool = TransferPool(max_concurrent=5)\n        for i in range(5):\n            pool.initiate_transfer(f"contact_{i}")\n        with pytest.raises(PoolExhaustedError):\n            pool.initiate_transfer("contact_overflow")\n\n    def test_allows_transfer_after_slot_freed(self):\n        pool = TransferPool(max_concurrent=5)\n        for i in range(5):\n            pool.initiate_transfer(f"contact_{i}")\n        pool.complete_transfer("contact_0")\n        pool.initiate_transfer("contact_new")  # should not raise`, language: 'python' },
      },
      {
        ticket_key: 'DE-160445',
        summary: 'Digital channel message delivery delayed by 30+ seconds intermittently',
        status: 'Open',
        blindspot: { title: 'Message Delivery Latency', description: 'No test validates message delivery SLA under intermittent network conditions' },
        generated_test: { code: `import pytest\nimport asyncio\nfrom app.digital import MessageBroker\n\nclass TestMessageDeliveryLatency:\n    @pytest.mark.asyncio\n    async def test_delivery_within_sla(self):\n        broker = MessageBroker()\n        start = asyncio.get_event_loop().time()\n        await broker.deliver("msg_001", channel="chat")\n        elapsed = asyncio.get_event_loop().time() - start\n        assert elapsed < 5.0  # 5 second SLA\n\n    @pytest.mark.asyncio\n    async def test_retry_on_transient_failure(self):\n        broker = MessageBroker(simulate_failures=2)\n        result = await broker.deliver("msg_002", channel="chat")\n        assert result.delivered is True\n        assert result.attempts == 3`, language: 'python' },
      },
      {
        ticket_key: 'AW-52100',
        summary: 'CX Agent workspace crashes when switching between 10+ active contacts',
        status: 'Open',
        blindspot: { title: 'Multi-Contact Switch Stability', description: 'No test validates workspace stability when rapidly switching between many active contacts' },
        generated_test: { code: `import pytest\nfrom app.workspace import AgentWorkspace\n\nclass TestMultiContactSwitch:\n    def test_switch_between_10_contacts(self):\n        ws = AgentWorkspace()\n        contacts = [ws.accept_contact(f"c_{i}") for i in range(10)]\n        for contact in contacts:\n            ws.switch_to(contact)\n        assert ws.active_contact == contacts[-1]\n        assert ws.is_stable() is True\n\n    def test_rapid_switching_no_crash(self):\n        ws = AgentWorkspace()\n        contacts = [ws.accept_contact(f"c_{i}") for i in range(15)]\n        for _ in range(50):  # rapid switching\n            ws.switch_to(contacts[_ % 15])\n        assert ws.is_stable() is True`, language: 'python' },
      },
    ],
  },

  '/api/generate': {
    message: 'Generated 3 new test cases from recent traffic patterns',
    count: 3,
  },

  '/api/run-tests': {
    message: 'Test execution complete',
    passed: 3,
    failed: 2,
  },
};
