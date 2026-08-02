import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Card,
  Button,
  Tag,
  Space,
  Descriptions,
  Spin,
  Alert,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Divider,
  Badge,
  Row,
  Col,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  ClockCircleOutlined,
  DatabaseOutlined,
  TagOutlined,
} from '@ant-design/icons';
import { api } from '../services/api';
import { Memory, MemoryStatus } from '../types';

function MemoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [memory, setMemory] = useState<Memory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (id) {
      fetchMemory(id);
    }
  }, [id]);

  const fetchMemory = async (memoryId: string) => {
    try {
      setLoading(true);
      const data = await api.getMemory(memoryId);
      setMemory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch memory');
    } finally {
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
    if (!id) return;
    try {
      await api.deleteMemory(id);
      message.success('Memory deleted successfully');
      navigate('/memories');
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'Failed to delete memory');
    }
  };

  const handleSubmit = async () => {
    if (!id) return;
    try {
      const values = await form.validateFields();
      const payload = {
        content: values.content,
        title: values.title,
        tags: values.tags ? values.tags.split(',').map((t: string) => t.trim()) : [],
      };
      await api.updateMemory(id, payload);
      message.success('Memory updated successfully');
      setIsModalVisible(false);
      fetchMemory(id);
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'Failed to update memory');
    }
  };

  const getStatusBadge = (status: MemoryStatus) => {
    switch (status) {
      case 'ACTIVE':
        return <Badge status="success" text="Active" />;
      case 'ARCHIVED':
        return <Badge status="default" text="Archived" />;
      case 'DELETED':
        return <Badge status="error" text="Deleted" />;
      case 'PENDING':
        return <Badge status="warning" text="Pending" />;
      default:
        return <Badge status="processing" text={status} />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error"
        description={error}
        type="error"
        showIcon
        action={
          <Space>
            <Button onClick={() => fetchMemory(id!)}>Retry</Button>
            <Link to="/memories">
              <Button type="link">Back to Memories</Button>
            </Link>
          </Space>
        }
      />
    );
  }

  if (!memory) {
    return (
      <Alert
        message="Memory Not Found"
        description="The requested memory does not exist."
        type="warning"
        showIcon
        action={
          <Link to="/memories">
            <Button type="primary">Back to Memories</Button>
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <Space size="middle" wrap>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/memories')}
          >
            Back
          </Button>
          <h1 className="text-xl font-bold m-0">
            {memory.title || 'Untitled Memory'}
          </h1>
        </Space>
        <Divider />
        <Space size="middle" wrap>
          {getStatusBadge(memory.status)}
          <span className="text-gray-500">
            <ClockCircleOutlined className="mr-1" />
            Created: {new Date(memory.createdAt).toLocaleString()}
          </span>
          <span className="text-gray-500">
            <ClockCircleOutlined className="mr-1" />
            Updated: {new Date(memory.updatedAt).toLocaleString()}
          </span>
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Content">
            <div className="prose max-w-none whitespace-pre-wrap">
              {memory.content}
            </div>
          </Card>

          <Card title="Metadata">
            {Object.entries(memory.metadata || {}).length > 0 ? (
              <Descriptions bordered column={1} size="small">
                {Object.entries(memory.metadata || {}).map(([key, value]) => (
                  <Descriptions.Item key={key} label={key}>
                    {JSON.stringify(value)}
                  </Descriptions.Item>
                ))}
              </Descriptions>
            ) : (
              <p className="text-gray-500">No metadata available</p>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Information">
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="ID">{memory.id}</Descriptions.Item>
              <Descriptions.Item label="Type">{memory.type}</Descriptions.Item>
              <Descriptions.Item label="Version">{memory.version}</Descriptions.Item>
              {memory.parentId && (
                <Descriptions.Item label="Parent ID">{memory.parentId}</Descriptions.Item>
              )}
              <Descriptions.Item label="Source">{memory.source || 'N/A'}</Descriptions.Item>
            </Descriptions>
          </Card>

          <Card title="Tags">
            {memory.tags && memory.tags.length > 0 ? (
              <Space size={[0, 8]} wrap>
                {memory.tags.map((tag) => (
                  <Tag key={tag} color="geekblue">
                    <TagOutlined className="mr-1" />
                    {tag}
                  </Tag>
                ))}
              </Space>
            ) : (
              <p className="text-gray-500">No tags</p>
            )}
          </Card>

          <Card title="Actions">
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Button
                type="primary"
                icon={<EditOutlined />}
                block
                onClick={handleEdit}
              >
                Edit Memory
              </Button>
              <Popconfirm
                title="Are you sure to delete this memory?"
                onConfirm={handleDelete}
                okText="Yes"
                cancelText="No"
              >
                <Button
                  type="primary"
                  danger
                  icon={<DeleteOutlined />}
                  block
                >
                  Delete Memory
                </Button>
              </Popconfirm>
            </Space>
          </Card>
        </Col>
      </Row>

      <Modal
        title="Edit Memory"
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
            Update
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
            <Input.TextArea rows={10} placeholder="Memory content" />
          </Form.Item>
          <Form.Item name="tags" label="Tags">
            <Input placeholder="Comma separated tags" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default MemoryDetailPage;