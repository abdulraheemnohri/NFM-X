import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Tag, Space, Spin, Alert, Modal, Descriptions } from 'antd';
import {
  AlertOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { api } from '../services/api';
import { Conflict, ConflictSeverity, ConflictType } from '../types';

interface ConflictWithKey extends Conflict {
  key: string;
}

function ConflictsPage() {
  const [conflicts, setConflicts] = useState<ConflictWithKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedConflict, setSelectedConflict] = useState<Conflict | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  useEffect(() => {
    fetchConflicts();
  }, []);

  const fetchConflicts = async () => {
    try {
      setLoading(true);
      const data = await api.listConflicts({ limit: 50, offset: 0, resolved: false });
      setConflicts(
        data.items.map((c: Conflict) => ({ ...c, key: c.id }))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch conflicts');
    } finally {
      setLoading(false);
    }
  };

  const handleDetect = async () => {
    try {
      setLoading(true);
      await api.detectConflicts();
      fetchConflicts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to detect conflicts');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (conflictId: string) => {
    try {
      await api.resolveConflict(conflictId);
      fetchConflicts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve conflict');
    }
  };

  const getSeverityTag = (severity: ConflictSeverity) => {
    switch (severity) {
      case 'LOW':
        return <Tag color="green" icon={<CheckCircleOutlined />}>
          Low
        </Tag>;
      case 'MEDIUM':
        return <Tag color="orange" icon={<ExclamationCircleOutlined />}>
          Medium
        </Tag>;
      case 'HIGH':
        return <Tag color="red" icon={<CloseCircleOutlined />}>
          High
        </Tag>;
      default:
        return <Tag color="gray">{severity}</Tag>;
    }
  };

  const getTypeTag = (type: ConflictType) => {
    switch (type) {
      case 'DUPLICATE':
        return <Tag color="blue">Duplicate</Tag>;
      case 'CONTRADICTION':
        return <Tag color="red">Contradiction</Tag>;
      case 'AMBIGUITY':
        return <Tag color="purple">Ambiguity</Tag>;
      default:
        return <Tag color="gray">{type}</Tag>;
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
      render: (desc: string) => (
        <div className="max-w-md truncate">{desc}</div>
      ),
    },
    {
      title: 'Memories',
      dataIndex: 'memoryIds',
      key: 'memoryIds',
      render: (ids: string[]) => (
        <Space size={[0, 8]} wrap>
          {ids.map((id) => (
            <Tag key={id} color="geekblue">{id.substring(0, 8)}...</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'Detected',
      dataIndex: 'detectedAt',
      key: 'detectedAt',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ConflictWithKey) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => {
              setSelectedConflict(record);
              setIsModalVisible(true);
            }}
          />
          <Button
            type="link"
            size="small"
            onClick={() => handleResolve(record.id)}
          >
            Resolve
          </Button>
        </Space>
      ),
    },
  ];

  if (loading && !conflicts.length) {
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
          <Button onClick={fetchConflicts}>Retry</Button>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">Conflicts</h1>
          <Button
            type="primary"
            icon={<AlertOutlined />}
            onClick={handleDetect}
            loading={loading}
          >
            Detect Conflicts
          </Button>
        </div>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={conflicts}
          loading={loading}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          scroll={{ x: true }}
        />
      </Card>

      <Modal
        title="Conflict Details"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button
            key="resolve"
            type="primary"
            onClick={() => {
              if (selectedConflict) {
                handleResolve(selectedConflict.id);
              }
              setIsModalVisible(false);
            }}
          >
            Resolve Conflict
          </Button>,
          <Button key="cancel" onClick={() => setIsModalVisible(false)}>
            Close
          </Button>,
        ]}
      >
        {selectedConflict && (
          <div className="space-y-4">
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="ID">{selectedConflict.id}</Descriptions.Item>
              <Descriptions.Item label="Type">
                {getTypeTag(selectedConflict.type)}
              </Descriptions.Item>
              <Descriptions.Item label="Severity">
                {getSeverityTag(selectedConflict.severity)}
              </Descriptions.Item>
              <Descriptions.Item label="Detected At">
                {new Date(selectedConflict.detectedAt).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="Resolved">
                {selectedConflict.resolved ? 'Yes' : 'No'}
              </Descriptions.Item>
            </Descriptions>

            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="Description">
                {selectedConflict.description}
              </Descriptions.Item>
            </Descriptions>

            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="Affected Memories">
                <Space size={[0, 8]} wrap>
                  {selectedConflict.memoryIds.map((id) => (
                    <Tag key={id} color="geekblue">{id}</Tag>
                  ))}
                </Space>
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default ConflictsPage;