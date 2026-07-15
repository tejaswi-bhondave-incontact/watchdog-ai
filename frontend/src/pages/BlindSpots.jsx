import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

export default function BlindSpots() {
  const [spots, setSpots] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    apiGet('/api/blindspots').then(setSpots);
  }, []);

  if (!spots) return <LoadingSpinner />;

  const categories = ['all', ...new Set(spots.map((s) => s.category))];
  const filtered = filter === 'all' ? spots : spots.filter((s) => s.category === filter);
  const sorted = [...filtered].sort((a, b) => {
    const order = { high: 0, medium: 1, low: 2 };
    return order[a.severity] - order[b.severity];
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Blind Spots</h1>

      <div className="mb-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {categories.map((c) => (
            <option key={c} value={c}>{c === 'all' ? 'All Categories' : c}</option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto bg-white rounded-lg border border-gray-200 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Flow</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sorted.map((spot, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{spot.flow}</td>
                <td className="px-6 py-4 whitespace-nowrap"><StatusBadge status={spot.severity} /></td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{spot.category}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{spot.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
