#!/usr/bin/env python3
"""
policy_utils.py - Utility functions for insurance policy data extraction.

This module provides common functions for parsing currencies, dates, addresses,
and other data types found in insurance policy schedules.
"""

import re
from datetime import datetime
from typing import Any, Optional, Union
import json


# =============================================================================
# CURRENCY PARSING
# =============================================================================

def parse_currency(value: str) -> Optional[float]:
    """
    Parse a currency string to float.
    
    Handles formats:
    - "R 1 943.22" -> 1943.22
    - "R1,943.22" -> 1943.22
    - "1943.22" -> 1943.22
    - "(500.00)" -> -500.00 (negative)
    - "R-" or "-" -> None
    
    Args:
        value: Currency string to parse
        
    Returns:
        Float value or None if parsing fails
    """
    if not value or not isinstance(value, str):
        return None
    
    value = value.strip()
    
    # Handle empty or dash values
    if value in ['-', 'R-', 'R -', '', 'N/A', 'n/a', 'TBA', 'tba']:
        return None
    
    # Check for negative values in parentheses
    is_negative = value.startswith('(') and value.endswith(')')
    if is_negative:
        value = value[1:-1]
    
    # Remove currency symbols and whitespace
    value = re.sub(r'[R$€£¥\s]', '', value)
    
    # Remove thousands separators (commas)
    value = value.replace(',', '')
    
    # Handle percentage signs (remove but note this changes meaning)
    value = value.replace('%', '')
    
    try:
        result = float(value)
        return -result if is_negative else result
    except (ValueError, TypeError):
        return None


def format_currency(value: Optional[float], currency: str = "R") -> str:
    """
    Format a float as currency string.
    
    Args:
        value: Float value to format
        currency: Currency symbol (default "R" for ZAR)
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return f"{currency} -"
    return f"{currency} {value:,.2f}"


# =============================================================================
# SUM INSURED PARSING
# =============================================================================

# Text-based sum insured patterns (case-insensitive matching)
TEXT_BASED_SUM_INSURED_PATTERNS = [
    "agreed value",
    "retail value",
    "market value",
    "replacement value",
    "trade value",
    "book value",
    "invoice value",
    "new replacement",
    "as per valuation",
    "as valued",
    "to be advised",
    "tba",
    "n/a",
]


def parse_sum_insured(value: str) -> dict:
    """
    Parse a sum insured value that may be numeric or text-based.

    Handles:
    - Numeric: "R 150,000" -> {"value": 150000.0, "text": None, "is_text_based": False}
    - Text: "Agreed Value" -> {"value": None, "text": "Agreed Value", "is_text_based": True}
    - Text: "Retail Value" -> {"value": None, "text": "Retail Value", "is_text_based": True}
    - Combined: "Agreed Value R500,000" -> {"value": 500000.0, "text": "Agreed Value", "is_text_based": True}

    Args:
        value: Sum insured string to parse

    Returns:
        Dictionary with:
        - value: numeric amount or None
        - text: original text if text-based, None otherwise
        - is_text_based: True if contains text like "Agreed Value", "Retail Value"
        - basis_of_valuation: inferred valuation basis (AGREED_VALUE, RETAIL_VALUE, etc.) or None
    """
    result = {
        "value": None,
        "text": None,
        "is_text_based": False,
        "basis_of_valuation": None
    }

    if not value or not isinstance(value, str):
        return result

    value_clean = value.strip()
    value_lower = value_clean.lower()

    # Check for text-based patterns
    for pattern in TEXT_BASED_SUM_INSURED_PATTERNS:
        if pattern in value_lower:
            result["is_text_based"] = True
            result["text"] = value_clean

            # Infer basis of valuation
            if "agreed" in value_lower:
                result["basis_of_valuation"] = "AGREED_VALUE"
            elif "retail" in value_lower:
                result["basis_of_valuation"] = "RETAIL_VALUE"
            elif "market" in value_lower:
                result["basis_of_valuation"] = "MARKET_VALUE"
            elif "replacement" in value_lower:
                result["basis_of_valuation"] = "REPLACEMENT_VALUE"
            elif "trade" in value_lower:
                result["basis_of_valuation"] = "MARKET_VALUE"
            elif "book" in value_lower:
                result["basis_of_valuation"] = "MARKET_VALUE"
            break

    # Try to extract numeric value (even if text-based, there might be an amount)
    currency_match = re.search(r'R\s*([\d\s,\.]+)', value_clean)
    if currency_match:
        result["value"] = parse_currency(currency_match.group(1))
    elif not result["is_text_based"]:
        # No R symbol but might still be numeric
        result["value"] = parse_currency(value_clean)

    return result


# =============================================================================
# DATE PARSING
# =============================================================================

DATE_FORMATS = [
    "%d/%m/%Y",      # 01/03/2025
    "%d-%m-%Y",      # 01-03-2025
    "%Y/%m/%d",      # 2025/03/01
    "%Y-%m-%d",      # 2025-03-01
    "%d %B %Y",      # 01 March 2025
    "%d %b %Y",      # 01 Mar 2025
    "%B %d, %Y",     # March 01, 2025
    "%b %d, %Y",     # Mar 01, 2025
]


def parse_date(value: str) -> Optional[str]:
    """
    Parse various date formats to ISO format (YYYY-MM-DD).
    
    Args:
        value: Date string to parse
        
    Returns:
        ISO formatted date string or None if parsing fails
    """
    if not value or not isinstance(value, str):
        return None
    
    value = value.strip()
    
    if value.lower() in ['tba', 'n/a', '-', '']:
        return None
    
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return None


def normalize_date(value: str) -> Optional[str]:
    """Alias for parse_date for backward compatibility."""
    return parse_date(value)


# =============================================================================
# ADDRESS PARSING
# =============================================================================

def parse_address(address_text: str) -> dict:
    """
    Parse a multi-line address into components.
    
    Args:
        address_text: Raw address text (may be multi-line)
        
    Returns:
        Dictionary with address components
    """
    result = {
        "line1": None,
        "line2": None,
        "line3": None,
        "city": None,
        "province_state": None,
        "postal_code": None,
        "country": "South Africa",
        "full_address": None
    }
    
    if not address_text or not isinstance(address_text, str):
        return result
    
    # Clean and split the address
    lines = [line.strip() for line in address_text.strip().split('\n') if line.strip()]
    
    if not lines:
        return result
    
    # Store full address
    result["full_address"] = ", ".join(lines)
    
    # Extract postal code (typically 4 digits in SA)
    postal_pattern = r'\b(\d{4})\b'
    for i, line in enumerate(lines):
        match = re.search(postal_pattern, line)
        if match:
            result["postal_code"] = match.group(1)
            # Remove postal code from line
            lines[i] = re.sub(postal_pattern, '', line).strip()
    
    # Common SA provinces
    provinces = [
        "gauteng", "western cape", "eastern cape", "northern cape",
        "free state", "kwazulu-natal", "kzn", "mpumalanga", "limpopo",
        "north west", "nw"
    ]
    
    # Try to identify province
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for province in provinces:
            if province in line_lower:
                result["province_state"] = line
                lines[i] = ""
                break
    
    # Remove empty lines
    lines = [l for l in lines if l]
    
    # Assign remaining lines
    if len(lines) >= 1:
        result["line1"] = lines[0]
    if len(lines) >= 2:
        result["line2"] = lines[1]
    if len(lines) >= 3:
        result["city"] = lines[2]
    if len(lines) >= 4:
        result["line3"] = lines[3]
    
    return result


# =============================================================================
# BOOLEAN PARSING
# =============================================================================

def parse_boolean(value: str) -> Optional[bool]:
    """
    Parse various boolean representations.
    
    Args:
        value: String to parse
        
    Returns:
        Boolean value or None
    """
    if not value or not isinstance(value, str):
        return None
    
    value = value.strip().lower()
    
    if value in ['yes', 'y', 'true', '1', '✓', '✔', 'x']:
        return True
    elif value in ['no', 'n', 'false', '0', '']:
        return False
    
    return None


# =============================================================================
# TEXT EXTRACTION HELPERS
# =============================================================================

def extract_field_value(text: str, field_name: str, delimiter: str = ":") -> Optional[str]:
    """
    Extract a field value from text given the field name.
    
    Args:
        text: Text to search
        field_name: Name of the field to find
        delimiter: Character separating field name from value
        
    Returns:
        Field value or None
    """
    pattern = rf'{re.escape(field_name)}\s*{re.escape(delimiter)}\s*(.+?)(?:\n|$)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    return None


def extract_table_rows(text: str, headers: list) -> list:
    """
    Extract table rows based on known headers.
    
    This is a simplified extractor - for complex tables,
    use specialized PDF parsing libraries.
    
    Args:
        text: Text containing table data
        headers: List of expected column headers
        
    Returns:
        List of dictionaries with extracted row data
    """
    rows = []
    lines = text.split('\n')
    
    # Find header line
    header_idx = -1
    for i, line in enumerate(lines):
        if all(h.lower() in line.lower() for h in headers):
            header_idx = i
            break
    
    if header_idx == -1:
        return rows
    
    # Extract data lines (simplified - assumes whitespace separation)
    for line in lines[header_idx + 1:]:
        if not line.strip():
            continue
        # This would need to be customized based on actual table format
        parts = line.split()
        if len(parts) >= len(headers):
            row = dict(zip(headers, parts[:len(headers)]))
            rows.append(row)
    
    return rows


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and normalizing.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


# =============================================================================
# VEHICLE PARSING
# =============================================================================

def parse_vehicle_description(description: str) -> dict:
    """
    Parse a vehicle description into components.
    
    Example: "2021 MERCEDES-BENZ ACTROS 2645LS/33 PURE 6X4 A/T T/T C/C"
    
    Args:
        description: Vehicle description string
        
    Returns:
        Dictionary with year, make, model
    """
    result = {
        "year": None,
        "make": None,
        "model": None,
        "full_description": description
    }
    
    if not description:
        return result
    
    # Extract year (4-digit number at start or standalone)
    year_match = re.match(r'^(\d{4})\s+', description)
    if year_match:
        result["year"] = int(year_match.group(1))
        description = description[year_match.end():]
    
    # Common vehicle makes
    makes = [
        "MERCEDES-BENZ", "MERCEDES", "TOYOTA", "SCANIA", "VOLVO", "MAN",
        "ISUZU", "HINO", "UD", "NISSAN", "FORD", "VOLKSWAGEN", "VW",
        "BMW", "AUDI", "JCB", "JOHN DEERE", "CASE", "MASSEY FERGUSON",
        "NEW HOLLAND", "CATERPILLAR", "CAT", "KOMATSU", "LEMKEN"
    ]
    
    for make in makes:
        if description.upper().startswith(make):
            result["make"] = make
            result["model"] = description[len(make):].strip()
            break
    
    if not result["make"]:
        # Try splitting on first space
        parts = description.split(None, 1)
        if len(parts) >= 1:
            result["make"] = parts[0]
        if len(parts) >= 2:
            result["model"] = parts[1]
    
    return result


def parse_registration_number(reg: str) -> Optional[str]:
    """
    Validate and normalize a vehicle registration number.
    
    Args:
        reg: Registration number string
        
    Returns:
        Normalized registration or None if invalid/TBA
    """
    if not reg or not isinstance(reg, str):
        return None
    
    reg = reg.strip().upper()
    
    if reg in ['TBA', 'N/A', '-', '']:
        return None
    
    return reg


# =============================================================================
# EXCESS PARSING
# =============================================================================

def parse_excess(text: str) -> dict:
    """
    Parse an excess/deductible specification.
    
    Examples:
    - "10% minimum R2,500"
    - "R5,000"
    - "5% of claim"
    - "0% of Retail Value"
    
    Args:
        text: Excess specification text
        
    Returns:
        Dictionary with percentage, minimum, maximum amounts
    """
    result = {
        "percentage_of_claim": None,
        "minimum_amount": None,
        "maximum_amount": None,
        "fixed_amount": None,
        "description": text
    }
    
    if not text:
        return result
    
    # Extract percentage
    pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    if pct_match:
        result["percentage_of_claim"] = float(pct_match.group(1))
    
    # Extract minimum amount
    min_match = re.search(r'(?:minimum|min)\s*R?\s*([\d,\s]+(?:\.\d{2})?)', text, re.IGNORECASE)
    if min_match:
        result["minimum_amount"] = parse_currency(min_match.group(1))
    
    # Extract maximum amount
    max_match = re.search(r'(?:maximum|max)\s*R?\s*([\d,\s]+(?:\.\d{2})?)', text, re.IGNORECASE)
    if max_match:
        result["maximum_amount"] = parse_currency(max_match.group(1))
    
    # If no percentage but has R amount, it might be fixed
    if result["percentage_of_claim"] is None:
        fixed_match = re.search(r'R\s*([\d,\s]+(?:\.\d{2})?)', text)
        if fixed_match:
            result["fixed_amount"] = parse_currency(fixed_match.group(1))
    
    return result


# =============================================================================
# JSON HELPERS
# =============================================================================

def create_extraction_metadata(source_document: str) -> dict:
    """
    Create metadata block for extraction.
    
    Args:
        source_document: Name/path of source document
        
    Returns:
        Metadata dictionary
    """
    return {
        "extracted_at": datetime.now().isoformat(),
        "source_document": source_document,
        "extraction_version": "1.0.0",
        "confidence_score": None
    }


def safe_json_serialize(obj: Any) -> Any:
    """
    Convert object to JSON-serializable format.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable version
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    return obj


def to_json(data: dict, pretty: bool = True) -> str:
    """
    Convert dictionary to JSON string.
    
    Args:
        data: Dictionary to convert
        pretty: Whether to format with indentation
        
    Returns:
        JSON string
    """
    indent = 2 if pretty else None
    return json.dumps(data, indent=indent, default=safe_json_serialize, ensure_ascii=False)


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_policy_number(policy_number: str) -> bool:
    """
    Validate policy number format.
    
    Args:
        policy_number: Policy number to validate
        
    Returns:
        True if valid format
    """
    if not policy_number:
        return False
    
    # Most policy numbers are alphanumeric, 8+ characters
    return bool(re.match(r'^[A-Z0-9]{8,}$', policy_number.upper()))


def validate_vin(vin: str) -> bool:
    """
    Validate vehicle VIN format.
    
    Args:
        vin: VIN to validate
        
    Returns:
        True if valid format (17 characters, no I/O/Q)
    """
    if not vin or vin.upper() == 'TBA':
        return True  # Allow empty/TBA
    
    # Standard VIN is 17 characters, no I, O, or Q
    vin = vin.upper()
    if len(vin) != 17:
        return False
    
    return bool(re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin))


if __name__ == "__main__":
    # Test examples
    print("Testing parse_currency:")
    print(f"  'R 1 943.22' -> {parse_currency('R 1 943.22')}")
    print(f"  'R1,943.22' -> {parse_currency('R1,943.22')}")
    print(f"  '(500.00)' -> {parse_currency('(500.00)')}")

    print("\nTesting parse_date:")
    print(f"  '01/03/2025' -> {parse_date('01/03/2025')}")
    print(f"  '01 March 2025' -> {parse_date('01 March 2025')}")

    print("\nTesting parse_vehicle_description:")
    desc = "2021 MERCEDES-BENZ ACTROS 2645LS/33 PURE 6X4"
    print(f"  '{desc}'")
    print(f"  -> {parse_vehicle_description(desc)}")

    print("\nTesting parse_sum_insured:")
    test_cases = [
        "R 150,000",
        "Agreed Value",
        "Retail Value",
        "Market Value R500,000",
        "R500000",
        "Agreed Value R 1,250,000",
        "TBA",
        "As per valuation",
    ]
    for case in test_cases:
        result = parse_sum_insured(case)
        print(f"  '{case}'")
        print(f"    -> value={result['value']}, text={result['text']}, "
              f"is_text_based={result['is_text_based']}, "
              f"basis={result['basis_of_valuation']}")
