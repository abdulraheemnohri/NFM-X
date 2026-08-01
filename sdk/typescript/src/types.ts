/**
 * Type definitions for NFM-X TypeScript SDK
 */

export type MemoryType = 
  | 'working'
  | 'episodic'
  | 'semantic'
  | 'preference'
  | 'project'
  | 'decision'
  | 'procedural'
  | 'skill'
  | 'failure'
  | 'success'
  | 'temporal'
  | 'causal'
  | 'hypothesis'
  | 'conflict'
  | 'source';

export type MemoryStatus = 'active' | 'historical' | 'superseded' | 'invalid';

export type ChangeType = 
  | 'CREATE'
  | 'REINFORCE'
  | 'REFINE'
  | 'EXPAND'
  | 'CORRECT'
  | 'MERGE'
  | 'SPLIT'
  | 'SUPERSEDE'
  | 'CONTRADICT'
  | 'RESTORE'
  | 'DISCOVER';

export interface Memory {
  id: string;
  root_id: string;
  version: number;
  type: MemoryType;
  content: string;
  normalized_content: string;
  status: MemoryStatus;
  confidence: number;
  importance: number;
  created_at: string;
  observed_at: string;
  valid_from: string;
  valid_until: string | null;
  agent_id: string;
  source_id: string;
  parent_id: string | null;
  evidence_ids: string[];
  relationship_ids: string[];
  content_hash: string;
  integrity_hash: string;
  metadata: Record<string, any>;
}

export interface MemoryVersion {
  version: number;
  memory_id: string;
  content: string;
  previous_version: number | null;
  change_type: ChangeType;
  change_reason: string;
  evidence: any[];
  confidence_change: number;
  actor: string;
  timestamp: string;
}

export interface ContextPack {
  task: string;
  current_state: any[];
  relevant_memories: Memory[];
  history: any[];
  preferences: any[];
  constraints: any[];
  decisions: any[];
  skills: any[];
  failures: any[];
  relationships: any[];
  uncertainties: any[];
  conflicts: any[];
  sources: any[];
}

export interface SearchResult {
  results: Memory[];
  total: number;
  scores: number[];
}