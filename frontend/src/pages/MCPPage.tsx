import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';

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
    setApiKeys(apiKeys.map(key => 
      key.id === id ? { ...key, enabled: !key.enabled } : key
    ));
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
    if (!expires_at) return { color: 'green', text: 'Never expires' };
    const expiryDate = new Date(expires_at);
    const now = new Date();
    const daysLeft = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));
    
    if (daysLeft < 0) return { color: 'red', text: 'Expired' };
    if (daysLeft < 7) return { color: 'yellow', text: 'Expires in ' + daysLeft + ' days' };
    return { color: 'green', text: 'Expires in ' + daysLeft + ' days' };
  };

  if (loading && !mcpConfig) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">MCP Authentication</h1>
            <p className="text-muted-foreground">Manage API keys and authentication.</p>
          </div>
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">MCP Authentication</h1>
          <p className="text-muted-foreground">Manage API keys for MCP integration.</p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="config" className="space-y-4">
          <TabsList>
            <TabsTrigger value="config">Configuration</TabsTrigger>
            <TabsTrigger value="keys">API Keys</TabsTrigger>
            <TabsTrigger value="authenticate">Test Auth</TabsTrigger>
            <TabsTrigger value="usage">Usage Guide</TabsTrigger>
          </TabsList>

          <TabsContent value="config">
            <Card>
              <CardHeader>
                <CardTitle>MCP Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div className="flex items-center justify-between p-4 border rounded">
                    <div>
                      <h3 className="font-medium">MCP Enabled</h3>
                    </div>
                    <Badge variant={mcpConfig?.enabled ? 'default' : 'secondary'}>
                      {mcpConfig?.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded">
                    <div>
                      <h3 className="font-medium">Rate Limit Default</h3>
                    </div>
                    <Badge variant="outline">{mcpConfig?.rate_limit_default || 100} req/min</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="keys">
            <div className="flex justify-end mb-4">
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button>Create API Key</Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[500px]">
                  <DialogHeader>
                    <DialogTitle>Create New API Key</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Name</Label>
                      <Input value={newKey.name} onChange={(e) => setNewKey({...newKey, name: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <Label>Description</Label>
                      <Textarea value={newKey.description} onChange={(e) => setNewKey({...newKey, description: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <Label>Permissions</Label>
                      <div className="flex flex-wrap gap-2">
                        {allPermissions.map(perm => (
                          <Button
                            key={perm}
                            variant={newKey.permissions.includes(perm) ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => {
                              const permissions = newKey.permissions.includes(perm)
                                ? newKey.permissions.filter(p => p !== perm)
                                : [...newKey.permissions, perm];
                              setNewKey({...newKey, permissions});
                            }}
                          >{perm}</Button>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label>Rate Limit</Label>
                      <Input type="number" value={newKey.rate_limit} onChange={(e) => setNewKey({...newKey, rate_limit: parseInt(e.target.value) || 100})} />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                    <Button onClick={createApiKey}>Create</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>

            {createdKey && (
              <Dialog open={!!createdKey} onOpenChange={() => setCreatedKey(null)}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>API Key Created!</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <Alert className="bg-yellow-50">
                      <AlertTitle>Important!</AlertTitle>
                      <AlertDescription>Copy this secret now. You will not be able to see it again.</AlertDescription>
                    </Alert>
                    <div className="space-y-2">
                      <Label>Key ID</Label>
                      <div className="flex gap-2">
                        <Input value={createdKey.key_id} readOnly />
                        <Button variant="outline" size="sm" onClick={() => copyToClipboard(createdKey.key_id)}>Copy</Button>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label>Secret</Label>
                      <div className="flex gap-2">
                        <Input type={showSecret ? 'text' : 'password'} value={createdKey.secret} readOnly />
                        <Button variant="outline" size="sm" onClick={() => setShowSecret(!showSecret)}>
                          {showSecret ? 'Hide' : 'Show'}
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => copyToClipboard(createdKey.secret)}>Copy</Button>
                      </div>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={() => setCreatedKey(null)}>I have copied the key</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            )}

            <Card>
              <CardHeader>
                <CardTitle>API Keys</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Key ID</TableHead>
                      <TableHead>Permissions</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Usage</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {apiKeys.map((key) => {
                      const expiryStatus = getExpiryStatus(key.expires_at);
                      return (
                        <TableRow key={key.id}>
                          <TableCell className="font-medium">{key.name}</TableCell>
                          <TableCell className="font-mono text-sm">{key.key_id.substring(0, 8)}...</TableCell>
                          <TableCell>
                            {key.permissions.map(p => <Badge key={p} variant="outline" className="mr-1">{p}</Badge>)}
                          </TableCell>
                          <TableCell>
                            <Badge variant={key.enabled ? 'default' : 'secondary'}>
                              {key.enabled ? 'Active' : 'Disabled'}
                            </Badge>
                          </TableCell>
                          <TableCell>{key.usage_count} reqs</TableCell>
                          <TableCell className="text-right">
                            <Button variant="destructive" size="sm" onClick={() => deleteApiKey(key.id)}>Delete</Button>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="authenticate">
            <Card>
              <CardHeader>
                <CardTitle>Test Authentication</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>API Key</Label>
                  <div className="flex gap-2">
                    <Input type="password" value={authToken} onChange={(e) => setAuthToken(e.target.value)} className="flex-1" />
                    <Button onClick={authenticate}>Authenticate</Button>
                  </div>
                </div>
                {authResult && (
                  <Alert variant={authResult.authenticated ? 'default' : 'destructive'}>
                    <AlertTitle>{authResult.authenticated ? 'Success!' : 'Failed'}</AlertTitle>
                    <AlertDescription>
                      {authResult.authenticated ? 'API key is valid' : 'Invalid API key'}
                    </AlertDescription>
                  </Alert>
                )}
                <div className="bg-muted/50 p-4 rounded">
                  <p className="text-sm font-medium mb-2">Usage Example:</p>
                  <pre className="bg-background p-3 rounded text-sm">
curl -H 'X-API-Key: your_key_here' https://server.com/api/mcp/config
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="usage">
            <Card>
              <CardHeader>
                <CardTitle>Usage Guide</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <h3 className="font-medium mb-2">Permissions</h3>
                <div className="grid gap-2">
                  <div className="p-3 border rounded"><strong>read:</strong> GET requests</div>
                  <div className="p-3 border rounded"><strong>write:</strong> POST, PUT requests</div>
                  <div className="p-3 border rounded"><strong>delete:</strong> DELETE requests</div>
                  <div className="p-3 border rounded"><strong>admin:</strong> Full access</div>
                </div>
                <h3 className="font-medium mb-2 pt-4 border-t">Endpoints</h3>
                <div className="space-y-2">
                  <div className="p-3 border rounded"><code>GET /api/mcp/config</code></div>
                  <div className="p-3 border rounded"><code>GET /api/mcp/keys</code></div>
                  <div className="p-3 border rounded"><code>POST /api/mcp/keys</code></div>
                  <div className="p-3 border rounded"><code>POST /api/mcp/authenticate</code></div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}