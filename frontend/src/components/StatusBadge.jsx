const styles = {
  active: 'bg-green-100 text-green-800',
  pass: 'bg-green-100 text-green-800',
  degraded: 'bg-yellow-100 text-yellow-800',
  medium: 'bg-yellow-100 text-yellow-800',
  down: 'bg-red-100 text-red-800',
  fail: 'bg-red-100 text-red-800',
  high: 'bg-red-100 text-red-800',
  low: 'bg-green-100 text-green-800',
};

const dots = {
  active: 'bg-green-500',
  pass: 'bg-green-500',
  degraded: 'bg-yellow-500',
  medium: 'bg-yellow-500',
  down: 'bg-red-500',
  fail: 'bg-red-500',
  high: 'bg-red-500',
  low: 'bg-green-500',
};

export default function StatusBadge({ status, showDot = false }) {
  const label = status.charAt(0).toUpperCase() + status.slice(1);
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
      {showDot && <span className={`w-2 h-2 rounded-full ${dots[status] || 'bg-gray-500'}`} />}
      {label}
    </span>
  );
}
