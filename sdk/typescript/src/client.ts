import axios from "axios";
export class NFMClient {
  constructor(private baseUrl: string = "http://localhost:8000") {}
  async createMemory(data: any) { return (await axios.post(this.baseUrl + "/v1/memory/", data)).data; }
  async getMemory(id: string) { return (await axios.get(this.baseUrl + "/v1/memory/" + id)).data; }
}