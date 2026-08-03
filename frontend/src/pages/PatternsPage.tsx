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

export default function PatternsPage() {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [newPattern, setNewPattern] = useState({
    name: '',
    pattern: '',
    description: '',
    case_sensitive: false,
    enabled: true,
    tags: []
  });
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [validationError, setValidationError] = useState(null);

  useEffect(() => {
    fetchPatterns();
  }, []);

  const fetchPatterns = async () => {
    try {
      setLoading(true);
      const mockPatterns = [
        { id: 1, key_id: 'pattern_001', name: 'Email Extractor', pattern: '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', description: 'Extracts email addresses', case_sensitive: false, enabled: true, tags: ['email', 'extraction'], created_at: '2024-01-15T10:00:00Z', usage_count: 45 },
        { id: 2, key_id: 'pattern_002', name: 'Date Finder', pattern: '\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', description: 'Finds dates in various formats', case_sensitive: false, enabled: true, tags: ['date', 'temporal'], created_at: '2024-01-14T09:30:00Z', usage_count: 32 },
        { id: 3, key_id: 'pattern_003', name: 'Amount Detector', pattern: '\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', description: 'Detects currency amounts', case_sensitive: false, enabled: true, tags: ['amount', 'finance'], created_at: '2024-01-13T11:15:00Z', usage_count: 28 },
      ];
      setPatterns(mockPatterns);
      setError(null);
    } catch (err) {
      setError('Failed to fetch patterns');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery) return;
    
    try {
      setSearchLoading(true);
      const mockResults = [
        { memory_id: 1, content: 'Contact support@example.com for help', matched_text: 'support@example.com', match_position: 7 },
        { memory_id: 2, content: 'Email me at user@domain.com', matched_text: 'user@domain.com', match_position: 10 },
        { memory_id: 3, content: 'Send feedback to feedback@company.org', matched_text: 'feedback@company.org', match_position: 17 },
      ];
      setSearchResults(mockResults);
    } catch (err) {
      setError('Search failed');
    } finally {
      setSearchLoading(false);
    }
  };

  const validatePattern = async () => {
    try {
      const response = await fetch('/api/v1/patterns/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern: newPattern.pattern })
      });
      const data = await response.json();
      if (!data.valid) {
        setValidationError(data.message);
        return false;
      }
      setValidationError(null);
      return true;
    } catch (err) {
      setValidationError('Validation failed');
      return false;
    }
  };

  const createPattern = async () => {
    if (!newPattern.name || !newPattern.pattern) {
      setValidationError('Name and pattern are required');
      return;
    }
    
    const isValid = await validatePattern();
    if (!isValid) return;
    
    try {
      const response = await fetch('/api/v1/patterns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPattern)
      });
      
      if (response.ok) {
        setIsDialogOpen(false);
        setNewPattern({ name: '', pattern: '', description: '', case_sensitive: false, enabled: true, tags: [] });
        fetchPatterns();
      }
    } catch (err) {
      setError('Failed to create pattern');
    }
  };

  const deletePattern = async (id) => {
    try {
      const response = await fetch(`/api/v1/patterns/${id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchPatterns();
      }
    } catch (err) {
      setError('Failed to delete pattern');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Pattern Search</h1>
            <p className="text-muted-foreground">Manage and search using regex patterns.</p>
          </div>
          <div className="grid gap-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-96 w-full" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Pattern Search</h1>
          <p className="text-muted-foreground">Create, manage, and search memories using regex patterns.</p>
        </div>

        <Tabs defaultValue="patterns" className="space-y-4">
          <TabsList>
            <TabsTrigger value="patterns">Saved Patterns</TabsTrigger>
            <TabsTrigger value="search">Search with Pattern</TabsTrigger>
            <TabsTrigger value="create">Create Pattern</TabsTrigger>
          </TabsList>

          <TabsContent value="patterns" className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Saved Patterns</CardTitle>
                <CardDescription>
                  Manage your saved regex patterns for searching memories.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Pattern</TableHead>
                      <TableHead>Tags</TableHead>
                      <TableHead>Usage</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {patterns.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="h-24 text-center">
                          No patterns found. Create your first pattern to get started.
                        </TableCell>
                      </TableRow>
                    ) : (
                      patterns.map((pattern) => (
                        <TableRow key={pattern.id}>
                          <TableCell className="font-medium">{pattern.name}</TableCell>
                          <TableCell className="font-mono text-sm">{pattern.pattern.substring(0, 40)}{pattern.pattern.length > 40 ? '...' : ''}</TableCell>
                          <TableCell>
                            {pattern.tags.map(tag => (
                              <Badge key={tag} variant="secondary" className="mr-1">{tag}</Badge>
                            ))}
                          </TableCell>
                          <TableCell>{pattern.usage_count} uses</TableCell>
                          <TableCell>
                            <Badge variant={pattern.enabled ? 'default' : 'secondary'}>
                              {pattern.enabled ? 'Enabled' : 'Disabled'}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button variant="outline" size="sm" className="mr-2">
                              Edit
                            </Button>
                            <Button variant="destructive" size="sm" onClick={() => deletePattern(pattern.id)}>
                              Delete
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="search" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Search with Pattern</CardTitle>
                <CardDescription>
                  Search memories using a regex pattern.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="search-pattern">Regex Pattern</Label>
                  <div className="flex gap-2">
                    <Input
                      id="search-pattern"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Enter regex pattern (e.g., \b\d{3}-\d{2}-\d{4}\b)"
                      className="flex-1"
                    />
                    <Button onClick={handleSearch} disabled={searchLoading}>
                      {searchLoading ? 'Searching...' : 'Search'}
                    </Button>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Use regex to find patterns in your memories. Example: <code className="bg-muted px-1 rounded">{"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"}</code> for emails.
                  </p>
                </div>

                {searchResults.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-medium">Search Results ({searchResults.length})</h3>
                    <div className="space-y-2">
                      {searchResults.map((result, index) => (
                        <Card key={index}>
                          <CardHeader>
                            <CardTitle className="text-sm">Memory #{result.memory_id}</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-sm mb-2">{result.content}</p>
                            <div className="bg-muted/50 p-2 rounded">
                              <p className="text-sm font-mono">
                                Matched: <span className="bg-primary/20 px-1 rounded">{result.matched_text}</span>
                              </p>
                              <p className="text-xs text-muted-foreground">
                                Position: {result.match_position}
                              </p>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="create" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Create New Pattern</CardTitle>
                <CardDescription>
                  Create a new regex pattern to save and reuse for searching memories.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>Create Pattern</Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                      <DialogTitle>Create New Pattern</DialogTitle>
                      <DialogDescription>
                        Create a new regex pattern to save and reuse.
                      </DialogDescription>
                    </DialogHeader>
                    
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="pattern-name">Name</Label>
                        <Input
                          id="pattern-name"
                          value={newPattern.name}
                          onChange={(e) => setNewPattern({...newPattern, name: e.target.value})}
                          placeholder="Email Extractor"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="pattern-pattern">Regex Pattern</Label>
                        <Input
                          id="pattern-pattern"
                          value={newPattern.pattern}
                          onChange={(e) => setNewPattern({...newPattern, pattern: e.target.value})}
                          placeholder="\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                        />
                        {validationError && (
                          <p className="text-sm text-destructive">{validationError}</p>
                        )}
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="pattern-description">Description</Label>
                        <Textarea
                          id="pattern-description"
                          value={newPattern.description}
                          onChange={(e) => setNewPattern({...newPattern, description: e.target.value})}
                          placeholder="Extracts email addresses from text"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Tags</Label>
                        <div className="flex flex-wrap gap-2">
                          {['email', 'date', 'amount', 'phone', 'extraction', 'validation'].map(tag => (
                            <Button
                              key={tag}
                              variant={newPattern.tags.includes(tag) ? 'default' : 'outline'}
                              size="sm"
                              onClick={() => {
                                const tags = newPattern.tags.includes(tag)
                                  ? newPattern.tags.filter(t => t !== tag)
                                  : [...newPattern.tags, tag];
                                setNewPattern({...newPattern, tags});
                              }}
                            >
                              {tag}
                            </Button>
                          ))}
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="case-sensitive"
                            checked={newPattern.case_sensitive}
                            onCheckedChange={(checked) => setNewPattern({...newPattern, case_sensitive: checked})}
                          />
                          <Label htmlFor="case-sensitive">Case Sensitive</Label>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="enabled"
                            checked={newPattern.enabled}
                            onCheckedChange={(checked) => setNewPattern({...newPattern, enabled: checked})}
                          />
                          <Label htmlFor="enabled">Enabled</Label>
                        </div>
                      </div>
                    </div>
                    
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={createPattern}>
                        Create Pattern
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>

                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Pattern Examples</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="space-y-1">
                        <code className="bg-muted px-2 py-1 rounded block">{"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"}</code>
                        <p className="text-sm text-muted-foreground">Email addresses</p>
                      </div>
                      <div className="space-y-1">
                        <code className="bg-muted px-2 py-1 rounded block">{"\\b\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}\\b"}</code>
                        <p className="text-sm text-muted-foreground">Dates (DD/MM/YYYY or MM/DD/YYYY)</p>
                      </div>
                      <div className="space-y-1">
                        <code className="bg-muted px-2 py-1 rounded block">{"\\$\\d{1,3}(?:,\\d{3})*(?:\\.\\d{2})?"}</code>
                        <p className="text-sm text-muted-foreground">Currency amounts ($100, $1,000.50)</p>
                      </div>
                      <div className="space-y-1">
                        <code className="bg-muted px-2 py-1 rounded block">{"\\b\\+?\\d{3}[-.\\s]??\\d{3}[-.\\s]??\\d{4}\\b"}</code>
                        <p className="text-sm text-muted-foreground">Phone numbers</p>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Regex Cheat Sheet</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="font-medium">Characters</p>
                          <p><code>. </code> Any character</p>
                          <p><code>\d </code> Digit (0-9)</p>
                          <p><code>\w </code> Word character</p>
                          <p><code>\s </code> Whitespace</p>
                        </div>
                        <div>
                          <p className="font-medium">Quantifiers</p>
                          <p><code>* </code> 0 or more</p>
                          <p><code>+ </code> 1 or more</p>
                          <p><code>? </code> 0 or 1</p>
                          <p><code>{n} </code> Exactly n</p>
                        </div>
                        <div>
                          <p className="font-medium">Groups</p>
                          <p><code>( ) </code> Capture group</p>
                          <p><code>(?: ) </code> Non-capturing</p>
                          <p><code>| </code> OR operator</p>
                        </div>
                        <div>
                          <p className="font-medium">Anchors</p>
                          <p><code>^ </code> Start of string</p>
                          <p><code>$ </code> End of string</p>
                          <p><code>\b </code> Word boundary</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}