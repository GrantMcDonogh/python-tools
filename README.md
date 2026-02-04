# Python Tools Platform

A modular platform for creating Python tools that AI agents can discover and use. Each tool follows Claude's Skills format for seamless integration.

## Quick Start

1. **Copy the template** to create a new tool:
   ```powershell
   Copy-Item -Recurse python-tools\_template python-tools\my-new-tool
   ```

2. **Edit the files**:
   - `SKILL.md` - Define when and how the tool should be used
   - `main.py` - Implement the tool logic

3. **Test your tool** (using UV runner):
   ```bash
   cd python-tools/my-new-tool
   uv run main.py --help
   ```

> **Note**: This platform uses [UV](https://github.com/astral-sh/uv) as the Python runner. UV automatically manages dependencies and provides fast, isolated execution.

## Folder Structure

```
python-tools/
├── README.md                    # This file
├── requirements.txt             # Shared dependencies
├── _template/                   # Template for new tools (copy this!)
│   ├── SKILL.md                 # Template skill definition
│   ├── main.py                  # Template entry point
│   └── README.md                # Template documentation
├── _shared/                     # Shared utilities
│   ├── __init__.py
│   └── utils.py                 # Common helper functions
└── <tool-name>/                 # Each tool in its own directory
    ├── SKILL.md                 # Tool definition (required)
    ├── main.py                  # Primary entry point (required)
    ├── requirements.txt         # Tool-specific dependencies
    ├── scripts/                 # Additional scripts (optional)
    └── tests/                   # Tool tests (optional)
```

## Creating a New Tool

### Step 1: Create the Directory

```powershell
Copy-Item -Recurse python-tools\_template python-tools\url-validator
```

### Step 2: Define the Skill (SKILL.md)

Edit `SKILL.md` with YAML frontmatter:

```yaml
---
name: url-validator
description: Validates URLs and checks if they are accessible. USE WHEN validating URLs, checking links, or verifying web addresses.
allowed-tools: Bash(python *)
---
```

The `description` field is critical - it tells AI agents when to use your tool. Include:
- What the tool does
- "USE WHEN" trigger phrases that describe scenarios

### Step 3: Implement the Tool (main.py)

Follow these conventions:

1. **Entry point**: Always `main.py`
2. **CLI interface**: Use `argparse` for argument parsing
3. **Output formats**: Support both text and JSON (`--format json`)
4. **Exit codes**: 0 for success, non-zero for errors
5. **Error handling**: Print errors to stderr, not stdout
6. **Runner**: Use `uv run main.py` to execute

```python
#!/usr/bin/env python3
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description='Tool description')
    parser.add_argument('input', help='Required input')
    parser.add_argument('--format', choices=['json', 'text'], default='text')
    args = parser.parse_args()
    
    try:
        result = process(args.input)
        output(result, args.format)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

Run with UV:
```bash
cd python-tools/my-tool
uv run main.py "input value" --format json
```

### Step 4: Add Dependencies (optional)

If your tool needs additional packages, create `requirements.txt`:

```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

### Step 5: Add Tests (optional)

Create tests in `tests/test_main.py`:

```python
import pytest
from main import process

def test_basic_input():
    result = process("test input")
    assert result is not None
```

Run tests with UV:
```bash
cd python-tools/my-tool
uv run python tests/test_main.py
# Or with pytest:
uv run pytest tests/
```

## SKILL.md Reference

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name (defaults to directory name). Lowercase, hyphens only. |
| `description` | Yes | What it does + "USE WHEN" triggers. AI uses this to decide when to invoke. |
| `disable-model-invocation` | No | `true` = manual only via `/name`. Default: `false` |
| `user-invocable` | No | `false` = AI only, hidden from menu. Default: `true` |
| `allowed-tools` | No | Tools allowed without permission (e.g., `Bash(python *)`) |
| `argument-hint` | No | Hint for autocomplete (e.g., `[url] [--timeout]`) |
| `context` | No | `fork` = run in isolated subagent |

### Content Structure

After the frontmatter, include:

```markdown
## Purpose
What the tool does and why it's useful.

## Usage
\```bash
uv run main.py <required> [--optional]
\```

## Arguments
- `input` (required): Description
- `--flag`: What this flag does

## Output
Description of what the tool outputs.

## Examples
\```bash
# Example 1: Basic usage
uv run main.py "input value"

# Example 2: JSON output
uv run main.py "input" --format json
\```
```

## Best Practices

### Naming Conventions

- **Directories**: `kebab-case` (e.g., `url-validator`, `json-formatter`)
- **Python files**: `snake_case` (e.g., `main.py`, `helper_utils.py`)
- **Functions**: `snake_case` (e.g., `validate_url`, `format_output`)

### Output Guidelines

1. **Text format** (default): Human-readable, suitable for display
2. **JSON format** (`--format json`): Machine-readable, structured data
3. **Errors**: Always to stderr, never mixed with output
4. **Progress**: Use stderr for progress indicators

### Error Handling

```python
import sys

# Good: Errors to stderr with exit code
print(f"Error: {message}", file=sys.stderr)
sys.exit(1)

# Bad: Errors mixed with output
print(f"Error: {message}")  # Don't do this
```

### Using Shared Utilities

Import from `_shared`:

```python
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / '_shared'))
from utils import output_result, setup_logging
```

## Integration with AI Agents

### Claude Code Integration

Option A - Symlink to personal skills (recommended):
```powershell
cmd /c mklink /D "%USERPROFILE%\.claude\skills\python-tools" "d:\i60NextCloud\Dev\MAIA3\python-tools"
```

Option B - Reference directly in conversation by path.

### How AI Agents Discover and Use Tools

1. AI reads `SKILL.md` description to understand what the tool does
2. When a user request matches the "USE WHEN" triggers, AI invokes the tool
3. AI navigates to the tool directory and runs `uv run main.py`
4. AI processes the output (use `--format json` for structured data)

### Example AI Usage Pattern

```bash
# AI navigates to tool directory
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool

# AI runs the tool with UV
uv run main.py "https://example.com" --format json

# AI parses JSON output and continues task
```

## Example Tool

See `example-tool/` for a complete working example that demonstrates:
- Proper SKILL.md structure with detailed examples
- Argument parsing with argparse
- JSON and text output formats
- Error handling
- Using shared utilities

Test it:
```bash
cd python-tools/example-tool
uv run main.py "https://github.com" --format json
```

## UV Runner

This platform uses [UV](https://github.com/astral-sh/uv) for running Python tools.

### Why UV?

- **Fast**: 10-100x faster than pip for dependency installation
- **Automatic**: Handles dependencies without manual `pip install`
- **Isolated**: Each tool runs with its own dependencies
- **Simple**: Just `uv run main.py` - no virtualenv activation needed

### Installing UV

```powershell
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Or with pip
pip install uv
```

### UV Commands

```bash
# Run a Python script (auto-installs deps)
uv run main.py

# Run with specific Python version
uv run --python 3.11 main.py

# Run pytest
uv run pytest tests/
```
