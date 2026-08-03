import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Card, Button, Tag, Space, Descriptions, Spin, Alert, Modal, Form, Input, message, Popconfirm, Divider, Badge, Row, Col, } from 'antd';
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined, ClockCircleOutlined, TagOutlined, } from '@ant-design/icons';
import { api } from '../services/api';
function MemoryDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [memory, setMemory] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();
    useEffect(() => {
        if (id) {
            fetchMemory(id);
        }
    }, [id]);
    const fetchMemory = async (memoryId) => {
        try {
            setLoading(true);
            const data = await api.getMemory(memoryId);
            setMemory(data);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch memory');
        }
        finally {
            setLoading(false);
        }
    };
    const handleEdit = () => {
        if (memory) {
            form.setFieldsValue({
                content: memory.content,
                title: memory.title,
                tags: memory.tags?.join(', '),
            });
            setIsModalVisible(true);
        }
    };
    const handleDelete = async () => {
        if (!id)
            return;
        try {
            await api.deleteMemory(id);
            message.success('Memory deleted successfully');
            navigate('/memories');
        }
        catch (err) {
            message.error(err instanceof Error ? err.message : 'Failed to delete memory');
        }
    };
    const handleSubmit = async () => {
        if (!id)
            return;
        try {
            const values = await form.validateFields();
            const payload = {
                content: values.content,
                title: values.title,
                tags: values.tags ? values.tags.split(',').map((t) => t.trim()) : [],
            };
            await api.updateMemory(id, payload);
            message.success('Memory updated successfully');
            setIsModalVisible(false);
            fetchMemory(id);
        }
        catch (err) {
            message.error(err instanceof Error ? err.message : 'Failed to update memory');
        }
    };
    const getStatusBadge = (status) => {
        switch (status) {
            case 'ACTIVE':
                return _jsx(Badge, { status: "success", text: "Active" });
            case 'ARCHIVED':
                return _jsx(Badge, { status: "default", text: "Archived" });
            case 'DELETED':
                return _jsx(Badge, { status: "error", text: "Deleted" });
            case 'PENDING':
                return _jsx(Badge, { status: "warning", text: "Pending" });
            default:
                return _jsx(Badge, { status: "processing", text: status });
        }
    };
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center h-64", children: _jsx(Spin, { size: "large" }) }));
    }
    if (error) {
        return (_jsx(Alert, { message: "Error", description: error, type: "error", showIcon: true, action: _jsxs(Space, { children: [_jsx(Button, { onClick: () => fetchMemory(id), children: "Retry" }), _jsx(Link, { to: "/memories", children: _jsx(Button, { type: "link", children: "Back to Memories" }) })] }) }));
    }
    if (!memory) {
        return (_jsx(Alert, { message: "Memory Not Found", description: "The requested memory does not exist.", type: "warning", showIcon: true, action: _jsx(Link, { to: "/memories", children: _jsx(Button, { type: "primary", children: "Back to Memories" }) }) }));
    }
    return (_jsxs("div", { className: "space-y-4", children: [_jsxs(Card, { children: [_jsxs(Space, { size: "middle", wrap: true, children: [_jsx(Button, { icon: _jsx(ArrowLeftOutlined, {}), onClick: () => navigate('/memories'), children: "Back" }), _jsx("h1", { className: "text-xl font-bold m-0", children: memory.title || 'Untitled Memory' })] }), _jsx(Divider, {}), _jsxs(Space, { size: "middle", wrap: true, children: [getStatusBadge(memory.status), _jsxs("span", { className: "text-gray-500", children: [_jsx(ClockCircleOutlined, { className: "mr-1" }), "Created: ", new Date(memory.createdAt).toLocaleString()] }), _jsxs("span", { className: "text-gray-500", children: [_jsx(ClockCircleOutlined, { className: "mr-1" }), "Updated: ", new Date(memory.updatedAt).toLocaleString()] })] })] }), _jsxs(Row, { gutter: [16, 16], children: [_jsxs(Col, { xs: 24, lg: 16, children: [_jsx(Card, { title: "Content", children: _jsx("div", { className: "prose max-w-none whitespace-pre-wrap", children: memory.content }) }), _jsx(Card, { title: "Metadata", children: Object.entries(memory.metadata || {}).length > 0 ? (_jsx(Descriptions, { bordered: true, column: 1, size: "small", children: Object.entries(memory.metadata || {}).map(([key, value]) => (_jsx(Descriptions.Item, { label: key, children: JSON.stringify(value) }, key))) })) : (_jsx("p", { className: "text-gray-500", children: "No metadata available" })) })] }), _jsxs(Col, { xs: 24, lg: 8, children: [_jsx(Card, { title: "Information", children: _jsxs(Descriptions, { bordered: true, column: 1, size: "small", children: [_jsx(Descriptions.Item, { label: "ID", children: memory.id }), _jsx(Descriptions.Item, { label: "Type", children: memory.type }), _jsx(Descriptions.Item, { label: "Version", children: memory.version }), memory.parentId && (_jsx(Descriptions.Item, { label: "Parent ID", children: memory.parentId })), _jsx(Descriptions.Item, { label: "Source", children: memory.source || 'N/A' })] }) }), _jsx(Card, { title: "Tags", children: memory.tags && memory.tags.length > 0 ? (_jsx(Space, { size: [0, 8], wrap: true, children: memory.tags.map((tag) => (_jsxs(Tag, { color: "geekblue", children: [_jsx(TagOutlined, { className: "mr-1" }), tag] }, tag))) })) : (_jsx("p", { className: "text-gray-500", children: "No tags" })) }), _jsx(Card, { title: "Actions", children: _jsxs(Space, { direction: "vertical", size: "small", style: { width: '100%' }, children: [_jsx(Button, { type: "primary", icon: _jsx(EditOutlined, {}), block: true, onClick: handleEdit, children: "Edit Memory" }), _jsx(Popconfirm, { title: "Are you sure to delete this memory?", onConfirm: handleDelete, okText: "Yes", cancelText: "No", children: _jsx(Button, { type: "primary", danger: true, icon: _jsx(DeleteOutlined, {}), block: true, children: "Delete Memory" }) })] }) })] })] }), _jsx(Modal, { title: "Edit Memory", open: isModalVisible, onCancel: () => setIsModalVisible(false), footer: [
                    _jsx(Button, { onClick: () => setIsModalVisible(false), children: "Cancel" }, "cancel"),
                    _jsx(Button, { type: "primary", onClick: handleSubmit, loading: loading, children: "Update" }, "submit"),
                ], children: _jsxs(Form, { form: form, layout: "vertical", children: [_jsx(Form.Item, { name: "title", label: "Title", rules: [{ required: false, message: 'Please enter a title' }], children: _jsx(Input, { placeholder: "Memory title" }) }), _jsx(Form.Item, { name: "content", label: "Content", rules: [{ required: true, message: 'Please enter content' }], children: _jsx(Input.TextArea, { rows: 10, placeholder: "Memory content" }) }), _jsx(Form.Item, { name: "tags", label: "Tags", children: _jsx(Input, { placeholder: "Comma separated tags" }) })] }) })] }));
}
export default MemoryDetailPage;
