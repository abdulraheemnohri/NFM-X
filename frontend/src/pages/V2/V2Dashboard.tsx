import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts';

export default function V2Dashboard() {
  const stats = [
    { name: 'Total Memories', value: 1247, change: '+12%' },
    { name: 'V2 Memories', value: 452, change: '+8%' },
    { name: 'Active Sessions', value: 42, change: '+5%' },
    { name: 'Storage Used', value: '2.4 GB', change: '+0.3 GB' },
  ];

  const memoryData = [
    { name: 'Jan', v1: 200, v2: 150 },
    { name: 'Feb', v1: 250, v2: 180 },
    { name: 'Mar', v1: 300, v2: 220 },
    { name: 'Apr', v1: 350, v2: 280 },
    { name: 'May', v1: 400, v2: 320 },
    { name: 'Jun', v1: 450, v2: 380 },
  ];

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'];

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">V2 Dashboard</h1>
          <p className="text-muted-foreground">NFM-X Version 2 Overview</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.name}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.change}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>V1 vs V2 Memory Growth</CardTitle>
            <CardDescription>Comparison of memory growth between versions</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={memoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="v1" stroke="#3b82f6" strokeWidth={2} name="V1" />
                <Line type="monotone" dataKey="v2" stroke="#8b5cf6" strokeWidth={2} name="V2" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Quick Access</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button asChild className="w-full">
                <Link to="/v2/memories">V2 Memories</Link>
              </Button>
              <Button asChild variant="outline" className="w-full">
                <Link to="/v2/graph">V2 Graph</Link>
              </Button>
              <Button asChild variant="outline" className="w-full">
                <Link to="/v2/conflicts">V2 Conflicts</Link>
              </Button>
              <Button asChild variant="outline" className="w-full">
                <Link to="/">Back to V4</Link>
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>V2 Features</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span>Enhanced Memory Management</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span>Advanced Search Capabilities</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span>Graph Relationships</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span>Enhanced Statistics</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span>Conflict Resolution</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}