import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const icons = {
  'API': '🔌',
  'Logs': '📋',
  'Jira': '🎫',
  'Git': '🌿',
  'DB': '🗄️',
  'CI/CD': '⚙️',
  'UI Clicks': '🖱️',
};

export default function Monitors() {
  const [monitors, setMonitors] = useState(null);

  useEffect(() => {
    apiGet('/api/monitors').then(setMonitors);
  }, []);

  if (!monitors) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Monitor Sources</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {monitors.map((m) => (
          <div key={m.name} className="bg-white border border-gray-200 rounded shadow-sm p-5 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{icons[m.name] || '📡'}</span>
                <span className="font-semibold text-gray-900">{m.name}</span>
              </div>
              <StatusBadge status={m.status} showDot />
            </div>
            <p className="text-sm text-gray-600 mb-2">{m.message}</p>
            <p className="text-xs text-gray-400">Last checked: {m.lastChecked}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
