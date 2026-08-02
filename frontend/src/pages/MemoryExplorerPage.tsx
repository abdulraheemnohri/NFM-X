import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Tag,
  Space,
  Modal,
  Form,
  message,
  Popconfirm,
  Badge,
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Memory, MemoryStatus } from '../types';

const { Search } = Input;
const { Option } = Select;

interface MemoryWithKey extends Memory {
  key: string;
}

function MemoryExplorerPage() {
  const [memories, setMemories] = useState<MemoryWithKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<MemoryStatus | 'all'>('all');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [editingMemory, setEditingMemory] = useState<Memory | null>(null);

  useEffect(() => {
    fetchMemories();
  }, [searchQuery, statusFilter]);

  const fetchMemories = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 50, offset: 0 };
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const data = await api.listMemories(params);
      setMemories(
        data.items.map((m: Memory) => ({ ...m, key: m.id }))
      );
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'Failed to fetch memories');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
  };

  const handleStatusChange = (value: MemoryStatus | 'all') => {
    setStatusFilter(value);
  };

  const handleCreate = () => {
    setEditingMemory(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (memory: Memory) => {
    setEditingMemory(memory);
    form.setFieldsValue({
      content: memory.content,
      title: memory.title,
      tags: memory.tags?.join(', '),
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (memoryId: string) => {
    try {
      await api.deleteMemory(memoryId);
      message.success('Memory deleted successfully');
      fetchMemories();
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'Failed to delete memory');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        content: values.content,
        title: values.title,
        tags: values.tags ? values.tags.split(',').map((t: string) => t.trim()) : [],
      };

      if (editingMemory) {
        await api.updateMemory(editingMemory.id, payload);
        message.success('Memory updated successfully');
      } else {
        await api.createMemory(payload);
        message.success('Memory created successfully');
      }
      setIsModalVisible(false);
      fetchMemories();
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'Failed to save memory');
    }
  };

  const getStatusTag = (status: MemoryStatus) => {
    switch (status) {
      case 'ACTIVE':
        return <Tag color="green">Active</Tag>;
      case 'ARCHIVED':
        return <Tag color="blue">Archived</Tag>;
      case 'DELETED':
        return <Tag color="red">Deleted</Tag>;
      case 'PENDING':
        return <Tag color="orange">Pending</Tag>;
      default:
        return <Tag color="gray">{status}</Tag>;
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      render: (id: string) => <Badge count={id} style={{ backgroundColor: '#1890ff' }} />,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      render: (title: string, record: MemoryWithKey) => (
        <Link to={`/memories/${record.id}`}>
          {title || 'Untitled'}
        </Link>
      ),
    },
    {
      title: 'Content',
      dataIndex: 'content',
      key: 'content',
      render: (content: string) => (
        <div className="max-w-xs truncate">{content.substring(0, 100)}...</div>
      ),
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
      render: (tags: string[] = []) => (
        <Space size={[0, 8]} wrap>
          {tags.map((tag) => (
            <Tag key={tag} color="geekblue">
              {tag}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: MemoryWithKey) => (
        <Space size="small">
          <Link to={`/memories/${record.id}`}>
            <Button type="link" icon={<EyeOutlined />} size="small" />
          </Link>
          <Button
            type="link"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          />
          <Popconfirm
            title="Are you sure to delete this memory?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <Card>
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex flex-wrap gap-4 items-center">
            <Search
              placeholder="Search memories..."
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              style={{ width: 300 }}
              onSearch={handleSearch}
            />
            <Select
              placeholder="Filter by status"
              value={statusFilter}
              onChange={handleStatusChange}
              size="large"
              style={{ width: 150 }}
            >
              <Option value="all">All Statuses</Option>
              <Option value="ACTIVE">Active</Option>
              <Option value="ARCHIVED">Archived</Option>
              <Option value="DELETED">Deleted</Option>
              <Option value="PENDING">Pending</Option>
            </Select>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            onClick={handleCreate}
          >
            Create Memory
          </Button>
        </div>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={memories}
          loading={loading}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          scroll={{ x: true }}
        />
      </Card>

      <Modal
        title={editingMemory ? 'Edit Memory' : 'Create Memory'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsModalVisible(false)}>
            Cancel
          </Button>,
          <Button
            key="submit"
            type="primary"
            onClick={handleSubmit}
            loading={loading}
          >
            {editingMemory ? 'Update' : 'Create'}
          </Button>,
        ]}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="Title"
            rules={[{ required: false, message: 'Please enter a title' }]}
          >
            <Input placeholder="Memory title" />
          </Form.Item>
          <Form.Item
            name="content"
            label="Content"
            rules={[{ required: true, message: 'Please enter content' }]}
          >
            <Input.TextArea rows={6} placeholder="Memory content" />
          </Form.Item>
          <Form.Item name="tags" label="Tags">
            <Input placeholder="Comma separated tags" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default MemoryExplorerPage;