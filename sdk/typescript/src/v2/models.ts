// NFM-X V2 TypeScript SDK Models
export type MemoryModality = any;
export type MemoryStatus = any;
export interface MemoryV2 {
  id: string;
  content: string;
  version: number;
  previous_version_id?: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
  tags: string[];
  status: MemoryStatus;
  modality: MemoryModality;
  source?: string;
  relationships: string[];
}
export interface SearchRequestV2 {
  query: string;
  limit?: number;
  semantic_weight?: number;
  keyword_weight?: number;
  bm25_weight?: number;
  filters?: Record<string, any>;
}
export interface SearchResultV2 {
  memory_id: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
  modality: MemoryModality;
}