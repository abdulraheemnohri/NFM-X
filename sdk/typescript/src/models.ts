export interface MemoryCreate {
  type: string;
  content: string;
  subtype?: string;
  agent_id?: string;
  source_id?: string;
  confidence?: number;
  importance?: number;
  metadata?: Record<string, any>;
}

export interface MemoryResponse {
  id: string;
  root_id: string;
  version: number;
  type: string;
  content: string;
  normalized_content?: string;
  agent_id?: string;
  source_id?: string;
  confidence: number;
  importance: number;
  status: string;
  created_at: string;
  observed_at?: string;
  valid_from?: string;
  valid_until?: string;
  parent_id?: string;
  metadata?: Record<string, any>;
}

export interface SearchQuery {
  query: string;
  agent_id?: string;
  limit?: number;
  memory_types?: string[];
}

export interface ContextQuery {
  agent_id: string;
  query: string;
  memory_types?: string[];
  max_memories?: number;
}

export interface StatsResponse {
  total_memories: number;
  active_memories: number;
  historical_versions: number;
  total_events: number;
  unresolved_conflicts: number;
  memories_by_type: Record<string, number>;
  avg_confidence: number;
  avg_importance: number;
}
