import { create } from 'zustand';
import { api } from '../services/api';
import { MemoryResponse } from '../../../sdk/typescript/src/models';

interface MemoryState {
  memories: MemoryResponse[];
  selectedMemory: MemoryResponse | null;
  searchQuery: string;
  stats: any;
  loading: boolean;
  error: string | null;
  fetchMemories: () => Promise<void>;
  searchMemories: (query: string) => Promise<void>;
  selectMemory: (memory: MemoryResponse | null) => void;
  fetchStats: () => Promise<void>;
}

export const useMemoryStore = create<MemoryState>((set) => ({
  memories: [],
  selectedMemory: null,
  searchQuery: '',
  stats: null,
  loading: false,
  error: null,

  fetchMemories: async () => {
    set({ loading: true, error: null });
    try {
      const result = await api.listMemories({ limit: 50 });
      set({ memories: result.memories, loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  searchMemories: async (query: string) => {
    set({ loading: true, error: null, searchQuery: query });
    try {
      const result = await api.search({ query, limit: 20 });
      set({ memories: result.results || [], loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  selectMemory: (memory) => set({ selectedMemory: memory }),

  fetchStats: async () => {
    try {
      const stats = await api.getStats();
      set({ stats });
    } catch (err: any) {
      set({ error: err.message });
    }
  },
}));
