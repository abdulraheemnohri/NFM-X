import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Paper,
  Button,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Graph as GraphIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import ReactForceGraph from 'react-force-graph';
import { graphApi } from '../services/api';
import { handleApiError } from '../services/api';

function GraphPage({ apiUrl }) {
  const { t } = useTranslation();
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [nodeDetailsOpen, setNodeDetailsOpen] = useState(false);
  const graphRef = useRef();

  useEffect(() => {
    fetchGraphData();
  }, [apiUrl]);

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      import { configureApi } from '../services/api';
      configureApi(apiUrl);
      
      const response = await graphApi.query({ query_type: 'full' });
      
      const nodes = response.data?.nodes || [];
      const edges = response.data?.edges || [];
      
      const graphNodes = nodes.map(node => ({
        id: node.id,
        name: node.label,
        nodeType: node.node_type,
        val: 10
      }));
      
      const graphLinks = edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        relationship: edge.relationship,
        weight: edge.weight
      }));
      
      setGraphData({ nodes: graphNodes, links: graphLinks });
      
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
      console.error('Error fetching graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    setNodeDetailsOpen(true);
  };

  const getNodeColor = (node) => {
    const colors = {
      memory: '#1976d2',
      concept: '#4caf50',
      entity: '#ff9800',
      event: '#f44336',
      goal: '#9c27b0',
      action: '#009688',
    };
    return colors[node?.nodeType?.toLowerCase()] || '#9e9e9e';
  };

  return (
    <Box sx={{ flexGrow: 1, position: 'relative' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('graph_title')}
        </Typography>
        <Tooltip title="Refresh Graph">
          <IconButton onClick={fetchGraphData} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {loading ? (
        <LinearProgress />
      ) : error ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error">{error}</Typography>
          <Button variant="contained" onClick={fetchGraphData} startIcon={<RefreshIcon />}>
            {t('clear')}
          </Button>
        </Paper>
      ) : (
        <Paper sx={{ height: 'calc(100vh - 200px)', position: 'relative' }} elevation={2}>
          {graphData.nodes.length > 0 ? (
            <ReactForceGraph
              ref={graphRef}
              graphData={graphData}
              nodeLabel="name"
              nodeAutoColorBy="nodeType"
              nodeColor={getNodeColor}
              onNodeClick={handleNodeClick}
              linkDirectionalArrowLength={6}
              linkDirectionalArrowRelPos={1}
            />
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'text.secondary' }}>
              <Typography>{t('graph_no_nodes')}</Typography>
            </Box>
          )}
        </Paper>
      )}

      <Paper sx={{ p: 2, mt: 2 }} elevation={2}>
        <Typography variant="subtitle2" gutterBottom>
          {t('graph_statistics')}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip label={`${t('graph_nodes')}: ${graphData.nodes.length}`} color="primary" />
          <Chip label={`${t('graph_edges')}: ${graphData.links.length}`} color="secondary" />
        </Box>
      </Paper>

      <Dialog open={nodeDetailsOpen} onClose={() => setNodeDetailsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {t('graph_node_details')}
          <IconButton onClick={() => setNodeDetailsOpen(false)} sx={{ position: 'absolute', right: 8, top: 8 }}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {selectedNode && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedNode.name}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">ID</Typography>
                <Typography>{selectedNode.id}</Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">{t('memory_type')}</Typography>
                <Chip label={selectedNode.nodeType} color="primary" size="small" />
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNodeDetailsOpen(false)} color="primary">Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default GraphPage;

// Urdu: NFM-X Graph Page
// یہ NFM-X کے لیے knowledge graph visualization page ہے