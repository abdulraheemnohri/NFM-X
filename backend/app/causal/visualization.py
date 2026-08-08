"""NFM-X V3 Causal Graph Visualization
Generates JSON representations of causal graphs for frontend rendering"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    id: str
    label: str
    node_type: str = "event"
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "type": self.node_type,
            "properties": self.properties
        }


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str
    relationship_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "type": self.relationship_type,
            "weight": self.weight,
            "properties": self.properties
        }


@dataclass
class CausalGraph:
    graph_id: str
    name: str
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_node(self, node_id: str, label: str, node_type: str = "event", properties: Optional[Dict] = None):
        node = GraphNode(id=node_id, label=label, node_type=node_type, properties=properties or {})
        self.nodes.append(node)
        return node
    
    def add_edge(self, source: str, target: str, relationship_type: str, weight: float = 1.0, properties: Optional[Dict] = None):
        edge = GraphEdge(
            id=str(uuid.uuid4()),
            source=source,
            target=target,
            relationship_type=relationship_type,
            weight=weight,
            properties=properties or {}
        )
        self.edges.append(edge)
        return edge
    
    def to_cytoscape_json(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges]
        }
    
    def to_d3_json(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "name": n.label, **n.properties} for n in self.nodes],
            "links": [{"source": e.source, "target": e.target, "value": e.weight, **e.properties} for e in self.edges]
        }
    
    def to_visjs_json(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "label": n.label, "title": str(n.properties), "group": n.node_type} for n in self.nodes],
            "edges": [{"from": e.source, "to": e.target, "title": e.relationship_type, "value": e.weight} for e in self.edges]
        }


class CausalGraphVisualizer:
    def __init__(self):
        self.graphs: Dict[str, CausalGraph] = {}
    
    def create_graph(self, name: str) -> CausalGraph:
        graph = CausalGraph(graph_id=str(uuid.uuid4()), name=name)
        self.graphs[graph.graph_id] = graph
        return graph
    
    def get_graph(self, graph_id: str) -> Optional[CausalGraph]:
        return self.graphs.get(graph_id)
    
    def export_graph(self, graph_id: str, format_type: str = "cytoscape") -> Dict[str, Any]:
        graph = self.graphs.get(graph_id)
        if not graph:
            raise ValueError(f"Graph not found: {graph_id}")
        
        if format_type == "cytoscape":
            return graph.to_cytoscape_json()
        elif format_type == "d3":
            return graph.to_d3_json()
        elif format_type == "visjs":
            return graph.to_visjs_json()
        else:
            return graph.to_cytoscape_json()
    
    def list_graphs(self) -> List[Dict[str, Any]]:
        return [
            {
                "graph_id": g.graph_id,
                "name": g.name,
                "created_at": g.created_at.isoformat(),
                "node_count": len(g.nodes),
                "edge_count": len(g.edges)
            }
            for g in self.graphs.values()
        ]