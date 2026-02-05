# PDF Text Extractor

Extract text from PDF documents and save to plain text files.

## Installation

No manual installation needed - UV handles dependencies automatically.

## Usage

```bash
cd python-tools/pdf-extractor
uv run main.py <pdf_file> [--output <file>] [--format {text,json}] [--verbose]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `pdf_file` | Yes | Path to the PDF file to extract text from |
| `--output`, `-o` | No | Output file path (default: same name with .txt extension) |
| `--format`, `-f` | No | Output format for results: `text` (default) or `json` |
| `--verbose`, `-v` | No | Enable verbose output |

## Examples

```bash
# Basic usage - extracts to document.txt
uv run main.py document.pdf

# Specify output file
uv run main.py document.pdf --output extracted.txt

# JSON output
uv run main.py document.pdf --format json

# Verbose mode
uv run main.py document.pdf --verbose
```

## Output

### Text Format (default)

```
status: success
input_file: /path/to/document.pdf
output_file: /path/to/document.txt
total_pages: 5
total_characters: 12345
characters_per_page: [2500, 2400, 2600, 2445, 2400]
```

### JSON Format

```json
{
  "status": "success",
  "input_file": "/path/to/document.pdf",
  "output_file": "/path/to/document.txt",
  "total_pages": 5,
  "total_characters": 12345,
  "characters_per_page": [2500, 2400, 2600, 2445, 2400]
}
```

## Development

### Running Tests

```bash
uv run python tests/test_main.py
# Or with pytest:
uv run pytest tests/
```

### Project Structure

```
pdf-extractor/
├── SKILL.md          # AI skill definition
├── main.py           # Main entry point
├── README.md         # This file
├── pyproject.toml    # Dependencies
└── tests/            # Test files
    └── test_main.py
```

## Dependencies

- PyMuPDF (pymupdf) - Fast PDF text extraction
