#!/usr/bin/env python3
"""Command line interface for the Bechdel test analyzer."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from core.analyzer import BechdelAnalyzer

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Analyze movie scripts using the Bechdel test"
    )
    parser.add_argument(
        "script_path",
        type=str,
        help="Path to the movie script file to analyze"
    )
    parser.add_argument(
        "--names-dataset",
        type=str,
        help="Optional path to names-gender dataset CSV file"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Optional path to save analysis results as JSON"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    return parser.parse_args()

def format_result(result_dict: dict) -> str:
    """Format analysis result for console output.
    
    Args:
        result_dict: Dictionary containing analysis results.
        
    Returns:
        Formatted string for display.
    """
    output = []
    
    # Add pass/fail status
    status = "PASSES" if result_dict["passes_test"] else "FAILS"
    output.append(f"\nBechdel Test Result: {status}\n")
    
    # Add female characters
    output.append("Female characters:")
    for char in result_dict["female_characters"]:
        output.append(f"  - {char}")
    
    # Add conversation counts
    output.append(f"\nFemale conversations: {result_dict['female_conversations_count']}")
    output.append(
        f"Non-male conversations: {result_dict['non_male_conversations_count']}\n"
    )
    
    # Add reasons
    output.append("Analysis:")
    for reason in result_dict["reasons"]:
        output.append(f"  - {reason}")
    
    return "\n".join(output)

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Validate script path
    script_path = Path(args.script_path)
    if not script_path.exists():
        print(f"Error: Script file not found: {args.script_path}", file=sys.stderr)
        sys.exit(1)
    
    # Validate names dataset path if provided
    names_dataset: Optional[str] = None
    if args.names_dataset:
        dataset_path = Path(args.names_dataset)
        if not dataset_path.exists():
            print(
                f"Error: Names dataset file not found: {args.names_dataset}",
                file=sys.stderr
            )
            sys.exit(1)
        names_dataset = str(dataset_path)
    
    # Create analyzer and process script
    try:
        analyzer = BechdelAnalyzer(names_dataset)
        result = analyzer.analyze_script_file(str(script_path))
        
        # Convert result to dict for output
        result_dict = result.to_dict()
        
        # Save to file if output path provided
        if args.output:
            analyzer.save_result(result, args.output)
        
        # Display results
        if args.json:
            print(json.dumps(result_dict, indent=2))
        else:
            print(format_result(result_dict))
            
    except Exception as e:
        print(f"Error analyzing script: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
