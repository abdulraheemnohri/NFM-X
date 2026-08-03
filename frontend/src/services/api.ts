/**
 * NFM-X API Service
 * 
 * Centralized API service for the NFM-X frontend.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import {
  Context,
  Conflict,
  ConflictFilters,
  GraphData,
  Memory,
  MemoryCreate,
  MemoryFilters,
  MemoryStats,
  MemoryUpdate,
  PaginatedResponse,
  SearchResponse,
} from '../types';

/**
 * NFM-X API Client
 * 
 * Provides methods for interacting with the NFM-X backend API.
 */
export class NFMApi {
  private client: AxiosInstance;

  constructor(baseURL: string = import.meta.env.VITE_API_URL || 'http://localhost:8000') {
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
  async createMemory(payload: MemoryCreate): Promise<Memory> {
    const response = await this.client.post<Memory>('/api/v1/memories/', payload);
    return response.data;
  }

  /**
   * Get a specific memory by ID
   */
  async getMemory(memoryId: string): Promise<Memory> {
    const response = await this.client.get<Memory>(`/api/v1/memories/${memoryId}`);
    return response.data;
  }

  /**
   * List memories with pagination and filters
   */
  async listMemories(filters: MemoryFilters = {}): Promise<PaginatedResponse<Memory>> {
    const params: any = {};
    if (filters.limit !== undefined) params.limit = filters.limit;
    if (filters.offset !== undefined) params.offset = filters.offset;
    if (filters.status) params.status = filters.status;
    if (filters.tags) params.tags = filters.tags.join(',');
    if (filters.search) params.query = filters.search;

    const response = await this.client.get<PaginatedResponse<Memory>>(
      '/api/v1/memories/',
      { params }
    );
    return response.data;
  }

  /**
   * Update a memory
   */
  async updateMemory(memoryId: string, payload: MemoryUpdate): Promise<Memory> {
    const response = await this.client.put<Memory>(
      `/api/v1/memories/${memoryId}`,
      payload
    );
    return response.data;
  }

  /**
   * Delete a memory (soft delete)
   */
  async deleteMemory(memoryId: string): Promise<boolean> {
    await this.client.delete(`/api/v1/memories/${memoryId}`);
    return true;
  }

  // Search Operations

  /**
   * Search memories
   */
  async search(
    query: string,
    limit: number = 10,
    semantic: boolean = true,
    keyword: boolean = true
  ): Promise<SearchResponse> {
    const params = { query, limit };
    const response = await this.client.get<SearchResponse>('/api/v1/search/', { params });
    return response.data;
  }

  // Context Operations

  /**
   * Build context from memories
   */
  async buildContext(
    query: string,
    limit: number = 5,
    maxTokens: number = 2000
  ): Promise<Context> {
    const payload = { query, max_memories: limit, max_tokens: maxTokens };
    const response = await this.client.post<Context>('/api/v1/memories/context', payload);
    return response.data;
  }

  // Statistics Operations

  /**
   * Get system statistics
   */
  async getStats(): Promise<MemoryStats> {
    const response = await this.client.get<MemoryStats>('/api/v1/stats/');
    return response.data;
  }

  // Conflict Operations

  /**
   * List conflicts
   */
  async listConflicts(filters: ConflictFilters = {}): Promise<PaginatedResponse<Conflict>> {
    const params: any = {};
    if (filters.limit !== undefined) params.limit = filters.limit;
    if (filters.offset !== undefined) params.offset = filters.offset;
    if (filters.resolved !== undefined) params.resolved = filters.resolved;

    const response = await this.client.get<PaginatedResponse<Conflict>>(
      '/api/v1/conflicts/',
      { params }
    );
    return response.data;
  }

  /**
   * Detect new conflicts
   */
  async detectConflicts(): Promise<{ count: number }> {
    const response = await this.client.post<{ count: number }>('/api/v1/conflicts/auto-resolve');
    return response.data;
  }

  /**
   * Resolve a conflict
   */
  async resolveConflict(conflictId: string): Promise<Conflict> {
    const response = await this.client.post<Conflict>(
      `/api/v1/conflicts/${conflictId}/resolve`
    );
    return response.data;
  }

  // Graph Operations

  /**
   * Get the memory graph
   */
  async getGraph(): Promise<GraphData> {
    const response = await this.client.get<GraphData>('/api/v1/graph/');
    return response.data;
  }

  /**
   * Create a relationship between memories
   */
  async createRelationship(
    sourceId: string,
    targetId: string,
    type: string,
    weight: number = 1.0
  ): Promise<any> {
    const payload = { from_id: sourceId, to_id: targetId, relationship_type: type, strength: weight };
    const response = await this.client.post('/api/v1/graph/relationships', payload);
    return response.data;
  }

  /**
   * Delete a relationship between memories
   */
  async deleteRelationship(sourceId: string, targetId: string): Promise<boolean> {
    await this.client.delete(`/api/v1/graph/relationships/${sourceId}`);
    return true;
  }

  // Health Check

  /**
   * Check if the API server is healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get API version information
   */
  async getVersion(): Promise<Record<string, string>> {
    const response = await this.client.get<Record<string, string>>('/version');
    return response.data;
  }
}

// Singleton instance
export const api = new NFMApi();