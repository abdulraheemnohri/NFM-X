import React from "react";
import { Typography, Card, Statistic } from "antd";
const { Title } = Typography;
export default function StatsPage() { return <div className="p-6"><Title level={2}>Statistics</Title><Card><Statistic title="Total Memories" value={0} /></Card></div>; }