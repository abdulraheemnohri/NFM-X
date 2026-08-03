import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
    return (_jsx(Router, { children: _jsx(Layout, { children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(HomePage, {}) }), _jsx(Route, { path: "/dashboard", element: _jsx(Dashboard, {}) }), _jsx(Route, { path: "/memories", element: _jsx(MemoryExplorerPage, {}) }), _jsx(Route, { path: "/memories/:id", element: _jsx(MemoryDetailPage, {}) }), _jsx(Route, { path: "/graph", element: _jsx(GraphPage, {}) }), _jsx(Route, { path: "/stats", element: _jsx(StatsPage, {}) }), _jsx(Route, { path: "/statistics", element: _jsx(StatisticsPage, {}) }), _jsx(Route, { path: "/conflicts", element: _jsx(ConflictsPage, {}) }), _jsx(Route, { path: "/documents", element: _jsx(DocumentsPage, {}) }), _jsx(Route, { path: "/upload", element: _jsx(UploadPage, {}) }), _jsx(Route, { path: "/health", element: _jsx(HealthPage, {}) }), _jsx(Route, { path: "/settings", element: _jsx(SettingsPage, {}) }), _jsx(Route, { path: "/patterns", element: _jsx(PatternsPage, {}) }), _jsx(Route, { path: "/skills", element: _jsx(SkillsPage, {}) }), _jsx(Route, { path: "/mcp", element: _jsx(MCPPage, {}) }), _jsx(Route, { path: "/v2", element: _jsx(V2Dashboard, {}) }), _jsx(Route, { path: "/v2/memories", element: _jsx(V2MemoryExplorer, {}) }), _jsx(Route, { path: "/v2/graph", element: _jsx(V2Graph, {}) }), _jsx(Route, { path: "*", element: _jsx(Navigate, { to: "/", replace: true }) })] }) }) }));
}
export default App;
