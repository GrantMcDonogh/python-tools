#!/usr/bin/env python3
"""
URL Validator - Validates URLs and checks if they are well-formed.

Usage:
    python main.py <url> [--check-dns] [--format {text,json}] [--verbose]

Examples:
    python main.py "https://example.com"
    python main.py "https://example.com" --check-dns
    python main.py "https://example.com/api" --format json
"""

import argparse
import json
import re
import socket
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, ParseResult

# Add _shared to path for common utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '_shared'))
try:
    from utils import output_result, setup_logging, log_verbose, log_error
except ImportError:
    # Fallback implementations if _shared is not available
    def output_result(data: Any, fmt: str = 'text') -> None:
        if fmt == 'json':
            print(json.dumps(data, indent=2))
        else:
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"{key}: {value}")
            else:
                print(data)
    
    def setup_logging(verbose: bool = False) -> None:
        pass
    
    def log_verbose(message: str, verbose: bool = False) -> None:
        if verbose:
            print(f"[DEBUG] {message}", file=sys.stderr)
    
    def log_error(message: str) -> None:
        print(f"Error: {message}", file=sys.stderr)


def validate_url(url: str, check_dns: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Validate a URL and return detailed results.
    
    Args:
        url: The URL to validate
        check_dns: Whether to check if the domain resolves
        verbose: Whether to log verbose output
    
    Returns:
        dict: Validation results
    """
    log_verbose(f"Validating URL: {url}", verbose)
    
    issues: List[str] = []
    result: Dict[str, Any] = {
        "url": url,
        "valid": False,
        "scheme": None,
        "domain": None,
        "port": None,
        "path": None,
        "query": None,
        "fragment": None,
        "issues": issues
    }
    
    # Check if URL is empty
    if not url or not url.strip():
        issues.append("URL is empty")
        return result
    
    url = url.strip()
    
    # Check for scheme
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
        issues.append("Missing scheme (e.g., https://). Did you mean https://" + url + "?")
        # Try to parse anyway with added scheme for analysis
        test_url = "https://" + url
    else:
        test_url = url
    
    # Parse the URL
    try:
        parsed: ParseResult = urlparse(test_url)
        log_verbose(f"Parsed URL: {parsed}", verbose)
    except Exception as e:
        issues.append(f"Failed to parse URL: {e}")
        return result
    
    # Extract components
    result["scheme"] = parsed.scheme if parsed.scheme else None
    result["domain"] = parsed.netloc.split(':')[0] if parsed.netloc else None
    result["path"] = parsed.path if parsed.path else "/"
    result["query"] = parsed.query if parsed.query else None
    result["fragment"] = parsed.fragment if parsed.fragment else None
    
    # Extract port if present
    if ':' in parsed.netloc:
        try:
            port_str = parsed.netloc.split(':')[1]
            result["port"] = int(port_str)
        except (ValueError, IndexError):
            pass
    
    # Validate scheme
    valid_schemes = ['http', 'https', 'ftp', 'ftps', 'mailto', 'file', 'ssh', 'git']
    if parsed.scheme and parsed.scheme.lower() not in valid_schemes:
        issues.append(f"Unusual scheme '{parsed.scheme}' (common schemes: http, https)")
    
    # Validate domain
    if not parsed.netloc:
        issues.append("Missing domain/host")
    else:
        domain = parsed.netloc.split(':')[0]
        
        # Check for invalid characters in domain
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$', domain):
            # Allow localhost and IP addresses
            if domain != 'localhost' and not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
                issues.append(f"Invalid characters in domain: {domain}")
        
        # Check domain length
        if len(domain) > 253:
            issues.append(f"Domain too long ({len(domain)} chars, max 253)")
        
        # Check for double dots
        if '..' in domain:
            issues.append("Domain contains consecutive dots")
    
    # Check for spaces or invalid characters in URL
    if ' ' in url:
        issues.append("URL contains spaces (should be encoded as %20)")
    
    # DNS check if requested
    if check_dns and result["domain"]:
        log_verbose(f"Checking DNS for: {result['domain']}", verbose)
        try:
            socket.gethostbyname(result["domain"])
            result["dns_resolves"] = True
            log_verbose(f"DNS resolved successfully", verbose)
        except socket.gaierror as e:
            result["dns_resolves"] = False
            issues.append(f"Domain does not resolve: {e}")
            log_verbose(f"DNS resolution failed: {e}", verbose)
    
    # Determine overall validity
    # URL is valid if it has a scheme (in original) and no critical issues
    critical_issues = [i for i in issues if "Missing scheme" not in i or "https://" not in url]
    result["valid"] = len([i for i in issues if "Missing" in i or "Invalid" in i or "does not resolve" in i]) == 0
    
    # Re-check: if original URL had proper scheme, it's valid unless other issues
    if re.match(r'^https?://', url) and not any("Invalid" in i or "does not resolve" in i for i in issues):
        result["valid"] = True
        # Remove the scheme warning if URL was actually valid
        result["issues"] = [i for i in issues if "Missing scheme" not in i]
    
    log_verbose(f"Validation complete. Valid: {result['valid']}", verbose)
    return result


def main() -> int:
    """Main entry point for the URL validator."""
    parser = argparse.ArgumentParser(
        description='Validate URLs and check if they are well-formed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://example.com"              Validate a URL
  %(prog)s "https://example.com" --check-dns  Also check DNS resolution
  %(prog)s "https://example.com" -f json      Output as JSON
        """
    )
    
    parser.add_argument(
        'url',
        help='The URL to validate'
    )
    
    parser.add_argument(
        '--check-dns', '-d',
        action='store_true',
        help='Check if the domain resolves via DNS'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    try:
        result = validate_url(
            args.url,
            check_dns=args.check_dns,
            verbose=args.verbose
        )
        
        output_result(result, args.format)
        
        # Return 0 if valid, 1 if invalid
        return 0 if result["valid"] else 1
        
    except Exception as e:
        log_error(str(e))
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
