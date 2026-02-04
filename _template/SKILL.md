---
name: tool-name
description: Brief description of what this tool does. USE WHEN trigger phrases that describe when AI should use this tool.
# Optional fields (uncomment as needed):
# disable-model-invocation: true    # Set to true for manual-only invocation via /tool-name
# user-invocable: false             # Set to false to hide from user menu (AI-only)
# allowed-tools: Bash(uv run *)     # Tools allowed without permission prompts
# argument-hint: [input] [--flag]   # Hint shown in autocomplete
# context: fork                     # Run in isolated subagent context
# agent: Explore                    # Subagent type when context: fork
---

## Purpose

Describe what this tool does and why it's useful.

## Usage

```bash
uv run main.py <required_argument> [--optional-flag]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | Yes | The primary input for the tool |
| `--format` | No | Output format: `text` (default) or `json` |
| `--verbose` | No | Enable verbose output |

## Output

Describe what the tool outputs. Include examples of both text and JSON formats.

**Text format (default):**
```
Result: processed value
Status: success
```

**JSON format:**
```json
{
  "result": "processed value",
  "status": "success"
}
```

## Examples

### Example 1: Basic Usage

When the user asks to process a simple input:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\tool-name
uv run main.py "input value"
```

Expected output:
```
input: input value
result: Processed: input value
status: success
```

### Example 2: JSON Output for Programmatic Use

When you need structured data to process further:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\tool-name
uv run main.py "input value" --format json
```

Expected output:
```json
{
  "input": "input value",
  "result": "Processed: input value",
  "status": "success"
}
```

### Example 3: Verbose Mode for Debugging

When troubleshooting or needing detailed logs:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\tool-name
uv run main.py "input value" --verbose
```

### Example 4: Piping Output

Chain with other tools:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\tool-name
uv run main.py "input" --format json | jq '.result'
```

## How to Use This Skill

1. **Navigate** to the tool directory first
2. **Run** with `uv run main.py` (handles dependencies automatically)
3. **Use `--format json`** when you need to parse the output programmatically
4. **Check exit code**: 0 = success, non-zero = error

## Error Handling

The tool returns:
- Exit code 0: Success
- Exit code 1: General error
- Exit code 2: Invalid arguments

Errors are printed to stderr and do not appear in stdout.

## Dependencies

Dependencies are managed via `pyproject.toml` or `requirements.txt`. UV will automatically install them on first run.

This tool requires:
- Python 3.8+
- (list other dependencies)
