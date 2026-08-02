import { StatsPanel } from '../components/StatsPanel';

export function HomePage() {
  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 font-semibold">Dashboard</h2>
      <StatsPanel />
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-2 text-gray-900">Welcome to NFM-X</h3>
        <p className="text-gray-600 leading-relaxed">
          Non-Forgettable Evolutionary AI Memory Layer. Navigate to Memories to explore
          your AI's long-term memory.
        </p>
      </div>
    </div>
  );
}
