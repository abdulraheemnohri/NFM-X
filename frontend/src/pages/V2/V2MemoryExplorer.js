import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
export default function V2MemoryExplorer() {
    const [memories, setMemories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterType, setFilterType] = useState('all');
    useEffect(() => {
        fetchMemories();
    }, [searchQuery, filterType]);
    const fetchMemories = async () => {
        try {
            setLoading(true);
            // Simulate API call
            const mockMemories = [
                { id: 1, content: 'Sample memory content for V2', subtype: 'text', confidence: 0.95, created_at: '2024-01-15T10:00:00Z' },
                { id: 2, content: 'Another memory with different content', subtype: 'text', confidence: 0.88, created_at: '2024-01-14T09:30:00Z' },
                { id: 3, content: 'Memory with table data', subtype: 'table', confidence: 0.92, created_at: '2024-01-13T11:15:00Z' },
                { id: 4, content: 'Key value pair memory', subtype: 'key_value', confidence: 0.85, created_at: '2024-01-12T08:45:00Z' },
                { id: 5, content: 'Entity extraction memory', subtype: 'entity', confidence: 0.91, created_at: '2024-01-11T13:20:00Z' },
            ].filter(m => {
                const matchesSearch = m.content.toLowerCase().includes(searchQuery.toLowerCase()) || searchQuery === '';
                const matchesFilter = filterType === 'all' || m.subtype === filterType;
                return matchesSearch && matchesFilter;
            });
            setMemories(mockMemories);
        }
        catch (err) {
            console.error('Failed to fetch memories:', err);
        }
        finally {
            setLoading(false);
        }
    };
    const memoryTypes = ['all', 'text', 'table', 'key_value', 'entity'];
    if (loading) {
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "V2 Memory Explorer" }), _jsx("p", { className: "text-muted-foreground", children: "Browse and search V2 memories" })] }), _jsxs("div", { className: "grid gap-4", children: [_jsx(Skeleton, { className: "h-10 w-full" }), _jsx(Skeleton, { className: "h-96 w-full" })] })] }) }));
    }
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "V2 Memory Explorer" }), _jsx("p", { className: "text-muted-foreground", children: "Browse and search your V2 memories with advanced filtering." })] }), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "Search & Filter" }) }), _jsx(CardContent, { className: "space-y-4", children: _jsxs("div", { className: "grid gap-4 md:grid-cols-2", children: [_jsx("div", { className: "space-y-2", children: _jsx(Input, { placeholder: "Search memories...", value: searchQuery, onChange: (e) => setSearchQuery(e.target.value) }) }), _jsx("div", { className: "space-y-2", children: _jsxs(Select, { value: filterType, onValueChange: setFilterType, children: [_jsx(SelectTrigger, { children: _jsx(SelectValue, { placeholder: "Filter by type" }) }), _jsx(SelectContent, { children: memoryTypes.map((type) => (_jsx(SelectItem, { value: type, children: type.replace('_', ' ') }, type))) })] }) })] }) })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsxs(CardTitle, { children: ["V2 Memories (", memories.length, ")"] }), _jsx(CardDescription, { children: "All your V2 memories with enhanced features" })] }), _jsx(CardContent, { children: _jsxs(Table, { children: [_jsx(TableHeader, { children: _jsxs(TableRow, { children: [_jsx(TableHead, { children: "ID" }), _jsx(TableHead, { children: "Content" }), _jsx(TableHead, { children: "Type" }), _jsx(TableHead, { children: "Confidence" }), _jsx(TableHead, { children: "Created" }), _jsx(TableHead, { className: "text-right", children: "Actions" })] }) }), _jsx(TableBody, { children: memories.length === 0 ? (_jsx(TableRow, { children: _jsx(TableCell, { colSpan: 6, className: "h-24 text-center", children: "No V2 memories found." }) })) : (memories.map((memory) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: memory.id }), _jsx(TableCell, { className: "max-w-96 truncate", children: memory.content }), _jsx(TableCell, { children: _jsx(Badge, { variant: "outline", children: memory.subtype }) }), _jsxs(TableCell, { children: [(memory.confidence * 100).toFixed(1), "%"] }), _jsx(TableCell, { children: new Date(memory.created_at).toLocaleDateString() }), _jsxs(TableCell, { className: "text-right", children: [_jsx(Button, { variant: "ghost", size: "sm", children: "View" }), _jsx(Button, { variant: "ghost", size: "sm", children: "Edit" })] })] }, memory.id)))) })] }) })] }), _jsx("div", { className: "flex justify-end", children: _jsx(Button, { asChild: true, children: _jsx(Link, { to: "/", children: "Back to V4 Dashboard" }) }) })] }) }));
}
