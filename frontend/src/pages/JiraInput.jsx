import { useState } from 'react';
import { apiPost } from '../api/client';
import CodeViewer from '../components/CodeViewer';
import LoadingSpinner from '../components/LoadingSpinner';

export default function JiraInput() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [jiraResults, setJiraResults] = useState(null);
  const [jiraLoading, setJiraLoading] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await apiPost('/api/jira-analyze', { ticket_text: text, ticket_id: 'MANUAL-001' });
      setResult(data);
    } catch (e) {
      setResult({ blindspot: { title: 'Error', description: e.message }, generated_test: { code: '# Error generating test: ' + e.message, language: 'python' } });
    }
    setLoading(false);
  };

  const handleFetchJira = async () => {
    setJiraLoading(true);
    setJiraResults(null);
    setSelectedTicket(null);
    const data = await apiPost('/api/jira-fetch', { max_results: 10 });
    setJiraResults(data);
    setJiraLoading(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Jira Bug → Test Generator</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Paste mode */}
        <div className="bg-white border border-gray-200 rounded shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Paste Bug Description</h2>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste a Jira bug description here..."
            rows={6}
            className="w-full px-4 py-3 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#0C6CBF] focus:border-transparent resize-y"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            className="mt-3 px-5 py-2.5 bg-[#0C6CBF] text-white rounded font-medium hover:bg-[#0A5A9E] disabled:opacity-50 transition-colors text-sm"
          >
            Generate Test
          </button>
        </div>

        {/* Right: Fetch from Jira */}
        <div className="bg-white border border-gray-200 rounded shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Fetch from Jira</h2>
          <p className="text-sm text-gray-600 mb-4">
            Pull recent bugs directly from NiCE Jira and generate tests for each one automatically.
          </p>
          <button
            onClick={handleFetchJira}
            disabled={jiraLoading}
            className="px-5 py-2.5 bg-[#0C6CBF] text-white rounded font-medium hover:bg-[#0A5A9E] disabled:opacity-50 transition-colors text-sm"
          >
            {jiraLoading ? 'Fetching...' : 'Fetch from Jira'}
          </button>
        </div>
      </div>

      {/* Paste mode result */}
      <div className="mt-6">
        {loading && <LoadingSpinner />}

        {!loading && result && (
          <div className="bg-white border border-gray-200 rounded shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Generated Test</h2>
            {result.blindspot && (
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-sm font-medium text-amber-800">Blind Spot: {result.blindspot.description || result.blindspot.title}</p>
              </div>
            )}
            <CodeViewer
              code={result.generated_test?.code || result.testCode || 'No test generated'}
              language={result.generated_test?.language || result.language || 'python'}
            />
          </div>
        )}
      </div>

      {/* Jira fetch results */}
      {jiraLoading && <div className="mt-6"><LoadingSpinner /></div>}

      {!jiraLoading && jiraResults && (
        <div className="mt-6">
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
            <p className="text-sm text-[#0C6CBF] font-medium">
              Analyzed {jiraResults.tickets_analyzed} tickets from Jira
            </p>
          </div>

          <div className="flex flex-col lg:flex-row gap-4">
            {/* Ticket list */}
            <div className="lg:w-1/3">
              <div className="bg-white border border-gray-200 rounded shadow-sm overflow-hidden">
                {jiraResults.results.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => setSelectedTicket(i)}
                    className={`w-full text-left px-4 py-3 border-b border-gray-100 last:border-b-0 transition-colors ${
                      selectedTicket === i
                        ? 'bg-blue-50 text-[#0C6CBF]'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-mono text-xs font-semibold">{item.ticket_key}</div>
                    <div className="text-sm text-gray-700 mt-1 line-clamp-2">{item.summary}</div>
                    <span className={`inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                      item.status === 'Open' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {item.status}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Generated test for selected ticket */}
            <div className="lg:w-2/3">
              {selectedTicket !== null && jiraResults.results[selectedTicket] && (
                <div>
                  <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <p className="text-sm font-medium text-amber-800">
                      Blind Spot: {jiraResults.results[selectedTicket].blindspot?.description || jiraResults.results[selectedTicket].blindspot?.title || 'Coverage gap detected'}
                    </p>
                  </div>
                  <CodeViewer
                    code={jiraResults.results[selectedTicket].generated_test?.code || 'No test generated'}
                    language={jiraResults.results[selectedTicket].generated_test?.language || 'python'}
                  />
                </div>
              )}
              {selectedTicket === null && (
                <p className="text-gray-500 text-sm text-center py-12">
                  Select a ticket from the left to view its generated test
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
