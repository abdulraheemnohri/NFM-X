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
  Autocomplete,
  Checkbox,
  ListItemText
} from '@mui/material';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { memoryApi } from '../../services/api';
import { handleApiError } from '../../services/api';

function MemoryForm({ onSubmit, onCancel, initialData = null, apiUrl }) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    content: initialData?.content || '',
    memory_type: initialData?.memory_type || 'episodic',
    tags: initialData?.tags || [],
    confidence: initialData?.confidence || 0.8,
    source: initialData?.source || ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const memoryTypes = [
    'episodic', 'semantic', 'procedural', 'preference', 
    'decision', 'failure', 'success', 'temporal', 
    'causal', 'hypothesis', 'conflict', 'multimodal'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleTagsChange = (event, newValue) => {
    setFormData(prev => ({ ...prev, tags: newValue }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      
      import { configureApi } from '../../services/api';
      configureApi(apiUrl);
      
      const submitData = { ...formData };
      
      if (onSubmit) {
        await onSubmit(submitData);
      } else {
        await memoryApi.create(submitData);
      }
      
      // Reset form if creating new memory
      if (!initialData) {
        setFormData({
          content: '',
          memory_type: 'episodic',
          tags: [],
          confidence: 0.8,
          source: ''
        });
      }
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
      console.error('Error submitting memory:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }} elevation={2} component="form" onSubmit={handleSubmit}>
      <Typography variant="h6" gutterBottom>
        {initialData ? t('memory_edit') : t('memory_create')}
      </Typography>

      {error && (
        <Typography color="error" paragraph>
          {error}
        </Typography>
      )}

      <TextField
        fullWidth
        label={t('memory_content')}
        name="content"
        value={formData.content}
        onChange={handleChange}
        multiline
        rows={4}
        margin="normal"
        required
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>{t('memory_type')}</InputLabel>
        <Select
          name="memory_type"
          value={formData.memory_type}
          onChange={handleChange}
          label={t('memory_type')}
        >
          {memoryTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {t('memory_type_' + type)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Autocomplete
        multiple
        options={[]}
        freeSolo
        value={formData.tags}
        onChange={handleTagsChange}
        renderTags={(value, getTagProps) =>
          value.map((option, index) => (
            <Chip label={option} {...getTagProps({ index })} />
          ))
        }
        renderInput={(params) => (
          <TextField 
            {...params} 
            label={t('memory_tags')} 
            placeholder="Add tags" 
            margin="normal"
          />
        )}
        renderOption={(props, option) => (
          <li {...props}>
            <Checkbox checked={formData.tags.indexOf(option) > -1} />
            <ListItemText primary={option} />
          </li>
        )}
      />

      <TextField
        fullWidth
        label={t('memory_source')}
        name="source"
        value={formData.source}
        onChange={handleChange}
        margin="normal"
        helperText="Where did this memory come from?"
      />

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button
          type="button"
          variant="outlined"
          onClick={onCancel}
          startIcon={<CancelIcon />}
          disabled={loading}
        >
          {t('cancel')}
        </Button>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          disabled={loading || !formData.content.trim()}
        >
          {t('save')}
        </Button>
      </Box>
    </Paper>
  );
}

export default MemoryForm;

// Urdu: NFM-X Memory Form
// یہ memory create/edit ke liye form component hai