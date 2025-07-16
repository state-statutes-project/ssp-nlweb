#!/bin/bash

# Script to load all state statute files into NLWeb database
# This script reads the manifest file and loads each state's data as a separate site

# Configuration
YEAR="2023"
DATA_DIR="data/json/by_state"
MANIFEST_FILE="${DATA_DIR}/manifest_${YEAR}.txt"
PYTHON_DIR="code/python"
LOG_DIR="logs/state_loading"
FAILED_STATES_FILE="${LOG_DIR}/failed_states.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Clear failed states file
> "$FAILED_STATES_FILE"

# Check if manifest file exists
if [ ! -f "$MANIFEST_FILE" ]; then
    echo -e "${RED}Error: Manifest file not found at $MANIFEST_FILE${NC}"
    echo "Please run 'python copy_statutes_by_state.py $YEAR' first"
    exit 1
fi

# Count total states
TOTAL_STATES=$(wc -l < "$MANIFEST_FILE")
CURRENT_STATE=0
SUCCESSFUL_STATES=0
FAILED_STATES=0

echo "========================================"
echo "NLWeb State Statutes Loader"
echo "========================================"
echo "Year: $YEAR"
echo "Total states to load: $TOTAL_STATES"
echo "Data directory: $DATA_DIR"
echo "========================================"
echo ""

# Function to load a single state
load_state() {
    local state=$1
    local state_file="${DATA_DIR}/${state}_${YEAR}.jsonl"
    local log_file="${LOG_DIR}/${state}_${YEAR}.log"
    
    # Check if file exists (from script directory)
    if [ ! -f "$state_file" ]; then
        echo -e "${RED}File not found: $state_file${NC}"
        return 1
    fi
    
    # Get file size
    local file_size=$(ls -lh "$state_file" | awk '{print $5}')
    
    echo -n "Loading $state ($file_size)... "
    
    # Save current directory
    local ORIGINAL_DIR=$(pwd)
    
    # Change to python directory and run the loader
    cd "$PYTHON_DIR" || exit 1
    
    # Run the data loader with output redirected to log file
    if python -m data_loading.db_load "../../${state_file}" "$state" > "../../${log_file}" 2>&1; then
        echo -e "${GREEN}SUCCESS${NC}"
        cd "$ORIGINAL_DIR"
        return 0
    else
        echo -e "${RED}FAILED${NC} (see $log_file for details)"
        echo "$state" >> "../../${FAILED_STATES_FILE}"
        cd "$ORIGINAL_DIR"
        return 1
    fi
}

# Ask for confirmation
echo "This will load statute data for all states."
echo "Each state will be loaded as a separate site in the database."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Starting data loading..."
echo "========================================"

# Read manifest and process each state
while IFS= read -r state; do
    # Skip empty lines
    [ -z "$state" ] && continue
    
    CURRENT_STATE=$((CURRENT_STATE + 1))
    echo ""
    echo "[$CURRENT_STATE/$TOTAL_STATES] Processing $state..."
    
    if load_state "$state"; then
        SUCCESSFUL_STATES=$((SUCCESSFUL_STATES + 1))
    else
        FAILED_STATES=$((FAILED_STATES + 1))
    fi
    
    # Optional: Add a small delay between loads to avoid overwhelming the system
    # sleep 1
done < "$MANIFEST_FILE"

# Print summary
echo ""
echo "========================================"
echo "Loading Complete!"
echo "========================================"
echo -e "Successful: ${GREEN}$SUCCESSFUL_STATES${NC}"
echo -e "Failed: ${RED}$FAILED_STATES${NC}"
echo "Total: $TOTAL_STATES"
echo ""

if [ $FAILED_STATES -gt 0 ]; then
    echo -e "${YELLOW}Failed states listed in: $FAILED_STATES_FILE${NC}"
    echo "You can retry failed states by running:"
    echo "  while read state; do"
    echo "    (cd $PYTHON_DIR && python -m data_loading.db_load \"../../${DATA_DIR}/\${state}_${YEAR}.jsonl\" \"\$state\")"
    echo "  done < $FAILED_STATES_FILE"
fi

# Update config suggestion
if [ $SUCCESSFUL_STATES -gt 0 ]; then
    echo ""
    echo "========================================"
    echo "Next Steps:"
    echo "========================================"
    echo "1. Update config/config_nlweb.yaml to include all states:"
    echo "   sites: \"$(cat "$MANIFEST_FILE" | tr '\n' ',' | sed 's/,$//')\""
    echo ""
    echo "2. Or use 'all' to allow queries across all sites:"
    echo "   sites: \"all\""
    echo ""
    echo "3. Restart the NLWeb server to apply changes"
fi