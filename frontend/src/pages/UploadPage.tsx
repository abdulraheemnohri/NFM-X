import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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
    } catch (err) {
      setError('Failed to upload files. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Upload Documents</h1>
          <p className="text-muted-foreground">Upload files for OCR processing and memory extraction.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Upload Files</CardTitle>
            <CardDescription>
              Drag and drop files here or click to browse.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="border-2 border-dashed border-muted rounded-lg p-6 text-center">
                <Input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.pptx,.txt,.jpg,.jpeg,.png,.gif"
                  className="hidden"
                  id="file-upload"
                />
                <Label htmlFor="file-upload" className="cursor-pointer">
                  <span className="text-primary hover:underline">Click to upload</span> or drag and drop
                </Label>
              </div>

              {files.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-sm font-medium">Selected Files ({files.length})</h3>
                  <div className="space-y-2">
                    {files.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 border rounded">
                        <span className="text-sm">{file.name} - {Math.round(file.size / 1024 / 1024 * 100) / 100} MB</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="language">OCR Language</Label>
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger id="language">
                      <SelectValue placeholder="Select language" />
                    </SelectTrigger>
                    <SelectContent>
                      {supportedLanguages.map((lang) => (
                        <SelectItem key={lang.value} value={lang.value}>
                          {lang.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="extract-tables"
                    checked={extractTables}
                    onCheckedChange={setExtractTables}
                  />
                  <Label htmlFor="extract-tables" className="cursor-pointer">
                    Extract Tables
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="extract-images"
                    checked={extractImages}
                    onCheckedChange={setExtractImages}
                  />
                  <Label htmlFor="extract-images" className="cursor-pointer">
                    Extract Images
                  </Label>
                </div>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="bg-green-50 border-green-200 text-green-800">
                  <AlertTitle>Success!</AlertTitle>
                  <AlertDescription>
                    {success.message} {success.count} files uploaded.
                  </AlertDescription>
                </Alert>
              )}

              {uploading ? (
                <div className="space-y-4">
                  <span>Uploading... {progress}%</span>
                  <Progress value={progress} className="h-2" />
                </div>
              ) : (
                <Button type="submit" className="w-full" disabled={files.length === 0}>
                  {files.length === 0 ? 'Select files to upload' : 'Upload ' + files.length + ' file(s)'}
                </Button>
              )}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}