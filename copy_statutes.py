"""
Improved script to copy statutes from state-kg/data/ssp-processed/serialized/state_laws
to the ssp-nlweb data/json folder.

This script:
- Copies all statutes for a given year from all states into a single JSONL file
- Prepends "https://law.justia.com" to all URLs
- Adds "@type": "Statute" for Schema.org compatibility
- Provides progress updates and statistics


Run from ssp-nlweb directory:
python copy_statutes.py 2023

After running, run the following command:
cd code/python
python -m data_loading.db_load ../../data/json/statutes_2023.jsonl ssp
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def process_statute(statute: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single statute to prepare it for NLWeb.
    
    Args:
        statute: The statute dictionary to process
        
    Returns:
        The processed statute with updated URL and type
    """
    # Add Schema.org type
    statute["@type"] = "Statute"
    
    # Prepend base URL to the URL field if it exists and is relative
    if "url" in statute and statute["url"]:
        if not statute["url"].startswith("http"):
            statute["url"] = "https://law.justia.com" + statute["url"]
    
    return statute

def copy_statutes_for_year(year: str, limit_states: int = None):
    """Copy all statutes for a given year from all states into a single JSONL file.
    
    Args:
        year: The year to process (e.g., "2023")
        limit_states: Optional limit on number of states to process (for testing)
    """
    # Define paths
    base_dir = Path("/Users/neelguha/Desktop/Research/legal_datasets/state_statutes_db")
    input_dir = base_dir / "state-kg/data/ssp-processed/serialized/state_laws"
    output_dir = base_dir / "ssp-nlweb/data/json"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all state directories
    state_dirs = [d for d in input_dir.iterdir() if d.is_dir() and d.name not in ['plots']]
    state_dirs.sort()
    
    print(f"Found {len(state_dirs)} states/territories to process for year {year}")
    
    if limit_states:
        print(f"Processing limited to first {limit_states} states")
        state_dirs = state_dirs[:limit_states]
    
    # Process each state and collect all statutes
    all_statutes = []
    states_processed = 0
    states_with_data = []
    states_without_data = []
    
    for i, state_dir in enumerate(state_dirs, 1):
        state_name = state_dir.name
        jsonl_file = state_dir / f"{year}.jsonl"
        
        if not jsonl_file.exists():
            states_without_data.append(state_name)
            print(f"[{i:2d}/{len(state_dirs)}] No {year} data for {state_name}")
            continue
            
        print(f"[{i:2d}/{len(state_dirs)}] Processing {state_name}...", end=" ")
        
        state_statutes = []
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        statute = json.loads(line.strip())
                        processed_statute = process_statute(statute)
                        state_statutes.append(processed_statute)
                    except json.JSONDecodeError as e:
                        print(f"\n  Warning: Invalid JSON on line {line_num} in {state_name}: {e}")
                        continue
        except Exception as e:
            print(f"\n  Error reading file for {state_name}: {e}")
            continue
        
        if state_statutes:
            all_statutes.extend(state_statutes)
            states_processed += 1
            states_with_data.append(state_name)
            print(f"Added {len(state_statutes):,} statutes")
        else:
            print("No valid statutes found")
        
        #break # Uncomment this to only process the first state
    
    # Write all statutes to a single JSONL file
    if all_statutes:
        output_file = output_dir / f"statutes_{year}.jsonl"
        print(f"\nWriting {len(all_statutes):,} statutes to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for statute in all_statutes:
                f.write(json.dumps(statute, ensure_ascii=False) + '\n')
        
        file_size = output_file.stat().st_size / (1024 * 1024)
        
        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"{'='*60}")
        print(f"Output file: {output_file.name}")
        print(f"File size: {file_size:.2f} MB")
        print(f"Total statutes: {len(all_statutes):,}")
        print(f"States processed: {states_processed} out of {len(state_dirs)}")
        print(f"\nStates with data ({len(states_with_data)}):")
        for state in sorted(states_with_data):
            print(f"  - {state}")
        if states_without_data:
            print(f"\nStates without {year} data ({len(states_without_data)}):")
            for state in sorted(states_without_data):
                print(f"  - {state}")
    else:
        print(f"\nNo statutes found for year {year}")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python copy_statutes_improved.py <year> [limit_states]")
        print("Examples:")
        print("  python copy_statutes_improved.py 2023        # Process all states")
        print("  python copy_statutes_improved.py 2023 5      # Process first 5 states (for testing)")
        sys.exit(1)
    
    year = sys.argv[1]
    limit_states = None
    
    if len(sys.argv) > 2:
        try:
            limit_states = int(sys.argv[2])
        except ValueError:
            print(f"Error: limit_states must be a number, got '{sys.argv[2]}'")
            sys.exit(1)
    
    copy_statutes_for_year(year, limit_states)

if __name__ == "__main__":
    main()