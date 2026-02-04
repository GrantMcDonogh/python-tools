"""
Common utility functions for Python tools.

This module provides shared functionality for:
- Output formatting (text and JSON)
- Logging and verbose output
- Common data transformations
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


# Global verbose flag
_verbose = False


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging/verbose output settings.
    
    Args:
        verbose: Whether to enable verbose output
    """
    global _verbose
    _verbose = verbose


def log_verbose(message: str, verbose: Optional[bool] = None) -> None:
    """
    Log a message to stderr if verbose mode is enabled.
    
    Args:
        message: The message to log
        verbose: Override the global verbose setting (optional)
    """
    should_log = verbose if verbose is not None else _verbose
    if should_log:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}", file=sys.stderr)


def log_error(message: str) -> None:
    """
    Log an error message to stderr.
    
    Args:
        message: The error message to log
    """
    print(f"Error: {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    """
    Log a warning message to stderr.
    
    Args:
        message: The warning message to log
    """
    print(f"Warning: {message}", file=sys.stderr)


def output_result(
    data: Any,
    fmt: str = 'text',
    indent: int = 2,
    sort_keys: bool = False
) -> None:
    """
    Output data in the specified format.
    
    Args:
        data: The data to output (dict, list, or scalar)
        fmt: Output format ('text' or 'json')
        indent: JSON indentation level (default: 2)
        sort_keys: Whether to sort JSON keys (default: False)
    """
    if fmt == 'json':
        print(json.dumps(data, indent=indent, sort_keys=sort_keys, default=str))
    else:
        _output_text(data)


def _output_text(data: Any, prefix: str = '') -> None:
    """
    Output data in human-readable text format.
    
    Args:
        data: The data to output
        prefix: Prefix for nested values
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                _output_text(value, prefix + '  ')
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                print(f"{prefix}[{i}]:")
                _output_text(item, prefix + '  ')
            else:
                print(f"{prefix}- {item}")
    else:
        print(f"{prefix}{data}")


def format_size(size_bytes: int) -> str:
    """
    Format a byte size as human-readable string.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds as human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Human-readable duration string (e.g., "2m 30s")
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def safe_get(data: Dict, *keys: str, default: Any = None) -> Any:
    """
    Safely get a nested value from a dictionary.
    
    Args:
        data: The dictionary to search
        *keys: The sequence of keys to traverse
        default: Default value if key not found
    
    Returns:
        The value at the nested key path, or default if not found
    
    Example:
        >>> data = {"a": {"b": {"c": 1}}}
        >>> safe_get(data, "a", "b", "c")
        1
        >>> safe_get(data, "a", "x", default="not found")
        'not found'
    """
    result = data
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    return result


def truncate_string(s: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        s: The string to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to append if truncated
    
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def read_stdin_or_file(file_path: Optional[str] = None) -> str:
    """
    Read input from stdin or a file.
    
    Args:
        file_path: Path to file to read, or None to read from stdin
    
    Returns:
        The content read
    """
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        if not sys.stdin.isatty():
            return sys.stdin.read()
        return ''
