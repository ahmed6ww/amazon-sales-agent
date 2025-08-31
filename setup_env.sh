#!/bin/bash

# Amazon Sales Agent - Environment Setup Script
# This script helps you configure environment variables for local and production environments

set -e

echo "🚀 Amazon Sales Agent - Environment Setup"
echo "=========================================="
echo

# Function to create local development environment
setup_local() {
    echo "Setting up LOCAL DEVELOPMENT environment..."
    
    ENV_FILE="frontend/.env.local"
    
    cat > "$ENV_FILE" << EOF
# Local Development Environment
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEBUG_MODE=true
NEXT_PUBLIC_API_TIMEOUT=30000
EOF
    
    echo "✅ Created $ENV_FILE"
    echo "📝 Configuration:"
    echo "   - Environment: development"
    echo "   - API URL: http://localhost:8000"
    echo "   - Debug mode: enabled"
    echo
}

# Function to display production setup instructions
setup_production() {
    echo "Setting up PRODUCTION environment..."
    echo
    echo "🌐 For production deployment, set these environment variables in your hosting platform:"
    echo
    echo "Environment Variables to Set:"
    echo "----------------------------"
    echo "NEXT_PUBLIC_ENVIRONMENT=production"
    echo "NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com"
    echo "NEXT_PUBLIC_DEBUG_MODE=false"
    echo
    echo "📝 Replace 'your-render-app.onrender.com' with your actual Render URL"
    echo
    echo "Platform-specific instructions:"
    echo "• Vercel: Add in Project Settings > Environment Variables"
    echo "• Netlify: Add in Site Settings > Environment Variables"
    echo "• Other platforms: Check their documentation for environment variables"
    echo
}

# Function to update the config file with user's Render URL
update_render_url() {
    echo "Would you like to update your Render URL in the config file? (y/n)"
    read -r response
    
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        echo "Enter your Render app URL (e.g., https://your-app.onrender.com):"
        read -r render_url
        
        if [[ -n "$render_url" ]]; then
            # Update the config file
            CONFIG_FILE="frontend/lib/config.ts"
            
            # Create a backup
            cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
            
            # Update the production URL
            sed -i "s|https://amazon-sales-agent\.onrender\.com|$render_url|g" "$CONFIG_FILE"
            
            echo "✅ Updated config file with URL: $render_url"
            echo "📄 Backup created: $CONFIG_FILE.backup"
        else
            echo "❌ No URL provided, skipping update"
        fi
    fi
}

# Function to test the current configuration
test_config() {
    echo "Testing current configuration..."
    echo
    
    if [[ -f "frontend/.env.local" ]]; then
        echo "📄 Found .env.local file:"
        cat frontend/.env.local
        echo
    else
        echo "📄 No .env.local file found (using defaults)"
    fi
    
    echo "🔧 To test your API connection:"
    echo "1. Start your backend server: cd backend && python -m uvicorn app.main:app --reload"
    echo "2. Start your frontend: cd frontend && npm run dev"
    echo "3. Visit http://localhost:3000/dashboard and check the API Status component"
    echo
}

# Main menu
echo "What would you like to do?"
echo "1) Setup Local Development"
echo "2) Show Production Setup Instructions"
echo "3) Update Render URL in config"
echo "4) Test Current Configuration"
echo "5) Exit"
echo

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        setup_local
        echo "🎯 Next steps:"
        echo "1. Start your backend: cd backend && python -m uvicorn app.main:app --reload"
        echo "2. Start your frontend: cd frontend && npm run dev"
        ;;
    2)
        setup_production
        ;;
    3)
        update_render_url
        ;;
    4)
        test_config
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

