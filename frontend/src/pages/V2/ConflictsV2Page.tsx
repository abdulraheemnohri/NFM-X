import React from "react";
import { Card, Typography, Table, Button, Tag } from "antd";

const { Title, Text } = Typography;

interface Conflict {
  id: string;
  memoryIds: string[];
  type: string;
  severity: string;
  status: string;
  detectedAt: string;
  resolution: string | null;
}

const ConflictsV2Page: React.FC = () => {
  const [conflicts, setConflicts] = React.useState<Conflict[]>([]);

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id"
    },
    {
      title: "Type",
      dataIndex: "type",
      key: "type"
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      render: (severity: string) => {
        let color = "default";
        if (severity === "high" || severity === "critical") color = "red";
        else if (severity === "medium") color = "orange";
        else if (severity === "low") color = "green";
        return <Tag color={color}>{severity}</Tag>;
      }
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => {
        let color = "default";
        if (status === "resolved") color = "green";
        else if (status === "resolving") color = "blue";
        else if (status === "detected") color = "orange";
        return <Tag color={color}>{status}</Tag>;
      }
    },
    {
      title: "Memories",
      dataIndex: "memoryIds",
      key: "memoryIds",
      render: (ids: string[]) => ids.join(", ")
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: any, record: Conflict) => (
        <Button type="primary" size="small">
          Auto-Resolve
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Conflicts V2 - AI Auto-Resolution</Title>
      <Text type="secondary">
        Advanced conflict detection and automatic resolution
      </Text>
      
      <Card style={{ marginTop: 24 }}>
        <Button type="primary" style={{ marginBottom: 16 }}>
          Detect All Conflicts
        </Button>
        <Button style={{ marginLeft: 8, marginBottom: 16 }}>
          Auto-Resolve All
        </Button>
        
        <Table
          columns={columns}
          dataSource={conflicts}
          rowKey="id"
        />
      </Card>
    </div>
  );
};

export default ConflictsV2Page;