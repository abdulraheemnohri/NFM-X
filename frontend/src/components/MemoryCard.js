import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function MemoryCard({ memory, onClick }) {
    const typeColors = {
        episodic: 'bg-purple-100 text-purple-800',
        semantic: 'bg-blue-100 text-blue-800',
        preference: 'bg-green-100 text-green-800',
        failure: 'bg-red-100 text-red-800',
        success: 'bg-emerald-100 text-emerald-800',
    };
    return (_jsxs("div", { onClick: onClick, className: "bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer flex flex-col justify-between", children: [_jsxs("div", { children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: `text-xs font-medium px-2 py-1 rounded-full ${typeColors[memory.type] || 'bg-gray-100 text-gray-800'}`, children: memory.type }), _jsx("span", { className: "text-xs text-gray-400", children: new Date(memory.created_at).toLocaleDateString() })] }), _jsx("p", { className: "text-sm text-gray-700 line-clamp-3 mb-4", children: memory.content })] }), _jsxs("div", { className: "flex items-center gap-4 text-xs text-gray-500 border-t border-gray-100 pt-3", children: [_jsxs("span", { children: ["Confidence: ", (memory.confidence * 100).toFixed(0), "%"] }), _jsxs("span", { children: ["Importance: ", (memory.importance * 100).toFixed(0), "%"] })] })] }));
}
