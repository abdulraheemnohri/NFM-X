import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Button,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  PieChart as PieChartIcon,
  BarChart as BarChartIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { systemApi, memoryApi } from '../services/api';
import { handleApiError } from '../services/api';
import MemoryTypeChart from '../components/dashboard/MemoryTypeChart';
import ActivityTimeline from '../components/dashboard/ActivityTimeline';
import ConfidenceScoresChart from '../components/dashboard/ConfidenceScoresChart';
import TopTagsChart from '../components/dashboard/TopTagsChart';

function AnalyticsPage({ apiUrl }) {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, [apiUrl]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      import { configureApi } from '../services/api';
      configureApi(apiUrl);
      
      const infoResponse = await systemApi.getInfo();
      setStats(infoResponse.data);
      
      const memoriesResponse = await memoryApi.getAll({ limit: 1000 });
      setMemories(memoriesResponse.data || []);
      
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMemoryTypeDistribution = () => {
    const typeCounts = {};
    memories.forEach(memory => {
      const type = memory.memory_type || 'unknown';
      typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    return Object.entries(typeCounts).map(([type, count]) => ({ type, count }));
  };

  const getConfidenceDistribution = () => {
    const ranges = { '0-0.3': 0, '0.3-0.6': 0, '0.6-0.8': 0, '0.8-1.0': 0 };
    
    memories.forEach(memory => {
      const confidence = memory.confidence || 0;
      if (confidence < 0.3) ranges['0-0.3']++;
      else if (confidence < 0.6) ranges['0.3-0.6']++;
      else if (confidence < 0.8) ranges['0.6-0.8']++;
      else ranges['0.8-1.0']++;
    });
    
    return Object.entries(ranges).map(([range, count]) => ({ range, count }));
  };

  const getTopTags = () => {
    const tagCounts = {};
    memories.forEach(memory => {
      (memory.tags || []).forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });
    return Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([tag, count]) => ({ tag, count }));
  };

  const getActivityByDate = () => {
    const dateCounts = {};
    memories.forEach(memory => {
      if (memory.created_at) {
        const date = new Date(memory.created_at).toISOString().split('T')[0];
        dateCounts[date] = (dateCounts[date] || 0) + 1;
      }
    });
    return Object.entries(dateCounts)
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([date, count]) => ({ date, count }));
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('analytics_title')}
        </Typography>
        <Tooltip title="Refresh Analytics">
          <IconButton onClick={fetchData} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {loading ? (
        <LinearProgress />
      ) : error ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error">{error}</Typography>
          <Button variant="contained" onClick={fetchData} startIcon={<RefreshIcon />}>
            {t('clear')}
          </Button>
        </Paper>
      ) : (
        <Box>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TrendingUpIcon color="primary" sx={{ mr: 1, fontSize: 40 }} />
                    <Typography variant="h6" color="text.secondary">Total Memories</Typography>
                  </Box>
                  <Typography variant="h4" component="div">{memories.length}</Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <PieChartIcon color="success" sx={{ mr: 1, fontSize: 40 }} />
                    <Typography variant="h6" color="text.secondary">Memory Types</Typography>
                  </Box>
                  <Typography variant="h4" component="div">{stats?.memory_types?.length || getMemoryTypeDistribution().length}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title={t('analytics_memory_distribution')} />
                <CardContent>
                  <MemoryTypeChart memoryTypes={getMemoryTypeDistribution()} height={300} />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title={t('analytics_confidence_scores')} />
                <CardContent>
                  <ConfidenceScoresChart data={getConfidenceDistribution()} height={300} />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title={t('analytics_activity_timeline')} />
                <CardContent>
                  <ActivityTimeline data={getActivityByDate()} height={300} />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title={t('analytics_top_tags')} />
                <CardContent>
                  <TopTagsChart data={getTopTags()} height={300} />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
}

export default AnalyticsPage;

// Urdu: NFM-X Analytics Page
// یہ NFM-X کے لیے analytics dashboard page ہے