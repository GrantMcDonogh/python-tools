#!/usr/bin/env python3
"""
Tool Name - Brief description of what this tool does.

Usage:
    uv run main.py <input> [--format {text,json}] [--verbose]

Examples:
    uv run main.py "example input"
    uv run main.py "example" --format json
    uv run main.py "example" --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add _shared to path for common utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '_shared'))
try:
    from utils import output_result, setup_logging, log_verbose  # type: ignore[import-not-found]
except ImportError:
    # Fallback if _shared is not available
    def output_result(data: Any, fmt: str = 'text') -> None:
        if fmt == 'json':
            print(json.dumps(data, indent=2))
        else:
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"{key}: {value}")
            else:
                print(data)
    
    def setup_logging(verbose: bool = False) -> None:
        pass
    
    def log_verbose(message: str, verbose: bool = False) -> None:
        if verbose:
            print(f"[DEBUG] {message}", file=sys.stderr)


def process(input_value: str, verbose: bool = False) -> dict:
    """
    Main processing function for the tool.
    
    Args:
        input_value: The input to process
        verbose: Whether to log verbose output
    
    Returns:
        dict: The processing result
    """
    log_verbose(f"Processing input: {input_value}", verbose)
    
    # TODO: Implement your tool logic here
    result = {
        "input": input_value,
        "result": f"Processed: {input_value}",
        "status": "success"
    }
    
    log_verbose(f"Processing complete", verbose)
    return result


def main() -> int:
    """Main entry point for the tool."""
    parser = argparse.ArgumentParser(
        description='Tool description - what this tool does',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "input value"              Process with text output
  %(prog)s "input" --format json      Process with JSON output
  %(prog)s "input" --verbose          Process with verbose logging
        """
    )
    
    # Required arguments
    parser.add_argument(
        'input',
        help='The input to process'
    )
    
    # Optional arguments
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        # Process the input
        result = process(args.input, verbose=args.verbose)
        
        # Output the result
        output_result(result, args.format)
        
        return 0
        
    except ValueError as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        return 2
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
