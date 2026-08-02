/**
 * NFM-X Frontend Types
 * 
 * Type definitions for the NFM-X frontend application.
 */

// Memory Types
export type MemoryStatus = 'ACTIVE' | 'ARCHIVED' | 'DELETED' | 'PENDING';
export type MemoryType = 'TEXT' | 'IMAGE' | 'AUDIO' | 'VIDEO' | 'DOCUMENT';

/** Memory entity */
export interface Memory {
  id: string;
  content: string;
  title?: string;
  type: MemoryType;
  status: MemoryStatus;
  tags: string[];
  source?: string;
  metadata: Record<string, any>;
  version: number;
  parentId?: string;
  createdAt: string;
  updatedAt: string;
}

/** Memory create payload */
export interface MemoryCreate {
  content: string;
  title?: string;
  type?: MemoryType;
  tags?: string[];
  source?: string;
  metadata?: Record<string, any>;
}

/** Memory update payload */
export interface MemoryUpdate {
  content?: string;
  title?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

// Search Types
export interface SearchResult {
  memoryId: string;
  title?: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

export interface SearchResponse {
  items: SearchResult[];
  total: number;
  query: string;
  semantic: boolean;
  keyword: boolean;
}

// Context Types
export interface Context {
  context: string;
  memoryIds: string[];
  tokenCount: number;
  query: string;
}

// Statistics Types
export interface MemoryStats {
  totalMemories: number;
  activeMemories: number;
  archivedMemories: number;
  deletedMemories: number;
  totalVersions: number;
  avgMemorySize: number;
  totalStorageSize: number;
  lastUpdated?: string;
  mostUsedTags: Record<string, number>;
}

// Conflict Types
export type ConflictType = 'DUPLICATE' | 'CONTRADICTION' | 'AMBIGUITY';
export type ConflictSeverity = 'LOW' | 'MEDIUM' | 'HIGH';

export interface Conflict {
  id: string;
  type: ConflictType;
  severity: ConflictSeverity;
  description: string;
  memoryIds: string[];
  detectedAt: string;
  resolved: boolean;
  resolvedAt?: string;
}

// Graph Types
export interface GraphNode {
  id: string;
  label?: string;
  type: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  nodeCount: number;
  edgeCount: number;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

// Filter Types
export interface MemoryFilters {
  limit?: number;
  offset?: number;
  status?: MemoryStatus;
  tags?: string[];
  search?: string;
}

export interface ConflictFilters {
  limit?: number;
  offset?: number;
  resolved?: boolean;
}

// UI State Types
export interface UIState {
  loading: boolean;
  error: string | null;
  lastUpdated: number;
}

// App Configuration
export interface AppConfig {
  apiBaseUrl: string;
  apiKey?: string;
  debug: boolean;
}