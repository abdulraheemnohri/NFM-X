import { MemoryCreate, MemoryResponse, SearchQuery, ContextQuery, StatsResponse } from "./models";

export class NFMClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;

  constructor(options: { baseUrl?: string; apiKey?: string; timeout?: number } = {}) {
    this.baseUrl = (options.baseUrl !== undefined ? options.baseUrl : "http://localhost:8765").replace(/\/$/, "");
    this.apiKey = options.apiKey;
    this.timeout = options.timeout || 30000;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: any,
    params?: Record<string, any>
  ): Promise<T> {
    const url = new URL(this.baseUrl + path);
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) url.searchParams.append(k, String(v));
      });
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
      clearTimeout(timer);

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`API error ${response.status}: ${text}`);
      }
      return await response.json();
    } catch (error) {
      clearTimeout(timer);
      throw error;
    }
  }

  async createMemory(memory: MemoryCreate): Promise<MemoryResponse> {
    return this.request<MemoryResponse>("POST", "/v1/memory/", memory);
  }

  async getMemory(memoryId: string): Promise<MemoryResponse> {
    return this.request<MemoryResponse>("GET", `/v1/memory/${memoryId}`);
  }

  async listMemories(params?: {
    agent_id?: string;
    memory_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ memories: MemoryResponse[]; total: number; limit: number; offset: number }> {
    return this.request("GET", "/v1/memory/", undefined, params);
  }

  async search(query: SearchQuery): Promise<any> {
    return this.request("POST", "/v1/memory/search", query);
  }

  async getContext(query: ContextQuery): Promise<any> {
    return this.request("POST", "/v1/memory/context", query);
  }

  async getHistory(memoryId: string): Promise<any> {
    return this.request("GET", `/v1/memory/${memoryId}/history`);
  }

  async getStats(): Promise<StatsResponse> {
    return this.request<StatsResponse>("GET", "/v1/stats");
  }

  async health(): Promise<any> {
    return this.request("GET", "/health");
  }
}
