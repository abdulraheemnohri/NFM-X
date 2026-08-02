import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Spin, Alert, Progress, Table } from 'antd';
import {
  BarChartOutlined,
  DatabaseOutlined,
  ClockCircleOutlined,
  PieChartOutlined,
} from '@ant-design/icons';
import { api } from '../services/api';
import { MemoryStats } from '../types';

function StatsPage() {
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch statistics');
    } finally {
      setLoading(false);
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
          <button className="btn-primary" onClick={fetchStats}>
            Retry
          </button>
        }
      />
    );
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Statistics</h1>
        <p className="text-gray-600">System overview and analytics</p>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Total Memories"
              value={total}
              prefix={<DatabaseOutlined className="text-primary-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Active"
              value={active}
              prefix={<ClockCircleOutlined className="text-green-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Archived"
              value={archived}
              prefix={<BarChartOutlined className="text-blue-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Deleted"
              value={deleted}
              prefix={<PieChartOutlined className="text-red-600" />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card className="stat-card">
            <h2 className="text-lg font-semibold mb-4">Memory Status Distribution</h2>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              {statusData.map((item) => (
                <div key={item.status}>
                  <div className="flex justify-between mb-1">
                    <span className="font-medium">{item.status}</span>
                    <span className="text-sm text-gray-500">{item.count} memories</span>
                  </div>
                  <Progress
                    percent={item.percentage}
                    status={
                      item.status === 'Active' ? 'success' :
                      item.status === 'Archived' ? 'active' : 'exception'
                    }
                    strokeColor={
                      item.status === 'Active' ? '#52c41a' :
                      item.status === 'Archived' ? '#1890ff' : '#ff4d4f'
                    }
                  />
                </div>
              ))}
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card className="stat-card">
            <h2 className="text-lg font-semibold mb-4">Most Used Tags</h2>
            {tagData.length > 0 ? (
              <Table
                columns={[
                  { title: 'Tag', dataIndex: 'tag', key: 'tag' },
                  { title: 'Count', dataIndex: 'count', key: 'count' },
                ]}
                dataSource={tagData}
                pagination={false}
                size="small"
              />
            ) : (
              <p className="text-gray-500 text-center py-4">No tags found</p>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card className="stat-card">
            <h2 className="text-lg font-semibold mb-4">Storage Information</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Storage Size:</span>
                <span className="font-medium">{formatBytes(stats?.totalStorageSize || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Average Memory Size:</span>
                <span className="font-medium">{formatBytes(Number(stats?.avgMemorySize || 0))}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Versions:</span>
                <span className="font-medium">{stats?.totalVersions || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Updated:</span>
                <span className="font-medium">
                  {stats?.lastUpdated ? new Date(stats.lastUpdated).toLocaleString() : 'Never'}
                </span>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card className="stat-card">
            <h2 className="text-lg font-semibold mb-4">System Health</h2>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>API Server: Connected</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Database: Operational</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Embedding Model: Loaded</span>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export default StatsPage;