import { useEffect } from 'react';
import { useMemoryStore } from '../stores/memoryStore';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export function StatsPage() {
  const { stats, fetchStats } = useMemoryStore();

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (!stats) return <div className="text-gray-500">Loading stats...</div>;

  const chartData = Object.entries(stats.memories_by_type || {}).map(([type, count]) => ({
    name: type,
    count: count,
  }));

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 font-semibold">System Stats</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Distribution</h3>
          {chartData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="text-gray-500 flex items-center justify-center h-64 font-medium">No memory data found.</div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Metrics Overview</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="border border-gray-100 p-3 rounded-lg bg-gray-50">
              <div className="text-xs text-gray-500 font-medium">Avg Confidence</div>
              <div className="text-2xl font-bold text-gray-900">{(stats.avg_confidence * 100).toFixed(1)}%</div>
            </div>
            <div className="border border-gray-100 p-3 rounded-lg bg-gray-50">
              <div className="text-xs text-gray-500 font-medium">Avg Importance</div>
              <div className="text-2xl font-bold text-gray-900">{(stats.avg_importance * 100).toFixed(1)}%</div>
            </div>
            <div className="border border-gray-100 p-3 rounded-lg bg-gray-50">
              <div className="text-xs text-gray-500 font-medium">Unresolved Conflicts</div>
              <div className="text-2xl font-bold text-gray-900">{stats.unresolved_conflicts}</div>
            </div>
            <div className="border border-gray-100 p-3 rounded-lg bg-gray-50">
              <div className="text-xs text-gray-500 font-medium">Total Events</div>
              <div className="text-2xl font-bold text-gray-900">{stats.total_events}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
