import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic, Spin, Alert } from 'antd';
import { DatabaseOutlined, SearchOutlined, AlertOutlined, ProjectOutlined, ClockCircleOutlined, } from '@ant-design/icons';
import { api } from '../services/api';
function HomePage() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    useEffect(() => {
        fetchStats();
    }, []);
    const fetchStats = async () => {
        try {
            setLoading(true);
            const data = await api.getStats();
            setStats(data);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch statistics');
        }
        finally {
            setLoading(false);
        }
    };
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center h-64", children: _jsx(Spin, { size: "large" }) }));
    }
    if (error) {
        return (_jsx(Alert, { message: "Error", description: error, type: "error", showIcon: true, action: _jsx("button", { className: "btn-primary", onClick: fetchStats, children: "Retry" }) }));
    }
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-2xl font-bold text-gray-900", children: "NFM-X Dashboard" }), _jsx("p", { className: "text-gray-600", children: "Non-Forgettable Memory Layer" })] }), _jsxs(Row, { gutter: [16, 16], children: [_jsx(Col, { xs: 24, sm: 12, lg: 8, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Total Memories", value: stats?.totalMemories || 0, prefix: _jsx(DatabaseOutlined, { className: "text-primary-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 8, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Active Memories", value: stats?.activeMemories || 0, prefix: _jsx(ClockCircleOutlined, { className: "text-green-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 8, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Total Versions", value: stats?.totalVersions || 0, prefix: _jsx(ProjectOutlined, { className: "text-purple-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 8, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Storage Size", value: formatBytes(stats?.totalStorageSize || 0), prefix: _jsx(DatabaseOutlined, { className: "text-blue-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 8, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Avg Memory Size", value: formatBytes(Number(stats?.avgMemorySize || 0)), prefix: _jsx(SearchOutlined, { className: "text-orange-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 8, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Conflicts", value: 0, prefix: _jsx(AlertOutlined, { className: "text-red-600" }) }) }) })] }), _jsxs(Card, { className: "stat-card", children: [_jsx("h2", { className: "text-xl font-semibold mb-4", children: "About NFM-X" }), _jsx("p", { className: "text-gray-600 mb-4", children: "NFM-X (Non-Forgettable Memory Layer) is a production-grade, model-independent, local-first long-term memory layer for AI systems." }), _jsxs("ul", { className: "list-disc list-inside text-gray-600 space-y-2", children: [_jsx("li", { children: "Never forget: Once memory is committed, it is never silently overwritten or lost" }), _jsx("li", { children: "Versioning: New information creates a new version, history is preserved" }), _jsx("li", { children: "Provenance: Every memory has a source and lineage" }), _jsx("li", { children: "Portability: Memory remains portable between models and applications" })] })] })] }));
}
function formatBytes(bytes) {
    if (bytes === 0)
        return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
export default HomePage;
