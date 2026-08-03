import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { Card, Table, Button, Tag, Space, Spin, Alert, Modal, Descriptions } from 'antd';
import { AlertOutlined, CheckCircleOutlined, ExclamationCircleOutlined, CloseCircleOutlined, EyeOutlined, } from '@ant-design/icons';
import { api } from '../services/api';
function ConflictsPage() {
    const [conflicts, setConflicts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedConflict, setSelectedConflict] = useState(null);
    const [isModalVisible, setIsModalVisible] = useState(false);
    useEffect(() => {
        fetchConflicts();
    }, []);
    const fetchConflicts = async () => {
        try {
            setLoading(true);
            const data = await api.listConflicts({ limit: 50, offset: 0, resolved: false });
            setConflicts(data.items.map((c) => ({ ...c, key: c.id })));
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch conflicts');
        }
        finally {
            setLoading(false);
        }
    };
    const handleDetect = async () => {
        try {
            setLoading(true);
            await api.detectConflicts();
            fetchConflicts();
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to detect conflicts');
        }
        finally {
            setLoading(false);
        }
    };
    const handleResolve = async (conflictId) => {
        try {
            await api.resolveConflict(conflictId);
            fetchConflicts();
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to resolve conflict');
        }
    };
    const getSeverityTag = (severity) => {
        switch (severity) {
            case 'LOW':
                return _jsx(Tag, { color: "green", icon: _jsx(CheckCircleOutlined, {}), children: "Low" });
            case 'MEDIUM':
                return _jsx(Tag, { color: "orange", icon: _jsx(ExclamationCircleOutlined, {}), children: "Medium" });
            case 'HIGH':
                return _jsx(Tag, { color: "red", icon: _jsx(CloseCircleOutlined, {}), children: "High" });
            default:
                return _jsx(Tag, { color: "gray", children: severity });
        }
    };
    const getTypeTag = (type) => {
        switch (type) {
            case 'DUPLICATE':
                return _jsx(Tag, { color: "blue", children: "Duplicate" });
            case 'CONTRADICTION':
                return _jsx(Tag, { color: "red", children: "Contradiction" });
            case 'AMBIGUITY':
                return _jsx(Tag, { color: "purple", children: "Ambiguity" });
            default:
                return _jsx(Tag, { color: "gray", children: type });
        }
    };
    const columns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            width: 100,
        },
        {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
            render: getTypeTag,
        },
        {
            title: 'Severity',
            dataIndex: 'severity',
            key: 'severity',
            render: getSeverityTag,
        },
        {
            title: 'Description',
            dataIndex: 'description',
            key: 'description',
            render: (desc) => (_jsx("div", { className: "max-w-md truncate", children: desc })),
        },
        {
            title: 'Memories',
            dataIndex: 'memoryIds',
            key: 'memoryIds',
            render: (ids) => (_jsx(Space, { size: [0, 8], wrap: true, children: ids.map((id) => (_jsxs(Tag, { color: "geekblue", children: [id.substring(0, 8), "..."] }, id))) })),
        },
        {
            title: 'Detected',
            dataIndex: 'detectedAt',
            key: 'detectedAt',
            render: (date) => new Date(date).toLocaleString(),
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (_jsxs(Space, { size: "small", children: [_jsx(Button, { type: "link", icon: _jsx(EyeOutlined, {}), size: "small", onClick: () => {
                            setSelectedConflict(record);
                            setIsModalVisible(true);
                        } }), _jsx(Button, { type: "link", size: "small", onClick: () => handleResolve(record.id), children: "Resolve" })] })),
        },
    ];
    if (loading && !conflicts.length) {
        return (_jsx("div", { className: "flex items-center justify-center h-64", children: _jsx(Spin, { size: "large" }) }));
    }
    if (error) {
        return (_jsx(Alert, { message: "Error", description: error, type: "error", showIcon: true, action: _jsx(Button, { onClick: fetchConflicts, children: "Retry" }) }));
    }
    return (_jsxs("div", { className: "space-y-4", children: [_jsx(Card, { children: _jsxs("div", { className: "flex justify-between items-center", children: [_jsx("h1", { className: "text-xl font-bold text-gray-900", children: "Conflicts" }), _jsx(Button, { type: "primary", icon: _jsx(AlertOutlined, {}), onClick: handleDetect, loading: loading, children: "Detect Conflicts" })] }) }), _jsx(Card, { children: _jsx(Table, { columns: columns, dataSource: conflicts, loading: loading, pagination: { pageSize: 10, showSizeChanger: true }, scroll: { x: true } }) }), _jsx(Modal, { title: "Conflict Details", open: isModalVisible, onCancel: () => setIsModalVisible(false), footer: [
                    _jsx(Button, { type: "primary", onClick: () => {
                            if (selectedConflict) {
                                handleResolve(selectedConflict.id);
                            }
                            setIsModalVisible(false);
                        }, children: "Resolve Conflict" }, "resolve"),
                    _jsx(Button, { onClick: () => setIsModalVisible(false), children: "Close" }, "cancel"),
                ], children: selectedConflict && (_jsxs("div", { className: "space-y-4", children: [_jsxs(Descriptions, { bordered: true, column: 1, size: "small", children: [_jsx(Descriptions.Item, { label: "ID", children: selectedConflict.id }), _jsx(Descriptions.Item, { label: "Type", children: getTypeTag(selectedConflict.type) }), _jsx(Descriptions.Item, { label: "Severity", children: getSeverityTag(selectedConflict.severity) }), _jsx(Descriptions.Item, { label: "Detected At", children: new Date(selectedConflict.detectedAt).toLocaleString() }), _jsx(Descriptions.Item, { label: "Resolved", children: selectedConflict.resolved ? 'Yes' : 'No' })] }), _jsx(Descriptions, { bordered: true, column: 1, size: "small", children: _jsx(Descriptions.Item, { label: "Description", children: selectedConflict.description }) }), _jsx(Descriptions, { bordered: true, column: 1, size: "small", children: _jsx(Descriptions.Item, { label: "Affected Memories", children: _jsx(Space, { size: [0, 8], wrap: true, children: selectedConflict.memoryIds.map((id) => (_jsx(Tag, { color: "geekblue", children: id }, id))) }) }) })] })) })] }));
}
export default ConflictsPage;
