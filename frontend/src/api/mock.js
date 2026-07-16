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
        ticket_key: 'SHOP-1042',
        summary: 'Cart total shows negative when 100% discount coupon applied with free shipping',
        status: 'Open',
        blindspot: { title: 'Negative Cart Total', description: 'No test covers cart total calculation when 100% discount coupon is combined with free shipping option' },
        generated_test: { code: `import pytest\nfrom app.cart import CartService\n\nclass TestNegativeCartTotal:\n    def test_cart_total_not_negative_with_full_discount(self):\n        cart = CartService()\n        cart.add_item(product_id="P001", price=49.99)\n        cart.apply_coupon("FREE100")  # 100% discount\n        cart.set_shipping("free")\n        assert cart.total >= 0, f"Cart total is negative: {cart.total}"\n\n    def test_cart_total_zero_with_full_discount(self):\n        cart = CartService()\n        cart.add_item(product_id="P001", price=49.99)\n        cart.apply_coupon("FREE100")\n        assert cart.total == 0.00`, language: 'python' },
      },
      {
        ticket_key: 'SHOP-1087',
        summary: 'User profile update crashes when display name contains emoji characters',
        status: 'Open',
        blindspot: { title: 'Emoji in Profile Name', description: 'No test covers profile update with emoji characters in display name field' },
        generated_test: { code: `import pytest\nimport httpx\n\nclass TestProfileEmojiName:\n    BASE_URL = "http://localhost:8001"\n\n    def test_profile_update_with_emoji(self):\n        response = httpx.put(\n            f"{self.BASE_URL}/api/users/1",\n            json={"name": "John 🚀", "email": "john@test.com"}\n        )\n        assert response.status_code != 500, "Server crashed on emoji input"\n        assert response.status_code in [200, 400]\n\n    def test_profile_update_with_unicode(self):\n        response = httpx.put(\n            f"{self.BASE_URL}/api/users/1",\n            json={"name": "José García", "email": "jose@test.com"}\n        )\n        assert response.status_code == 200`, language: 'python' },
      },
      {
        ticket_key: 'SHOP-1103',
        summary: 'Concurrent checkout causes duplicate orders when user double-clicks Place Order',
        status: 'Open',
        blindspot: { title: 'Double-Click Duplicate Order', description: 'No test validates idempotency of order creation endpoint under concurrent requests' },
        generated_test: { code: `import pytest\nimport httpx\nimport asyncio\n\nclass TestDuplicateOrderPrevention:\n    BASE_URL = "http://localhost:8001"\n\n    @pytest.mark.asyncio\n    async def test_double_click_creates_single_order(self):\n        order_data = {"user_id": "1", "product_id": "1", "quantity": 1}\n        async with httpx.AsyncClient() as client:\n            results = await asyncio.gather(\n                client.post(f"{self.BASE_URL}/api/orders", json=order_data),\n                client.post(f"{self.BASE_URL}/api/orders", json=order_data),\n            )\n        success_count = sum(1 for r in results if r.status_code == 201)\n        assert success_count == 1, f"Expected 1 order, got {success_count} (duplicate!)"`, language: 'python' },
      },
      {
        ticket_key: 'SHOP-1118',
        summary: 'Search API returns results for deleted products causing 404 on click',
        status: 'Open',
        blindspot: { title: 'Stale Search Index', description: 'No test validates that deleted products are removed from search index' },
        generated_test: { code: `import pytest\nimport httpx\n\nclass TestSearchIndexConsistency:\n    BASE_URL = "http://localhost:8001"\n\n    def test_deleted_product_not_in_search(self):\n        # Delete a product\n        httpx.delete(f"{self.BASE_URL}/api/products/99")\n        # Search should not return it\n        response = httpx.get(f"{self.BASE_URL}/api/products/99")\n        assert response.status_code == 404\n\n    def test_search_results_all_accessible(self):\n        response = httpx.get(f"{self.BASE_URL}/api/products")\n        products = response.json()\n        for product in products:\n            detail = httpx.get(f"{self.BASE_URL}/api/products/{product['id']}")\n            assert detail.status_code == 200, f"Product {product['id']} returned {detail.status_code}"`, language: 'python' },
      },
      {
        ticket_key: 'SHOP-1125',
        summary: 'Password reset token never expires - security vulnerability',
        status: 'Open',
        blindspot: { title: 'Token Expiry Missing', description: 'No test validates that password reset tokens expire after the configured time window' },
        generated_test: { code: `import pytest\nfrom datetime import datetime, timedelta\nfrom app.auth import PasswordResetService\n\nclass TestPasswordResetExpiry:\n    def test_token_expires_after_1_hour(self):\n        service = PasswordResetService()\n        token = service.create_reset_token(user_id=42)\n        # Simulate 2 hours passing\n        token.created_at = datetime.now() - timedelta(hours=2)\n        assert service.validate_token(token) is False, "Token should be expired after 1 hour"\n\n    def test_token_valid_within_window(self):\n        service = PasswordResetService()\n        token = service.create_reset_token(user_id=42)\n        assert service.validate_token(token) is True\n\n    def test_token_expiry_not_null(self):\n        service = PasswordResetService()\n        token = service.create_reset_token(user_id=42)\n        assert token.expires_at is not None, "Token expiry should never be NULL"`, language: 'python' },
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
