# URL Validator

A Python tool that validates URLs and checks if they are well-formed. Optionally verifies that the domain resolves via DNS.

## Installation

No manual installation needed - UV handles everything automatically.

## Usage

```bash
cd python-tools/example-tool
uv run main.py <url> [--check-dns] [--format {text,json}] [--verbose]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `url` | Yes | The URL to validate |
| `--check-dns`, `-d` | No | Check if the domain resolves via DNS |
| `--format`, `-f` | No | Output format: `text` (default) or `json` |
| `--verbose`, `-v` | No | Enable verbose debug output |

## Examples

### Basic Validation

```bash
uv run main.py "https://example.com"
```

Output:
```
url: https://example.com
valid: True
scheme: https
domain: example.com
port: None
path: /
query: None
fragment: None
issues: []
```

### Check DNS Resolution

```bash
uv run main.py "https://example.com" --check-dns
```

### JSON Output

```bash
uv run main.py "https://example.com/api/v1?key=value" --format json
```

Output:
```json
{
  "url": "https://example.com/api/v1?key=value",
  "valid": true,
  "scheme": "https",
  "domain": "example.com",
  "port": null,
  "path": "/api/v1",
  "query": "key=value",
  "fragment": null,
  "issues": []
}
```

### Invalid URL

```bash
uv run main.py "not-a-valid-url"
```

Output:
```
url: not-a-valid-url
valid: False
scheme: https
domain: not-a-valid-url
port: None
path: /
query: None
fragment: None
issues: ['Missing scheme (e.g., https://). Did you mean https://not-a-valid-url?']
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | URL is valid |
| 1 | URL is invalid |
| 2 | Error occurred during validation |

## Validation Checks

The tool performs the following validations:

1. **Scheme check**: Verifies URL has a valid scheme (http, https, ftp, etc.)
2. **Domain check**: Validates domain format and length
3. **Character check**: Detects invalid characters or spaces
4. **DNS check** (optional): Verifies the domain resolves

## Integration

This tool follows the Python Tools Platform conventions:
- Standard argparse CLI interface
- Supports text and JSON output formats
- Uses shared utilities from `_shared/`
- Errors go to stderr, results to stdout
