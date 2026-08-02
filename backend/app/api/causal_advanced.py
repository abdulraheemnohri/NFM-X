"""NFM-X V3 Causal Advanced API
Causal graph visualization and advanced operations"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

from backend.app.causal.visualization import CausalGraphVisualizer

router = APIRouter(prefix="/api/v1/causal", tags=["Causal Advanced"])


class GraphFormat(str, Enum):
    CYTOSCAPE = "cytoscape"
    D3 = "d3"
    VISJS = "visjs"


class GraphNodeRequest(BaseModel):
    node_id: str
    label: str
    node_type: Optional[str] = "event"
    properties: Optional[Dict[str, Any]] = None


class GraphEdgeRequest(BaseModel):
    source: str
    target: str
    relationship_type: str
    weight: Optional[float] = 1.0
    properties: Optional[Dict[str, Any]] = None


class CreateGraphRequest(BaseModel):
    name: str
    nodes: Optional[List[GraphNodeRequest]] = None
    edges: Optional[List[GraphEdgeRequest]] = None


causal_visualizer = CausalGraphVisualizer()


@router.post("/graphs", status_code=201)
async def create_graph(request: CreateGraphRequest):
    graph = causal_visualizer.create_graph(request.name)
    
    if request.nodes:
        for node_req in request.nodes:
            graph.add_node(node_req.node_id, node_req.label, node_req.node_type or "event", node_req.properties or {})
    
    if request.edges:
        for edge_req in request.edges:
            graph.add_edge(edge_req.source, edge_req.target, edge_req.relationship_type, edge_req.weight or 1.0, edge_req.properties or {})
    
    return {"graph_id": graph.graph_id, "name": graph.name, "message": "Graph created successfully"}


@router.get("/graphs")
async def list_graphs():
    return causal_visualizer.list_graphs()


@router.get("/graphs/{graph_id}")
async def get_graph(graph_id: str, format: str = "cytoscape"):
    try:
        graph_data = causal_visualizer.export_graph(graph_id, format)
        return graph_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/graphs/{graph_id}/nodes", status_code=201)
async def add_node(graph_id: str, node: GraphNodeRequest):
    graph = causal_visualizer.get_graph(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail=f"Graph {graph_id} not found")
    
    graph.add_node(node.node_id, node.label, node.node_type or "event", node.properties or {})
    return {"message": "Node added successfully", "node_id": node.node_id}


@router.post("/graphs/{graph_id}/edges", status_code=201)
async def add_edge(graph_id: str, edge: GraphEdgeRequest):
    graph = causal_visualizer.get_graph(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail=f"Graph {graph_id} not found")
    
    graph.add_edge(edge.source, edge.target, edge.relationship_type, edge.weight or 1.0, edge.properties or {})
    return {"message": "Edge added successfully", "source": edge.source, "target": edge.target}