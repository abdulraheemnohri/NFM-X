import React from "react";
import { Card, Typography, Button, Steps, Divider } from "antd";

const { Title, Text } = Typography;

interface ConflictResolverV2Props {
  conflictId: string;
  conflictType: string;
  severity: string;
  onResolve: (strategy: string) => void;
}

const ConflictResolverV2: React.FC<ConflictResolverV2Props> = ({
  conflictId,
  conflictType,
  severity,
  onResolve
}) => {
  const [currentStep, setCurrentStep] = React.useState(0);

  const steps = [
    {
      title: "Detect",
      description: "Analyzing conflict..."
    },
    {
      title: "Analyze",
      description: "Understanding conflict type..."
    },
    {
      title: "Resolve",
      description: "Applying resolution strategy..."
    }
  ];

  const resolutionStrategies = [
    { name: "Merge", description: "Combine conflicting memories" },
    { name: "Prioritize", description: "Keep the most recent version" },
    { name: "Archive", description: "Archive old versions" },
    { name: "Manual", description: "Mark for manual review" }
  ];

  return (
    <Card style={{ margin: 16 }}>
      <Title level={4}>Conflict Resolver V2</Title>
      <Text type="secondary">ID: {conflictId}</Text>
      <Divider />
      
      <Steps current={currentStep} items={steps} />
      
      <Divider />
      
      <Title level={5}>Type: {conflictType}</Title>
      <Text type="secondary">Severity: {severity}</Text>
      
      <Divider />
      
      <Title level={5}>Resolution Strategies</Title>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {resolutionStrategies.map(strategy => (
          <Button
            key={strategy.name}
            type="primary"
            onClick={() => {
              onResolve(strategy.name);
              setCurrentStep(2);
            }}
          >
            {strategy.name}
          </Button>
        ))}
      </div>
    </Card>
  );
};

export default ConflictResolverV2;