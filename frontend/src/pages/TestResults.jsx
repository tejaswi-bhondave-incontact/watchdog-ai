import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

export default function TestResults() {
  const [results, setResults] = useState(null);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    apiGet('/api/test-results').then(setResults);
  }, []);

  if (!results) return <LoadingSpinner />;

  const passed = results.filter((r) => r.status === 'pass').length;
  const failed = results.filter((r) => r.status === 'fail').length;

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Test Results</h1>

      <div className="mb-4 p-3 bg-white border border-gray-200 rounded text-sm">
        <span className="text-green-700 font-medium">{passed} passed</span>
        <span className="text-gray-400 mx-2">|</span>
        <span className="text-red-700 font-medium">{failed} failed</span>
        <span className="text-gray-400 mx-2">|</span>
        <span className="text-gray-600">{results.length} total</span>
      </div>

      <div className="bg-white border border-gray-200 rounded shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Test Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {results.map((r, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-mono text-gray-900">{r.name}</td>
                <td className="px-6 py-4"><StatusBadge status={r.status} /></td>
                <td className="px-6 py-4 text-sm text-gray-600">{r.duration}</td>
                <td className="px-6 py-4">
                  {r.error && (
                    <button
                      onClick={() => setExpanded(expanded === i ? null : i)}
                      className="text-xs text-[#0C6CBF] hover:text-[#0A5A9E] font-medium"
                    >
                      {expanded === i ? 'Hide' : 'Show Error'}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {expanded !== null && results[expanded]?.error && (
          <div className="px-6 py-4 bg-red-50 border-t border-red-200">
            <p className="text-sm text-red-800 font-mono">{results[expanded].error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
