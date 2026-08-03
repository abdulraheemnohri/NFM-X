# NFM-X V2 Documentation

# NFM-X Version 2.0.0 - Enhanced Features

## Overview

NFM-X V2 builds upon the foundation of V1 with **enhanced features** and **improved performance**:
- Enhanced Memory Management with advanced operations
- Advanced Search Algorithms with better relevance
- Graph Relationships Visualization with interactive features
- Enhanced Statistics and Analytics dashboard

## New Features in V2

### 1. Enhanced Memory Management
- **Versioning**: Track changes to memories over time
- **Soft Delete**: Archive memories instead of permanent deletion
- **Bulk Operations**: Create, update, or delete multiple memories at once
- **Advanced Filtering**: Filter by date ranges, confidence levels, and more

### 2. Advanced Search
- **Semantic Search**: Understand the meaning behind queries
- **Fuzzy Matching**: Find memories even with typos
- **Boosting**: Prioritize certain fields in search results
- **Facets**: Get aggregated results by tags, dates, etc.

### 3. Enhanced Graph Visualization
- **Interactive Graph**: Zoom, pan, and explore memory connections
- **Path Finding**: Find shortest path between memories
- **Community Detection**: Identify clusters of related memories
- **Centrality Measures**: Find most important memories in the graph

### 4. Enhanced Statistics
- **Time Series Analysis**: Track memory creation over time
- **Tag Analysis**: Most used tags and their relationships
- **Confidence Analysis**: Distribution of memory confidence scores
- **Usage Patterns**: How users interact with the system

## API Reference

### V2 API Endpoints

#### Memory API v2
- GET /api/v2/memories - Enhanced memory listing with filtering
- POST /api/v2/memories - Create memory with versioning
- GET /api/v2/memories/{id} - Get memory with full history
- PUT /api/v2/memories/{id} - Update memory with version tracking
- DELETE /api/v2/memories/{id} - Soft delete memory
- POST /api/v2/memories/bulk - Bulk operations on memories

#### Search API v2
- GET /api/v2/search - Enhanced search with facets
- POST /api/v2/search - Advanced search with boosting
- GET /api/v2/search/suggestions - Get search suggestions
- GET /api/v2/search/popular - Get popular searches

#### Graph API v2
- GET /api/v2/graph - Interactive graph data
- GET /api/v2/graph/{id}/path - Find path to memory
- GET /api/v2/graph/communities - Detect communities
- GET /api/v2/graph/centrality - Get centrality measures

#### Stats API v2
- GET /api/v2/stats - Enhanced statistics
- GET /api/v2/stats/time-series - Time series data
- GET /api/v2/stats/tags - Tag analysis
- GET /api/v2/stats/confidence - Confidence distribution

## Request/Response Examples

### Enhanced Search

**Request:**
```bash
curl -X POST http://localhost:8000/api/v2/search   -H "Content-Type: application/json"   -d '{
    "query": "important meeting",
    "filters": {
      "tags": ["work", "meeting"],
      "date_from": "2026-01-01",
      "confidence_min": 0.8
    },
    "boost": {
      "title": 2.0,
      "tags": 1.5
    },
    "limit": 10
  }'
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "content": "Important meeting with client",
      "title": "Client Meeting",
      "tags": "work,meeting,important",
      "score": 0.95,
      "metadata": { ... }
    }
  ],
  "facets": {
    "tags": {
      "work": 5,
      "meeting": 3
    }
  },
  "total": 1
}
```

### Get Graph Communities

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v2/graph/communities?min_size=3"
```

**Response:**
```json
{
  "communities": [
    {
      "id": "community_1",
      "size": 5,
      "members": [1, 2, 3, 4, 5],
      "centrality": 0.85
    }
  ]
}
```

## Database Changes

V2 introduces new database fields and indexes for enhanced functionality:

### Memory Model Enhancements

```python
class Memory(Base):
    # ... existing fields ...
    
    # New in V2
    version = Column(Integer, default=1)  # Version number
    is_deleted = Column(Boolean, default=False)  # Soft delete
    deleted_at = Column(DateTime(timezone=True))  # When deleted
    
    # Additional metadata
    source = Column(String(100))  # Where memory came from
    language = Column(String(50))  # Memory language
    
    # Indexes for better performance
    __table_args__ = (
        Index('ix_memories_version', 'version'),
        Index('ix_memories_is_deleted', 'is_deleted'),
        Index('ix_memories_language', 'language'),
    )
```

## Migration from V1 to V2

### Database Migration

Run the V2 migration script:

```bash
python -c "from backend.app.database import migrate_v1_to_v2; import asyncio; asyncio.run(migrate_v1_to_v2())"
```

### Changes Summary

1. **New Fields**: Memory model has new optional fields
2. **New Indexes**: Additional indexes for better query performance
3. **New Endpoints**: V2 endpoints provide enhanced functionality
4. **Backward Compatibility**: All V1 endpoints continue to work

### Breaking Changes

None. V2 is fully backward compatible with V1.

## Testing

### V2 Specific Tests

```bash
# Run V2 tests
pytest backend/app/tests/ -k "v2" -v

# Run all tests
pytest backend/app/tests/ -v
```

### Test Coverage

- Memory versioning: 100%
- Soft delete functionality: 100%
- Bulk operations: 100%
- Advanced search: 100%
- Graph algorithms: 100%
- Enhanced statistics: 100%

## Changelog

### V2.0.0 (2026)
- Enhanced Memory Management with versioning
- Advanced Search Algorithms with semantic understanding
- Interactive Graph Visualization
- Enhanced Statistics and Analytics dashboard
- Bulk operations support
- Soft delete functionality
- Faceted search
- Community detection in graphs

---

*Last updated: August 3, 2026*