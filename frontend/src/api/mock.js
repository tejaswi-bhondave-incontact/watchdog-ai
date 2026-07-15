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
    testCode: `import pytest
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
