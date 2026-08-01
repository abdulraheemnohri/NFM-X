import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CssBaseline, Drawer, AppBar, Toolbar, Typography, IconButton, List, ListItem, ListItemIcon, ListItemText, Container, Button, Menu, MenuItem, Divider } from '@mui/material';
import { Memory as MemoryIcon, Search as SearchIcon, Graph as GraphIcon, Analytics as AnalyticsIcon, Settings as SettingsIcon, Menu as MenuIcon, Language as LanguageIcon, Dashboard as DashboardIcon } from '@mui/icons-material';
import DashboardPage from './pages/DashboardPage';
import MemoriesPage from './pages/MemoriesPage';
import SearchPage from './pages/SearchPage';
import GraphPage from './pages/GraphPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import MemoryForm from './components/memory/MemoryForm';

const drawerWidth = 240;

function App() {
  const { t, i18n } = useTranslation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [apiUrl, setApiUrl] = useState(localStorage.getItem('nfmApiUrl') || 'http://localhost:8000');

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);
  const handleLanguageMenu = (event) => setAnchorEl(event.currentTarget);
  const handleLanguageClose = () => setAnchorEl(null);

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('nfmLanguage', lng);
    handleLanguageClose();
  };

  const navigationItems = [
    { path: '/', icon: <DashboardIcon />, label: t('nav_dashboard') },
    { path: '/memories', icon: <MemoryIcon />, label: t('nav_memories') },
    { path: '/search', icon: <SearchIcon />, label: t('nav_search') },
    { path: '/graph', icon: <GraphIcon />, label: t('nav_graph') },
    { path: '/analytics', icon: <AnalyticsIcon />, label: t('nav_analytics') },
    { path: '/settings', icon: <SettingsIcon />, label: t('nav_settings') },
  ];

  const drawer = (
    <div>
      <Toolbar />
      <Divider />
      <List>
        {navigationItems.map((item) => (
          <ListItem button key={item.path} component="a" href={item.path} onClick={handleDrawerToggle}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ width: { sm: 'calc(100% - 240px)', ml: { sm: '240px' } }}>
        <Toolbar>
          <IconButton color="inherit" aria-label="open drawer" edge="start" onClick={handleDrawerToggle} sx={{ mr: 2, display: { sm: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {t('app_name')}
          </Typography>
          <Button color="inherit" startIcon={<LanguageIcon />} onClick={handleLanguageMenu}>
            {i18n.language.toUpperCase()}
          </Button>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleLanguageClose}>
            <MenuItem onClick={() => changeLanguage('en')}>English</MenuItem>
            <MenuItem onClick={() => changeLanguage('ur')}>Urdu</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { sm: 240 } }}>
        <Drawer variant="temporary" open={mobileOpen} onClose={handleDrawerToggle} ModalProps={{ keepMounted: true }} sx={{ display: { xs: 'block', sm: 'none' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 } }}>
          {drawer}
        </Drawer>
        <Drawer variant="permanent" sx={{ display: { xs: 'none', sm: 'block' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 } }} open>
          {drawer}
        </Drawer>
      </Box>
      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { sm: 'calc(100% - 240px)' } }}>
        <Toolbar />
        <Container maxWidth="xl" sx={{ py: 4 }}>
          <Routes>
            <Route path="/" element={<DashboardPage apiUrl={apiUrl} />} />
            <Route path="/memories" element={<MemoriesPage apiUrl={apiUrl} />} />
            <Route path="/memories/create" element={<MemoryForm apiUrl={apiUrl} />} />
            <Route path="/memories/:id/edit" element={<MemoryForm apiUrl={apiUrl} isEdit={true} />} />
            <Route path="/search" element={<SearchPage apiUrl={apiUrl} />} />
            <Route path="/graph" element={<GraphPage apiUrl={apiUrl} />} />
            <Route path="/analytics" element={<AnalyticsPage apiUrl={apiUrl} />} />
            <Route path="/settings" element={<SettingsPage setApiUrl={setApiUrl} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

export default App;