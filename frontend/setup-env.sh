#!/bin/bash

# Setup script for Amazon Sales Agent Frontend
# This script creates the .env.local file with the correct backend URL

echo "🚀 Setting up Amazon Sales Agent Frontend Environment"
echo "=================================================="

# Create .env.local file
cat > .env.local << EOF
# Local environment configuration for Amazon Sales Agent Frontend
# This file is used for local development and testing

# Backend API URL - using your deployed Render backend
NEXT_PUBLIC_API_URL=https://amazon-sales-agent.onrender.com

# Environment specification
NEXT_PUBLIC_ENVIRONMENT=production

# Optional settings
NEXT_PUBLIC_DEBUG_MODE=false
NEXT_PUBLIC_ENABLE_ANALYTICS=false
EOF

echo "✅ Created .env.local file with production backend URL"
echo "📡 Backend URL: https://amazon-sales-agent.onrender.com"
echo ""
echo "🏃 To start the development server:"
echo "   npm run dev"
echo ""
echo "🔧 To customize the configuration:"
echo "   Edit .env.local file directly"
echo ""
echo "📚 For more information, see README.md" 