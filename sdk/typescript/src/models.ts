export enum MemoryType { TEXT = "TEXT", CONVERSATION = "CONVERSATION", DOCUMENT = "DOCUMENT", CODE = "CODE" }
export enum MemoryStatus { ACTIVE = "ACTIVE", ARCHIVED = "ARCHIVED" }
export interface Memory { id: string; content: string; title?: string; memory_type: MemoryType; status: MemoryStatus; version: number; created_at: string; }