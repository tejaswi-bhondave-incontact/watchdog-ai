import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import CodeViewer from '../components/CodeViewer';
import LoadingSpinner from '../components/LoadingSpinner';

export default function GeneratedTests() {
  const [tests, setTests] = useState(null);
  const [selected, setSelected] = useState(0);

  useEffect(() => {
    apiGet('/api/generated-tests').then((data) => {
      setTests(data);
      setSelected(0);
    });
  }, []);

  if (!tests) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Generated Tests</h1>

      <div className="flex flex-col lg:flex-row gap-4">
        <div className="lg:w-1/3">
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
            {tests.map((test, i) => (
              <button
                key={i}
                onClick={() => setSelected(i)}
                className={`w-full text-left px-4 py-3 text-sm border-b border-gray-100 last:border-b-0 transition-colors ${
                  selected === i
                    ? 'bg-indigo-50 text-indigo-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <div className="font-mono text-xs">{test.name}</div>
                <div className="text-xs text-gray-400 mt-1">{test.language}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:w-2/3">
          {tests[selected] && (
            <CodeViewer code={tests[selected].code} language={tests[selected].language} />
          )}
        </div>
      </div>
    </div>
  );
}
