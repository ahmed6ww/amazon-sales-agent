# Environment Configuration Guide

This guide explains how to configure your Amazon Sales Agent application for different environments (local development and production).

## Overview

The application automatically detects the environment and configures API endpoints accordingly:

- **Local Development**: Uses `http://localhost:8000`
- **Production**: Uses your deployed Render backend URL

## Environment Detection

The app uses multiple methods to detect the environment:

1. **Browser hostname detection** (most reliable for local dev)
2. **NEXT_PUBLIC_ENVIRONMENT** variable
3. **NODE_ENV** fallback
4. **Production as default** (for safety)

## Setup Instructions

### 1. Local Development

For local development, you have two options:

**Option A: No configuration needed (recommended)**
- Just run `npm run dev` or `npm start`
- The app will automatically detect localhost and use `http://localhost:8000`

**Option B: Use environment file**
Create a `.env.local` file in the frontend directory:

```bash
# Development environment
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEBUG_MODE=true
```

### 2. Production Deployment

For production deployment (like Vercel, Netlify, etc.), set these environment variables:

```bash
# Production environment
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
NEXT_PUBLIC_DEBUG_MODE=false
```

**Replace `https://your-render-app.onrender.com` with your actual Render deployment URL.**

### 3. Staging (Optional)

If you have a staging environment:

```bash
# Staging environment
NEXT_PUBLIC_ENVIRONMENT=staging
NEXT_PUBLIC_API_URL=https://your-staging-app.onrender.com
NEXT_PUBLIC_DEBUG_MODE=true
```

## Configuration Priority

The application uses this priority order for API URL:

1. **NEXT_PUBLIC_API_URL** (highest priority)
2. **Environment-specific defaults** based on detected environment
3. **Hostname detection** for local development

## Updating Your Render URL

Update the production URL in `/frontend/lib/config.ts`:

```typescript
// Update this line with your actual Render URL
baseUrl: 'https://your-actual-render-app.onrender.com',
```

## Verification

To verify your configuration is working:

1. **Development**: Check browser console for `[DEBUG]` messages
2. **Production**: Use the API test endpoint in your application
3. **Manual check**: The config info is available via `getConfigInfo()` function

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_ENVIRONMENT` | No | Explicit environment setting | `development`, `production`, `staging` |
| `NEXT_PUBLIC_API_URL` | No* | Override API base URL | `https://your-app.onrender.com` |
| `NEXT_PUBLIC_DEBUG_MODE` | No | Enable debug logging | `true`, `false` |

*Required for production if not using the default configured URL.

## Troubleshooting

1. **API calls failing**: Check the browser network tab for the actual URLs being called
2. **Wrong environment detected**: Set `NEXT_PUBLIC_ENVIRONMENT` explicitly
3. **Debug info**: Enable debug mode and check console logs

## Testing

You can test your configuration by calling the test endpoint:

```javascript
import { api } from '@/lib/api';

// Test API connection
const result = await api.testConnection();
console.log('API Test Result:', result);
``` 