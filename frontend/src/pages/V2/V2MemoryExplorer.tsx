import React, { useState, useEffect } from 'react';
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
    } catch (err) {
      console.error('Failed to fetch memories:', err);
    } finally {
      setLoading(false);
    }
  };

  const memoryTypes = ['all', 'text', 'table', 'key_value', 'entity'];

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">V2 Memory Explorer</h1>
            <p className="text-muted-foreground">Browse and search V2 memories</p>
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
          <h1 className="text-3xl font-bold">V2 Memory Explorer</h1>
          <p className="text-muted-foreground">Browse and search your V2 memories with advanced filtering.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Search & Filter</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Input
                  placeholder="Search memories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    {memoryTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type.replace('_', ' ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>V2 Memories ({memories.length})</CardTitle>
            <CardDescription>All your V2 memories with enhanced features</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Content</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {memories.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="h-24 text-center">
                      No V2 memories found.
                    </TableCell>
                  </TableRow>
                ) : (
                  memories.map((memory) => (
                    <TableRow key={memory.id}>
                      <TableCell>{memory.id}</TableCell>
                      <TableCell className="max-w-96 truncate">{memory.content}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{memory.subtype}</Badge>
                      </TableCell>
                      <TableCell>
                        {(memory.confidence * 100).toFixed(1)}%
                      </TableCell>
                      <TableCell>
                        {new Date(memory.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm">View</Button>
                        <Button variant="ghost" size="sm">Edit</Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button asChild>
            <Link to="/">Back to V4 Dashboard</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}