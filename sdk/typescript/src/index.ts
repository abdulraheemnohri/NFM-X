/**
 * NFM-X TypeScript SDK
 * 
 * Main entry point for the NFM-X TypeScript SDK.
 */

export {
  NFMClient,
  createClient,
  NFMClientConfig,
} from './client';

export type {
  Memory,
  MemoryCreate,
  MemoryUpdate,
  MemoryStatus,
  MemoryType,
  SearchResult,
  SearchResponse,
  Context,
  MemoryStats,
  Conflict,
  ConflictType,
  ConflictSeverity,
  GraphNode,
  GraphEdge,
  GraphData,
  ApiResponse,
  PaginatedResponse,
  ErrorResponse,
} from './models';