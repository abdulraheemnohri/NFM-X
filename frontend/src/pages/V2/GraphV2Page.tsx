import React from "react";
import { Card, Typography, Graph } from "antd";

const { Title, Text } = Typography;

interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

interface GraphEdge {
  source: string;
  target: string;
  label: string;
}

const GraphV2Page: React.FC = () => {
  const [nodes, setNodes] = React.useState<GraphNode[]>([]);
  const [edges, setEdges] = React.useState<GraphEdge[]>([]);

  const graphData = {
    nodes,
    edges
  };

  const graphConfig = {
    nodeLabel: {
      style: {
        fill: "#000"
      }
    },
    edgeLabel: {
      style: {
        fill: "#666"
      }
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Memory Graph V2</Title>
      <Text type="secondary">
        Interactive visualization of memory relationships and connections
      </Text>
      
      <Card style={{ marginTop: 24 }}>
        <Graph
          data={graphData}
          config={graphConfig}
          style={{ height: 600, width: "100%" }}
        />
      </Card>
    </div>
  );
};

export default GraphV2Page;