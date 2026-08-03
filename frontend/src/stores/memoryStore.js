/**
 * NFM-X Memory Store
 *
 * Zustand store for managing memory state in the frontend.
 */
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { api } from '../services/api';
export const useMemoryStore = create()(devtools(persist((set, get) => ({
    // Initial state
    memories: [],
    filteredMemories: [],
    selectedMemory: null,
    loading: false,
    error: null,
    filters: {},
    // Actions
    fetchMemories: async (filters) => {
        try {
            set({ loading: true, error: null });
            const currentFilters = filters || get().filters;
            const response = await api.listMemories(currentFilters);
            set({
                memories: response.items,
                filteredMemories: response.items,
                filters: currentFilters,
                loading: false,
            });
        }
        catch (err) {
            set({
                error: err instanceof Error ? err.message : 'Failed to fetch memories',
                loading: false,
            });
        }
    },
    fetchMemory: async (memoryId) => {
        try {
            set({ loading: true, error: null });
            const memory = await api.getMemory(memoryId);
            set({ selectedMemory: memory, loading: false });
        }
        catch (err) {
            set({
                error: err instanceof Error ? err.message : 'Failed to fetch memory',
                loading: false,
            });
        }
    },
    createMemory: async (payload) => {
        try {
            set({ loading: true, error: null });
            const memory = await api.createMemory(payload);
            set((state) => ({
                memories: [memory, ...state.memories],
                filteredMemories: [memory, ...state.filteredMemories],
                loading: false,
            }));
            return memory;
        }
        catch (err) {
            set({
                error: err instanceof Error ? err.message : 'Failed to create memory',
                loading: false,
            });
            return null;
        }
    },
    updateMemory: async (memoryId, payload) => {
        try {
            set({ loading: true, error: null });
            const memory = await api.updateMemory(memoryId, payload);
            set((state) => ({
                memories: state.memories.map((m) => (m.id === memoryId ? memory : m)),
                filteredMemories: state.filteredMemories.map((m) => (m.id === memoryId ? memory : m)),
                selectedMemory: state.selectedMemory?.id === memoryId ? memory : state.selectedMemory,
                loading: false,
            }));
            return memory;
        }
        catch (err) {
            set({
                error: err instanceof Error ? err.message : 'Failed to update memory',
                loading: false,
            });
            return null;
        }
    },
    deleteMemory: async (memoryId) => {
        try {
            set({ loading: true, error: null });
            await api.deleteMemory(memoryId);
            set((state) => ({
                memories: state.memories.filter((m) => m.id !== memoryId),
                filteredMemories: state.filteredMemories.filter((m) => m.id !== memoryId),
                selectedMemory: state.selectedMemory?.id === memoryId ? null : state.selectedMemory,
                loading: false,
            }));
            return true;
        }
        catch (err) {
            set({
                error: err instanceof Error ? err.message : 'Failed to delete memory',
                loading: false,
            });
            return false;
        }
    },
    searchMemories: async (query) => {
        try {
            set({ loading: true, error: null });
            const response = await api.search(query);
            set({
                filteredMemories: response.items,
                loading: false,
            });
        }
        catch (err) {
            set({
                error: err instanceof Error ? err.message : 'Failed to search memories',
                loading: false,
            });
        }
    },
    setFilters: (filters) => {
        set({ filters });
    },
    selectMemory: (memory) => {
        set({ selectedMemory: memory });
    },
    clearError: () => {
        set({ error: null });
    },
}), { name: 'memory-store' }), { name: 'MemoryStore' }));
// Selector hooks for better performance
export const useMemories = () => useMemoryStore((state) => state.memories);
export const useFilteredMemories = () => useMemoryStore((state) => state.filteredMemories);
export const useSelectedMemory = () => useMemoryStore((state) => state.selectedMemory);
export const useMemoryLoading = () => useMemoryStore((state) => state.loading);
export const useMemoryError = () => useMemoryStore((state) => state.error);
