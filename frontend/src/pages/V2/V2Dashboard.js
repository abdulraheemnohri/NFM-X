import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
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
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "V2 Dashboard" }), _jsx("p", { className: "text-muted-foreground", children: "NFM-X Version 2 Overview" })] }), _jsx("div", { className: "grid gap-4 md:grid-cols-2 lg:grid-cols-4", children: stats.map((stat) => (_jsxs(Card, { children: [_jsx(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: _jsx(CardTitle, { className: "text-sm font-medium", children: stat.name }) }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold", children: stat.value }), _jsx("p", { className: "text-xs text-muted-foreground", children: stat.change })] })] }, stat.name))) }), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "V1 vs V2 Memory Growth" }), _jsx(CardDescription, { children: "Comparison of memory growth between versions" })] }), _jsx(CardContent, { children: _jsx(ResponsiveContainer, { width: "100%", height: 300, children: _jsxs(LineChart, { data: memoryData, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3" }), _jsx(XAxis, { dataKey: "name" }), _jsx(YAxis, {}), _jsx(Tooltip, {}), _jsx(Legend, {}), _jsx(Line, { type: "monotone", dataKey: "v1", stroke: "#3b82f6", strokeWidth: 2, name: "V1" }), _jsx(Line, { type: "monotone", dataKey: "v2", stroke: "#8b5cf6", strokeWidth: 2, name: "V2" })] }) }) })] }), _jsxs("div", { className: "grid gap-4 md:grid-cols-2", children: [_jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "Quick Access" }) }), _jsxs(CardContent, { className: "space-y-4", children: [_jsx(Button, { asChild: true, className: "w-full", children: _jsx(Link, { to: "/v2/memories", children: "V2 Memories" }) }), _jsx(Button, { asChild: true, variant: "outline", className: "w-full", children: _jsx(Link, { to: "/v2/graph", children: "V2 Graph" }) }), _jsx(Button, { asChild: true, variant: "outline", className: "w-full", children: _jsx(Link, { to: "/v2/conflicts", children: "V2 Conflicts" }) }), _jsx(Button, { asChild: true, variant: "outline", className: "w-full", children: _jsx(Link, { to: "/", children: "Back to V4" }) })] })] }), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "V2 Features" }) }), _jsx(CardContent, { children: _jsxs("div", { className: "space-y-2", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "h-2 w-2 rounded-full bg-green-500" }), _jsx("span", { children: "Enhanced Memory Management" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "h-2 w-2 rounded-full bg-green-500" }), _jsx("span", { children: "Advanced Search Capabilities" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "h-2 w-2 rounded-full bg-green-500" }), _jsx("span", { children: "Graph Relationships" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "h-2 w-2 rounded-full bg-green-500" }), _jsx("span", { children: "Enhanced Statistics" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "h-2 w-2 rounded-full bg-green-500" }), _jsx("span", { children: "Conflict Resolution" })] })] }) })] })] })] }) }));
}
