/**
 * API Status Component
 * Displays current API configuration and connection status
 * Useful for debugging and verifying configuration in different environments
 */

'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { getConfigInfo, config } from '@/lib/config';

interface ApiStatus {
  isOnline: boolean;
  responseTime: number | null;
  error: string | null;
  lastChecked: Date | null;
}

export function ApiStatus() {
  const [status, setStatus] = useState<ApiStatus>({
    isOnline: false,
    responseTime: null,
    error: null,
    lastChecked: null,
  });
  const [isChecking, setIsChecking] = useState(false);

  const checkApiStatus = async () => {
    setIsChecking(true);
    const startTime = Date.now();

    try {
      const result = await api.testConnection();
      const responseTime = Date.now() - startTime;

      if (result.success) {
        setStatus({
          isOnline: true,
          responseTime,
          error: null,
          lastChecked: new Date(),
        });
      } else {
        setStatus({
          isOnline: false,
          responseTime: null,
          error: result.error || 'Unknown error',
          lastChecked: new Date(),
        });
      }
    } catch (error) {
      setStatus({
        isOnline: false,
        responseTime: null,
        error: error instanceof Error ? error.message : 'Connection failed',
        lastChecked: new Date(),
      });
    } finally {
      setIsChecking(false);
    }
  };

  // Check status on component mount
  useEffect(() => {
    checkApiStatus();
  }, []);

  const configInfo = getConfigInfo();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>API Status</span>
          <div className="flex items-center gap-2">
            <Badge variant={status.isOnline ? 'default' : 'destructive'}>
              {status.isOnline ? 'Online' : 'Offline'}
            </Badge>
            <Button
              onClick={checkApiStatus}
              disabled={isChecking}
              size="sm"
              variant="outline"
            >
              {isChecking ? 'Checking...' : 'Test'}
            </Button>
          </div>
        </CardTitle>
        <CardDescription>
          API connection status and configuration details
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* API Status */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Status:</span>
            <span className={`ml-2 ${status.isOnline ? 'text-green-600' : 'text-red-600'}`}>
              {status.isOnline ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          {status.responseTime && (
            <div>
              <span className="font-medium">Response Time:</span>
              <span className="ml-2">{status.responseTime}ms</span>
            </div>
          )}
          {status.lastChecked && (
            <div className="col-span-2">
              <span className="font-medium">Last Checked:</span>
              <span className="ml-2">{status.lastChecked.toLocaleTimeString()}</span>
            </div>
          )}
          {status.error && (
            <div className="col-span-2">
              <span className="font-medium text-red-600">Error:</span>
              <span className="ml-2 text-red-600">{status.error}</span>
            </div>
          )}
        </div>

        {/* Configuration Details */}
        <div className="border-t pt-4">
          <h4 className="font-medium mb-2">Configuration</h4>
          <div className="space-y-2 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Environment:</span>
                <Badge variant="outline" className="ml-2">
                  {configInfo.environment}
                </Badge>
              </div>
              <div>
                <span className="font-medium">Debug Mode:</span>
                <Badge variant={configInfo.features.enableDebugMode ? 'default' : 'secondary'} className="ml-2">
                  {configInfo.features.enableDebugMode ? 'On' : 'Off'}
                </Badge>
              </div>
            </div>
            <div>
              <span className="font-medium">API Base URL:</span>
              <span className="ml-2 font-mono text-xs">{configInfo.apiBaseUrl}</span>
            </div>
          </div>
        </div>

        {/* Environment Detection Details */}
        {config.features.enableDebugMode && (
          <div className="border-t pt-4">
            <h4 className="font-medium mb-2">Debug Info</h4>
            <div className="space-y-1 text-xs font-mono">
              <div>NODE_ENV: {configInfo.detectedEnv.NODE_ENV}</div>
              <div>NEXT_PUBLIC_ENVIRONMENT: {configInfo.detectedEnv.NEXT_PUBLIC_ENVIRONMENT || 'not set'}</div>
              <div>NEXT_PUBLIC_API_URL: {configInfo.detectedEnv.NEXT_PUBLIC_API_URL || 'not set'}</div>
              <div>Hostname: {configInfo.detectedEnv.hostname}</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 