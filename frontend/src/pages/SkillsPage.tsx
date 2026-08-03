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

export default function SkillsPage() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [executionLoading, setExecutionLoading] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [inputData, setInputData] = useState('{}');
  const [executionResults, setExecutionResults] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [progress, setProgress] = useState(0);

  const skillTypes = [
    { value: 'extraction', label: 'Extraction' },
    { value: 'analysis', label: 'Analysis' },
    { value: 'summarization', label: 'Summarization' },
    { value: 'translation', label: 'Translation' },
    { value: 'classification', label: 'Classification' },
    { value: 'custom', label: 'Custom' }
  ];

  useEffect(() => {
    fetchSkills();
    fetchExecutions();
  }, []);

  const fetchSkills = async () => {
    try {
      setLoading(true);
      const mockSkills = [
        { id: 1, name: 'Text Extractor', description: 'Extracts text from documents', skill_type: 'extraction', handler: 'skills.text_extractor', version: '1.0.0', author: 'System', enabled: true, tags: ['extraction', 'text'], status: 'available', created_at: '2024-01-15T10:00:00Z', execution_count: 124, last_executed_at: '2024-01-20T14:30:00Z' },
        { id: 2, name: 'Sentiment Analyzer', description: 'Analyzes sentiment of text', skill_type: 'analysis', handler: 'skills.sentiment', version: '1.1.0', author: 'System', enabled: true, tags: ['analysis', 'sentiment'], status: 'available', created_at: '2024-01-14T09:30:00Z', execution_count: 89, last_executed_at: '2024-01-19T16:45:00Z' },
        { id: 3, name: 'Document Summarizer', description: 'Summarizes long documents', skill_type: 'summarization', handler: 'skills.summarizer', version: '1.0.0', author: 'System', enabled: true, tags: ['summarization', 'document'], status: 'available', created_at: '2024-01-13T11:15:00Z', execution_count: 67, last_executed_at: '2024-01-18T10:20:00Z' },
        { id: 4, name: 'Language Translator', description: 'Translates text between languages', skill_type: 'translation', handler: 'skills.translator', version: '1.2.0', author: 'System', enabled: false, tags: ['translation', 'language'], status: 'disabled', created_at: '2024-01-12T08:45:00Z', execution_count: 42, last_executed_at: '2024-01-17T13:10:00Z' },
      ];
      setSkills(mockSkills);
      setError(null);
    } catch (err) {
      setError('Failed to fetch skills');
    } finally {
      setLoading(false);
    }
  };

  const fetchExecutions = async () => {
    try {
      setExecutionLoading(true);
      const mockExecutions = [
        { execution_id: 'exec_1_202401201430', skill_id: 1, skill_name: 'Text Extractor', status: 'completed', started_at: '2024-01-20T14:30:00Z', completed_at: '2024-01-20T14:30:05Z' },
        { execution_id: 'exec_2_202401191645', skill_id: 2, skill_name: 'Sentiment Analyzer', status: 'completed', started_at: '2024-01-19T16:45:00Z', completed_at: '2024-01-19T16:45:12Z' },
        { execution_id: 'exec_3_202401181020', skill_id: 3, skill_name: 'Document Summarizer', status: 'failed', started_at: '2024-01-18T10:20:00Z', completed_at: '2024-01-18T10:20:15Z' },
        { execution_id: 'exec_1_202401171310', skill_id: 1, skill_name: 'Text Extractor', status: 'completed', started_at: '2024-01-17T13:10:00Z', completed_at: '2024-01-17T13:10:03Z' },
      ];
      setExecutions(mockExecutions);
    } catch (err) {
      setError('Failed to fetch executions');
    } finally {
      setExecutionLoading(false);
    }
  };

  const executeSkill = async () => {
    if (!selectedSkill || !inputData) return;
    
    setIsExecuting(true);
    setProgress(0);
    setExecutionResults(null);
    
    try {
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setProgress(i);
      }
      
      const mockResult = {
        execution_id: 'exec_' + selectedSkill.id + '_' + Date.now(),
        status: 'completed',
        output: {
          result: 'Sample extracted text or analysis result',
          confidence: 0.95,
          processing_time: 1250
        }
      };
      
      setExecutionResults(mockResult);
      fetchExecutions();
    } catch (err) {
      setError('Execution failed');
    } finally {
      setIsExecuting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'running': return 'bg-blue-500';
      case 'failed': return 'bg-red-500';
      case 'disabled': return 'bg-gray-500';
      default: return 'bg-yellow-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Skills</h1>
            <p className="text-muted-foreground">Manage and execute skills for advanced processing.</p>
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
          <h1 className="text-3xl font-bold">Skills</h1>
          <p className="text-muted-foreground">Create, manage, and execute skills for advanced memory processing.</p>
        </div>

        <Tabs defaultValue="skills" className="space-y-4">
          <TabsList>
            <TabsTrigger value="skills">Available Skills</TabsTrigger>
            <TabsTrigger value="execute">Execute Skill</TabsTrigger>
            <TabsTrigger value="executions">Execution History</TabsTrigger>
          </TabsList>

          <TabsContent value="skills" className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Available Skills</CardTitle>
                <CardDescription>
                  Manage your skills for advanced memory processing.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Version</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Executions</TableHead>
                      <TableHead>Last Used</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {skills.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="h-24 text-center">
                          No skills found.
                        </TableCell>
                      </TableRow>
                    ) : (
                      skills.map((skill) => (
                        <TableRow key={skill.id}>
                          <TableCell className="font-medium">{skill.name}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{skill.skill_type}</Badge>
                          </TableCell>
                          <TableCell>{skill.version}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <div className={"h-2 w-2 rounded-full " + getStatusColor(skill.status)} />
                              <span className="capitalize">{skill.status}</span>
                            </div>
                          </TableCell>
                          <TableCell>{skill.execution_count}</TableCell>
                          <TableCell>
                            {skill.last_executed_at ? new Date(skill.last_executed_at).toLocaleDateString() : 'Never'}
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="outline"
                              size="sm"
                              className="mr-2"
                              onClick={() => {
                                setSelectedSkill(skill);
                                setIsDialogOpen(true);
                              }}
                            >
                              Execute
                            </Button>
                            <Button variant="ghost" size="sm">
                              Configure
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Skills</CardTitle>
                  <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{skills.length}</div>
                  <p className="text-xs text-muted-foreground">Available skills</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
                  <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9V3m0 18a9 9 0 009-9M3 12a9 9 0 019-9" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {skills.reduce((sum, skill) => sum + skill.execution_count, 0)}
                  </div>
                  <p className="text-xs text-muted-foreground">All skill executions</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Skills</CardTitle>
                  <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    {skills.filter(s => s.status === 'available' && s.enabled).length}
                  </div>
                  <p className="text-xs text-muted-foreground">Enabled and available</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="execute" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Execute Skill</CardTitle>
                <CardDescription>
                  Execute a skill with custom input data.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="skill-select">Select Skill</Label>
                  <Select
                    value={selectedSkill?.id?.toString() || ''}
                    onValueChange={(value) => {
                      const skill = skills.find(s => s.id.toString() === value);
                      setSelectedSkill(skill);
                    }}
                  >
                    <SelectTrigger id="skill-select">
                      <SelectValue placeholder="Select a skill to execute" />
                    </SelectTrigger>
                    <SelectContent>
                      {skills.map((skill) => (
                        <SelectItem key={skill.id} value={skill.id.toString()}>
                          <div className="flex items-center gap-2">
                            <span>{skill.name}</span>
                            <Badge variant="outline" className="text-xs">{skill.skill_type}</Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {selectedSkill && (
                  <>
                    <Card>
                      <CardHeader>
                        <CardTitle>{selectedSkill.name}</CardTitle>
                        <CardDescription>{selectedSkill.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <p className="text-sm"><strong>Type:</strong> {selectedSkill.skill_type}</p>
                          <p className="text-sm"><strong>Version:</strong> {selectedSkill.version}</p>
                          <p className="text-sm"><strong>Handler:</strong> <code className="bg-muted px-1 rounded">{selectedSkill.handler}</code></p>
                          <p className="text-sm"><strong>Status:</strong> 
                            <Badge variant={selectedSkill.enabled ? 'default' : 'secondary'}>
                              {selectedSkill.enabled ? 'Enabled' : 'Disabled'}
                            </Badge>
                          </p>
                          {selectedSkill.tags.length > 0 && (
                            <p className="text-sm">
                              <strong>Tags:</strong> 
                              {selectedSkill.tags.map(tag => (
                                <Badge key={tag} variant="outline" className="mr-1">{tag}</Badge>
                              ))}
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    <div className="space-y-2">
                      <Label htmlFor="input-data">Input Data (JSON)</Label>
                      <Textarea
                        id="input-data"
                        value={inputData}
                        onChange={(e) => setInputData(e.target.value)}
                        placeholder='{"text": "Sample text to process", "options": {}}'
                        className="min-h-32"
                      />
                      <p className="text-sm text-muted-foreground">
                        Enter input data in JSON format. The format depends on the selected skill.
                      </p>
                    </div>

                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                      <DialogTrigger asChild>
                        <Button onClick={() => setIsDialogOpen(true)} disabled={!selectedSkill || !inputData}>
                          Execute Skill
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="sm:max-w-[500px]">
                        <DialogHeader>
                          <DialogTitle>Confirm Execution</DialogTitle>
                          <DialogDescription>
                            Execute {selectedSkill?.name} with the provided input data?
                          </DialogDescription>
                        </DialogHeader>
                        
                        <div className="space-y-4 py-4">
                          {isExecuting ? (
                            <div className="space-y-4">
                              <div className="flex items-center gap-2">
                                <div className="h-4 w-4 rounded-full bg-blue-500 animate-pulse" />
                                <span>Executing...</span>
                              </div>
                              <Progress value={progress} className="h-2" />
                              <p className="text-sm text-muted-foreground">{progress}% complete</p>
                            </div>
                          ) : executionResults ? (
                            <div className="space-y-4">
                              <Alert className="bg-green-50 border-green-200 text-green-800">
                                <AlertTitle>Execution Completed!</AlertTitle>
                                <AlertDescription>
                                  Skill executed successfully in {executionResults.output?.processing_time || 0}ms
                                </AlertDescription>
                              </Alert>
                              <div className="space-y-2">
                                <h4 className="font-medium">Output:</h4>
                                <pre className="bg-muted p-2 rounded text-sm overflow-auto">
                                  {JSON.stringify(executionResults.output, null, 2)}
                                </pre>
                              </div>
                            </div>
                          ) : (
                            <div className="space-y-2">
                              <p><strong>Skill:</strong> {selectedSkill?.name}</p>
                              <p><strong>Input:</strong></p>
                              <pre className="bg-muted p-2 rounded text-sm overflow-auto">
                                {inputData}
                              </pre>
                            </div>
                          )}
                        </div>
                        
                        {!isExecuting && !executionResults && (
                          <DialogFooter>
                            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                              Cancel
                            </Button>
                            <Button onClick={executeSkill}>
                              Confirm Execution
                            </Button>
                          </DialogFooter>
                        )}
                        
                        {executionResults && (
                          <DialogFooter>
                            <Button onClick={() => {
                              setIsDialogOpen(false);
                              setExecutionResults(null);
                              setSelectedSkill(null);
                              setInputData('{}');
                            }}>
                              Close
                            </Button>
                          </DialogFooter>
                        )}
                      </DialogContent>
                    </Dialog>
                  </>
                )}

                {!selectedSkill && (
                  <Alert variant="info">
                    <AlertTitle>No Skill Selected</AlertTitle>
                    <AlertDescription>
                      Please select a skill from the dropdown above to see its details and execute it.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Skill Examples</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium">Text Extractor</h4>
                  <p className="text-sm text-muted-foreground">Extracts text content from documents</p>
                  <pre className="bg-muted p-2 rounded text-sm">
{{"document_id": "doc_123", "pages": [1, 2, 3]}}
                  </pre>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">Sentiment Analyzer</h4>
                  <p className="text-sm text-muted-foreground">Analyzes the sentiment of text</p>
                  <pre className="bg-muted p-2 rounded text-sm">
{{"text": "I love this product! It works great."}}
                  </pre>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">Document Summarizer</h4>
                  <p className="text-sm text-muted-foreground">Creates a summary of long documents</p>
                  <pre className="bg-muted p-2 rounded text-sm">
{{"document_id": "doc_456", "max_length": 200}}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="executions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Execution History</CardTitle>
                <CardDescription>
                  View all skill executions and their status.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {executionLoading ? (
                  <Skeleton className="h-96 w-full" />
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Execution ID</TableHead>
                        <TableHead>Skill</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Completed</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {executions.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={6} className="h-24 text-center">
                            No executions found.
                          </TableCell>
                        </TableRow>
                      ) : (
                        executions.map((execution) => (
                          <TableRow key={execution.execution_id}>
                            <TableCell className="font-mono text-sm">
                              {execution.execution_id.substring(0, 20)}...
                            </TableCell>
                            <TableCell>{execution.skill_name}</TableCell>
                            <TableCell>
                              <Badge variant={execution.status === 'completed' ? 'default' : execution.status === 'failed' ? 'destructive' : 'secondary'}>
                                {execution.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {new Date(execution.started_at).toLocaleString()}
                            </TableCell>
                            <TableCell>
                              {execution.completed_at ? new Date(execution.completed_at).toLocaleString() : '-'}
                            </TableCell>
                            <TableCell className="text-right">
                              <Button variant="outline" size="sm">
                                View Details
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}