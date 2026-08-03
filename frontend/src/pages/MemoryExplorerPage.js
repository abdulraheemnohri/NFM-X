import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { Card, Table, Button, Input, Select, Tag, Space, Modal, Form, message, Popconfirm, Badge, } from 'antd';
import { SearchOutlined, PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
const { Search } = Input;
const { Option } = Select;
function MemoryExplorerPage() {
    const [memories, setMemories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();
    const [editingMemory, setEditingMemory] = useState(null);
    useEffect(() => {
        fetchMemories();
    }, [searchQuery, statusFilter]);
    const fetchMemories = async () => {
        try {
            setLoading(true);
            const params = { limit: 50, offset: 0 };
            if (statusFilter !== 'all') {
                params.status = statusFilter;
            }
            const data = await api.listMemories(params);
            setMemories(data.items.map((m) => ({ ...m, key: m.id })));
        }
        catch (err) {
            message.error(err instanceof Error ? err.message : 'Failed to fetch memories');
        }
        finally {
            setLoading(false);
        }
    };
    const handleSearch = (value) => {
        setSearchQuery(value);
    };
    const handleStatusChange = (value) => {
        setStatusFilter(value);
    };
    const handleCreate = () => {
        setEditingMemory(null);
        form.resetFields();
        setIsModalVisible(true);
    };
    const handleEdit = (memory) => {
        setEditingMemory(memory);
        form.setFieldsValue({
            content: memory.content,
            title: memory.title,
            tags: memory.tags?.join(', '),
        });
        setIsModalVisible(true);
    };
    const handleDelete = async (memoryId) => {
        try {
            await api.deleteMemory(memoryId);
            message.success('Memory deleted successfully');
            fetchMemories();
        }
        catch (err) {
            message.error(err instanceof Error ? err.message : 'Failed to delete memory');
        }
    };
    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const payload = {
                content: values.content,
                title: values.title,
                tags: values.tags ? values.tags.split(',').map((t) => t.trim()) : [],
            };
            if (editingMemory) {
                await api.updateMemory(editingMemory.id, payload);
                message.success('Memory updated successfully');
            }
            else {
                await api.createMemory(payload);
                message.success('Memory created successfully');
            }
            setIsModalVisible(false);
            fetchMemories();
        }
        catch (err) {
            message.error(err instanceof Error ? err.message : 'Failed to save memory');
        }
    };
    const getStatusTag = (status) => {
        switch (status) {
            case 'ACTIVE':
                return _jsx(Tag, { color: "green", children: "Active" });
            case 'ARCHIVED':
                return _jsx(Tag, { color: "blue", children: "Archived" });
            case 'DELETED':
                return _jsx(Tag, { color: "red", children: "Deleted" });
            case 'PENDING':
                return _jsx(Tag, { color: "orange", children: "Pending" });
            default:
                return _jsx(Tag, { color: "gray", children: status });
        }
    };
    const columns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            width: 100,
            render: (id) => _jsx(Badge, { count: id, style: { backgroundColor: '#1890ff' } }),
        },
        {
            title: 'Title',
            dataIndex: 'title',
            key: 'title',
            render: (title, record) => (_jsx(Link, { to: `/memories/${record.id}`, children: title || 'Untitled' })),
        },
        {
            title: 'Content',
            dataIndex: 'content',
            key: 'content',
            render: (content) => (_jsxs("div", { className: "max-w-xs truncate", children: [content.substring(0, 100), "..."] })),
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: getStatusTag,
        },
        {
            title: 'Tags',
            dataIndex: 'tags',
            key: 'tags',
            render: (tags = []) => (_jsx(Space, { size: [0, 8], wrap: true, children: tags.map((tag) => (_jsx(Tag, { color: "geekblue", children: tag }, tag))) })),
        },
        {
            title: 'Created',
            dataIndex: 'createdAt',
            key: 'createdAt',
            render: (date) => new Date(date).toLocaleDateString(),
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (_jsxs(Space, { size: "small", children: [_jsx(Link, { to: `/memories/${record.id}`, children: _jsx(Button, { type: "link", icon: _jsx(EyeOutlined, {}), size: "small" }) }), _jsx(Button, { type: "link", icon: _jsx(EditOutlined, {}), size: "small", onClick: () => handleEdit(record) }), _jsx(Popconfirm, { title: "Are you sure to delete this memory?", onConfirm: () => handleDelete(record.id), okText: "Yes", cancelText: "No", children: _jsx(Button, { type: "link", icon: _jsx(DeleteOutlined, {}), size: "small", danger: true }) })] })),
        },
    ];
    return (_jsxs("div", { className: "space-y-4", children: [_jsx(Card, { children: _jsxs("div", { className: "flex flex-wrap gap-4 items-center justify-between", children: [_jsxs("div", { className: "flex flex-wrap gap-4 items-center", children: [_jsx(Search, { placeholder: "Search memories...", allowClear: true, enterButton: _jsx(SearchOutlined, {}), size: "large", style: { width: 300 }, onSearch: handleSearch }), _jsxs(Select, { placeholder: "Filter by status", value: statusFilter, onChange: handleStatusChange, size: "large", style: { width: 150 }, children: [_jsx(Option, { value: "all", children: "All Statuses" }), _jsx(Option, { value: "ACTIVE", children: "Active" }), _jsx(Option, { value: "ARCHIVED", children: "Archived" }), _jsx(Option, { value: "DELETED", children: "Deleted" }), _jsx(Option, { value: "PENDING", children: "Pending" })] })] }), _jsx(Button, { type: "primary", icon: _jsx(PlusOutlined, {}), size: "large", onClick: handleCreate, children: "Create Memory" })] }) }), _jsx(Card, { children: _jsx(Table, { columns: columns, dataSource: memories, loading: loading, pagination: { pageSize: 10, showSizeChanger: true }, scroll: { x: true } }) }), _jsx(Modal, { title: editingMemory ? 'Edit Memory' : 'Create Memory', open: isModalVisible, onCancel: () => setIsModalVisible(false), footer: [
                    _jsx(Button, { onClick: () => setIsModalVisible(false), children: "Cancel" }, "cancel"),
                    _jsx(Button, { type: "primary", onClick: handleSubmit, loading: loading, children: editingMemory ? 'Update' : 'Create' }, "submit"),
                ], children: _jsxs(Form, { form: form, layout: "vertical", children: [_jsx(Form.Item, { name: "title", label: "Title", rules: [{ required: false, message: 'Please enter a title' }], children: _jsx(Input, { placeholder: "Memory title" }) }), _jsx(Form.Item, { name: "content", label: "Content", rules: [{ required: true, message: 'Please enter content' }], children: _jsx(Input.TextArea, { rows: 6, placeholder: "Memory content" }) }), _jsx(Form.Item, { name: "tags", label: "Tags", children: _jsx(Input, { placeholder: "Comma separated tags" }) })] }) })] }));
}
export default MemoryExplorerPage;
