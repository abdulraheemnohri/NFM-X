import React from "react";
import { Card, Typography } from "antd";

const { Title, Text } = Typography;

interface MemoryGraphV2Props {
  memoryId: string;
  connections: number;
  depth: number;
}

const MemoryGraphV2: React.FC<MemoryGraphV2Props> = ({ memoryId, connections, depth }) => {
  return (
    <Card style={{ margin: 16 }}>
      <Title level={4}>Memory Graph V2</Title>
      <Text>ID: {memoryId}</Text>
      <div style={{ marginTop: 16 }}>
        <Text type="secondary">Connections: {connections}</Text>
      </div>
      <div>
        <Text type="secondary">Traversal Depth: {depth}</Text>
      </div>
    </Card>
  );
};

export default MemoryGraphV2;