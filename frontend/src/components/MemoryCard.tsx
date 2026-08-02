import { MemoryResponse } from '../../../sdk/typescript/src/models';

interface Props {
  memory: MemoryResponse;
  onClick: () => void;
}

export function MemoryCard({ memory, onClick }: Props) {
  const typeColors: Record<string, string> = {
    episodic: 'bg-purple-100 text-purple-800',
    semantic: 'bg-blue-100 text-blue-800',
    preference: 'bg-green-100 text-green-800',
    failure: 'bg-red-100 text-red-800',
    success: 'bg-emerald-100 text-emerald-800',
  };

  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${typeColors[memory.type] || 'bg-gray-100 text-gray-800'}`}>
            {memory.type}
          </span>
          <span className="text-xs text-gray-400">
            {new Date(memory.created_at).toLocaleDateString()}
          </span>
        </div>
        <p className="text-sm text-gray-700 line-clamp-3 mb-4">{memory.content}</p>
      </div>
      <div className="flex items-center gap-4 text-xs text-gray-500 border-t border-gray-100 pt-3">
        <span>Confidence: {(memory.confidence * 100).toFixed(0)}%</span>
        <span>Importance: {(memory.importance * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
}
