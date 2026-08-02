import { useEffect } from 'react';
import { useMemoryStore } from '../stores/memoryStore';

export function StatsPanel() {
  const { stats, fetchStats } = useMemoryStore();

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (!stats) return <div className="text-gray-500">Loading stats...</div>;

  const cards = [
    { label: 'Total Memories', value: stats.total_memories, color: 'bg-blue-500' },
    { label: 'Active', value: stats.active_memories, color: 'bg-green-500' },
    { label: 'Versions', value: stats.historical_versions, color: 'bg-purple-500' },
    { label: 'Conflicts', value: stats.unresolved_conflicts, color: 'bg-red-500' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {cards.map((card) => (
        <div key={card.label} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <div className={`w-2.5 h-2.5 rounded-full ${card.color}`} />
            <div className="text-xs text-gray-500 font-medium uppercase tracking-wider">{card.label}</div>
          </div>
          <div className="text-3xl font-bold text-gray-900">{card.value}</div>
        </div>
      ))}
    </div>
  );
}
