import React from "react";
import { Card, Typography, List, Divider } from "antd";

const { Title, Text } = Typography;

interface MemoryVersion {
  id: string;
  version: number;
  content: string;
  createdAt: string;
  tags: string[];
}

const MemoryV2Page: React.FC = () => {
  const [versions, setVersions] = React.useState<MemoryVersion[]>([]);
  const [selectedVersion, setSelectedVersion] = React.useState<MemoryVersion | null>(null);

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Memory V2 - Versioned Explorer</Title>
      <Text type="secondary">
        Enhanced memory management with complete version history and rollback capability
      </Text>
      
      <Divider />
      
      <div style={{ display: "flex", gap: 24 }}>
        <div style={{ flex: 1 }}>
          <Card title="Version History">
            <List
              dataSource={versions}
              renderItem={(item) => (
                <List.Item
                  onClick={() => setSelectedVersion(item)}
                  style={{ cursor: "pointer" }}
                >
                  <List.Item.Meta
                    title={`Version ${item.version}`}
                    description={item.createdAt}
                  />
                  <div>
                    {item.tags.map(tag => (
                      <span key={tag} style={{ marginRight: 8 }}>
                        #{tag}
                      </span>
                    ))}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </div>
        
        <div style={{ flex: 1 }}>
          <Card title="Version Content">
            {selectedVersion ? (
              <div>
                <Title level={4}>Version {selectedVersion.version}</Title>
                <Text type="secondary">
                  Created: {selectedVersion.createdAt}
                </Text>
                <Divider />
                <pre style={{ whiteSpace: "pre-wrap" }}>{selectedVersion.content}</pre>
              </div>
            ) : (
              <Text type="secondary">Select a version to view content</Text>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MemoryV2Page;