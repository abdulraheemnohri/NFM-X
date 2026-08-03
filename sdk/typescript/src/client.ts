/**
 * NFM-X TypeScript SDK Client
 * 
 * Async client for interacting with NFM-X API.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import {
  Context,
  Conflict,
  GraphData,
  Memory,
  MemoryCreate,
  MemoryStats,
  MemoryUpdate,
  PaginatedResponse,
  SearchResponse,
} from './models';

/** Configuration options for the NFM-X client */
export interface NFMClientConfig {
  baseURL?: string;
  apiKey?: string;
  timeout?: number;
}

/** NFM-X TypeScript Client */
export class NFMClient {
  private client: AxiosInstance;
  private config: NFMClientConfig;

  /**
   * Create a new NFM-X client.
   * 
   * @param config - Client configuration
   */
  constructor(config: NFMClientConfig = {}) {
    this.config = {
      baseURL: 'http://localhost:8000',
      timeout: 30000,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'User-Agent': 'NFM-X-TypeScript-SDK/1.5.0',
        ...(this.config.apiKey ? { Authorization: `Bearer ${this.config.apiKey}` } : {}),
      },
    });
  }

  /**
   * Make an HTTP request to the API.
   */
  private async request<T>(
    method: 'get' | 'post' | 'put' | 'delete' | 'patch',
    path: string,
    data?: any,
    params?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    try {
      const response = await this.client.request<T>({
        method,
        url: path,
        data,
        params,
        ...config,
      });
      return response;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          `API Error: ${error.response?.status} - ${error.response?.data?.message || error.message}`
        );
      }
      throw error;
    }
  }

  // Memory Operations

  /**
   * Create a new memory.
   */
  async createMemory(payload: MemoryCreate): Promise<Memory> {
    const response = await this.request<Memory>('post', '/api/memorie
s', payload);
    return response.data;
  }

  /**
   * Get a specific memory by ID.
   */
  async getMemory(memoryId: string): Promise<Memory> {
    const response = await this.request<Memory>('get', `/api/v1/memories/${memoryId}`);
    return response.data;
  }

  /**
   * List memories with pagination.
   */
  async listMemories(
    limit: number = 10,
    offset: number = 0,
    status?: string,
    tags?: string[]
  ): Promise<PaginatedResponse<Memory>> {
    const params: any = { limit, offset };
    if (status) params.status = status;
    if (tags) params.tags = tags.join(',');

    const response = await this.request<PaginatedResponse<Memory>>(
      'get',
      '/api/v1/memories',
      undefined,
      params
    );
    return response.data;
  }

  /**
   * Update a memory.
   */
  async updateMemory(memoryId: string, payload: MemoryUpdate): Promise<Memory> {
    const response = await this.request<Memory>(
      'put',
      `/api/v1/memories/${memoryId}`,
      payload
    );
    return response.data;
  }

  /**
   * Delete a memory (soft delete).
   */
  async deleteMemory(memoryId: string): Promise<boolean> {
    await this.request('delete', `/api/v1/memories/${memoryId}`);
    return true;
  }

  // Search Operations

  /**
   * Search memories.
   */
  async search(
    query: string,
    limit: number = 10,
    semantic: boolean = true,
    keyword: boolean = true
  ): Promise<SearchResponse> {
    const params = { q: query, limit, semantic, keyword };
    const response = await this.request<SearchResponse>(
      'get',
      '/api/v1/search',
      undefined,
      params
    );
    return response.data;
  }

  // Context Operations

  /**
   * Build context from memories.
   */
  async buildContext(
    query: string,
    limit: number = 5,
    maxTokens: number = 2000
  ): Promise<Context> {
    const params = { query, limit, max_tokens: maxTokens };
    const response = await this.request<Context>('get', '/api/v1/context', undefined, params);
    return respon
se.data;
  }

  // Statistics Operations

  /**
   * Get system statistics.
   */
  async getStats(): Promise<MemoryStats> {
    const response = await this.request<MemoryStats>('get', '/api/stats');
    return response.data;
  }

  // Conflict Operations

  /**
   * List conflicts.
   */
  async listConflicts(
    limit: number = 10,
    offset: number = 0,
    resolved?: boolean
  ): Promise<PaginatedResponse<Conflict>> {
    const params: any = { limit, offset };
    if (resolved !== undefined) params.resolved = resolved;

    const response = await this.request<PaginatedResponse<Conflict>>(
      'get',
      '/api/v1/conflicts',
      undefined,
      params
    );
    return response.data;
  }

  /**
   * Detect new conflicts.
   */
  async detectConflicts(): Promise<{ count: number }> {
    const response = await this.request<{ count: number }>('post', '/api/v1/conflicts/detect');
    return response.data;
  }

  /**
   * Resolve a conflict.
   */
  async resolveConflict(conflictId: string): Promise<Conflict> {
    const response = await this.request<Conflict>(
      'post',
      `/api/v1/conflicts/${conflictId}/resolve`
    );
    return response.data;
  }

  // Graph Operations

  /**
   * Get the memory graph.
   */
  async getGraph(): Promise<GraphData> {
    const response = await this.request<GraphData>('get', '/api/v1/graph');
    return response.data;
  }

  /**
   * Create a relationship between memories.
   */
  async createRelationship(
    sourceId: string,
    targetId: string,
    type: string,
    weight: number = 1.0
  ): Promise<any> {
    const payload = { source_id: sourceId, target_id: targetId, type, weight };
    const response = await this.request('post', '/api/v1/graph/relationships', payload);
    return response.data;
  }

  /**
   * Delete a relationship between memories.
   */
  async deleteRelationship(sourceId: string, targetId: string): Promise<boolean> {
    await this.request('delete', `/api/v1/graph/relationships/${sourceId}/${targetId}`);
  
  return true;
  }

  // Health Check

  /**
   * Check if the API server is healthy.
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.request('get', '/health');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get API version information.
   */
  async getVersion(): Promise<Record<string, string>> {
    const response = await this.request<Record<string, string>>('get', '/version');
    return response.data;
  }
}

/**
 * Create a new NFM-X client with default configuration.
 */
export function createClient(config?: NFMClientConfig): NFMClient {
  return new NFMClient(config);
}

export default NFMClient;