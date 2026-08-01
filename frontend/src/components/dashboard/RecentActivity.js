import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  Typography,
  Box,
  Divider
} from '@mui/material';
import {
  Memory as MemoryIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';

function RecentActivity({ memories, formatDate }) {
  const { t } = useTranslation();

  const getMemoryTypeColor = (type) => {
    const colors = {
      episodic: 'error',
      semantic: 'info',
      procedural: 'primary',
      preference: 'success',
      decision: 'warning',
      failure: 'default',
      success: 'success',
      temporal: 'secondary',
      causal: 'primary',
      hypothesis: 'warning',
      conflict: 'error',
      multimodal: 'info',
    };
    return colors[type?.toLowerCase()] || 'default';
  };

  const getMemoryTypeLabel = (type) => {
    return t('memory_type_' + (type?.toLowerCase() || 'unknown'));
  };

  if (!memories || memories.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        {t('memories_empty')}
      </Typography>
    );
  }

  return (
    <List dense>
      {memories.map((memory, index) => (
        <React.Fragment key={memory.id}>
          <ListItem>
            <ListItemAvatar>
              <Avatar sx={{ bgcolor: getMemoryTypeColor(memory.memory_type) }}>
                <MemoryIcon fontSize="small" />
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip label={getMemoryTypeLabel(memory.memory_type)} color={getMemoryTypeColor(memory.memory_type)} size="small" />
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(memory.created_at)}
                  </Typography>
                </Box>
              }
              secondary={memory.content}
            />
          </ListItem>
          {index < memories.length - 1 && <Divider component="li" />}
        </React.Fragment>
      ))}
    </List>
  );
}

export default RecentActivity;

// Urdu: NFM-X Recent Activity