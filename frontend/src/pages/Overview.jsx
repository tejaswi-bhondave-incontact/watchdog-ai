import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

const cards = [
  { key: 'blindSpots', label: 'Blind Spots Found', icon: '🔍', color: 'border-red-400 bg-red-50' },
  { key: 'testsGenerated', label: 'Tests Generated', icon: '🧪', color: 'border-indigo-400 bg-indigo-50' },
  { key: 'bugsFound', label: 'Bugs Discovered', icon: '🐛', color: 'border-orange-400 bg-orange-50' },
  { key: 'coveragePct', label: 'Coverage %', icon: '🛡️', color: 'border-green-400 bg-green-50', suffix: '%' },
];

export default function Overview() {
  const [data, setData] = useState(null);
  const [actionMsg, setActionMsg] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiGet('/api/overview').then(setData);
  }, []);

  const handleAction = async (endpoint) => {
    setLoading(true);
    setActionMsg('');
    const result = await apiPost(endpoint);
    setActionMsg(result.message);
    setLoading(false);
  };

  if (!data) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {cards.map((card) => (
          <div key={card.key} className={`border-l-4 ${card.color} rounded-lg shadow-sm p-6`}>
            <div className="text-3xl mb-2">{card.icon}</div>
            <div className="text-3xl font-bold text-gray-900">
              {data[card.key]}{card.suffix || ''}
            </div>
            <div className="text-sm text-gray-600 mt-1">{card.label}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-4 flex-wrap">
        <button
          onClick={() => handleAction('/api/generate')}
          disabled={loading}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          Generate Tests
        </button>
        <button
          onClick={() => handleAction('/api/run-tests')}
          disabled={loading}
          className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          Run Tests
        </button>
      </div>

      {actionMsg && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800 text-sm">
          {actionMsg}
        </div>
      )}
    </div>
  );
}
