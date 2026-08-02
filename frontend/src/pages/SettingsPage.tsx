import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    general: {
      appName: 'NFM-X',
      theme: 'system',
      language: 'en',
      timezone: 'UTC'
    },
    ocr: {
      defaultLanguage: 'eng',
      tableExtraction: true,
      imageExtraction: false,
      confidenceThreshold: 70
    },
    memory: {
      autoCompression: true,
      compressionInterval: 'daily',
      maxMemories: 10000,
      retentionDays: 365
    },
    api: {
      rateLimit: 100,
      corsOrigins: '*',
      authRequired: false
    }
  });
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // Save settings logic
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Configure your NFM-X application.</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="ocr">OCR</TabsTrigger>
            <TabsTrigger value="memory">Memory</TabsTrigger>
            <TabsTrigger value="api">API</TabsTrigger>
          </TabsList>

          <TabsContent value="general" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>General Settings</CardTitle>
                <CardDescription>
                  Basic application configuration.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="appName">Application Name</Label>
                  <Input
                    id="appName"
                    value={settings.general.appName}
                    onChange={(e) => updateSetting('general', 'appName', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="theme">Theme</Label>
                  <Select
                    value={settings.general.theme}
                    onValueChange={(v) => updateSetting('general', 'theme', v)}
                  >
                    <SelectTrigger id="theme">
                      <SelectValue placeholder="Select theme" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select
                    value={settings.general.language}
                    onValueChange={(v) => updateSetting('general', 'language', v)}
                  >
                    <SelectTrigger id="language">
                      <SelectValue placeholder="Select language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="ur">Urdu</SelectItem>
                      <SelectItem value="ar">Arabic</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select
                    value={settings.general.timezone}
                    onValueChange={(v) => updateSetting('general', 'timezone', v)}
                  >
                    <SelectTrigger id="timezone">
                      <SelectValue placeholder="Select timezone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="Asia/Karachi">Asia/Karachi (PKT)</SelectItem>
                      <SelectItem value="America/New_York">America/New_York (EST)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ocr" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>OCR Settings</CardTitle>
                <CardDescription>
                  Configure OCR processing options.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="ocrLanguage">Default OCR Language</Label>
                  <Select
                    value={settings.ocr.defaultLanguage}
                    onValueChange={(v) => updateSetting('ocr', 'defaultLanguage', v)}
                  >
                    <SelectTrigger id="ocrLanguage">
                      <SelectValue placeholder="Select language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="eng">English</SelectItem>
                      <SelectItem value="urd">Urdu</SelectItem>
                      <SelectItem value="ara">Arabic</SelectItem>
                      <SelectItem value="fra">French</SelectItem>
                      <SelectItem value="spa">Spanish</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="tableExtraction">Table Extraction</Label>
                    <p className="text-sm text-muted-foreground">Extract tables from documents</p>
                  </div>
                  <Switch
                    id="tableExtraction"
                    checked={settings.ocr.tableExtraction}
                    onCheckedChange={(v) => updateSetting('ocr', 'tableExtraction', v)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="imageExtraction">Image Extraction</Label>
                    <p className="text-sm text-muted-foreground">Extract images from documents</p>
                  </div>
                  <Switch
                    id="imageExtraction"
                    checked={settings.ocr.imageExtraction}
                    onCheckedChange={(v) => updateSetting('ocr', 'imageExtraction', v)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confidence">Confidence Threshold (%)</Label>
                  <Slider
                    id="confidence"
                    value={[settings.ocr.confidenceThreshold]}
                    onValueChange={(v) => updateSetting('ocr', 'confidenceThreshold', v[0])}
                    min={50}
                    max={95}
                    step={5}
                  />
                  <p className="text-sm text-muted-foreground">
                    Minimum confidence for text extraction: {settings.ocr.confidenceThreshold}%
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="memory" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Memory Settings</CardTitle>
                <CardDescription>
                  Configure memory management options.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="autoCompression">Auto Compression</Label>
                    <p className="text-sm text-muted-foreground">Automatically compress old memories</p>
                  </div>
                  <Switch
                    id="autoCompression"
                    checked={settings.memory.autoCompression}
                    onCheckedChange={(v) => updateSetting('memory', 'autoCompression', v)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="compressionInterval">Compression Interval</Label>
                  <Select
                    value={settings.memory.compressionInterval}
                    onValueChange={(v) => updateSetting('memory', 'compressionInterval', v)}
                  >
                    <SelectTrigger id="compressionInterval">
                      <SelectValue placeholder="Select interval" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hourly">Hourly</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxMemories">Max Memories</Label>
                  <Input
                    id="maxMemories"
                    type="number"
                    value={settings.memory.maxMemories}
                    onChange={(e) => updateSetting('memory', 'maxMemories', parseInt(e.target.value) || 0)}
                    min={100}
                    max={100000}
                  />
                  <p className="text-sm text-muted-foreground">Maximum number of memories to store</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="retentionDays">Retention Days</Label>
                  <Input
                    id="retentionDays"
                    type="number"
                    value={settings.memory.retentionDays}
                    onChange={(e) => updateSetting('memory', 'retentionDays', parseInt(e.target.value) || 0)}
                    min={1}
                    max={3650}
                  />
                  <p className="text-sm text-muted-foreground">Number of days to retain memories</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>API Settings</CardTitle>
                <CardDescription>
                  Configure API options and security.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="rateLimit">Rate Limit (requests/minute)</Label>
                  <Input
                    id="rateLimit"
                    type="number"
                    value={settings.api.rateLimit}
                    onChange={(e) => updateSetting('api', 'rateLimit', parseInt(e.target.value) || 0)}
                    min={10}
                    max={1000}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="corsOrigins">CORS Origins</Label>
                  <Input
                    id="corsOrigins"
                    value={settings.api.corsOrigins}
                    onChange={(e) => updateSetting('api', 'corsOrigins', e.target.value)}
                    placeholder="*, https://example.com"
                  />
                  <p className="text-sm text-muted-foreground">Comma-separated list of allowed origins</p>
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="authRequired">Authentication Required</Label>
                    <p className="text-sm text-muted-foreground">Require API key for all endpoints</p>
                  </div>
                  <Switch
                    id="authRequired"
                    checked={settings.api.authRequired}
                    onCheckedChange={(v) => updateSetting('api', 'authRequired', v)}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {saved && (
          <Alert className="bg-green-50 border-green-200 text-green-800">
            <AlertTitle>Settings saved!</AlertTitle>
            <AlertDescription>
              Your settings have been saved successfully.
            </AlertDescription>
          </Alert>
        )}

        <div className="flex justify-end">
          <Button onClick={handleSave}>
            Save All Settings
          </Button>
        </div>
      </div>
    </div>
  );
}