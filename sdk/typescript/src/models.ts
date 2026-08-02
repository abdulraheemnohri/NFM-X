/**
 * NFM-X TypeScript SDK Models
 * 
 * Data models for the NFM-X TypeScript SDK.
 */

/** Status of a memory */
export type MemoryStatus = 'ACTIVE' | 'ARCHIVED' | 'DELETED' | 'PENDING';

/** Type of memory */
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

/** Request model for creating a memory */
export interface MemoryCreate {
  content: string;
  title?: string;
  type?: MemoryType;
  tags?: string[];
  source?: string;
  metadata?: Record<string, any>;
}

/** Request model for updating a memory */
export interface MemoryUpdate {
  content?: string;
  title?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

/** Search result */
export interface SearchResult {
  memoryId: string;
  title?: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

/** Search response */
export interface SearchResponse {
  items: SearchResult[];
  total: number;
  query: string;
  semantic: boolean;
  keyword: boolean;
}

/** Built context from memories */
export interface Context {
  context: string;
  memoryIds: string[];
  tokenCount: number;
  query: string;
}

/** Memory statistics */
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

/** Type of conflict */
export type ConflictType = 'DUPLICATE' | 'CONTRADICTION' | 'AMBIGUITY';

/** Severity of a conflict */
export type ConflictSeverity = 'LOW' | 'MEDIUM' | 'HIGH';

/** Conflict entity */
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

/** Graph node */
export interface GraphNode {
  id: string;
  label?: string;
  type: string;
}

/** Graph edge */
export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight: number;
}

/** Graph data */
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  nodeCount: number;
  edgeCount: number;
}

/** API response wrapper */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/** Paginated response */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

/** Error response */
export interface ErrorResponse {
  error: string;
  message: string;
  statusCode: number;
}