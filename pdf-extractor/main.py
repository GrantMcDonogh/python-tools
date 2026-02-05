#!/usr/bin/env python3
"""
PDF Text Extractor - Extract text from PDF documents and save to text files.

Usage:
    uv run main.py <pdf_file> [--output <output_file>] [--format {text,json}] [--verbose]

Examples:
    uv run main.py document.pdf
    uv run main.py document.pdf --output extracted.txt
    uv run main.py document.pdf --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add _shared to path for common utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '_shared'))
try:
    from utils import output_result, setup_logging, log_verbose, log_error  # type: ignore[import-not-found]
except ImportError:
    # Fallback implementations if _shared is not available
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

    def log_error(message: str) -> None:
        print(f"Error: {message}", file=sys.stderr)


try:
    import pymupdf  # PyMuPDF
except ImportError:
    pymupdf = None


def extract_text_from_pdf(
    pdf_path: str,
    output_path: Optional[str] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Extract text from a PDF file and save to a text file.

    Args:
        pdf_path: Path to the PDF file
        output_path: Optional output file path (default: same name with .txt extension)
        verbose: Whether to log verbose output

    Returns:
        dict: Extraction results including status, paths, and statistics
    """
    log_verbose(f"Processing PDF: {pdf_path}", verbose)

    pdf_file = Path(pdf_path)

    # Validate input file
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_file.suffix.lower() == '.pdf':
        raise ValueError(f"File does not have .pdf extension: {pdf_path}")

    # Determine output path
    if output_path:
        output_file = Path(output_path)
    else:
        output_file = pdf_file.with_suffix('.txt')

    log_verbose(f"Output will be saved to: {output_file}", verbose)

    # Check if PyMuPDF is available
    if pymupdf is None:
        raise ImportError(
            "PyMuPDF is not installed. Install it with: pip install pymupdf"
        )

    # Extract text from PDF
    log_verbose("Opening PDF document...", verbose)
    doc = pymupdf.open(str(pdf_file))

    total_pages = len(doc)
    log_verbose(f"PDF has {total_pages} pages", verbose)

    extracted_text = []
    chars_per_page = []

    for page_num in range(total_pages):
        log_verbose(f"Extracting text from page {page_num + 1}/{total_pages}", verbose)
        page = doc[page_num]
        page_text = page.get_text()
        extracted_text.append(page_text)
        chars_per_page.append(len(page_text))

    doc.close()

    # Combine all text
    full_text = "\n\n".join(extracted_text)
    total_chars = len(full_text)

    log_verbose(f"Total characters extracted: {total_chars}", verbose)

    # Save to output file
    log_verbose(f"Writing text to: {output_file}", verbose)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(full_text, encoding='utf-8')

    result = {
        "status": "success",
        "input_file": str(pdf_file.absolute()),
        "output_file": str(output_file.absolute()),
        "total_pages": total_pages,
        "total_characters": total_chars,
        "characters_per_page": chars_per_page
    }

    log_verbose("Extraction complete", verbose)
    return result


def main() -> int:
    """Main entry point for the PDF text extractor."""
    parser = argparse.ArgumentParser(
        description='Extract text from PDF documents and save to text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf                    Extract to document.txt
  %(prog)s document.pdf -o output.txt      Extract to specific file
  %(prog)s document.pdf --format json      Output results as JSON
  %(prog)s document.pdf --verbose          Show detailed progress
        """
    )

    parser.add_argument(
        'pdf_file',
        help='Path to the PDF file to extract text from'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: same name with .txt extension)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format for results (default: text)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        result = extract_text_from_pdf(
            args.pdf_file,
            output_path=args.output,
            verbose=args.verbose
        )

        output_result(result, args.format)
        return 0

    except FileNotFoundError as e:
        log_error(str(e))
        return 1

    except ValueError as e:
        log_error(f"Invalid input: {e}")
        return 2

    except ImportError as e:
        log_error(str(e))
        return 1

    except Exception as e:
        log_error(str(e))
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
