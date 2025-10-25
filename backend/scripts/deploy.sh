#!/bin/bash
set -e

echo "🚀 Manual Deployment Script"
echo "==============================================="

# Check if on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: You're on branch '$CURRENT_BRANCH', not 'main'"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ You have uncommitted changes!"
    echo "Please commit or stash them first."
    exit 1
fi

# Run tests
echo ""
echo "🧪 Running tests before deployment..."
./scripts/test.sh

echo ""
echo "✅ Tests passed!"
echo ""

# Push to GitHub (triggers auto-deploy on Render)
echo "📤 Pushing to GitHub..."
git push origin "$CURRENT_BRANCH"

echo ""
echo "==============================================="
echo "✅ Code pushed to GitHub!"
echo "==============================================="
echo ""
echo "Render will automatically deploy from the '$CURRENT_BRANCH' branch."
echo "Monitor deployment: https://dashboard.render.com/"
echo ""
echo "To check deployment status:"
echo "  ./scripts/health_check.sh https://your-app.onrender.com"
echo ""

