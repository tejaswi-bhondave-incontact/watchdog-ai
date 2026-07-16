import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

const cards = [
  { key: 'blindSpots', label: 'Blind Spots Found', icon: '🔍', color: 'border-l-[#E53935]' },
  { key: 'testsGenerated', label: 'Tests Generated', icon: '🧪', color: 'border-l-[#0C6CBF]' },
  { key: 'bugsFound', label: 'Bugs Discovered', icon: '🐛', color: 'border-l-[#F57C00]' },
  { key: 'coveragePct', label: 'Coverage %', icon: '🛡️', color: 'border-l-[#43A047]', suffix: '%' },
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
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Dashboard Overview</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {cards.map((card) => (
          <div key={card.key} className={`bg-white border border-gray-200 border-l-4 ${card.color} rounded shadow-sm p-6`}>
            <div className="text-3xl mb-2">{card.icon}</div>
            <div className="text-3xl font-bold text-gray-900">
              {data[card.key]}{card.suffix || ''}
            </div>
            <div className="text-sm text-gray-500 mt-1">{card.label}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 flex-wrap">
        <button
          onClick={() => handleAction('/api/generate')}
          disabled={loading}
          className="px-5 py-2.5 bg-[#0C6CBF] text-white rounded font-medium hover:bg-[#0A5A9E] disabled:opacity-50 transition-colors text-sm"
        >
          Generate Tests
        </button>
        <button
          onClick={() => handleAction('/api/run-tests')}
          disabled={loading}
          className="px-5 py-2.5 bg-white border border-gray-300 text-gray-700 rounded font-medium hover:bg-gray-50 disabled:opacity-50 transition-colors text-sm"
        >
          Run Tests
        </button>
      </div>

      {actionMsg && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-[#0C6CBF] text-sm">
          {actionMsg}
        </div>
      )}
    </div>
  );
}
