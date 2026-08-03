import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
export default function DocumentsPage() {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    useEffect(() => {
        async function fetchDocuments() {
            try {
                setLoading(true);
                // Simulate API call
                const mockDocuments = [
                    { id: 1, name: 'invoice_2024.pdf', type: 'pdf', size: '2.4 MB', pages: 12, status: 'processed', extracted: 45, date: '2024-01-15' },
                    { id: 2, name: 'contract.docx', type: 'docx', size: '1.8 MB', pages: 8, status: 'processed', extracted: 32, date: '2024-01-14' },
                    { id: 3, name: 'presentation.pptx', type: 'pptx', size: '5.6 MB', pages: 24, status: 'processing', extracted: 0, date: '2024-01-13' },
                    { id: 4, name: 'notes.txt', type: 'txt', size: '56 KB', pages: 1, status: 'error', extracted: 0, date: '2024-01-12' },
                    { id: 5, name: 'report.pdf', type: 'pdf', size: '3.2 MB', pages: 15, status: 'processed', extracted: 67, date: '2024-01-10' },
                ];
                setDocuments(mockDocuments);
                setError(null);
            }
            catch (err) {
                setError('Failed to fetch documents');
                setDocuments([]);
            }
            finally {
                setLoading(false);
            }
        }
        fetchDocuments();
    }, []);
    const getStatusBadge = (status) => {
        switch (status) {
            case 'processed':
                return _jsx(Badge, { variant: "default", children: status });
            case 'processing':
                return _jsx(Badge, { variant: "secondary", children: status });
            case 'error':
                return _jsx(Badge, { variant: "destructive", children: status });
            default:
                return _jsx(Badge, { variant: "outline", children: status });
        }
    };
    if (loading) {
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Documents" }), _jsx("p", { className: "text-muted-foreground", children: "Manage your uploaded documents." })] }), _jsxs("div", { className: "space-y-4", children: [_jsx(Skeleton, { className: "h-10 w-full" }), _jsx(Skeleton, { className: "h-96 w-full" })] })] }) }));
    }
    if (error) {
        return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Documents" }), _jsx("p", { className: "text-muted-foreground", children: "Manage your uploaded documents." })] }), _jsxs(Alert, { variant: "destructive", children: [_jsx(AlertTitle, { children: "Error" }), _jsx(AlertDescription, { children: error })] })] }) }));
    }
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Documents" }), _jsx("p", { className: "text-muted-foreground", children: "Manage your uploaded documents and OCR results." })] }), _jsx(Button, { asChild: true, children: _jsx(Link, { to: "/upload", children: "Upload New Document" }) })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "All Documents" }), _jsx(CardDescription, { children: "View and manage all your uploaded documents with OCR processing status." })] }), _jsx(CardContent, { children: _jsxs(Table, { children: [_jsx(TableHeader, { children: _jsxs(TableRow, { children: [_jsx(TableHead, { children: "Name" }), _jsx(TableHead, { children: "Type" }), _jsx(TableHead, { children: "Size" }), _jsx(TableHead, { children: "Pages" }), _jsx(TableHead, { children: "Status" }), _jsx(TableHead, { children: "Extracted Memories" }), _jsx(TableHead, { children: "Date" }), _jsx(TableHead, { className: "text-right", children: "Actions" })] }) }), _jsx(TableBody, { children: documents.length === 0 ? (_jsx(TableRow, { children: _jsx(TableCell, { colSpan: 8, className: "h-24 text-center", children: "No documents found. Upload your first document to get started." }) })) : (documents.map((doc) => (_jsxs(TableRow, { children: [_jsx(TableCell, { className: "font-medium", children: doc.name }), _jsx(TableCell, { children: doc.type.toUpperCase() }), _jsx(TableCell, { children: doc.size }), _jsx(TableCell, { children: doc.pages }), _jsx(TableCell, { children: getStatusBadge(doc.status) }), _jsx(TableCell, { children: doc.extracted }), _jsx(TableCell, { children: doc.date }), _jsxs(TableCell, { className: "text-right", children: [_jsx(Button, { variant: "ghost", size: "sm", asChild: true, children: _jsx(Link, { to: `/documents/${doc.id}`, children: "View" }) }), _jsx(Button, { variant: "ghost", size: "sm", children: "Reprocess" })] })] }, doc.id)))) })] }) })] }), _jsxs("div", { className: "grid gap-4 md:grid-cols-3", children: [_jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: [_jsx(CardTitle, { className: "text-sm font-medium", children: "Total Documents" }), _jsx("svg", { className: "h-4 w-4 text-muted-foreground", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" }) })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold", children: documents.length }), _jsx("p", { className: "text-xs text-muted-foreground", children: "+12% from last month" })] })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: [_jsx(CardTitle, { className: "text-sm font-medium", children: "Processed" }), _jsx("svg", { className: "h-4 w-4 text-muted-foreground", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M5 13l4 4L19 7" }) })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold text-green-600", children: documents.filter(d => d.status === 'processed').length }), _jsx("p", { className: "text-xs text-muted-foreground", children: "Successfully processed" })] })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between space-y-0 pb-2", children: [_jsx(CardTitle, { className: "text-sm font-medium", children: "Total Memories Extracted" }), _jsx("svg", { className: "h-4 w-4 text-muted-foreground", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M13 10V3L4 14h7v7l9-11h-7z" }) })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "text-2xl font-bold", children: documents.reduce((sum, d) => sum + d.extracted, 0) }), _jsx("p", { className: "text-xs text-muted-foreground", children: "From all documents" })] })] })] })] }) }));
}
