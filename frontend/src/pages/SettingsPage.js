import React, { useState, useEffect } from 'react';
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
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Card,
  CardContent,
  CardHeader
} from '@mui/material';
import { Save as SaveIcon, Language as LanguageIcon } from '@mui/icons-material';

function SettingsPage({ setApiUrl, setTheme, theme }) {
  const { t, i18n } = useTranslation();
  const [apiUrl, setApiUrlState] = useState(localStorage.getItem('nfmApiUrl') || 'http://localhost:8000');
  const [apiKey, setApiKey] = useState(localStorage.getItem('nfmApiKey') || '');
  const [language, setLanguage] = useState(i18n.language || 'en');
  const [themeMode, setThemeMode] = useState(theme || 'light');
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    setTheme(themeMode);
  }, [themeMode, setTheme]);

  const handleSave = () => {
    localStorage.setItem('nfmApiUrl', apiUrl);
    setApiUrl(apiUrl);
    
    if (apiKey) {
      localStorage.setItem('nfmApiKey', apiKey);
    } else {
      localStorage.removeItem('nfmApiKey');
    }
    
    localStorage.setItem('nfmLanguage', language);
    i18n.changeLanguage(language);
    
    localStorage.setItem('nfmTheme', themeMode);
    setTheme(themeMode);
    
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleLanguageChange = (lng) => {
    setLanguage(lng);
    i18n.changeLanguage(lng);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('settings_title')}
      </Typography>

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title={t('settings_language')} />
        <CardContent>
          <FormControl fullWidth>
            <InputLabel>{t('settings_language')}</InputLabel>
            <Select
              value={language}
              label={t('settings_language')}
              onChange={(e) => handleLanguageChange(e.target.value)}
              startAdornment={<LanguageIcon color="action" sx={{ mr: 1 }} />}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="ur">اردو</MenuItem>
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title="API Configuration" />
        <CardContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              fullWidth
              label="API URL"
              variant="outlined"
              value={apiUrl}
              onChange={(e) => setApiUrlState(e.target.value)}
              placeholder="http://localhost:8000"
              helperText="Enter the URL of your NFM-X API server"
            />
            
            <TextField
              fullWidth
              label="API Key (Optional)"
              variant="outlined"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your API key if authentication is enabled"
              type="password"
              helperText="Leave empty if no authentication is required"
            />
          </Box>
        </CardContent>
      </Card>

      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title={t('settings_theme')} />
        <CardContent>
          <FormControlLabel
            control={
              <Switch
                checked={themeMode === 'dark'}
                onChange={(e) => setThemeMode(e.target.checked ? 'dark' : 'light')}
                color="primary"
              />
            }
            label={themeMode === 'dark' ? 'Dark Mode' : 'Light Mode'}
          />
        </CardContent>
      </Card>

      <Card elevation={2}>
        <CardHeader title="About NFM-X" />
        <CardContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            NFM-X (Non-Forgettable Evolutionary AI Memory) is a comprehensive memory system
            that allows you to store, retrieve, and evolve memories with full provenance tracking.
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Version: 0.1.0
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Repository: <a href="https://github.com/abdulraheemnohri/NFM-X" target="_blank" rel="noopener noreferrer">
              https://github.com/abdulraheemnohri/NFM-X
            </a>
          </Typography>
        </CardContent>
      </Card>

      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          startIcon={<SaveIcon />}
          size="large"
        >
          {t('settings_save')}
        </Button>
      </Box>
    </Box>
  );
}

export default SettingsPage;

// Urdu: NFM-X Settings Page
// یہ NFM-X کے لیے settings page ہے