import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
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
        }
        catch (err) {
            setError('Failed to fetch patterns');
        }
        finally {
            setLoading(false);
        }
    };
    const handleSearch = async () => {
        if (!searchQuery)
            return;
        try {
            setSearchLoading(true);
            const mockResults = [
                { memory_id: 1, content: 'Contact support@example.com for help', matched_text: 'support@example.com', match_position: 7 },
                { memory_id: 2, content: 'Email me at user@domain.com', matched_text: 'user@domain.com', match_position: 10 },
                { memory_id: 3, content: 'Send feedback to feedback@company.org', matched_text: 'feedback@company.org', match_position: 17 },
            ];
            setSearchResults(mockResults);
        }
        catch (err) {
            setError('Search failed');
        }
        finally {
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
        }
        catch (err) {
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
        if (!isValid)
            return;
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
        }
        catch (err) {
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
        }
        catch (err) {
            setError('Failed to delete pattern');
        }
    };
    if (loading) {
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Pattern Search" }), _jsx("p", { className: "text-muted-foreground", children: "Manage and search using regex patterns." })] }), _jsxs("div", { className: "grid gap-4", children: [_jsx(Skeleton, { className: "h-10 w-full" }), _jsx(Skeleton, { className: "h-96 w-full" })] })] }) }));
    }
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Pattern Search" }), _jsx("p", { className: "text-muted-foreground", children: "Create, manage, and search memories using regex patterns." })] }), _jsxs(Tabs, { defaultValue: "patterns", className: "space-y-4", children: [_jsxs(TabsList, { children: [_jsx(TabsTrigger, { value: "patterns", children: "Saved Patterns" }), _jsx(TabsTrigger, { value: "search", children: "Search with Pattern" }), _jsx(TabsTrigger, { value: "create", children: "Create Pattern" })] }), _jsxs(TabsContent, { value: "patterns", className: "space-y-4", children: [error && (_jsxs(Alert, { variant: "destructive", children: [_jsx(AlertTitle, { children: "Error" }), _jsx(AlertDescription, { children: error })] })), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Saved Patterns" }), _jsx(CardDescription, { children: "Manage your saved regex patterns for searching memories." })] }), _jsx(CardContent, { children: _jsxs(Table, { children: [_jsx(TableHeader, { children: _jsxs(TableRow, { children: [_jsx(TableHead, { children: "Name" }), _jsx(TableHead, { children: "Pattern" }), _jsx(TableHead, { children: "Tags" }), _jsx(TableHead, { children: "Usage" }), _jsx(TableHead, { children: "Status" }), _jsx(TableHead, { className: "text-right", children: "Actions" })] }) }), _jsx(TableBody, { children: patterns.length === 0 ? (_jsx(TableRow, { children: _jsx(TableCell, { colSpan: 6, className: "h-24 text-center", children: "No patterns found. Create your first pattern to get started." }) })) : (patterns.map((pattern) => (_jsxs(TableRow, { children: [_jsx(TableCell, { className: "font-medium", children: pattern.name }), _jsxs(TableCell, { className: "font-mono text-sm", children: [pattern.pattern.substring(0, 40), pattern.pattern.length > 40 ? '...' : ''] }), _jsx(TableCell, { children: pattern.tags.map(tag => (_jsx(Badge, { variant: "secondary", className: "mr-1", children: tag }, tag))) }), _jsxs(TableCell, { children: [pattern.usage_count, " uses"] }), _jsx(TableCell, { children: _jsx(Badge, { variant: pattern.enabled ? 'default' : 'secondary', children: pattern.enabled ? 'Enabled' : 'Disabled' }) }), _jsxs(TableCell, { className: "text-right", children: [_jsx(Button, { variant: "outline", size: "sm", className: "mr-2", children: "Edit" }), _jsx(Button, { variant: "destructive", size: "sm", onClick: () => deletePattern(pattern.id), children: "Delete" })] })] }, pattern.id)))) })] }) })] })] }), _jsx(TabsContent, { value: "search", className: "space-y-4", children: _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Search with Pattern" }), _jsx(CardDescription, { children: "Search memories using a regex pattern." })] }), _jsxs(CardContent, { className: "space-y-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx(Label, { htmlFor: "search-pattern", children: "Regex Pattern" }), _jsxs("div", { className: "flex gap-2", children: [_jsx(Input, { id: "search-pattern", value: searchQuery, onChange: (e) => setSearchQuery(e.target.value), placeholder: "Enter regex pattern (e.g., \\b\\d{3}-\\d{2}-\\d{4}\\b)", className: "flex-1" }), _jsx(Button, { onClick: handleSearch, disabled: searchLoading, children: searchLoading ? 'Searching...' : 'Search' })] }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Use regex to find patterns in your memories. Example: ", _jsx("code", { className: "bg-muted px-1 rounded", children: "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b" }), " for emails."] })] }), searchResults.length > 0 && (_jsxs("div", { className: "space-y-4", children: [_jsxs("h3", { className: "font-medium", children: ["Search Results (", searchResults.length, ")"] }), _jsx("div", { className: "space-y-2", children: searchResults.map((result, index) => (_jsxs(Card, { children: [_jsx(CardHeader, { children: _jsxs(CardTitle, { className: "text-sm", children: ["Memory #", result.memory_id] }) }), _jsxs(CardContent, { children: [_jsx("p", { className: "text-sm mb-2", children: result.content }), _jsxs("div", { className: "bg-muted/50 p-2 rounded", children: [_jsxs("p", { className: "text-sm font-mono", children: ["Matched: ", _jsx("span", { className: "bg-primary/20 px-1 rounded", children: result.matched_text })] }), _jsxs("p", { className: "text-xs text-muted-foreground", children: ["Position: ", result.match_position] })] })] })] }, index))) })] }))] })] }) }), _jsx(TabsContent, { value: "create", className: "space-y-4", children: _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Create New Pattern" }), _jsx(CardDescription, { children: "Create a new regex pattern to save and reuse for searching memories." })] }), _jsxs(CardContent, { className: "space-y-4", children: [_jsxs(Dialog, { open: isDialogOpen, onOpenChange: setIsDialogOpen, children: [_jsx(DialogTrigger, { asChild: true, children: _jsx(Button, { children: "Create Pattern" }) }), _jsxs(DialogContent, { className: "sm:max-w-[600px]", children: [_jsxs(DialogHeader, { children: [_jsx(DialogTitle, { children: "Create New Pattern" }), _jsx(DialogDescription, { children: "Create a new regex pattern to save and reuse." })] }), _jsxs("div", { className: "space-y-4 py-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx(Label, { htmlFor: "pattern-name", children: "Name" }), _jsx(Input, { id: "pattern-name", value: newPattern.name, onChange: (e) => setNewPattern({ ...newPattern, name: e.target.value }), placeholder: "Email Extractor" })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { htmlFor: "pattern-pattern", children: "Regex Pattern" }), _jsx(Input, { id: "pattern-pattern", value: newPattern.pattern, onChange: (e) => setNewPattern({ ...newPattern, pattern: e.target.value }), placeholder: "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b" }), validationError && (_jsx("p", { className: "text-sm text-destructive", children: validationError }))] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { htmlFor: "pattern-description", children: "Description" }), _jsx(Textarea, { id: "pattern-description", value: newPattern.description, onChange: (e) => setNewPattern({ ...newPattern, description: e.target.value }), placeholder: "Extracts email addresses from text" })] }), _jsxs("div", { className: "space-y-2", children: [_jsx(Label, { children: "Tags" }), _jsx("div", { className: "flex flex-wrap gap-2", children: ['email', 'date', 'amount', 'phone', 'extraction', 'validation'].map(tag => (_jsx(Button, { variant: newPattern.tags.includes(tag) ? 'default' : 'outline', size: "sm", onClick: () => {
                                                                                        const tags = newPattern.tags.includes(tag)
                                                                                            ? newPattern.tags.filter(t => t !== tag)
                                                                                            : [...newPattern.tags, tag];
                                                                                        setNewPattern({ ...newPattern, tags });
                                                                                    }, children: tag }, tag))) })] }), _jsx("div", { className: "space-y-2", children: _jsxs("div", { className: "flex items-center space-x-2", children: [_jsx(Checkbox, { id: "case-sensitive", checked: newPattern.case_sensitive, onCheckedChange: (checked) => setNewPattern({ ...newPattern, case_sensitive: checked }) }), _jsx(Label, { htmlFor: "case-sensitive", children: "Case Sensitive" })] }) }), _jsx("div", { className: "space-y-2", children: _jsxs("div", { className: "flex items-center space-x-2", children: [_jsx(Checkbox, { id: "enabled", checked: newPattern.enabled, onCheckedChange: (checked) => setNewPattern({ ...newPattern, enabled: checked }) }), _jsx(Label, { htmlFor: "enabled", children: "Enabled" })] }) })] }), _jsxs(DialogFooter, { children: [_jsx(Button, { variant: "outline", onClick: () => setIsDialogOpen(false), children: "Cancel" }), _jsx(Button, { onClick: createPattern, children: "Create Pattern" })] })] })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "Pattern Examples" }) }), _jsxs(CardContent, { className: "space-y-2", children: [_jsxs("div", { className: "space-y-1", children: [_jsx("code", { className: "bg-muted px-2 py-1 rounded block", children: "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Email addresses" })] }), _jsxs("div", { className: "space-y-1", children: [_jsx("code", { className: "bg-muted px-2 py-1 rounded block", children: "\\b\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}\\b" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Dates (DD/MM/YYYY or MM/DD/YYYY)" })] }), _jsxs("div", { className: "space-y-1", children: [_jsx("code", { className: "bg-muted px-2 py-1 rounded block", children: "\\$\\d{1,3}(?:,\\d{3})*(?:\\.\\d{2})?" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Currency amounts ($100, $1,000.50)" })] }), _jsxs("div", { className: "space-y-1", children: [_jsx("code", { className: "bg-muted px-2 py-1 rounded block", children: "\\b\\+?\\d{3}[-.\\s]??\\d{3}[-.\\s]??\\d{4}\\b" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Phone numbers" })] })] })] }), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: "Regex Cheat Sheet" }) }), _jsx(CardContent, { children: _jsxs("div", { className: "grid grid-cols-2 gap-4 text-sm", children: [_jsxs("div", { children: [_jsx("p", { className: "font-medium", children: "Characters" }), _jsxs("p", { children: [_jsx("code", { children: ". " }), " Any character"] }), _jsxs("p", { children: [_jsx("code", { children: "\\d " }), " Digit (0-9)"] }), _jsxs("p", { children: [_jsx("code", { children: "\\w " }), " Word character"] }), _jsxs("p", { children: [_jsx("code", { children: "\\s " }), " Whitespace"] })] }), _jsxs("div", { children: [_jsx("p", { className: "font-medium", children: "Quantifiers" }), _jsxs("p", { children: [_jsx("code", { children: "* " }), " 0 or more"] }), _jsxs("p", { children: [_jsx("code", { children: "+ " }), " 1 or more"] }), _jsxs("p", { children: [_jsx("code", { children: "? " }), " 0 or 1"] }), _jsxs("p", { children: [_jsxs("code", { children: [n, " "] }), " Exactly n"] })] }), _jsxs("div", { children: [_jsx("p", { className: "font-medium", children: "Groups" }), _jsxs("p", { children: [_jsx("code", { children: "( ) " }), " Capture group"] }), _jsxs("p", { children: [_jsx("code", { children: "(?: ) " }), " Non-capturing"] }), _jsxs("p", { children: [_jsx("code", { children: "| " }), " OR operator"] })] }), _jsxs("div", { children: [_jsx("p", { className: "font-medium", children: "Anchors" }), _jsxs("p", { children: [_jsx("code", { children: "^ " }), " Start of string"] }), _jsxs("p", { children: [_jsx("code", { children: "$ " }), " End of string"] }), _jsxs("p", { children: [_jsx("code", { children: "\\b " }), " Word boundary"] })] })] }) })] })] })] })] }) })] })] }) }));
}
