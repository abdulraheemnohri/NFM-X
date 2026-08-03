import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { Card, Spin, Alert, Button, Space, Table, Tag } from 'antd';
import { ProjectOutlined, ReloadOutlined, NodeIndexOutlined, BranchOutlined, } from '@ant-design/icons';
import { api } from '../services/api';
import { Row, Col } from 'antd';
function GraphPage() {
    const [graphData, setGraphData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    useEffect(() => {
        fetchGraph();
    }, []);
    const fetchGraph = async () => {
        try {
            setLoading(true);
            const data = await api.getGraph();
            setGraphData(data);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch graph data');
        }
        finally {
            setLoading(false);
        }
    };
    if (loading && !graphData) {
        return (_jsx("div", { className: "flex items-center justify-center h-64", children: _jsx(Spin, { size: "large" }) }));
    }
    if (error) {
        return (_jsx(Alert, { message: "Error", description: error, type: "error", showIcon: true, action: _jsx(Button, { onClick: fetchGraph, children: "Retry" }) }));
    }
    const nodeColumns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
        },
        {
            title: 'Label',
            dataIndex: 'label',
            key: 'label',
        },
        {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
            render: (type) => _jsx(Tag, { color: "geekblue", children: type }),
        },
    ];
    const edgeColumns = [
        {
            title: 'Source',
            dataIndex: 'source',
            key: 'source',
            render: (source) => _jsxs(Tag, { color: "blue", children: [source.substring(0, 8), "..."] }),
        },
        {
            title: 'Target',
            dataIndex: 'target',
            key: 'target',
            render: (target) => _jsxs(Tag, { color: "green", children: [target.substring(0, 8), "..."] }),
        },
        {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
            render: (type) => _jsx(Tag, { color: "purple", children: type }),
        },
        {
            title: 'Weight',
            dataIndex: 'weight',
            key: 'weight',
            render: (weight) => _jsx(Tag, { color: "orange", children: weight.toFixed(2) }),
        },
    ];
    return (_jsxs("div", { className: "space-y-4", children: [_jsx(Card, { children: _jsxs("div", { className: "flex justify-between items-center", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-xl font-bold text-gray-900", children: "Memory Graph" }), _jsx("p", { className: "text-gray-600", children: "Visualize memory relationships" })] }), _jsx(Button, { type: "default", icon: _jsx(ReloadOutlined, {}), onClick: fetchGraph, loading: loading, children: "Refresh" })] }) }), graphData && (_jsxs("div", { className: "space-y-4", children: [_jsxs(Row, { gutter: [16, 16], children: [_jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsxs(Space, { direction: "vertical", size: "middle", children: [_jsx(NodeIndexOutlined, { className: "text-2xl text-primary-600" }), _jsxs("div", { children: [_jsx("div", { className: "text-2xl font-bold", children: graphData.nodeCount }), _jsx("div", { className: "text-sm text-gray-500", children: "Nodes" })] })] }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsxs(Space, { direction: "vertical", size: "middle", children: [_jsx(BranchOutlined, { className: "text-2xl text-green-600" }), _jsxs("div", { children: [_jsx("div", { className: "text-2xl font-bold", children: graphData.edgeCount }), _jsx("div", { className: "text-sm text-gray-500", children: "Edges" })] })] }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsxs(Space, { direction: "vertical", size: "middle", children: [_jsx(ProjectOutlined, { className: "text-2xl text-purple-600" }), _jsxs("div", { children: [_jsx("div", { className: "text-2xl font-bold", children: graphData.nodes.length > 0
                                                            ? new Set(graphData.nodes.map((n) => n.type)).size
                                                            : 0 }), _jsx("div", { className: "text-sm text-gray-500", children: "Node Types" })] })] }) }) }), _jsx(Col, { xs: 24, sm: 12, lg: 6, children: _jsx(Card, { className: "stat-card card-hover", children: _jsxs(Space, { direction: "vertical", size: "middle", children: [_jsx(ProjectOutlined, { className: "text-2xl text-orange-600" }), _jsxs("div", { children: [_jsx("div", { className: "text-2xl font-bold", children: graphData.edges.length > 0
                                                            ? new Set(graphData.edges.map((e) => e.type)).size
                                                            : 0 }), _jsx("div", { className: "text-sm text-gray-500", children: "Edge Types" })] })] }) }) })] }), _jsxs(Row, { gutter: [16, 16], children: [_jsx(Col, { xs: 24, lg: 12, children: _jsx(Card, { title: "Nodes", children: _jsx(Table, { columns: nodeColumns, dataSource: graphData.nodes.map((n) => ({ ...n, key: n.id })), pagination: { pageSize: 10 }, scroll: { y: 400 } }) }) }), _jsx(Col, { xs: 24, lg: 12, children: _jsx(Card, { title: "Edges (Relationships)", children: _jsx(Table, { columns: edgeColumns, dataSource: graphData.edges.map((e) => ({
                                            ...e,
                                            key: `${e.source}-${e.target}-${e.type}`,
                                        })), pagination: { pageSize: 10 }, scroll: { y: 400 } }) }) })] }), graphData.nodes.length > 0 && (_jsx(Card, { title: "Graph Visualization", children: _jsxs("div", { className: "bg-gray-50 p-8 rounded-lg text-center text-gray-500", children: [_jsx(ProjectOutlined, { className: "text-4xl mb-4" }), _jsx("p", { children: "Interactive graph visualization coming soon..." }), _jsx("p", { className: "text-sm mt-2", children: "Use the tables above to explore nodes and relationships" })] }) }))] }))] }));
}
export default GraphPage;
