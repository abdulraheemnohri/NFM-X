import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

export default function V2Graph() {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">V2 Graph</h1>
          <p className="text-muted-foreground">Visualize relationships between V2 memories.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Graph Visualization</CardTitle>
            <CardDescription>
              Interactive graph showing connections between your V2 memories.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-96 flex items-center justify-center bg-muted/50 rounded">
            <div className="text-center">
              <h3 className="text-lg font-medium mb-2">Graph Viewer</h3>
              <p className="text-muted-foreground">
                Interactive graph visualization will be rendered here.
              </p>
              <p className="text-sm text-muted-foreground mt-4">
                Use the V4 Graph page for enhanced visualization features.
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Graph Features</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <span>Node-based visualization</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <span>Connection mapping</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <span>Interactive exploration</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <span>Filter by memory type</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button asChild className="w-full">
                <Link to="/v2">V2 Dashboard</Link>
              </Button>
              <Button asChild variant="outline" className="w-full">
                <Link to="/v2/memories">V2 Memories</Link>
              </Button>
              <Button asChild variant="outline" className="w-full">
                <Link to="/v2/conflicts">V2 Conflicts</Link>
              </Button>
              <Button asChild variant="outline" className="w-full">
                <Link to="/">Back to V4</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}