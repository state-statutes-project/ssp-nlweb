"""
Script to copy statutes from state-kg/data/ssp-processed/serialized/state_laws
to the ssp-nlweb data/json folder, creating separate files for each state.

This script:
- Creates separate JSONL files for each state
- Prepends "https://law.justia.com" to all URLs
- Adds "@type": "Statute" for Schema.org compatibility
- Provides progress updates and statistics

Run from ssp-nlweb directory:
python copy_statutes_by_state.py 2023

After running, use the load_all_states.sh script to load each state into the database.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

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

def copy_statutes_by_state_for_year(year: str):
    """Copy statutes for a given year, creating separate files for each state.
    
    Args:
        year: The year to process (e.g., "2023")
    """
    # Define paths
    base_dir = Path("/Users/neelguha/Desktop/Research/legal_datasets/state_statutes_db")
    input_dir = base_dir / "state-kg/data/ssp-processed/serialized/state_laws"
    output_dir = base_dir / "ssp-nlweb/data/json/by_state"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all state directories
    state_dirs = [d for d in input_dir.iterdir() if d.is_dir() and d.name not in ['plots']]
    state_dirs.sort()
    
    print(f"Found {len(state_dirs)} states/territories to process for year {year}")
    print(f"Output directory: {output_dir}")
    print("="*60)
    
    # Process statistics
    total_statutes = 0
    states_processed = 0
    states_with_data = []
    states_without_data = []
    file_sizes = {}
    
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
            # Write state-specific file
            output_file = output_dir / f"{state_name}_{year}.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                for statute in state_statutes:
                    f.write(json.dumps(statute, ensure_ascii=False) + '\n')
            
            file_size = output_file.stat().st_size / (1024 * 1024)
            file_sizes[state_name] = file_size
            
            total_statutes += len(state_statutes)
            states_processed += 1
            states_with_data.append(state_name)
            print(f"Added {len(state_statutes):,} statutes ({file_size:.1f} MB)")
        else:
            print("No valid statutes found")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"{'='*60}")
    print(f"Output directory: {output_dir}")
    print(f"Total statutes: {total_statutes:,}")
    print(f"States processed: {states_processed} out of {len(state_dirs)}")
    print(f"\nFile sizes by state:")
    for state, size in sorted(file_sizes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {state:20s}: {size:6.1f} MB")
    print(f"\nTotal size: {sum(file_sizes.values()):.1f} MB")
    
    if states_without_data:
        print(f"\nStates without {year} data ({len(states_without_data)}):")
        for state in sorted(states_without_data):
            print(f"  - {state}")
    
    # Create a manifest file for the bash script
    manifest_file = output_dir / f"manifest_{year}.txt"
    with open(manifest_file, 'w') as f:
        for state in sorted(states_with_data):
            f.write(f"{state}\n")
    print(f"\nCreated manifest file: {manifest_file}")

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python copy_statutes_by_state.py <year>")
        print("Example: python copy_statutes_by_state.py 2023")
        sys.exit(1)
    
    year = sys.argv[1]
    copy_statutes_by_state_for_year(year)

if __name__ == "__main__":
    main()