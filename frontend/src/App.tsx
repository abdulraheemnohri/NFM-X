import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './Layout';

// Import all pages
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import MemoryExplorerPage from './pages/MemoryExplorerPage';
import MemoryDetailPage from './pages/MemoryDetailPage';
import GraphPage from './pages/GraphPage';
import StatsPage from './pages/StatsPage';
import ConflictsPage from './pages/ConflictsPage';
import DocumentsPage from './pages/DocumentsPage';
import UploadPage from './pages/UploadPage';
import HealthPage from './pages/HealthPage';
import SettingsPage from './pages/SettingsPage';
import StatisticsPage from './pages/StatisticsPage';
import PatternsPage from './pages/PatternsPage';
import SkillsPage from './pages/SkillsPage';
import MCPPage from './pages/MCPPage';

// V2 Pages
import V2Dashboard from './pages/V2/V2Dashboard';
import V2MemoryExplorer from './pages/V2/V2MemoryExplorer';
import V2Graph from './pages/V2/V2Graph';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Root and Home */}
          <Route path="/" element={<HomePage />} />
          
          {/* Dashboard & Overview */}
          <Route path="/dashboard" element={<Dashboard />} />
          
          {/* Memory Management */}
          <Route path="/memories" element={<MemoryExplorerPage />} />
          <Route path="/memories/:id" element={<MemoryDetailPage />} />
          
          {/* Graph & Relationships */}
          <Route path="/graph" element={<GraphPage />} />
          
          {/* Statistics */}
          <Route path="/stats" element={<StatsPage />} />
          <Route path="/statistics" element={<StatisticsPage />} />
          
          {/* Conflicts */}
          <Route path="/conflicts" element={<ConflictsPage />} />
          
          {/* Documents & Upload */}
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/upload" element={<UploadPage />} />
          
          {/* System */}
          <Route path="/health" element={<HealthPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          
          {/* V4 Features */}
          <Route path="/patterns" element={<PatternsPage />} />
          <Route path="/skills" element={<SkillsPage />} />
          <Route path="/mcp" element={<MCPPage />} />
          
          {/* V2 Pages */}
          <Route path="/v2" element={<V2Dashboard />} />
          <Route path="/v2/memories" element={<V2MemoryExplorer />} />
          <Route path="/v2/graph" element={<V2Graph />} />
          
          {/* Fallback - Redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;