import { useEffect } from 'react';
import { useMemoryStore } from '../stores/memoryStore';
import { SearchBar } from '../components/SearchBar';
import { MemoryCard } from '../components/MemoryCard';

export function MemoryExplorerPage() {
  const { memories, selectedMemory, fetchMemories, selectMemory, loading } = useMemoryStore();

  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 font-semibold">Memory Explorer</h2>
      <SearchBar />

      {loading && <div className="text-gray-500 mb-4 animate-pulse">Loading memories...</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {memories.map((memory) => (
          <MemoryCard
            key={memory.id}
            memory={memory}
            onClick={() => selectMemory(memory)}
          />
        ))}
      </div>

      {selectedMemory && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 transition-opacity">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6 shadow-xl border border-gray-100">
            <div className="flex justify-between items-start mb-4 border-b border-gray-100 pb-3">
              <h3 className="text-xl font-bold text-gray-900">Memory Details</h3>
              <button
                onClick={() => selectMemory(null)}
                className="text-gray-400 hover:text-gray-600 transition p-1 rounded-full hover:bg-gray-100"
              >
                Close
              </button>
            </div>
            <div className="space-y-4 text-sm text-gray-700">
              <div className="flex border-b border-gray-50 pb-2">
                <span className="w-24 font-semibold text-gray-500">ID:</span>
                <span className="font-mono text-gray-900 break-all">{selectedMemory.id}</span>
              </div>
              <div className="flex border-b border-gray-50 pb-2">
                <span className="w-24 font-semibold text-gray-500">Type:</span>
                <span className="font-medium text-gray-900 uppercase tracking-wider">{selectedMemory.type}</span>
              </div>
              <div className="flex border-b border-gray-50 pb-2">
                <span className="w-24 font-semibold text-gray-500">Content:</span>
                <span className="text-gray-900 whitespace-pre-wrap flex-1">{selectedMemory.content}</span>
              </div>
              <div className="flex border-b border-gray-50 pb-2">
                <span className="w-24 font-semibold text-gray-500">Confidence:</span>
                <span className="text-gray-900">{(selectedMemory.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="flex border-b border-gray-50 pb-2">
                <span className="w-24 font-semibold text-gray-500">Importance:</span>
                <span className="text-gray-900">{(selectedMemory.importance * 100).toFixed(0)}%</span>
              </div>
              <div className="flex pb-2">
                <span className="w-24 font-semibold text-gray-500">Created:</span>
                <span className="text-gray-900">{new Date(selectedMemory.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
