import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function HealthPage() {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchHealth() {
      try {
        setLoading(true);
        // Simulate API call to /api/health/detailed
        const mockHealth = {
          status: 'healthy',
          timestamp: new Date().toISOString(),
          uptime: 86400,
          subsystems: {
            database: { status: 'healthy', latency: 5, connected: true },
            vector_store: { status: 'healthy', latency: 12, connected: true },
            ocr: { status: 'healthy', latency: 25, backends: ['EasyOCR', 'Tesseract'] },
            storage: { status: 'healthy', disk_usage: 0.65, connected: true },
            cache: { status: 'healthy', hit_rate: 0.85, connected: true }
          },
          checks: {
            memory_usage: { status: 'healthy', value: 0.45, unit: '%' },
            cpu_usage: { status: 'healthy', value: 0.23, unit: '%' },
            disk_space: { status: 'healthy', value: 0.65, unit: '%' },
            api_responsiveness: { status: 'healthy', latency: 45, unit: 'ms' }
          }
        };
        setHealthData(mockHealth);
        setError(null);
      } catch (err) {
        setError('Failed to fetch health data');
        setHealthData(null);
      } finally {
        setLoading(false);
      }
    }
    fetchHealth();

    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      case 'unhealthy':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return days + 'd ' + hours + 'h ' + minutes + 'm ' + secs + 's';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">System Health</h1>
            <p className="text-muted-foreground">Monitor the health of all NFM-X subsystems.</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">System Health</h1>
          </div>
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">System Health</h1>
          <p className="text-muted-foreground">Monitor the health of all NFM-X subsystems.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Status</CardTitle>
              <div className={"h-4 w-4 rounded-full " + getStatusColor(healthData.status)} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold capitalize">{healthData.status}</div>
              <p className="text-xs text-muted-foreground">Last checked: {new Date(healthData.timestamp).toLocaleString()}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatUptime(healthData.uptime)}</div>
              <p className="text-xs text-muted-foreground">Continuous operation time</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Healthy Subsystems</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Object.values(healthData.subsystems).filter(s => s.status === 'healthy').length} / {Object.keys(healthData.subsystems).length}
              </div>
              <p className="text-xs text-muted-foreground">Subsystems operational</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Latency</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(Object.values(healthData.subsystems).reduce((sum, s) => sum + s.latency, 0) / Object.keys(healthData.subsystems).length)} ms
              </div>
              <p className="text-xs text-muted-foreground">Average response time</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Subsystem Health</CardTitle>
            <CardDescription>
              Detailed status of each subsystem component.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              {Object.entries(healthData.subsystems).map(([name, subsystem]) => (
                <div key={name} className="flex items-center justify-between p-4 border rounded">
                  <div>
                    <h3 className="font-medium capitalize">{name.replace('_', ' ')}</h3>
                    {subsystem.connected !== undefined && (
                      <p className="text-sm text-muted-foreground">
                        {subsystem.connected ? 'Connected' : 'Disconnected'}
                      </p>
                    )}
                    {subsystem.backends && (
                      <p className="text-sm text-muted-foreground">
                        Backends: {subsystem.backends.join(', ')}
                      </p>
                    )}
                    {subsystem.disk_usage && (
                      <p className="text-sm text-muted-foreground">
                        Disk Usage: {(subsystem.disk_usage * 100).toFixed(1)}%
                      </p>
                    )}
                    {subsystem.hit_rate && (
                      <p className="text-sm text-muted-foreground">
                        Hit Rate: {(subsystem.hit_rate * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={subsystem.status === 'healthy' ? 'default' : subsystem.status === 'degraded' ? 'secondary' : 'destructive'}>
                      {subsystem.status}
                    </Badge>
                    <span className="text-sm text-muted-foreground">{subsystem.latency}ms</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Checks</CardTitle>
            <CardDescription>
              Individual health check results.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {Object.entries(healthData.checks).map(([name, check]) => (
                <div key={name} className="p-4 border rounded">
                  <h3 className="font-medium capitalize mb-2">{name.replace('_', ' ')}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">{check.value}{check.unit}</span>
                    <div className={"h-3 w-3 rounded-full " + getStatusColor(check.status)} />
                  </div>
                  <Badge variant={check.status === 'healthy' ? 'default' : 'destructive'} className="mt-2">
                    {check.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-center">
          <Button onClick={() => window.location.reload()}>
            Refresh Health Data
          </Button>
        </div>
      </div>
    </div>
  );
}