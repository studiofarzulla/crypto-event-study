#!/usr/bin/env bash
# Launcher script for cryptocurrency event study analysis
# Handles Python path setup and virtual environment activation

set -e  # Exit on error

# Get the directory where this script is located (project root)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Cryptocurrency Event Study Analysis"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please create one first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✓${NC} Activating virtual environment..."
source venv/bin/activate

# Verify dependencies
echo -e "${GREEN}✓${NC} Checking dependencies..."
python -c "import pandas, numpy, scipy, statsmodels, matplotlib" 2>/dev/null || {
    echo -e "${RED}Error: Missing dependencies${NC}"
    echo "Install them with:"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
}

# Verify data files exist
echo -e "${GREEN}✓${NC} Checking data files..."
if [ ! -f "data/btc.csv" ] || [ ! -f "data/events.csv" ] || [ ! -f "data/gdelt.csv" ]; then
    echo -e "${RED}Error: Required data files missing in data/ directory${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} All checks passed"
echo ""
echo "Starting analysis pipeline..."
echo "This will take 5-10 minutes..."
echo ""

# Run the analysis using Python module syntax
# This ensures all imports work correctly
python -m code.scripts.run_event_study_analysis "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Analysis complete!${NC}"
    echo ""
    echo "Results saved to:"
    echo "  - outputs/analysis_results/"
    echo "  - outputs/publication/"
else
    echo -e "${RED}✗ Analysis failed with exit code $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi
