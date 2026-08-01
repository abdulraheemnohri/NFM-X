import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  LinearProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Memory as MemoryIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { searchApi } from '../services/api';
import { handleApiError } from '../services/api';

function SearchPage({ apiUrl }) {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [strategy, setStrategy] = useState('hybrid');
  const [limit, setLimit] = useState(10);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [memoryTypes, setMemoryTypes] = useState([]);

  const searchStrategies = ['semantic', 'keyword', 'temporal', 'graph', 'hybrid'];
  
  const allMemoryTypes = [
    'episodic', 'semantic', 'procedural', 'preference', 
    'decision', 'failure', 'success', 'temporal', 
    'causal', 'hypothesis', 'conflict', 'multimodal'
  ];

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      import { configureApi } from '../services/api';
      configureApi(apiUrl);
      
      const searchData = {
        query,
        strategy,
        limit,
        ...(memoryTypes.length > 0 && { memory_types: memoryTypes })
      };
      
      const response = await searchApi.search(searchData);
      setResults(response.data || []);
      
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
      console.error('Error searching memories:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('search_title')}
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }} elevation={2} component="form" onSubmit={handleSearch}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField
            fullWidth
            label={t('search_placeholder')}
            variant="outlined"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            InputProps={{ startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} /> }}
            required
          />
          <Button type="submit" variant="contained" color="primary" size="large" startIcon={<SearchIcon />} disabled={loading || !query.trim()}>
            {t('search')}
          </Button>
        </Box>
      </Paper>
      {loading && <LinearProgress />}
      {error && <Paper sx={{ p: 2, mb: 2, backgroundColor: 'error.light' }}><Typography color="error">{error}</Typography></Paper>}
      {results.length > 0 && <Paper sx={{ p: 2 }} elevation={2}><Typography variant="h6" gutterBottom>{t('search_results')} ({results.length})</Typography></Paper>}
    </Box>
  );
}

export default SearchPage;

// Urdu: NFM-X Search Page
// یہ NFM-X کے لیے search page ہے