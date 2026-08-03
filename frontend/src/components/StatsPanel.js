import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect } from 'react';
import { useMemoryStore } from '../stores/memoryStore';
export function StatsPanel() {
    const { stats, fetchStats } = useMemoryStore();
    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, [fetchStats]);
    if (!stats)
        return _jsx("div", { className: "text-gray-500", children: "Loading stats..." });
    const cards = [
        { label: 'Total Memories', value: stats.total_memories, color: 'bg-blue-500' },
        { label: 'Active', value: stats.active_memories, color: 'bg-green-500' },
        { label: 'Versions', value: stats.historical_versions, color: 'bg-purple-500' },
        { label: 'Conflicts', value: stats.unresolved_conflicts, color: 'bg-red-500' },
    ];
    return (_jsx("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-4 mb-6", children: cards.map((card) => (_jsxs("div", { className: "bg-white rounded-lg p-4 border border-gray-200 shadow-sm", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [_jsx("div", { className: `w-2.5 h-2.5 rounded-full ${card.color}` }), _jsx("div", { className: "text-xs text-gray-500 font-medium uppercase tracking-wider", children: card.label })] }), _jsx("div", { className: "text-3xl font-bold text-gray-900", children: card.value })] }, card.label))) }));
}
