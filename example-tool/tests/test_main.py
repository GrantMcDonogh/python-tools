#!/usr/bin/env python3
"""
Tests for the URL Validator tool.

Run with: pytest test_main.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from main import validate_url


class TestValidateUrl:
    """Tests for the validate_url function."""
    
    def test_valid_https_url(self):
        """Test a valid HTTPS URL."""
        result = validate_url("https://example.com")
        assert result["valid"] is True
        assert result["scheme"] == "https"
        assert result["domain"] == "example.com"
        assert len(result["issues"]) == 0
    
    def test_valid_http_url(self):
        """Test a valid HTTP URL."""
        result = validate_url("http://example.com")
        assert result["valid"] is True
        assert result["scheme"] == "http"
    
    def test_url_with_path(self):
        """Test a URL with a path."""
        result = validate_url("https://example.com/api/v1/users")
        assert result["valid"] is True
        assert result["path"] == "/api/v1/users"
    
    def test_url_with_query(self):
        """Test a URL with query parameters."""
        result = validate_url("https://example.com/search?q=test&page=1")
        assert result["valid"] is True
        assert result["query"] == "q=test&page=1"
    
    def test_url_with_fragment(self):
        """Test a URL with a fragment."""
        result = validate_url("https://example.com/page#section")
        assert result["valid"] is True
        assert result["fragment"] == "section"
    
    def test_url_with_port(self):
        """Test a URL with a custom port."""
        result = validate_url("https://example.com:8080/api")
        assert result["valid"] is True
        assert result["port"] == 8080
    
    def test_missing_scheme(self):
        """Test a URL without a scheme."""
        result = validate_url("example.com")
        assert result["valid"] is False
        assert any("Missing scheme" in issue for issue in result["issues"])
    
    def test_empty_url(self):
        """Test an empty URL."""
        result = validate_url("")
        assert result["valid"] is False
        assert any("empty" in issue.lower() for issue in result["issues"])
    
    def test_url_with_spaces(self):
        """Test a URL with spaces."""
        result = validate_url("https://example.com/path with spaces")
        assert any("spaces" in issue.lower() for issue in result["issues"])
    
    def test_localhost(self):
        """Test localhost URL."""
        result = validate_url("http://localhost:3000")
        assert result["valid"] is True
        assert result["domain"] == "localhost"
        assert result["port"] == 3000
    
    def test_ip_address(self):
        """Test URL with IP address."""
        result = validate_url("http://192.168.1.1:8080")
        assert result["valid"] is True
        assert result["domain"] == "192.168.1.1"
    
    def test_ftp_url(self):
        """Test FTP URL."""
        result = validate_url("ftp://files.example.com/document.pdf")
        assert result["valid"] is True
        assert result["scheme"] == "ftp"


class TestDnsCheck:
    """Tests for DNS resolution checking."""
    
    def test_dns_check_real_domain(self):
        """Test DNS check with a real domain (requires network)."""
        result = validate_url("https://example.com", check_dns=True)
        # example.com is a reserved domain that should always resolve
        assert result["valid"] is True
        assert "dns_resolves" in result
    
    def test_dns_check_invalid_domain(self):
        """Test DNS check with an invalid domain."""
        result = validate_url("https://this-domain-definitely-does-not-exist-12345.com", check_dns=True)
        assert result["dns_resolves"] is False
        assert any("does not resolve" in issue for issue in result["issues"])


if __name__ == '__main__':
    # Simple test runner if pytest is not available
    import traceback
    
    test_classes = [TestValidateUrl, TestDnsCheck]
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    getattr(instance, method_name)()
                    print(f"  PASS: {test_class.__name__}.{method_name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  FAIL: {test_class.__name__}.{method_name}")
                    print(f"        {e}")
                    failed += 1
                except Exception as e:
                    print(f"  ERROR: {test_class.__name__}.{method_name}")
                    print(f"        {e}")
                    failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
