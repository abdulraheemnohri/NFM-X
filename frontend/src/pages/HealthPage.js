import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
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
            }
            catch (err) {
                setError('Failed to fetch health data');
                setHealthData(null);
            }
            finally {
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
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "System Health" }), _jsx("p", { className: "text-muted-foreground", children: "Monitor the health of all NFM-X subsystems." })] }), _jsx("div", { className: "grid gap-4 md:grid-cols-2 lg:grid-cols-4", children: [1, 2, 3, 4].map((i) => (_jsx(Skeleton, { className: "h-32 w-full" }, i))) })] }) }));
    }
    if (error) {
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsx("div", { children: _jsx("h1", { className: "text-3xl font-bold", children: "System Health" }) }), _jsxs(Alert, { variant: "destructive", children: [_jsx(AlertTitle, { children: "Error" }), _jsx(AlertDescription, { children: error })] })] }) }));
    }
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "System Health" }), _jsx("p", { className: "text-muted-foreground", children: "Monitor the health of all NFM-X subsystems." })] }), _jsxs("div", { className: "grid gap-4 md:grid-cols-2 lg:grid-cols-4", children: [_jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: [_jsx(CardTitle, { className: "text-sm font-medium", children: "Overall Status" }), _jsx("div", { className: "h-4 w-4 rounded-full " + getStatusColor(healthData.status) })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold capitalize", children: healthData.status }), _jsxs("p", { className: "text-xs text-muted-foreground", children: ["Last checked: ", new Date(healthData.timestamp).toLocaleString()] })] })] }), _jsxs(Card, { children: [_jsx(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: _jsx(CardTitle, { className: "text-sm font-medium", children: "System Uptime" }) }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold", children: formatUptime(healthData.uptime) }), _jsx("p", { className: "text-xs text-muted-foreground", children: "Continuous operation time" })] })] }), _jsxs(Card, { children: [_jsx(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: _jsx(CardTitle, { className: "text-sm font-medium", children: "Healthy Subsystems" }) }), _jsxs(CardContent, { children: [_jsxs("div", { className: "text-2xl font-bold", children: [Object.values(healthData.subsystems).filter(s => s.status === 'healthy').length, " / ", Object.keys(healthData.subsystems).length] }), _jsx("p", { className: "text-xs text-muted-foreground", children: "Subsystems operational" })] })] }), _jsxs(Card, { children: [_jsx(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: _jsx(CardTitle, { className: "text-sm font-medium", children: "Average Latency" }) }), _jsxs(CardContent, { children: [_jsxs("div", { className: "text-2xl font-bold", children: [Math.round(Object.values(healthData.subsystems).reduce((sum, s) => sum + s.latency, 0) / Object.keys(healthData.subsystems).length), " ms"] }), _jsx("p", { className: "text-xs text-muted-foreground", children: "Average response time" })] })] })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Subsystem Health" }), _jsx(CardDescription, { children: "Detailed status of each subsystem component." })] }), _jsx(CardContent, { children: _jsx("div", { className: "grid gap-4", children: Object.entries(healthData.subsystems).map(([name, subsystem]) => (_jsxs("div", { className: "flex items-center justify-between p-4 border rounded", children: [_jsxs("div", { children: [_jsx("h3", { className: "font-medium capitalize", children: name.replace('_', ' ') }), subsystem.connected !== undefined && (_jsx("p", { className: "text-sm text-muted-foreground", children: subsystem.connected ? 'Connected' : 'Disconnected' })), subsystem.backends && (_jsxs("p", { className: "text-sm text-muted-foreground", children: ["Backends: ", subsystem.backends.join(', ')] })), subsystem.disk_usage && (_jsxs("p", { className: "text-sm text-muted-foreground", children: ["Disk Usage: ", (subsystem.disk_usage * 100).toFixed(1), "%"] })), subsystem.hit_rate && (_jsxs("p", { className: "text-sm text-muted-foreground", children: ["Hit Rate: ", (subsystem.hit_rate * 100).toFixed(1), "%"] }))] }), _jsxs("div", { className: "flex items-center space-x-2", children: [_jsx(Badge, { variant: subsystem.status === 'healthy' ? 'default' : subsystem.status === 'degraded' ? 'secondary' : 'destructive', children: subsystem.status }), _jsxs("span", { className: "text-sm text-muted-foreground", children: [subsystem.latency, "ms"] })] })] }, name))) }) })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "System Checks" }), _jsx(CardDescription, { children: "Individual health check results." })] }), _jsx(CardContent, { children: _jsx("div", { className: "grid gap-4 md:grid-cols-2 lg:grid-cols-4", children: Object.entries(healthData.checks).map(([name, check]) => (_jsxs("div", { className: "p-4 border rounded", children: [_jsx("h3", { className: "font-medium capitalize mb-2", children: name.replace('_', ' ') }), _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("span", { className: "text-2xl font-bold", children: [check.value, check.unit] }), _jsx("div", { className: "h-3 w-3 rounded-full " + getStatusColor(check.status) })] }), _jsx(Badge, { variant: check.status === 'healthy' ? 'default' : 'destructive', className: "mt-2", children: check.status })] }, name))) }) })] }), _jsx("div", { className: "flex justify-center", children: _jsx(Button, { onClick: () => window.location.reload(), children: "Refresh Health Data" }) })] }) }));
}
