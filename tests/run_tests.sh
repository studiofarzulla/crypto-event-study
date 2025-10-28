#!/bin/bash
# Quick test runner for cryptocurrency event study
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Event Study Test Suite Runner${NC}"
echo -e "${BLUE}========================================${NC}"

# Parse command line arguments
MODE=${1:-all}

case "$MODE" in
    "all")
        echo -e "\n${GREEN}Running all tests...${NC}"
        pytest -v
        ;;
    "fast")
        echo -e "\n${GREEN}Running fast tests only (skipping slow)...${NC}"
        pytest -v -m "not slow"
        ;;
    "coverage")
        echo -e "\n${GREEN}Running tests with coverage report...${NC}"
        pytest --cov=event_study/code --cov-report=html --cov-report=term-missing
        echo -e "\n${BLUE}Coverage report generated at: htmlcov/index.html${NC}"
        ;;
    "data")
        echo -e "\n${GREEN}Running data validation tests...${NC}"
        pytest -v -m data_validation
        ;;
    "models")
        echo -e "\n${GREEN}Running GARCH model tests...${NC}"
        pytest -v tests/test_garch_models.py
        ;;
    "stats")
        echo -e "\n${GREEN}Running statistical tests...${NC}"
        pytest -v -m statistical
        ;;
    "integration")
        echo -e "\n${GREEN}Running integration tests...${NC}"
        pytest -v -m integration
        ;;
    "edge")
        echo -e "\n${GREEN}Running edge case tests...${NC}"
        pytest -v -m edge_case
        ;;
    "repro")
        echo -e "\n${GREEN}Running reproducibility tests...${NC}"
        pytest -v -m reproducibility
        ;;
    "parallel")
        echo -e "\n${GREEN}Running tests in parallel (4 workers)...${NC}"
        pytest -n 4
        ;;
    "debug")
        echo -e "\n${GREEN}Running tests with debugging...${NC}"
        pytest -vv -s --tb=short
        ;;
    "help")
        echo -e "\n${YELLOW}Usage:${NC} ./run_tests.sh [mode]"
        echo -e "\n${YELLOW}Available modes:${NC}"
        echo "  all          - Run all tests (default)"
        echo "  fast         - Run fast tests only (skip slow)"
        echo "  coverage     - Run with coverage report"
        echo "  data         - Run data validation tests"
        echo "  models       - Run GARCH model tests"
        echo "  stats        - Run statistical tests"
        echo "  integration  - Run integration tests"
        echo "  edge         - Run edge case tests"
        echo "  repro        - Run reproducibility tests"
        echo "  parallel     - Run tests in parallel"
        echo "  debug        - Run with verbose debugging"
        echo "  help         - Show this help message"
        echo ""
        exit 0
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Tests completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}✗ Some tests failed${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
