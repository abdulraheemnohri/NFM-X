import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Spin, Alert, Progress, Table } from 'antd';
import { BarChartOutlined, DatabaseOutlined, ClockCircleOutlined, PieChartOutlined, } from '@ant-design/icons';
import { api } from '../services/api';
function StatsPage() {
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
    const total = stats?.totalMemories || 0;
    const active = stats?.activeMemories || 0;
    const archived = stats?.archivedMemories || 0;
    const deleted = stats?.deletedMemories || 0;
    const statusData = [
        { status: 'Active', count: active, percentage: total > 0 ? (active / total) * 100 : 0 },
        { status: 'Archived', count: archived, percentage: total > 0 ? (archived / total) * 100 : 0 },
        { status: 'Deleted', count: deleted, percentage: total > 0 ? (deleted / total) * 100 : 0 },
    ];
    const tagData = Object.entries(stats?.mostUsedTags || {}).map(([tag, count]) => ({
        key: tag,
        tag,
        count,
    }));
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-2xl font-bold text-gray-900", children: "Statistics" }), _jsx("p", { className: "text-gray-600", children: "System overview and analytics" })] }), _jsxs(Row, { gutter: [16, 16], children: [_jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Total Memories", value: total, prefix: _jsx(DatabaseOutlined, { className: "text-primary-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Active", value: active, prefix: _jsx(ClockCircleOutlined, { className: "text-green-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Archived", value: archived, prefix: _jsx(BarChartOutlined, { className: "text-blue-600" }) }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsx(Statistic, { title: "Deleted", value: deleted, prefix: _jsx(PieChartOutlined, { className: "text-red-600" }) }) }) })] }), _jsxs(Row, { gutter: [16, 16], children: [_jsx(Col, { xs: 24, lg: 12, children: _jsxs(Card, { className: "stat-card", children: [_jsx("h2", { className: "text-lg font-semibold mb-4", children: "Memory Status Distribution" }), _jsx(Space, { direction: "vertical", size: "middle", style: { width: '100%' }, children: statusData.map((item) => (_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-1", children: [_jsx("span", { className: "font-medium", children: item.status }), _jsxs("span", { className: "text-sm text-gray-500", children: [item.count, " memories"] })] }), _jsx(Progress, { percent: item.percentage, status: item.status === 'Active' ? 'success' :
                                                    item.status === 'Archived' ? 'active' : 'exception', strokeColor: item.status === 'Active' ? '#52c41a' :
                                                    item.status === 'Archived' ? '#1890ff' : '#ff4d4f' })] }, item.status))) })] }) }), _jsx(Col, { xs: 24, lg: 12, children: _jsxs(Card, { className: "stat-card", children: [_jsx("h2", { className: "text-lg font-semibold mb-4", children: "Most Used Tags" }), tagData.length > 0 ? (_jsx(Table, { columns: [
                                        { title: 'Tag', dataIndex: 'tag', key: 'tag' },
                                        { title: 'Count', dataIndex: 'count', key: 'count' },
                                    ], dataSource: tagData, pagination: false, size: "small" })) : (_jsx("p", { className: "text-gray-500 text-center py-4", children: "No tags found" }))] }) })] }), _jsxs(Row, { gutter: [16, 16], children: [_jsx(Col, { xs: 24, lg: 12, children: _jsxs(Card, { className: "stat-card", children: [_jsx("h2", { className: "text-lg font-semibold mb-4", children: "Storage Information" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Total Storage Size:" }), _jsx("span", { className: "font-medium", children: formatBytes(stats?.totalStorageSize || 0) })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Average Memory Size:" }), _jsx("span", { className: "font-medium", children: formatBytes(Number(stats?.avgMemorySize || 0)) })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Total Versions:" }), _jsx("span", { className: "font-medium", children: stats?.totalVersions || 0 })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Last Updated:" }), _jsx("span", { className: "font-medium", children: stats?.lastUpdated ? new Date(stats.lastUpdated).toLocaleString() : 'Never' })] })] })] }) }), _jsx(Col, { xs: 24, lg: 12, children: _jsxs(Card, { className: "stat-card", children: [_jsx("h2", { className: "text-lg font-semibold mb-4", children: "System Health" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-3 h-3 bg-green-500 rounded-full" }), _jsx("span", { children: "API Server: Connected" })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-3 h-3 bg-green-500 rounded-full" }), _jsx("span", { children: "Database: Operational" })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-3 h-3 bg-green-500 rounded-full" }), _jsx("span", { children: "Embedding Model: Loaded" })] })] })] }) })] })] }));
}
function formatBytes(bytes) {
    if (bytes === 0)
        return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
export default StatsPage;
