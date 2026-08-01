/**
 * Model definitions for NFM-X TypeScript SDK
 */

export interface Agent {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: string;
  type: string;
  reference: string;
  reliability: number;
  metadata: Record<string, any>;
}

export interface Evidence {
  id: string;
  source_id: string;
  memory_id: string;
  confidence: number;
  timestamp: string;
  data: any;
}

export interface Relationship {
  id: string;
  source_id: string;
  target_id: string;
  type: string;
  confidence: number;
  source: string;
  evidence: Evidence[];
  timestamp: string;
  valid_from: string;
  valid_until: string | null;
}

export interface Conflict {
  id: string;
  memory_ids: string[];
  type: string;
  status: 'unresolved' | 'resolved' | 'dismissed';
  detected_at: string;
  resolved_at: string | null;
  resolution: string | null;
}

export interface Pattern {
  id: string;
  name: string;
  description: string;
  supporting_memories: string[];
  confidence: number;
  discovered_at: string;
  validated_at: string | null;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  procedure: any;
  success_count: number;
  failure_count: number;
  conditions: any;
  learned_at: string;
  last_used_at: string | null;
}

export interface Procedure {
  id: string;
  name: string;
  steps: any[];
  success_rate: number;
  execution_count: number;
  version: number;
}

export interface Preference {
  id: string;
  key: string;
  value: any;
  confidence: number;
  evidence: Evidence[];
  last_confirmed: string;
  current_status: string;
  evolution_history: any[];
}

export interface ProjectMemory {
  id: string;
  name: string;
  goals: string[];
  architecture: any;
  technology: string[];
  decisions: any[];
  requirements: any[];
  tasks: any[];
  bugs: any[];
  features: any[];
  constraints: any[];
  files: any[];
  versions: any[];
  milestones: any[];
}