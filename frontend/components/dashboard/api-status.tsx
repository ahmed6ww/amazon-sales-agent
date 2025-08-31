/**
 * API Status Component
 * Displays current API configuration and connection status
 * Useful for debugging and verifying configuration in different environments
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getConfigInfo, isDevelopment, isProduction, isStaging } from '@/lib/config';
import { api } from '@/lib/api';

interface ApiStatusProps {
  showDetails?: boolean;
  className?: string;
}

export function ApiStatus({ showDetails = true, className = '' }: ApiStatusProps) {
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'disconnected' | 'error'>('checking');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const checkApiConnection = async () => {
    setConnectionStatus('checking');
    setErrorMessage('');

    try {
      const response = await api.testConnection();
      
      if (response.success) {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
        setErrorMessage(response.error || 'Unknown error');
      }
    } catch (error) {
      setConnectionStatus('disconnected');
      setErrorMessage(error instanceof Error ? error.message : 'Connection failed');
    }

    setLastChecked(new Date());
  };

  useEffect(() => {
    // Check connection on component mount
    checkApiConnection();

    // Auto-refresh in development every 30 seconds
    if (isDevelopment()) {
      const interval = setInterval(checkApiConnection, 30000);
      return () => clearInterval(interval);
    }
  }, []);

  const configInfo = getConfigInfo();

  const getStatusBadge = () => {
    switch (connectionStatus) {
      case 'checking':
        return <Badge variant="outline">Checking...</Badge>;
      case 'connected':
        return <Badge variant="default" className="bg-green-500">Connected</Badge>;
      case 'disconnected':
        return <Badge variant="destructive">Disconnected</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getEnvironmentBadge = () => {
    if (isDevelopment()) {
      return <Badge variant="outline" className="bg-blue-100 text-blue-800">Development</Badge>;
    }
    if (isStaging()) {
      return <Badge variant="outline" className="bg-yellow-100 text-yellow-800">Staging</Badge>;
    }
    if (isProduction()) {
      return <Badge variant="outline" className="bg-green-100 text-green-800">Production</Badge>;
    }
    return <Badge variant="outline">Unknown</Badge>;
  };

  if (!showDetails) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <span className="text-sm text-gray-600">API:</span>
        {getStatusBadge()}
        {getEnvironmentBadge()}
      </div>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>API Configuration</span>
          <div className="flex gap-2">
            {getEnvironmentBadge()}
            {getStatusBadge()}
          </div>
        </CardTitle>
        <CardDescription>
          Current API configuration and connection status
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Connection Status */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Connection Status:</span>
            <div className="flex items-center gap-2">
              {getStatusBadge()}
              <Button
                variant="outline"
                size="sm"
                onClick={checkApiConnection}
                disabled={connectionStatus === 'checking'}
              >
                {connectionStatus === 'checking' ? 'Checking...' : 'Test Connection'}
              </Button>
            </div>
          </div>
          
          {lastChecked && (
            <p className="text-xs text-gray-500">
              Last checked: {lastChecked.toLocaleTimeString()}
            </p>
          )}
          
          {errorMessage && (
            <p className="text-xs text-red-600 bg-red-50 p-2 rounded">
              Error: {errorMessage}
            </p>
          )}
        </div>

        {/* Configuration Details */}
        <div className="space-y-3 border-t pt-4">
          <h4 className="font-medium text-sm">Configuration Details</h4>
          
          <div className="grid grid-cols-1 gap-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Environment:</span>
              <span className="font-mono">{configInfo.environment}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">API Base URL:</span>
              <span className="font-mono text-xs break-all">{configInfo.apiBaseUrl}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Debug Mode:</span>
              <span className="font-mono">{configInfo.features.enableDebugMode ? 'Enabled' : 'Disabled'}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Analytics:</span>
              <span className="font-mono">{configInfo.features.enableAnalytics ? 'Enabled' : 'Disabled'}</span>
            </div>
          </div>
        </div>

        {/* Available Endpoints */}
        {isDevelopment() && (
          <div className="space-y-3 border-t pt-4">
            <h4 className="font-medium text-sm">Available Endpoints</h4>
            <div className="grid grid-cols-1 gap-1 text-xs">
              {Object.entries(configInfo.endpoints).map(([key, path]) => (
                <div key={key} className="flex justify-between font-mono">
                  <span className="text-gray-600">{key}:</span>
                  <span>{path}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Environment Variables Status */}
        {isDevelopment() && (
          <div className="space-y-3 border-t pt-4">
            <h4 className="font-medium text-sm">Environment Variables</h4>
            <div className="grid grid-cols-1 gap-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">NEXT_PUBLIC_API_URL:</span>
                <span className="font-mono">
                  {process.env.NEXT_PUBLIC_API_URL ? '✅ Set' : '❌ Not set'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">NODE_ENV:</span>
                <span className="font-mono">{process.env.NODE_ENV}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">NEXT_PUBLIC_ENVIRONMENT:</span>
                <span className="font-mono">
                  {process.env.NEXT_PUBLIC_ENVIRONMENT || 'Not set (inferred)'}
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default ApiStatus; 