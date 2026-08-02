import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import HomePage from './pages/HomePage';
import MemoryExplorerPage from './pages/MemoryExplorerPage';
import StatsPage from './pages/StatsPage';
import MemoryDetailPage from './pages/MemoryDetailPage';
import ConflictsPage from './pages/ConflictsPage';
import GraphPage from './pages/GraphPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/memories" element={<MemoryExplorerPage />} />
        <Route path="/memories/:id" element={<MemoryDetailPage />} />
        <Route path="/stats" element={<StatsPage />} />
        <Route path="/conflicts" element={<ConflictsPage />} />
        <Route path="/graph" element={<GraphPage />} />
      </Routes>
    </Layout>
  );
}

export default App;