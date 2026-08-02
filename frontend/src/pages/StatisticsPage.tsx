import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts';

export default function StatisticsPage() {
  const [timeRange, setTimeRange] = useState('30d');
  const [activeTab, setActiveTab] = useState('overview');

  const timeRanges = [
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
    { value: '1y', label: 'Last Year' },
    { value: 'all', label: 'All Time' }
  ];

  const memoryStats = {
    total: 12478,
    today: 45,
    thisWeek: 321,
    thisMonth: 1247,
    growth: 18.5
  };

  const memoryByType = [
    { name: 'Text', value: 5432, percentage: 43.5 },
    { name: 'Images', value: 3210, percentage: 25.7 },
    { name: 'Documents', value: 2567, percentage: 20.6 },
    { name: 'Audio', value: 890, percentage: 7.1 },
    { name: 'Video', value: 379, percentage: 3.1 }
  ];

  const dailyActivity = [
    { date: 'Mon', memories: 120, documents: 8 },
    { date: 'Tue', memories: 150, documents: 12 },
    { date: 'Wed', memories: 95, documents: 6 },
    { date: 'Thu', memories: 180, documents: 15 },
    { date: 'Fri', memories: 210, documents: 18 },
    { date: 'Sat', memories: 145, documents: 10 },
    { date: 'Sun', memories: 85, documents: 5 }
  ];

  const monthlyGrowth = [
    { month: 'Jan', count: 800 },
    { month: 'Feb', count: 950 },
    { month: 'Mar', count: 1100 },
    { month: 'Apr', count: 1350 },
    { month: 'May', count: 1600 },
    { month: 'Jun', count: 1850 }
  ];

  const apiStats = {
    totalRequests: 45678,
    successRate: 98.5,
    avgResponseTime: 45,
    errors: 682
  };

  const errorTypes = [
    { name: 'Timeout', value: 234 },
    { name: 'Validation', value: 189 },
    { name: 'Not Found', value: 156 },
    { name: 'Server Error', value: 103 }
  ];

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Statistics</h1>
            <p className="text-muted-foreground">Detailed analytics and insights for your NFM-X system.</p>
          </div>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent>
              {timeRanges.map((range) => (
                <SelectItem key={range.value} value={range.value}>
                  {range.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="memory">Memory Stats</TabsTrigger>
            <TabsTrigger value="api">API Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Memories</CardTitle>
                  <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{memoryStats.total.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">+{memoryStats.growth}% this month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Today's Activity</CardTitle>
                  <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{memoryStats.today}</div>
                  <p className="text-xs text-muted-foreground">New memories added today</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">API Requests</CardTitle>
                  <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9V3m0 18a9 9 0 009-9M3 12a9 9 0 019-9" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{apiStats.totalRequests.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">{apiStats.successRate}% success rate</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
                  <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2.4 GB</div>
                  <p className="text-xs text-muted-foreground">Of 10 GB available</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Daily Activity</CardTitle>
                  <CardDescription>Memories and documents added per day</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dailyActivity}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="memories" fill="#3b82f6" name="Memories" />
                      <Bar dataKey="documents" fill="#8b5cf6" name="Documents" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Monthly Growth</CardTitle>
                  <CardDescription>Memory growth over the last 6 months</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={monthlyGrowth}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} name="Memories" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="memory" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Memory by Type</CardTitle>
                  <CardDescription>Distribution of memories by content type</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={memoryByType}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8b5cf6"
                        dataKey="value"
                        label={({ name, percent }) => name + ' ' + (percent * 100).toFixed(1) + '%'}
                      >
                        {memoryByType.map((entry, index) => (
                          <Cell key={index} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Memory Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>This Week</span>
                      <span className="font-medium">{memoryStats.thisWeek} memories</span>
                    </div>
                    <div className="flex justify-between">
                      <span>This Month</span>
                      <span className="font-medium">{memoryStats.thisMonth} memories</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Growth Rate</span>
                      <span className="font-medium text-green-600">+{memoryStats.growth}%</span>
                    </div>
                  </div>
                  <div className="space-y-2 pt-4 border-t">
                    {memoryByType.map((type) => (
                      <div key={type.name} className="flex justify-between">
                        <span>{type.name}</span>
                        <span className="font-medium">{type.value.toLocaleString()} ({type.percentage}%)</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="api" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{apiStats.totalRequests.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">All API requests</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{apiStats.successRate}%</div>
                  <p className="text-xs text-muted-foreground">Successful requests</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{apiStats.avgResponseTime} ms</div>
                  <p className="text-xs text-muted-foreground">Average latency</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Error Types</CardTitle>
                  <CardDescription>API errors by type</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={errorTypes}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" fill="#ef4444" name="Errors" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>API Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Total Requests</span>
                      <span className="font-medium">{apiStats.totalRequests.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Successful</span>
                      <span className="font-medium text-green-600">{(apiStats.totalRequests * apiStats.successRate / 100).toFixed(0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Failed</span>
                      <span className="font-medium text-red-600">{apiStats.errors}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Success Rate</span>
                      <span className="font-medium">{apiStats.successRate}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Avg Response Time</span>
                      <span className="font-medium">{apiStats.avgResponseTime} ms</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}