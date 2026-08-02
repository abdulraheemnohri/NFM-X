// NFM-X V2 TypeScript Client
import { MemoryV2, SearchRequestV2, SearchResultV2 } from "./models";

export class NFMXClientV2 {
  private baseUrl: string;
  private apiKey: string | undefined;
  private headers: Record<string, string>;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.headers = { "Content-Type": "application/json" };
    if (apiKey) {
      this.headers["Authorization"] = "Bearer " + apiKey;
    }
  }

  async createMemory(content: string, options: any): Promise<any> {
    var url = this.baseUrl + "/api/v2/memory/";
    var body = JSON.stringify({ content: content, ...options });
    var response = await fetch(url, {
      method: "POST",
      headers: this.headers,
      body: body
    });
    if (!response.ok) throw new Error("HTTP error");
    return response.json();
  }
}