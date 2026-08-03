import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
export default function UploadPage() {
    const navigate = useNavigate();
    const [files, setFiles] = useState([]);
    const [language, setLanguage] = useState('eng');
    const [extractTables, setExtractTables] = useState(true);
    const [extractImages, setExtractImages] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const supportedLanguages = [
        { value: 'eng', label: 'English' },
        { value: 'urd', label: 'Urdu' },
        { value: 'ara', label: 'Arabic' },
        { value: 'fra', label: 'French' },
        { value: 'spa', label: 'Spanish' },
    ];
    const handleFileChange = (e) => {
        const selectedFiles = Array.from(e.target.files);
        setFiles(selectedFiles);
        setError(null);
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (files.length === 0) {
            setError('Please select at least one file');
            return;
        }
        setUploading(true);
        setProgress(0);
        try {
            for (let i = 0; i <= 100; i += 10) {
                await new Promise(resolve => setTimeout(resolve, 300));
                setProgress(i);
            }
            setSuccess({ message: 'Files uploaded successfully!', count: files.length });
            setTimeout(() => {
                setFiles([]);
                setLanguage('eng');
                navigate('/documents');
            }, 3000);
        }
        catch (err) {
            setError('Failed to upload files. Please try again.');
        }
        finally {
            setUploading(false);
        }
    };
    return (_jsx("div", { className: "min-h-screen bg-background p-6", children: _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold", children: "Upload Documents" }), _jsx("p", { className: "text-muted-foreground", children: "Upload files for OCR processing and memory extraction." })] }), _jsxs(Card, { children: [_jsxs(CardHeader, { children: [_jsx(CardTitle, { children: "Upload Files" }), _jsx(CardDescription, { children: "Drag and drop files here or click to browse." })] }), _jsx(CardContent, { children: _jsxs("form", { onSubmit: handleSubmit, className: "space-y-6", children: [_jsxs("div", { className: "border-2 border-dashed border-muted rounded-lg p-6 text-center", children: [_jsx(Input, { type: "file", multiple: true, onChange: handleFileChange, accept: ".pdf,.docx,.pptx,.txt,.jpg,.jpeg,.png,.gif", className: "hidden", id: "file-upload" }), _jsxs(Label, { htmlFor: "file-upload", className: "cursor-pointer", children: [_jsx("span", { className: "text-primary hover:underline", children: "Click to upload" }), " or drag and drop"] })] }), files.length > 0 && (_jsxs("div", { className: "space-y-4", children: [_jsxs("h3", { className: "text-sm font-medium", children: ["Selected Files (", files.length, ")"] }), _jsx("div", { className: "space-y-2", children: files.map((file, index) => (_jsx("div", { className: "flex items-center justify-between p-2 border rounded", children: _jsxs("span", { className: "text-sm", children: [file.name, " - ", Math.round(file.size / 1024 / 1024 * 100) / 100, " MB"] }) }, index))) })] })), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "space-y-2", children: [_jsx(Label, { htmlFor: "language", children: "OCR Language" }), _jsxs(Select, { value: language, onValueChange: setLanguage, children: [_jsx(SelectTrigger, { id: "language", children: _jsx(SelectValue, { placeholder: "Select language" }) }), _jsx(SelectContent, { children: supportedLanguages.map((lang) => (_jsx(SelectItem, { value: lang.value, children: lang.label }, lang.value))) })] })] }), _jsxs("div", { className: "flex items-center space-x-2", children: [_jsx(Checkbox, { id: "extract-tables", checked: extractTables, onCheckedChange: setExtractTables }), _jsx(Label, { htmlFor: "extract-tables", className: "cursor-pointer", children: "Extract Tables" })] }), _jsxs("div", { className: "flex items-center space-x-2", children: [_jsx(Checkbox, { id: "extract-images", checked: extractImages, onCheckedChange: setExtractImages }), _jsx(Label, { htmlFor: "extract-images", className: "cursor-pointer", children: "Extract Images" })] })] }), error && (_jsxs(Alert, { variant: "destructive", children: [_jsx(AlertTitle, { children: "Error" }), _jsx(AlertDescription, { children: error })] })), success && (_jsxs(Alert, { className: "bg-green-50 border-green-200 text-green-800", children: [_jsx(AlertTitle, { children: "Success!" }), _jsxs(AlertDescription, { children: [success.message, " ", success.count, " files uploaded."] })] })), uploading ? (_jsxs("div", { className: "space-y-4", children: [_jsxs("span", { children: ["Uploading... ", progress, "%"] }), _jsx(Progress, { value: progress, className: "h-2" })] })) : (_jsx(Button, { type: "submit", className: "w-full", disabled: files.length === 0, children: files.length === 0 ? 'Select files to upload' : 'Upload ' + files.length + ' file(s)' }))] }) })] })] }) }));
}
