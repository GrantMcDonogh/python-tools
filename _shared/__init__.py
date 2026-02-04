"""
Shared utilities for Python tools.

This module provides common functionality used across multiple tools:
- output_result: Format and print results in text or JSON format
- setup_logging: Configure logging for verbose output
- log_verbose: Log messages when verbose mode is enabled
"""

from .utils import output_result, setup_logging, log_verbose

__all__ = ['output_result', 'setup_logging', 'log_verbose']
