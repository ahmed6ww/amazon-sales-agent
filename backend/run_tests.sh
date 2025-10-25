#!/bin/bash
#
# Test runner script for Amazon scraper anti-blocking features
# Usage: ./run_tests.sh [options]
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Amazon Scraper Anti-Blocking Test Suite                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing...${NC}"
    pip install pytest pytest-timeout pytest-mock
fi

# Change to backend directory
cd "$(dirname "$0")"

# Parse arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:-}"

echo -e "${YELLOW}Test Type: $TEST_TYPE${NC}\n"

case "$TEST_TYPE" in
    unit)
        echo -e "${BLUE}🧪 Running UNIT TESTS (fast, no HTTP requests)${NC}\n"
        pytest tests/test_anti_blocking.py -v -m "not integration" $VERBOSE
        ;;
    
    integration)
        echo -e "${YELLOW}⚠️  WARNING: Integration tests make REAL requests to Amazon${NC}"
        echo -e "${YELLOW}⚠️  This may get your IP temporarily blocked if run too frequently${NC}\n"
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "\n${BLUE}🌐 Running INTEGRATION TESTS (makes real HTTP requests)${NC}\n"
            pytest tests/test_anti_blocking_integration.py -v -m integration -s $VERBOSE
        else
            echo -e "${YELLOW}Integration tests skipped${NC}"
            exit 0
        fi
        ;;
    
    smoke)
        echo -e "${BLUE}💨 Running SMOKE TESTS (quick sanity checks)${NC}\n"
        pytest tests/test_anti_blocking.py::TestUserAgentRotation -v $VERBOSE
        pytest tests/test_anti_blocking.py::TestAntiBlockingSettings -v $VERBOSE
        ;;
    
    all)
        echo -e "${BLUE}🧪 Running ALL UNIT TESTS${NC}\n"
        pytest tests/test_anti_blocking.py -v -m "not integration" $VERBOSE
        
        echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
        echo -e "${YELLOW}Integration tests skipped (use './run_tests.sh integration' to run)${NC}"
        ;;
    
    coverage)
        echo -e "${BLUE}📊 Running tests with COVERAGE${NC}\n"
        pip install pytest-cov >/dev/null 2>&1 || true
        pytest tests/test_anti_blocking.py \
            --cov=app.services.amazon \
            --cov-report=html \
            --cov-report=term \
            -v -m "not integration" $VERBOSE
        echo -e "\n${GREEN}Coverage report generated: htmlcov/index.html${NC}"
        ;;
    
    help|--help|-h)
        echo "Usage: ./run_tests.sh [test_type] [verbose_flag]"
        echo ""
        echo "Test Types:"
        echo "  unit         - Run unit tests only (no HTTP requests) [DEFAULT]"
        echo "  integration  - Run integration tests (makes real HTTP requests)"
        echo "  smoke        - Run quick smoke tests"
        echo "  all          - Run all unit tests"
        echo "  coverage     - Run tests with coverage report"
        echo ""
        echo "Verbose Flag:"
        echo "  -vv          - Extra verbose output"
        echo "  -s           - Show print statements"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                    # Run all unit tests"
        echo "  ./run_tests.sh unit -vv           # Run unit tests with extra verbosity"
        echo "  ./run_tests.sh integration -s     # Run integration tests with output"
        echo "  ./run_tests.sh smoke              # Quick sanity check"
        echo "  ./run_tests.sh coverage           # Generate coverage report"
        exit 0
        ;;
    
    *)
        echo -e "${RED}❌ Unknown test type: $TEST_TYPE${NC}"
        echo "Use './run_tests.sh help' for usage"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Tests PASSED${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ Tests FAILED${NC}\n"
    exit 1
fi
