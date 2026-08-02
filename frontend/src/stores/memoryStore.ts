import { create } from "zustand";
interface MemoryState { memories: any[]; loading: boolean; }
export const useMemoryStore = create<MemoryState>((set) => ({
  memories: [],
  loading: false,
  fetchMemories: async () => { set({ loading: true }); set({ loading: false }); }
}));