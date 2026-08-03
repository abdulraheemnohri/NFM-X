/**
 * NFM-X API Service
 *
 * Centralized API service for the NFM-X frontend.
 */
import axios from 'axios';
/**
 * NFM-X API Client
 *
 * Provides methods for interacting with the NFM-X backend API.
 */
export class NFMApi {
    constructor(baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000') {
        this.client = axios.create({
            baseURL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }
    // Memory Operations
    /**
     * Create a new memory
     */
    async createMemory(payload) {
        const response = await this.client.post('/api/v1/memories/', payload);
        return response.data;
    }
    /**
     * Get a specific memory by ID
     */
    async getMemory(memoryId) {
        const response = await this.client.get(`/api/v1/memories/${memoryId}`);
        return response.data;
    }
    /**
     * List memories with pagination and filters
     */
    async listMemories(filters = {}) {
        const params = {};
        if (filters.limit !== undefined)
            params.limit = filters.limit;
        if (filters.offset !== undefined)
            params.offset = filters.offset;
        if (filters.status)
            params.status = filters.status;
        if (filters.tags)
            params.tags = filters.tags.join(',');
        if (filters.search)
            params.query = filters.search;
        const response = await this.client.get('/api/v1/memories/', { params });
        return response.data;
    }
    /**
     * Update a memory
     */
    async updateMemory(memoryId, payload) {
        const response = await this.client.put(`/api/v1/memories/${memoryId}`, payload);
        return response.data;
    }
    /**
     * Delete a memory (soft delete)
     */
    async deleteMemory(memoryId) {
        await this.client.delete(`/api/v1/memories/${memoryId}`);
        return true;
    }
    // Search Operations
    /**
     * Search memories
     */
    async search(query, limit = 10, semantic = true, keyword = true) {
        const params = { query, limit };
        const response = await this.client.get('/api/v1/search/', { params });
        return response.data;
    }
    // Context Operations
    /**
     * Build context from memories
     */
    async buildContext(query, limit = 5, maxTokens = 2000) {
        const payload = { query, max_memories: limit, max_tokens: maxTokens };
        const response = await this.client.post('/api/v1/memories/context', payload);
        return response.data;
    }
    // Statistics Operations
    /**
     * Get system statistics
     */
    async getStats() {
        const response = await this.client.get('/api/v1/stats/');
        return response.data;
    }
    // Conflict Operations
    /**
     * List conflicts
     */
    async listConflicts(filters = {}) {
        const params = {};
        if (filters.limit !== undefined)
            params.limit = filters.limit;
        if (filters.offset !== undefined)
            params.offset = filters.offset;
        if (filters.resolved !== undefined)
            params.resolved = filters.resolved;
        const response = await this.client.get('/api/v1/conflicts/', { params });
        return response.data;
    }
    /**
     * Detect new conflicts
     */
    async detectConflicts() {
        const response = await this.client.post('/api/v1/conflicts/auto-resolve');
        return response.data;
    }
    /**
     * Resolve a conflict
     */
    async resolveConflict(conflictId) {
        const response = await this.client.post(`/api/v1/conflicts/${conflictId}/resolve`);
        return response.data;
    }
    // Graph Operations
    /**
     * Get the memory graph
     */
    async getGraph() {
        const response = await this.client.get('/api/v1/graph/');
        return response.data;
    }
    /**
     * Create a relationship between memories
     */
    async createRelationship(sourceId, targetId, type, weight = 1.0) {
        const payload = { from_id: sourceId, to_id: targetId, relationship_type: type, strength: weight };
        const response = await this.client.post('/api/v1/graph/relationships', payload);
        return response.data;
    }
    /**
     * Delete a relationship between memories
     */
    async deleteRelationship(sourceId, targetId) {
        await this.client.delete(`/api/v1/graph/relationships/${sourceId}`);
        return true;
    }
    // Health Check
    /**
     * Check if the API server is healthy
     */
    async healthCheck() {
        try {
            await this.client.get('/health');
            return true;
        }
        catch {
            return false;
        }
    }
    /**
     * Get API version information
     */
    async getVersion() {
        const response = await this.client.get('/version');
        return response.data;
    }
}
// Singleton instance
export const api = new NFMApi();
