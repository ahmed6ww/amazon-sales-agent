#!/bin/bash
set -e

echo "🧪 Running test suite..."
echo "==============================================="

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install pytest pytest-cov
fi

# Run tests
echo "Running unit tests..."
pytest tests/ -v --tb=short

echo ""
echo "==============================================="
echo "✅ All tests passed!"
echo "==============================================="

