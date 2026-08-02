import React, { useEffect, useState } from 'react';
import { Card, Spin, Alert, Button, Space, Table, Tag } from 'antd';
import {
  ProjectOutlined,
  ReloadOutlined,
  NodeIndexOutlined,
  BranchOutlined,
} from '@ant-design/icons';
import { api } from '../services/api';
import { GraphData, GraphNode, GraphEdge } from '../types';
import { Row, Col } from 'antd';

function GraphPage() {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGraph();
  }, []);

  const fetchGraph = async () => {
    try {
      setLoading(true);
      const data = await api.getGraph();
      setGraphData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch graph data');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !graphData) {
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
          <Button onClick={fetchGraph}>Retry</Button>
        }
      />
    );
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
      render: (type: string) => <Tag color="geekblue">{type}</Tag>,
    },
  ];

  const edgeColumns = [
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      render: (source: string) => <Tag color="blue">{source.substring(0, 8)}...</Tag>,
    },
    {
      title: 'Target',
      dataIndex: 'target',
      key: 'target',
      render: (target: string) => <Tag color="green">{target.substring(0, 8)}...</Tag>,
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => <Tag color="purple">{type}</Tag>,
    },
    {
      title: 'Weight',
      dataIndex: 'weight',
      key: 'weight',
      render: (weight: number) => <Tag color="orange">{weight.toFixed(2)}</Tag>,
    },
  ];

  return (
    <div className="space-y-4">
      <Card>
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Memory Graph</h1>
            <p className="text-gray-600">Visualize memory relationships</p>
          </div>
          <Button
            type="default"
            icon={<ReloadOutlined />}
            onClick={fetchGraph}
            loading={loading}
          >
            Refresh
          </Button>
        </div>
      </Card>

      {graphData && (
        <div className="space-y-4">
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Card className="stat-card card-hover">
                <Space direction="vertical" size="middle">
                  <NodeIndexOutlined className="text-2xl text-primary-600" />
                  <div>
                    <div className="text-2xl font-bold">{graphData.nodeCount}</div>
                    <div className="text-sm text-gray-500">Nodes</div>
                  </div>
                </Space>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card className="stat-card card-hover">
                <Space direction="vertical" size="middle">
                  <BranchOutlined className="text-2xl text-green-600" />
                  <div>
                    <div className="text-2xl font-bold">{graphData.edgeCount}</div>
                    <div className="text-sm text-gray-500">Edges</div>
                  </div>
                </Space>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card className="stat-card card-hover">
                <Space direction="vertical" size="middle">
                  <ProjectOutlined className="text-2xl text-purple-600" />
                  <div>
                    <div className="text-2xl font-bold">
                      {graphData.nodes.length > 0
                        ? new Set(graphData.nodes.map((n: GraphNode) => n.type)).size
                        : 0}
                    </div>
                    <div className="text-sm text-gray-500">Node Types</div>
                  </div>
                </Space>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card className="stat-card card-hover">
                <Space direction="vertical" size="middle">
                  <ProjectOutlined className="text-2xl text-orange-600" />
                  <div>
                    <div className="text-2xl font-bold">
                      {graphData.edges.length > 0
                        ? new Set(graphData.edges.map((e: GraphEdge) => e.type)).size
                        : 0}
                    </div>
                    <div className="text-sm text-gray-500">Edge Types</div>
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="Nodes">
                <Table
                  columns={nodeColumns}
                  dataSource={graphData.nodes.map((n: GraphNode) => ({ ...n, key: n.id }))}
                  pagination={{ pageSize: 10 }}
                  scroll={{ y: 400 }}
                />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="Edges (Relationships)">
                <Table
                  columns={edgeColumns}
                  dataSource={graphData.edges.map((e: GraphEdge) => ({
                    ...e,
                    key: `${e.source}-${e.target}-${e.type}`,
                  }))}
                  pagination={{ pageSize: 10 }}
                  scroll={{ y: 400 }}
                />
              </Card>
            </Col>
          </Row>

          {graphData.nodes.length > 0 && (
            <Card title="Graph Visualization">
              <div className="bg-gray-50 p-8 rounded-lg text-center text-gray-500">
                <ProjectOutlined className="text-4xl mb-4" />
                <p>Interactive graph visualization coming soon...</p>
                <p className="text-sm mt-2">
                  Use the tables above to explore nodes and relationships
                </p>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}

export default GraphPage;