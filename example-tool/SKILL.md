---
name: url-validator
description: Validates URLs and checks if they are well-formed. USE WHEN validating URLs, checking link formats, verifying web addresses, or parsing URL components.
allowed-tools: Bash(uv run *)
argument-hint: [url] [--check-dns] [--format json]
---

## Purpose

Validates URLs to ensure they are properly formatted and optionally checks if the domain resolves. Useful for:
- Validating user input
- Checking configuration files
- Verifying links before processing

## Usage

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool
uv run main.py <url> [--check-dns] [--format {text,json}] [--verbose]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `url` | Yes | The URL to validate |
| `--check-dns` | No | Also verify the domain resolves via DNS |
| `--format` | No | Output format: `text` (default) or `json` |
| `--verbose` | No | Enable verbose output |

## Output

Returns validation results including:
- `valid`: Whether the URL is well-formed
- `scheme`: Protocol (http, https, etc.)
- `domain`: The domain/host
- `path`: URL path
- `issues`: List of any problems found

## Examples

### Example 1: Validate a Simple URL

When the user asks to check if a URL is valid:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool
uv run main.py "https://example.com"
```

Expected output:
```
url: https://example.com
valid: True
scheme: https
domain: example.com
port: None
path: /
query: None
fragment: None
issues:
```

### Example 2: Get JSON Output for Processing

When you need to check validity programmatically:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool
uv run main.py "https://example.com/api/v1?key=value" --format json
```

Expected output:
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

### Example 3: Check if Domain Actually Exists

When you need to verify the domain resolves (requires network):

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool
uv run main.py "https://example.com" --check-dns --format json
```

Expected output includes `dns_resolves: true` or `false`.

### Example 4: Validate a Potentially Invalid URL

When checking user-provided input that might be malformed:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool
uv run main.py "not-a-url"
```

Expected output:
```
url: not-a-url
valid: False
scheme: https
domain: not-a-url
port: None
path: /
query: None
fragment: None
issues:
  - Missing scheme (e.g., https://). Did you mean https://not-a-url?
```

### Example 5: Batch Validation in a Script

Validate multiple URLs and collect results:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool
for url in "https://google.com" "https://github.com" "invalid"; do
  echo "=== $url ==="
  uv run main.py "$url" --format json
done
```

## How to Use This Skill

1. **Navigate** to `d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool`
2. **Run** with `uv run main.py "<url>"`
3. **Use `--format json`** when you need to parse the result
4. **Use `--check-dns`** when you need to verify the domain exists
5. **Check exit code**: 0 = valid URL, 1 = invalid URL, 2 = error

## Error Cases

- Missing scheme: `example.com` → suggests adding `https://`
- Invalid characters: Reports specific invalid characters
- Malformed URL: Reports parsing errors
- DNS failure: Reports when domain doesn't resolve (with `--check-dns`)
