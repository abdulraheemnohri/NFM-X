import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic, Spin, Alert } from 'antd';
import {
  DatabaseOutlined,
  SearchOutlined,
  AlertOutlined,
  ProjectOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { api } from '../services/api';
import { MemoryStats } from '../types';

function HomePage() {
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">NFM-X Dashboard</h1>
        <p className="text-gray-600">Non-Forgettable Memory Layer</p>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={8}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Total Memories"
              value={stats?.totalMemories || 0}
              prefix={<DatabaseOutlined className="text-primary-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Active Memories"
              value={stats?.activeMemories || 0}
              prefix={<ClockCircleOutlined className="text-green-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Total Versions"
              value={stats?.totalVersions || 0}
              prefix={<ProjectOutlined className="text-purple-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Storage Size"
              value={formatBytes(stats?.totalStorageSize || 0)}
              prefix={<DatabaseOutlined className="text-blue-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Avg Memory Size"
              value={formatBytes(Number(stats?.avgMemorySize || 0))}
              prefix={<SearchOutlined className="text-orange-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className="stat-card card-hover">
            <Statistic
              title="Conflicts"
              value={0}
              prefix={<AlertOutlined className="text-red-600" />}
            />
          </Card>
        </Col>
      </Row>

      <Card className="stat-card">
        <h2 className="text-xl font-semibold mb-4">About NFM-X</h2>
        <p className="text-gray-600 mb-4">
          NFM-X (Non-Forgettable Memory Layer) is a production-grade, model-independent, 
          local-first long-term memory layer for AI systems.
        </p>
        <ul className="list-disc list-inside text-gray-600 space-y-2">
          <li>Never forget: Once memory is committed, it is never silently overwritten or lost</li>
          <li>Versioning: New information creates a new version, history is preserved</li>
          <li>Provenance: Every memory has a source and lineage</li>
          <li>Portability: Memory remains portable between models and applications</li>
        </ul>
      </Card>
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

export default HomePage;