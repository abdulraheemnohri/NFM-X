import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
export default function MCPPage() {
    const [apiKeys, setApiKeys] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [mcpConfig, setMcpConfig] = useState(null);
    const [newKey, setNewKey] = useState({
        name: '',
        description: '',
        permissions: ['read', 'write'],
        rate_limit: 100
    });
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [createdKey, setCreatedKey] = useState(null);
    const [showSecret, setShowSecret] = useState(false);
    const [authToken, setAuthToken] = useState('');
    const [authResult, setAuthResult] = useState(null);
    const allPermissions = ['read', 'write', 'delete', 'admin'];
    useEffect(() => {
        const mockConfig = {
            enabled: true,
            require_authentication: true,
            default_permissions: ['read', 'write'],
            rate_limit_default: 100
        };
        setMcpConfig(mockConfig);
        const mockKeys = [
            { id: 1, key_id: 'key_abc123', name: 'Production Key', description: 'Main production API key', permissions: ['read', 'write'], enabled: true, created_at: '2024-01-15T10:00:00Z', expires_at: null, last_used_at: '2024-01-20T14:30:00Z', usage_count: 1247, rate_limit: 100 },
            { id: 2, key_id: 'key_def456', name: 'Development Key', description: 'Development and testing API key', permissions: ['read', 'write', 'delete'], enabled: true, created_at: '2024-01-14T09:30:00Z', expires_at: '2024-07-14T00:00:00Z', last_used_at: '2024-01-19T16:45:00Z', usage_count: 892, rate_limit: 200 },
        ];
        setApiKeys(mockKeys);
        setLoading(false);
    }, []);
    const createApiKey = async () => {
        if (!newKey.name) {
            setError('Key name is required');
            return;
        }
        const mockKey = {
            id: apiKeys.length + 1,
            key_id: 'key_' + Math.random().toString(36).substring(2, 8),
            name: newKey.name,
            description: newKey.description,
            permissions: newKey.permissions,
            enabled: true,
            created_at: new Date().toISOString(),
            expires_at: null,
            last_used_at: null,
            usage_count: 0,
            rate_limit: newKey.rate_limit,
            secret: 'sk_' + Math.random().toString(36).substring(2, 34)
        };
        setCreatedKey(mockKey);
        setIsDialogOpen(false);
        setNewKey({ name: '', description: '', permissions: ['read', 'write'], rate_limit: 100 });
    };
    const deleteApiKey = async (id) => {
        setApiKeys(apiKeys.filter(key => key.id !== id));
    };
    const toggleKeyStatus = async (id) => {
        setApiKeys(apiKeys.map(key => key.id === id ? { ...key, enabled: !key.enabled } : key));
    };
    const authenticate = async () => {
        if (!authToken) {
            setError('Please enter an API key');
            return;
        }
        const mockResult = {
            authenticated: true,
            key_id: 'key_abc123',
            permissions: ['read', 'write'],
            expires_at: null
        };
        setAuthResult(mockResult);
    };
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };
    const getExpiryStatus = (expires_at) => {
        if (!expires_at)
            return { color: 'green', text: 'Never expires' };
        const expiryDate = new Date(expires_at);
        const now = new Date();
        const daysLeft = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));
        if (daysLeft < 0)
            return { color: 'red', text: 'Expired' };
        if (daysLeft < 7)
            return { color: 'yellow', text: 'Expires in ' + daysLeft + ' days' };
        return { color: 'green', text: 'Expires in ' + daysLeft + ' days' };
    };
    if (loading && !mcpConfig) {
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "MCP Authentication" }), _jsx("p", { className: "text-muted-foreground", children: "Manage API keys and authentication." })] }), _jsx(Skeleton, { className: "h-96 w-full" })] }) }));
    }
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "MCP Authentication" }), _jsx("p", { className: "text-muted-foreground", children: "Manage API keys for MCP integration." })] }), error && (_jsxs(Alert, { variant: "destructive", children: [_jsx(AlertTitle, { children: "Error" }), _jsx(AlertDescription, { children: error })] })), _jsxs(Tabs, { defaultValue: "config", className: "space-y-4", children: [_jsxs(TabsList, { children: [_jsx(TabsTrigger, { value: "config", children: "Configuration" }), _jsx(TabsTrigger, { value: "keys", children: "API Keys" }), _jsx(TabsTrigger, { value: "authenticate", children: "Test Auth" }), _jsx(TabsTrigger, { value: "usage", children: "Usage Guide" })] }), _jsx(TabsContent, { value: "config", children: _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "MCP Configuration" }) }), _jsx(CardContent, { className: "space-y-4", children: _jsxs("div", { className: "grid gap-4", children: [_jsxs("div", { className: "flex items-center justify-between p-4 border rounded", children: [_jsx("div", { children: _jsx("h3", { className: "font-medium", children: "MCP Enabled" }) }), _jsx(Badge, { variant: mcpConfig?.enabled ? 'default' : 'secondary', children: mcpConfig?.enabled ? 'Enabled' : 'Disabled' })] }), _jsxs("div", { className: "flex items-center justify-between p-4 border rounded", children: [_jsx("div", { children: _jsx("h3", { className: "font-medium", children: "Rate Limit Default" }) }), _jsxs(Badge, { variant: "outline", children: [mcpConfig?.rate_limit_default || 100, " req/min"] })] })] }) })] }) }), _jsxs(TabsContent, { value: "keys", children: [_jsx("div", { className: "flex justify-end mb-4", children: _jsxs(Dialog, { open: isDialogOpen, onOpenChange: setIsDialogOpen, children: [_jsx(DialogTrigger, { asChild: true, children: _jsx(Button, { children: "Create API Key" }) }), _jsxs(DialogContent, { className: "sm:max-w-[500px]", children: [_jsx(DialogHeader, { children: _jsx(DialogTitle, { children: "Create New API Key" }) }), _jsxs("div", { className: "space-y-4 py-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "Name" }), _jsx(Input, { value: newKey.name, onChange: (e) => setNewKey({ ...newKey, name: e.target.value }) })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "Description" }), _jsx(Textarea, { value: newKey.description, onChange: (e) => setNewKey({ ...newKey, description: e.target.value }) })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "Permissions" }), _jsx("div", { className: "flex flex-wrap gap-2", children: allPermissions.map(perm => (_jsx(Button, { variant: newKey.permissions.includes(perm) ? 'default' : 'outline', size: "sm", onClick: () => {
                                                                                const permissions = newKey.permissions.includes(perm)
                                                                                    ? newKey.permissions.filter(p => p !== perm)
                                                                                    : [...newKey.permissions, perm];
                                                                                setNewKey({ ...newKey, permissions });
                                                                            }, children: perm }, perm))) })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "Rate Limit" }), _jsx(Input, { type: "number", value: newKey.rate_limit, onChange: (e) => setNewKey({ ...newKey, rate_limit: parseInt(e.target.value) || 100 }) })] })] }), _jsxs(DialogFooter, { children: [_jsx(Button, { variant: "outline", onClick: () => setIsDialogOpen(false), children: "Cancel" }), _jsx(Button, { onClick: createApiKey, children: "Create" })] })] })] }) }), createdKey && (_jsx(Dialog, { open: !!createdKey, onOpenChange: () => setCreatedKey(null), children: _jsxs(DialogContent, { children: [_jsx(DialogHeader, { children: _jsx(DialogTitle, { children: "API Key Created!" }) }), _jsxs("div", { className: "space-y-4 py-4", children: [_jsxs(Alert, { className: "bg-yellow-50", children: [_jsx(AlertTitle, { children: "Important!" }), _jsx(AlertDescription, { children: "Copy this secret now. You will not be able to see it again." })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "Key ID" }), _jsxs("div", { className: "flex gap-2", children: [_jsx(Input, { value: createdKey.key_id, readOnly: true }), _jsx(Button, { variant: "outline", size: "sm", onClick: () => copyToClipboard(createdKey.key_id), children: "Copy" })] })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "Secret" }), _jsxs("div", { className: "flex gap-2", children: [_jsx(Input, { type: showSecret ? 'text' : 'password', value: createdKey.secret, readOnly: true }), _jsx(Button, { variant: "outline", size: "sm", onClick: () => setShowSecret(!showSecret), children: showSecret ? 'Hide' : 'Show' }), _jsx(Button, { variant: "outline", size: "sm", onClick: () => copyToClipboard(createdKey.secret), children: "Copy" })] })] })] }), _jsx(DialogFooter, { children: _jsx(Button, { onClick: () => setCreatedKey(null), children: "I have copied the key" }) })] }) })), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "API Keys" }) }), _jsx(CardContent, { children: _jsxs(Table, { children: [_jsx(TableHeader, { children: _jsxs(TableRow, { children: [_jsx(TableHead, { children: "Name" }), _jsx(TableHead, { children: "Key ID" }), _jsx(TableHead, { children: "Permissions" }), _jsx(TableHead, { children: "Status" }), _jsx(TableHead, { children: "Usage" }), _jsx(TableHead, { className: "text-right", children: "Actions" })] }) }), _jsx(TableBody, { children: apiKeys.map((key) => {
                                                            const expiryStatus = getExpiryStatus(key.expires_at);
                                                            return (_jsxs(TableRow, { children: [_jsx(TableCell, { className: "font-medium", children: key.name }), _jsxs(TableCell, { className: "font-mono text-sm", children: [key.key_id.substring(0, 8), "..."] }), _jsx(TableCell, { children: key.permissions.map(p => _jsx(Badge, { variant: "outline", className: "mr-1", children: p }, p)) }), _jsx(TableCell, { children: _jsx(Badge, { variant: key.enabled ? 'default' : 'secondary', children: key.enabled ? 'Active' : 'Disabled' }) }), _jsxs(TableCell, { children: [key.usage_count, " reqs"] }), _jsx(TableCell, { className: "text-right", children: _jsx(Button, { variant: "destructive", size: "sm", onClick: () => deleteApiKey(key.id), children: "Delete" }) })] }, key.id));
                                                        }) })] }) })] })] }), _jsx(TabsContent, { value: "authenticate", children: _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "Test Authentication" }) }), _jsxs(CardContent, { className: "space-y-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "API Key" }), _jsxs("div", { className: "flex gap-2", children: [_jsx(Input, { type: "password", value: authToken, onChange: (e) => setAuthToken(e.target.value), className: "flex-1" }), _jsx(Button, { onClick: authenticate, children: "Authenticate" })] })] }), authResult && (_jsxs(Alert, { variant: authResult.authenticated ? 'default' : 'destructive', children: [_jsx(AlertTitle, { children: authResult.authenticated ? 'Success!' : 'Failed' }), _jsx(AlertDescription, { children: authResult.authenticated ? 'API key is valid' : 'Invalid API key' })] })), _jsxs("div", { className: "bg-muted/50 p-4 rounded", children: [_jsx("p", { className: "text-sm font-medium mb-2", children: "Usage Example:" }), _jsx("pre", { className: "bg-background p-3 rounded text-sm", children: "curl -H 'X-API-Key: your_key_here' https://server.com/api/mcp/config" })] })] })] }) }), _jsx(TabsContent, { value: "usage", children: _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "Usage Guide" }) }), _jsxs(CardContent, { className: "space-y-4", children: [_jsx("h3", { className: "font-medium mb-2", children: "Permissions" }), _jsxs("div", { className: "grid gap-2", children: [_jsxs("div", { className: "p-3 border rounded", children: [_jsx("strong", { children: "read:" }), " GET requests"] }), _jsxs("div", { className: "p-3 border rounded", children: [_jsx("strong", { children: "write:" }), " POST, PUT requests"] }), _jsxs("div", { className: "p-3 border rounded", children: [_jsx("strong", { children: "delete:" }), " DELETE requests"] }), _jsxs("div", { className: "p-3 border rounded", children: [_jsx("strong", { children: "admin:" }), " Full access"] })] }), _jsx("h3", { className: "font-medium mb-2 pt-4 border-t", children: "Endpoints" }), _jsxs("div", { className: "space-y-2", children: [_jsx("div", { className: "p-3 border rounded", children: _jsx("code", { children: "GET /api/mcp/config" }) }), _jsx("div", { className: "p-3 border rounded", children: _jsx("code", { children: "GET /api/mcp/keys" }) }), _jsx("div", { className: "p-3 border rounded", children: _jsx("code", { children: "POST /api/mcp/keys" }) }), _jsx("div", { className: "p-3 border rounded", children: _jsx("code", { children: "POST /api/mcp/authenticate" }) })] })] })] }) })] })] }) }));
}
