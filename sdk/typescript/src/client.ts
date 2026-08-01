/**
 * NFM-X Client for TypeScript
 */

import axios, { AxiosInstance } from 'axios';
import { Memory, ContextPack, SearchResult, MemoryVersion } from './types';

export interface NFMClientConfig {
  baseURL: string;
  apiKey?: string;
  timeout?: number;
}

export class NFMClient {
  private client: AxiosInstance;
  private config: NFMClientConfig;

  constructor(config: NFMClientConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { Authorization: `Bearer ${config.apiKey}` }),
      },
    });
  }

  async createMemory(memory: any): Promise<Memory> {
    const response = await this.client.post('/v1/memory', memory);
    return response.data;
  }

  async getMemory(id: string): Promise<Memory> {
    const response = await this.client.get(`/v1/memory/${id}`);
    return response.data;
  }

  async searchMemories(query: string, options?: { limit?: number; filters?: any }): Promise<SearchResult> {
    const response = await this.client.post('/v1/memory/search', {
      query,
      limit: options?.limit || 10,
      filters: options?.filters || {},
    });
    return response.data;
  }

  async getContext(agentId: string, query: string, task?: string): Promise<ContextPack> {
    const response = await this.client.post('/v1/memory/context', {
      agent_id: agentId,
      query,
      task: task || '',
    });
    return response.data;
  }

  async captureExperience(data: {
    agentId: string;
    userInput: string;
    aiOutput: string;
    tools?: any[];
    toolResults?: any[];
    files?: any[];
    taskResult?: string;
  }): Promise<any> {
    const response = await this.client.post('/v1/memory/experience', {
      agent_id: data.agentId,
      user_input: data.userInput,
      ai_output: data.aiOutput,
      tools: data.tools || [],
      tool_results: data.toolResults || [],
      files: data.files || [],
      task_result: data.taskResult || '',
    });
    return response.data;
  }

  async evolveMemory(memoryId: string, newContent: string, reason: string): Promise<Memory> {
    const response = await this.client.post(`/v1/memory/${memoryId}/evolve`, {
      new_content: newContent,
      change_reason: reason,
    });
    return response.data;
  }

  async confirmMemory(memoryId: string): Promise<Memory> {
    const response = await this.client.post(`/v1/memory/${memoryId}/confirm`);
    return response.data;
  }

  async contradictMemory(memoryId: string, contradictingContent: string, evidence: any[] = []): Promise<any> {
    const response = await this.client.post(`/v1/memory/${memoryId}/contradict`, {
      contradicting_content: contradictingContent,
      evidence,
    });
    return response.data;
  }

  async getMemoryHistory(memoryId: string): Promise<MemoryVersion[]> {
    const response = await this.client.get(`/v1/memory/${memoryId}/history`);
    return response.data.versions;
  }

  async getMemoryLineage(memoryId: string): Promise<any> {
    const response = await this.client.get(`/v1/memory/${memoryId}/lineage`);
    return response.data;
  }

  async getMemoryEvidence(memoryId: string): Promise<any> {
    const response = await this.client.get(`/v1/memory/${memoryId}/evidence`);
    return response.data;
  }

  async getGraph(limit?: number, nodeType?: string): Promise<any> {
    const params: any = {};
    if (limit) params.limit = limit;
    if (nodeType) params.type = nodeType;
    const response = await this.client.get('/v1/graph', { params });
    return response.data;
  }

  async getStats(): Promise<any> {
    const response = await this.client.get('/v1/stats');
    return response.data;
  }

  async createBackup(name: string, encrypted: boolean = false): Promise<any> {
    const response = await this.client.post('/v1/backup', {
      backup_name: name,
      encrypted,
    });
    return response.data;
  }

  async restoreBackup(name: string): Promise<any> {
    const response = await this.client.post('/v1/restore', {
      backup_name: name,
    });
    return response.data;
  }

  async consolidate(): Promise<any> {
    const response = await this.client.post('/v1/consolidate');
    return response.data;
  }

  async chat(agentId: string, message: string, options?: any): Promise<string> {
    const context = await this.getContext(agentId, message);
    return `Response based on context: ${JSON.stringify(context)}`;
  }
}

export default NFMClient;