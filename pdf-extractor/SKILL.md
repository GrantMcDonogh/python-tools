---
name: pdf-extractor
description: Extract text from PDF documents and save to text files. USE WHEN user wants to extract text from a PDF, convert PDF to text, read PDF contents, or get text from PDF documents.
allowed-tools: Bash(uv run *)
argument-hint: <pdf_file> [--output <file>] [--format json]
---

## Purpose

Extracts all text content from PDF documents and saves it to a plain text file. By default, the output file has the same name as the input PDF but with a `.txt` extension.

## Usage

```bash
cd /mnt/c/Users/Admin/Documents/Dev/python-tools/pdf-extractor
uv run main.py <pdf_file> [--output <output_file>] [--format {text,json}] [--verbose]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `pdf_file` | Yes | Path to the PDF file to extract text from |
| `--output`, `-o` | No | Output file path (default: same name with .txt extension) |
| `--format`, `-f` | No | Output format for results: `text` (default) or `json` |
| `--verbose`, `-v` | No | Enable verbose output showing extraction progress |

## Output

**Text format (default):**
```
status: success
input_file: /path/to/document.pdf
output_file: /path/to/document.txt
total_pages: 5
total_characters: 12345
characters_per_page: [2500, 2400, 2600, 2445, 2400]
```

**JSON format:**
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

## Examples

### Example 1: Basic Text Extraction

Extract text from a PDF to a text file with the same name:

```bash
cd /mnt/c/Users/Admin/Documents/Dev/python-tools/pdf-extractor
uv run main.py "/path/to/document.pdf"
```

This creates `document.txt` in the same directory as the PDF.

### Example 2: Specify Output File

Extract text to a specific output file:

```bash
cd /mnt/c/Users/Admin/Documents/Dev/python-tools/pdf-extractor
uv run main.py "/path/to/document.pdf" --output "/path/to/extracted.txt"
```

### Example 3: JSON Output for Programmatic Use

Get extraction results as JSON:

```bash
cd /mnt/c/Users/Admin/Documents/Dev/python-tools/pdf-extractor
uv run main.py "/path/to/document.pdf" --format json
```

### Example 4: Verbose Mode for Debugging

See detailed progress during extraction:

```bash
cd /mnt/c/Users/Admin/Documents/Dev/python-tools/pdf-extractor
uv run main.py "/path/to/document.pdf" --verbose
```

### Example 5: Extract and Process with Other Tools

Extract text and count words:

```bash
cd /mnt/c/Users/Admin/Documents/Dev/python-tools/pdf-extractor
uv run main.py "/path/to/document.pdf" && wc -w "/path/to/document.txt"
```

## How to Use This Skill

1. **Navigate** to the tool directory first
2. **Run** with `uv run main.py <pdf_file>` (UV handles dependencies automatically)
3. **Check the output file** - by default it's the same name as the PDF with `.txt` extension
4. **Use `--format json`** when you need to parse the results programmatically

## Error Handling

The tool returns:
- Exit code 0: Success
- Exit code 1: General error (file not found, extraction failed)
- Exit code 2: Invalid arguments

Errors are printed to stderr and do not appear in stdout.

## Dependencies

- Python 3.8+
- PyMuPDF (pymupdf) - automatically installed by UV
