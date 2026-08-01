import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Button, Grid, Paper, Typography } from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Memory as MemoryIcon,
  Graph as GraphIcon
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

function QuickActions() {
  const { t } = useTranslation();

  const actions = [
    {
      title: t('quick_create_memory'),
      icon: <AddIcon />,
      to: '/memories/create',
      color: 'primary'
    },
    {
      title: t('quick_search'),
      icon: <SearchIcon />,
      to: '/search',
      color: 'secondary'
    },
    {
      title: t('quick_view_graph'),
      icon: <GraphIcon />,
      to: '/graph',
      color: 'info'
    },
    {
      title: t('quick_view_memories'),
      icon: <MemoryIcon />,
      to: '/memories',
      color: 'success'
    }
  ];

  return (
    <Grid container spacing={2}>
      {actions.map((action, index) => (
        <Grid item xs={6} sm={3} key={index}>
          <Button
            component={Link}
            to={action.to}
            variant="outlined"
            color={action.color}
            fullWidth
            startIcon={action.icon}
            sx={{ height: '100%' }}
          >
            <Typography variant="body2" noWrap>
              {action.title}
            </Typography>
          </Button>
        </Grid>
      ))}
    </Grid>
  );
}

export default QuickActions;

// Urdu: NFM-X Quick Actions
// یہ tezi actions ke liye component hai