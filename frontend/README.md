This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Environment Configuration

This project uses environment-based configuration to handle different deployment environments (development, staging, production).

### Setup Instructions

1. **Copy the environment template:**
   ```bash
   cp env.example .env.local
   ```

2. **Configure your environment variables:**
   ```bash
   # Required for production
   NEXT_PUBLIC_API_URL=https://amazon-sales-agent.onrender.com
   
   # Optional environment specification
   NEXT_PUBLIC_ENVIRONMENT=production
   ```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Production/Staging | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_ENVIRONMENT` | No | Inferred from NODE_ENV | Environment: development, staging, production |
| `NEXT_PUBLIC_DEBUG_MODE` | No | `true` in dev, `false` in prod | Enable debug logging |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | No | `false` in dev, `true` in prod | Enable analytics |

### Configuration Usage

The application includes a centralized configuration system:

```typescript
import { config, getApiUrl, api } from '@/lib/config';

// Get the full API URL for a specific endpoint
const analyzeUrl = getApiUrl('analyze');

// Use the API client
const response = await api.startAnalysis({
  asin_or_url: 'B00EXAMPLE',
  marketplace: 'US',
  revenue_csv: file1,
  design_csv: file2
});
```

### API Client

The application includes a complete API client (`@/lib/api`) with:

- Automatic environment-based URL configuration
- Error handling and timeout management
- TypeScript support with proper types
- Debug logging in development
- Support for file uploads and JSON requests

### Environment-Specific Behavior

- **Development**: Uses `http://localhost:8000`, enables debug mode, disables analytics
- **Staging**: Uses staging API URL, production-like settings with optional debug
- **Production**: Uses production API URL, disables debug mode, enables analytics

## Deployment

### Vercel (Recommended)

1. Set environment variables in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://amazon-sales-agent.onrender.com
   NEXT_PUBLIC_ENVIRONMENT=production
   ```

2. Deploy:
   ```bash
   npm run build
   npm run start
   ```

### Docker

1. Build the container:
   ```bash
   docker build -t amazon-sales-agent-frontend .
   ```

2. Run with environment variables:
   ```bash
   docker run -p 3000:3000 \
     -e NEXT_PUBLIC_API_URL=https://amazon-sales-agent.onrender.com \
     -e NEXT_PUBLIC_ENVIRONMENT=production \
     amazon-sales-agent-frontend
   ```

### Manual Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Set environment variables and start:
   ```bash
   export NEXT_PUBLIC_API_URL=https://amazon-sales-agent.onrender.com
   export NEXT_PUBLIC_ENVIRONMENT=production
   npm run start
   ```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
