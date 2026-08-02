import React from "react";
import { Typography, Card, List, Button } from "antd";
const { Title } = Typography;
export default function MemoryExplorerPage() { return <div className="p-6"><Title level={2}>Memory Explorer</Title><Card><List dataSource={[]} renderItem={(item) => <List.Item>{item}</List.Item>} /></Card></div>; }