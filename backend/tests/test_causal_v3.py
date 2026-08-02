"""Tests for NFM-X V3 Causal Graph Visualization"""

import pytest
from backend.app.causal.visualization import CausalGraphVisualizer, CausalGraph


class TestCausalV3:
    def test_create_graph(self):
        """Test creating a causal graph"""
        visualizer = CausalGraphVisualizer()
        graph = visualizer.create_graph("Test Graph")
        
        assert graph.graph_id is not None
        assert graph.name == "Test Graph"
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_add_node(self):
        """Test adding nodes to a graph"""
        visualizer = CausalGraphVisualizer()
        graph = visualizer.create_graph("Test Graph")
        
        node = graph.add_node("node_1", "Node 1", "event", {"color": "red"})
        assert node.id == "node_1"
        assert node.label == "Node 1"
        assert len(graph.nodes) == 1
    
    def test_add_edge(self):
        """Test adding edges to a graph"""
        visualizer = CausalGraphVisualizer()
        graph = visualizer.create_graph("Test Graph")
        
        graph.add_node("node_1", "Node 1")
        graph.add_node("node_2", "Node 2")
        edge = graph.add_edge("node_1", "node_2", "causes", 0.8)
        
        assert edge.source == "node_1"
        assert edge.target == "node_2"
        assert edge.relationship_type == "causes"
        assert len(graph.edges) == 1
    
    def test_export_cytoscape(self):
        """Test exporting to Cytoscape format"""
        visualizer = CausalGraphVisualizer()
        graph = visualizer.create_graph("Test Graph")
        graph.add_node("node_1", "Node 1")
        graph.add_node("node_2", "Node 2")
        graph.add_edge("node_1", "node_2", "causes")
        
        result = graph.to_cytoscape_json()
        
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 2
        assert len(result["edges"]) == 1
    
    def test_export_d3(self):
        """Test exporting to D3 format"""
        visualizer = CausalGraphVisualizer()
        graph = visualizer.create_graph("Test Graph")
        graph.add_node("node_1", "Node 1")
        graph.add_node("node_2", "Node 2")
        graph.add_edge("node_1", "node_2", "causes")
        
        result = graph.to_d3_json()
        
        assert "nodes" in result
        assert "links" in result
        assert len(result["nodes"]) == 2
        assert len(result["links"]) == 1
    
    def test_list_graphs(self):
        """Test listing all graphs"""
        visualizer = CausalGraphVisualizer()
        visualizer.create_graph("Graph 1")
        visualizer.create_graph("Graph 2")
        
        graphs = visualizer.list_graphs()
        assert len(graphs) == 2
    
    def test_get_graph(self):
        """Test getting a specific graph"""
        visualizer = CausalGraphVisualizer()
        graph = visualizer.create_graph("Test Graph")
        
        retrieved = visualizer.get_graph(graph.graph_id)
        assert retrieved is not None
        assert retrieved.graph_id == graph.graph_id
    
    def test_get_nonexistent_graph(self):
        """Test getting a non-existent graph"""
        visualizer = CausalGraphVisualizer()
        
        retrieved = visualizer.get_graph("nonexistent")
        assert retrieved is None