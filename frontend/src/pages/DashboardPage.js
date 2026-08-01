import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  Button,
  Chip,
  LinearProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Memory as MemoryIcon,
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as AccessTimeIcon,
  Add as AddIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { systemApi, memoryApi } from '../services/api';
import { handleApiError } from '../services/api';
import MemoryTypeChart from '../components/dashboard/MemoryTypeChart';
import RecentActivity from '../components/dashboard/RecentActivity';
import QuickActions from '../components/dashboard/QuickActions';

function DashboardPage({ apiUrl }) {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recentMemories, setRecentMemories] = useState([]);

  useEffect(() => {
    fetchData();
  }, [apiUrl]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Configure API URL
      import { configureApi } from '../services/api';
      configureApi(apiUrl);
      
      // Fetch system info
      const infoResponse = await systemApi.getInfo();
      setStats(infoResponse.data);
      
      // Fetch recent memories
      const memoriesResponse = await memoryApi.getAll({ limit: 5 });
      setRecentMemories(memoriesResponse.data || []);
      
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMemoryTypeColor = (type) => {
    const colors = {
      episodic: '#FF6B6B',
      semantic: '#4ECDC4',
      procedural: '#45B7D1',
      preference: '#96CEB4',
      decision: '#FFEAA7',
      failure: '#DDDDDD',
      success: '#2ECC71',
      temporal: '#9B59B6',
      causal: '#3498DB',
      hypothesis: '#F39C12',
      conflict: '#E74C3C',
      multimodal: '#1ABC9C',
    };
    return colors[type?.toLowerCase()] || '#95A5A6';
  };

  const formatDate = (dateString) => {
    if (!dateString) return t('time_just_now');
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    const intervals = {
      year: 31536000,
      month: 2592000,
      week: 604800,
      day: 86400,
      hour: 3600,
      minute: 60
    };
    
    for (const [unit, seconds] of Object.entries(intervals)) {
      const interval = Math.floor(diffInSeconds / seconds);
      if (interval >= 1) {
        return t(`time_${unit}s_ago`, { count: interval });
      }
    }
    
    return t('time_just_now');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <LinearProgress sx={{ width: '100%' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="error">{error}</Typography>
        <Button variant="contained" onClick={fetchData} startIcon={<RefreshIcon />}>
          {t('clear')}
        </Button>
      </Paper>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('dashboard_title')}
        </Typography>
        <Tooltip title={t('tooltip_search')}>
          <Button 
            variant="contained" 
            color="primary" 
            component={Link} 
            to="/memories/create"
            startIcon={<AddIcon />}
          >
            {t('memories_create')}
          </Button>
        </Tooltip>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <MemoryIcon />
                </Avatar>
                <Typography variant="h6" color="text.secondary">
                  {t('dashboard_total_memories')}
                </Typography>
              </Box>
              <Typography variant="h4" component="div">
                {stats?.total_memories || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <TrendingUpIcon />
                </Avatar>
                <Typography variant="h6" color="text.secondary">
                  {t('dashboard_memory_types')}
                </Typography>
              </Box>
              <Typography variant="h4" component="div">
                {stats?.memory_types?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                  <SearchIcon />
                </Avatar>
                <Typography variant="h6" color="text.secondary">
                  API Status
                </Typography>
              </Box>
              <Chip 
                label={stats?.status || 'Unknown'} 
                color={stats?.status === 'healthy' ? 'success' : 'error'}
                size="medium"
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <AccessTimeIcon />
                </Avatar>
                <Typography variant="h6" color="text.secondary">
                  Uptime
                </Typography>
              </Box>
              <Typography variant="body2" component="div">
                {stats?.uptime || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Memory Type Distribution */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardHeader title={t('dashboard_memory_types')} />
            <CardContent>
              {stats?.memory_types ? (
                <MemoryTypeChart memoryTypes={stats.memory_types} />
              ) : (
                <Typography>{t('memories_empty')}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardHeader 
              title={t('dashboard_recent_activity')} 
              action={
                <Tooltip title="Refresh">
                  <IconButton onClick={fetchData}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              <RecentActivity memories={recentMemories} formatDate={formatDate} />
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card elevation={3} sx={{ mt: 3 }}>
            <CardHeader title={t('dashboard_quick_actions')} />
            <CardContent>
              <QuickActions />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage;

// Urdu: NFM-X Dashboard Page
// یہ NFM-X کے لیے main dashboard page ہے
// اس میں:
// - Statistics cards
// - Memory type distribution chart
// - Recent activity list
// - Quick actions
// - API integration
// - Urdu/English support