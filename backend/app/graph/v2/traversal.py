"""NFM-X V2 Graph Traversal - Advanced graph navigation"""

from typing import List, Dict, Set, Optional
from collections import deque
from .relationships import MemoryRelationshipManager, RelationshipType


class GraphTraversalEngine:
    """Implements various graph traversal algorithms for memory exploration"""
    
    def __init__(self, relationship_manager: MemoryRelationshipManager):
        self.relationships = relationship_manager
    
    def bfs(
        self,
        start_id: str,
        max_depth: int = 3,
        relationship_filter: Optional[RelationshipType] = None
    ) -> Dict[str, int]:
        """
        Breadth-First Search traversal
        Returns dict of {memory_id: depth}
        """
        visited = {start_id: 0}
        queue = deque([(start_id, 0)])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
            
            for rel in self.relationships.get_relationships(current_id):
                if relationship_filter and rel.relationship_type != relationship_filter:
                    continue
                
                neighbor_id = rel.target_id
                if neighbor_id not in visited:
                    visited[neighbor_id] = depth + 1
                    queue.append((neighbor_id, depth + 1))
        
        return visited
    
    def dfs(
        self,
        start_id: str,
        max_depth: int = 3,
        relationship_filter: Optional[RelationshipType] = None
    ) -> List[str]:
        """
        Depth-First Search traversal
        Returns list of memory IDs in traversal order
        """
        visited = set()
        result = []
        
        def _dfs(node_id: str, depth: int):
            if node_id in visited or depth > max_depth:
                return
            visited.add(node_id)
            result.append(node_id)
            
            for rel in self.relationships.get_relationships(node_id):
                if relationship_filter and rel.relationship_type != relationship_filter:
                    continue
                _dfs(rel.target_id, depth + 1)
        
        _dfs(start_id, 0)
        return result
    
    def find_shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """Find shortest path between two memories using BFS"""
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            if current_id == end_id:
                return path
            
            if len(path) > max_depth:
                continue
            
            for neighbor_id in self.relationships.get_connected_memories(current_id):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None  # No path found