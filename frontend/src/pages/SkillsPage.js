import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
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
        }
        catch (err) {
            setError('Failed to fetch skills');
        }
        finally {
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
        }
        catch (err) {
            setError('Failed to fetch executions');
        }
        finally {
            setExecutionLoading(false);
        }
    };
    const executeSkill = async () => {
        if (!selectedSkill || !inputData)
            return;
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
        }
        catch (err) {
            setError('Execution failed');
        }
        finally {
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
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Skills" }), _jsx("p", { className: "text-muted-foreground", children: "Manage and execute skills for advanced processing." })] }), _jsxs("div", { className: "grid gap-4", children: [_jsx(Skeleton, { className: "h-10 w-full" }), _jsx(Skeleton, { className: "h-96 w-full" })] })] }) }));
    }
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Skills" }), _jsx("p", { className: "text-muted-foreground", children: "Create, manage, and execute skills for advanced memory processing." })] }), _jsxs(Tabs, { defaultValue: "skills", className: "space-y-4", children: [_jsxs(TabsList, { children: [_jsx(TabsTrigger, { value: "skills", children: "Available Skills" }), _jsx(TabsTrigger, { value: "execute", children: "Execute Skill" }), _jsx(TabsTrigger, { value: "executions", children: "Execution History" })] }), _jsxs(TabsContent, { value: "skills", className: "space-y-4", children: [error && (_jsxs(Alert, { variant: "destructive", children: [_jsx(AlertTitle, { children: "Error" }), _jsx(AlertDescription, { children: error })] })), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Available Skills" }), _jsx(CardDescription, { children: "Manage your skills for advanced memory processing." })] }), _jsx(CardContent, { children: _jsxs(Table, { children: [_jsx(TableHeader, { children: _jsxs(TableRow, { children: [_jsx(TableHead, { children: "Name" }), _jsx(TableHead, { children: "Type" }), _jsx(TableHead, { children: "Version" }), _jsx(TableHead, { children: "Status" }), _jsx(TableHead, { children: "Executions" }), _jsx(TableHead, { children: "Last Used" }), _jsx(TableHead, { className: "text-right", children: "Actions" })] }) }), _jsx(TableBody, { children: skills.length === 0 ? (_jsx(TableRow, { children: _jsx(TableCell, { colSpan: 7, className: "h-24 text-center", children: "No skills found." }) })) : (skills.map((skill) => (_jsxs(TableRow, { children: [_jsx(TableCell, { className: "font-medium", children: skill.name }), _jsx(TableCell, { children: _jsx(Badge, { variant: "outline", children: skill.skill_type }) }), _jsx(TableCell, { children: skill.version }), _jsx(TableCell, { children: _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "h-2 w-2 rounded-full " + getStatusColor(skill.status) }), _jsx("span", { className: "capitalize", children: skill.status })] }) }), _jsx(TableCell, { children: skill.execution_count }), _jsx(TableCell, { children: skill.last_executed_at ? new Date(skill.last_executed_at).toLocaleDateString() : 'Never' }), _jsxs(TableCell, { className: "text-right", children: [_jsx(Button, { variant: "outline", size: "sm", className: "mr-2", onClick: () => {
                                                                                setSelectedSkill(skill);
                                                                                setIsDialogOpen(true);
                                                                            }, children: "Execute" }), _jsx(Button, { variant: "ghost", size: "sm", children: "Configure" })] })] }, skill.id)))) })] }) })] }), _jsxs("div", { className: "grid gap-4 md:grid-cols-3", children: [_jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: [_jsx(CardTitle, { className: "text-sm font-medium", children: "Total Skills" }), _jsx("svg", { className: "h-4 w-4 text-muted-foreground", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M13 10V3L4 14h7v7l9-11h-7z" }) })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold", children: skills.length }), _jsx("p", { className: "text-xs text-muted-foreground", children: "Available skills" })] })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: [_jsx(CardTitle, { className: "text-sm font-medium", children: "Total Executions" }), _jsx("svg", { className: "h-4 w-4 text-muted-foreground", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9V3m0 18a9 9 0 009-9M3 12a9 9 0 019-9" }) })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold", children: skills.reduce((sum, skill) => sum + skill.execution_count, 0) }), _jsx("p", { className: "text-xs text-muted-foreground", children: "All skill executions" })] })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: [_jsx(CardTitle, { className: "text-sm font-medium", children: "Active Skills" }), _jsx("svg", { className: "h-4 w-4 text-muted-foreground", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M13 10V3L4 14h7v7l9-11h-7z" }) })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold text-green-600", children: skills.filter(s => s.status === 'available' && s.enabled).length }), _jsx("p", { className: "text-xs text-muted-foreground", children: "Enabled and available" })] })] })] })] }), _jsxs(TabsContent, { value: "execute", className: "space-y-4", children: [_jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Execute Skill" }), _jsx(CardDescription, { children: "Execute a skill with custom input data." })] }), _jsxs(CardContent, { className: "space-y-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx(Label, { htmlFor: "skill-select", children: "Select Skill" }), _jsxs(Select, { value: selectedSkill?.id?.toString() || '', onValueChange: (value) => {
                                                                const skill = skills.find(s => s.id.toString() === value);
                                                                setSelectedSkill(skill);
                                                            }, children: [_jsx(SelectTrigger, { id: "skill-select", children: _jsx(SelectValue, { placeholder: "Select a skill to execute" }) }), _jsx(SelectContent, { children: skills.map((skill) => (_jsx(SelectItem, { value: skill.id.toString(), children: _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("span", { children: skill.name }), _jsx(Badge, { variant: "outline", className: "text-xs", children: skill.skill_type })] }) }, skill.id))) })] })] }), selectedSkill && (_jsxs(_Fragment, { children: [_jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: selectedSkill.name }), _jsx(CardDescription, { children: selectedSkill.description })] }), _jsx(CardContent, { children: _jsxs("div", { className: "space-y-2", children: [_jsxs("p", { className: "text-sm", children: [_jsx("strong", { children: "Type:" }), " ", selectedSkill.skill_type] }), _jsxs("p", { className: "text-sm", children: [_jsx("strong", { children: "Version:" }), " ", selectedSkill.version] }), _jsxs("p", { className: "text-sm", children: [_jsx("strong", { children: "Handler:" }), " ", _jsx("code", { className: "bg-muted px-1 rounded", children: selectedSkill.handler })] }), _jsxs("p", { className: "text-sm", children: [_jsx("strong", { children: "Status:" }), _jsx(Badge, { variant: selectedSkill.enabled ? 'default' : 'secondary', children: selectedSkill.enabled ? 'Enabled' : 'Disabled' })] }), selectedSkill.tags.length > 0 && (_jsxs("p", { className: "text-sm", children: [_jsx("strong", { children: "Tags:" }), selectedSkill.tags.map(tag => (_jsx(Badge, { variant: "outline", className: "mr-1", children: tag }, tag)))] }))] }) })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { htmlFor: "input-data", children: "Input Data (JSON)" }), _jsx(Textarea, { id: "input-data", value: inputData, onChange: (e) => setInputData(e.target.value), placeholder: '{"text": "Sample text to process", "options": {}}', className: "min-h-32" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Enter input data in JSON format. The format depends on the selected skill." })] }), _jsxs(Dialog, { open: isDialogOpen, onOpenChange: setIsDialogOpen, children: [_jsx(DialogTrigger, { asChild: true, children: _jsx(Button, { onClick: () => setIsDialogOpen(true), disabled: !selectedSkill || !inputData, children: "Execute Skill" }) }), _jsxs(DialogContent, { className: "sm:max-w-[500px]", children: [_jsxs(DialogHeader, { children: [_jsx(DialogTitle, { children: "Confirm Execution" }), _jsxs(DialogDescription, { children: ["Execute ", selectedSkill?.name, " with the provided input data?"] })] }), _jsx("div", { className: "space-y-4 py-4", children: isExecuting ? (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "h-4 w-4 rounded-full bg-blue-500 animate-pulse" }), _jsx("span", { children: "Executing..." })] }), _jsx(Progress, { value: progress, className: "h-2" }), _jsxs("p", { className: "text-sm text-muted-foreground", children: [progress, "% complete"] })] })) : executionResults ? (_jsxs("div", { className: "space-y-4", children: [_jsxs(Alert, { className: "bg-green-50 border-green-200 text-green-800", children: [_jsx(AlertTitle, { children: "Execution Completed!" }), _jsxs(AlertDescription, { children: ["Skill executed successfully in ", executionResults.output?.processing_time || 0, "ms"] })] }), _jsxs("div", { className: "space-y-2", children: [_jsx("h4", { className: "font-medium", children: "Output:" }), _jsx("pre", { className: "bg-muted p-2 rounded text-sm overflow-auto", children: JSON.stringify(executionResults.output, null, 2) })] })] })) : (_jsxs("div", { className: "space-y-2", children: [_jsxs("p", { children: [_jsx("strong", { children: "Skill:" }), " ", selectedSkill?.name] }), _jsx("p", { children: _jsx("strong", { children: "Input:" }) }), _jsx("pre", { className: "bg-muted p-2 rounded text-sm overflow-auto", children: inputData })] })) }), !isExecuting && !executionResults && (_jsxs(DialogFooter, { children: [_jsx(Button, { variant: "outline", onClick: () => setIsDialogOpen(false), children: "Cancel" }), _jsx(Button, { onClick: executeSkill, children: "Confirm Execution" })] })), executionResults && (_jsx(DialogFooter, { children: _jsx(Button, { onClick: () => {
                                                                                    setIsDialogOpen(false);
                                                                                    setExecutionResults(null);
                                                                                    setSelectedSkill(null);
                                                                                    setInputData('{}');
                                                                                }, children: "Close" }) }))] })] })] })), !selectedSkill && (_jsxs(Alert, { variant: "info", children: [_jsx(AlertTitle, { children: "No Skill Selected" }), _jsx(AlertDescription, { children: "Please select a skill from the dropdown above to see its details and execute it." })] }))] })] }), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "Skill Examples" }) }), _jsxs(CardContent, { className: "space-y-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx("h4", { className: "font-medium", children: "Text Extractor" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Extracts text content from documents" }), _jsx("pre", { className: "bg-muted p-2 rounded text-sm", children: { "document_id": "doc_123", "pages": [1, 2, 3] } })] }), _jsxs("div", { className: "space-y-2", children: [_jsx("h4", { className: "font-medium", children: "Sentiment Analyzer" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Analyzes the sentiment of text" }), _jsx("pre", { className: "bg-muted p-2 rounded text-sm", children: { "text": "I love this product! It works great." } })] }), _jsxs("div", { className: "space-y-2", children: [_jsx("h4", { className: "font-medium", children: "Document Summarizer" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Creates a summary of long documents" }), _jsx("pre", { className: "bg-muted p-2 rounded text-sm", children: { "document_id": "doc_456", "max_length": 200 } })] })] })] })] }), _jsx(TabsContent, { value: "executions", className: "space-y-4", children: _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Execution History" }), _jsx(CardDescription, { children: "View all skill executions and their status." })] }), _jsx(CardContent, { children: executionLoading ? (_jsx(Skeleton, { className: "h-96 w-full" })) : (_jsxs(Table, { children: [_jsx(TableHeader, { children: _jsxs(TableRow, { children: [_jsx(TableHead, { children: "Execution ID" }), _jsx(TableHead, { children: "Skill" }), _jsx(TableHead, { children: "Status" }), _jsx(TableHead, { children: "Started" }), _jsx(TableHead, { children: "Completed" }), _jsx(TableHead, { className: "text-right", children: "Actions" })] }) }), _jsx(TableBody, { children: executions.length === 0 ? (_jsx(TableRow, { children: _jsx(TableCell, { colSpan: 6, className: "h-24 text-center", children: "No executions found." }) })) : (executions.map((execution) => (_jsxs(TableRow, { children: [_jsxs(TableCell, { className: "font-mono text-sm", children: [execution.execution_id.substring(0, 20), "..."] }), _jsx(TableCell, { children: execution.skill_name }), _jsx(TableCell, { children: _jsx(Badge, { variant: execution.status === 'completed' ? 'default' : execution.status === 'failed' ? 'destructive' : 'secondary', children: execution.status }) }), _jsx(TableCell, { children: new Date(execution.started_at).toLocaleString() }), _jsx(TableCell, { children: execution.completed_at ? new Date(execution.completed_at).toLocaleString() : '-' }), _jsx(TableCell, { className: "text-right", children: _jsx(Button, { variant: "outline", size: "sm", children: "View Details" }) })] }, execution.execution_id)))) })] })) })] }) })] })] }) }));
}
