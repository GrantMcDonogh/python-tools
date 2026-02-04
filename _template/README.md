# Tool Name

Brief description of what this tool does.

## Installation

No manual installation needed - UV handles dependencies automatically.

## Usage

```bash
cd python-tools/tool-name
uv run main.py <input> [--format {text,json}] [--verbose]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | Yes | The primary input for the tool |
| `--format` | No | Output format: `text` (default) or `json` |
| `--verbose` | No | Enable verbose output |

## Examples

```bash
# Basic usage
uv run main.py "example input"

# JSON output
uv run main.py "example" --format json

# Verbose mode
uv run main.py "example" --verbose
```

## Output

### Text Format (default)

```
input: example
result: Processed: example
status: success
```

### JSON Format

```json
{
  "input": "example",
  "result": "Processed: example",
  "status": "success"
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
tool-name/
├── SKILL.md          # AI skill definition
├── main.py           # Main entry point
├── README.md         # This file
├── requirements.txt  # Dependencies
├── scripts/          # Additional helper scripts
└── tests/            # Test files
    └── test_main.py
```
