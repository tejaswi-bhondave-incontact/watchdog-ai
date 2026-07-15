import { useState } from 'react';
import { apiPost } from '../api/client';
import CodeViewer from '../components/CodeViewer';
import LoadingSpinner from '../components/LoadingSpinner';

export default function JiraInput() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    const data = await apiPost('/api/jira-analyze', { text });
    setResult(data);
    setLoading(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Jira Bug → Test Generator</h1>

      <div className="mb-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste a Jira bug description here..."
          rows={6}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-y"
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
        className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
      >
        Generate Test
      </button>

      <div className="mt-6">
        {loading && <LoadingSpinner />}

        {!loading && !result && (
          <p className="text-gray-500 text-sm text-center py-8">
            Paste a bug description above and click Generate to see an AI-generated test case.
          </p>
        )}

        {!loading && result && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Generated Test</h2>
            <CodeViewer code={result.testCode} language={result.language} />
          </div>
        )}
      </div>
    </div>
  );
}
