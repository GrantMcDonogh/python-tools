# Python Tools Platform

This directory contains standalone Python tools that AI agents can discover and use. Each tool follows Claude's Skills format and uses UV for dependency management and execution.

## Directory Structure

```
python-tools/
├── _template/          # Copy this to create new tools
├── _shared/            # Shared utilities (import with sys.path)
├── example-tool/       # Working example (URL validator)
└── <tool-name>/        # Each tool in its own directory
```

## Using Existing Tools

### Quick Reference

```bash
# 1. Navigate to the tool directory
cd d:\i60NextCloud\Dev\MAIA3\python-tools\<tool-name>

# 2. Run with UV (handles dependencies automatically)
uv run main.py <arguments>

# 3. For structured output, use --format json
uv run main.py <arguments> --format json
```

### Why UV?

- **Automatic dependency management**: UV installs required packages on first run
- **Fast**: Much faster than pip
- **Isolated**: Each tool can have its own dependencies without conflicts

### Example: Using the URL Validator

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\example-tool
uv run main.py "https://example.com" --format json
```

## Creating New Tools

### Step 1: Copy the Template

```powershell
Copy-Item -Recurse "d:\i60NextCloud\Dev\MAIA3\python-tools\_template" "d:\i60NextCloud\Dev\MAIA3\python-tools\<tool-name>"
```

Use `kebab-case` for tool directory names (e.g., `url-validator`, `json-formatter`).

### Step 2: Edit SKILL.md

Update the frontmatter:

```yaml
---
name: tool-name
description: What it does. USE WHEN trigger phrases describing when to use this tool.
allowed-tools: Bash(uv run *)
---
```

**Critical**: The `description` field determines when AI agents will use the tool. Include:
- A brief description of what the tool does
- "USE WHEN" followed by trigger phrases/scenarios

**Important**: Include detailed examples showing:
- The exact command to run
- Expected output for common scenarios
- How to handle errors

### Step 3: Implement main.py

Follow these conventions:

1. **Entry point**: Always `main.py`
2. **CLI**: Use `argparse` for argument parsing
3. **Output formats**: Support `--format json` and `--format text` (default)
4. **Exit codes**: 0 = success, 1 = error, 2 = invalid arguments
5. **Errors**: Print to stderr, not stdout
6. **Shared utilities**: Import from `_shared/utils.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '_shared'))
from utils import output_result, setup_logging, log_verbose
```

### Step 4: Add Dependencies

Create `pyproject.toml` for UV:

```toml
[project]
name = "tool-name"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
]
```

Or use `requirements.txt`:

```
requests>=2.28.0
```

UV will read either format.

## Tool Conventions

| Convention | Requirement |
|------------|-------------|
| Entry point | `main.py` |
| Skill definition | `SKILL.md` with YAML frontmatter |
| Runner | `uv run main.py` |
| Output flag | `--format {text,json}` |
| Verbose flag | `--verbose` or `-v` |
| Error output | stderr only |
| Exit code 0 | Success |
| Exit code 1 | Error |
| Exit code 2 | Invalid arguments |

## SKILL.md Template Structure

Every SKILL.md should include:

1. **Frontmatter** with name, description, allowed-tools
2. **Purpose** section explaining what the tool does
3. **Usage** section with the exact command syntax
4. **Arguments** table documenting all options
5. **Examples** section with multiple scenarios showing:
   - The exact command to run (with full path or cd first)
   - Expected output
   - Common use cases
6. **How to Use This Skill** summary for quick reference

## Shared Utilities

The `_shared/utils.py` module provides:

- `output_result(data, fmt)` - Print data as text or JSON
- `setup_logging(verbose)` - Configure verbose logging
- `log_verbose(message, verbose)` - Log debug messages to stderr
- `log_error(message)` - Log errors to stderr
- `format_size(bytes)` - Human-readable file sizes
- `format_duration(seconds)` - Human-readable durations
- `safe_get(dict, *keys, default)` - Safely access nested dict values

## Running Tools

Always use this pattern:

```bash
# Navigate first
cd d:\i60NextCloud\Dev\MAIA3\python-tools\<tool-name>

# Run with UV
uv run main.py <arguments> --format json
```

## Testing Tools

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\<tool-name>
uv run python tests/test_main.py
```

Or with pytest:

```bash
cd d:\i60NextCloud\Dev\MAIA3\python-tools\<tool-name>
uv run pytest tests/
```
