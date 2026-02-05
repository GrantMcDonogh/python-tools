#!/usr/bin/env python3
"""
validate_policy_json.py - Validate extracted policy JSON against schema.

Usage:
    python validate_policy_json.py <json_file> [--schema schema.json]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple


def load_json(filepath: str) -> dict:
    """Load JSON from file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_required_fields(data: dict, required: list, path: str = "") -> List[str]:
    """Check that required fields are present."""
    errors = []
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {path}{field}")
    return errors


def validate_type(value, expected_type: str, path: str) -> List[str]:
    """Validate value type."""
    errors = []
    
    type_map = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict
    }
    
    if expected_type in type_map:
        expected = type_map[expected_type]
        if value is not None and not isinstance(value, expected):
            errors.append(f"Type error at {path}: expected {expected_type}, got {type(value).__name__}")
    
    return errors


def validate_policy_data(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate policy data against expected structure.
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    warnings = []
    
    # Check top-level required fields
    top_level_required = ["policy_details", "policyholder", "sections"]
    errors.extend(validate_required_fields(data, top_level_required))
    
    # Validate policy_details
    if "policy_details" in data and data["policy_details"]:
        pd = data["policy_details"]
        if not pd.get("policy_number"):
            errors.append("Missing policy_details.policy_number")
        if not pd.get("insurer_name"):
            warnings.append("Warning: Missing policy_details.insurer_name")
    
    # Validate policyholder
    if "policyholder" in data and data["policyholder"]:
        ph = data["policyholder"]
        if not ph.get("name"):
            errors.append("Missing policyholder.name")
    
    # Validate sections
    if "sections" in data and isinstance(data["sections"], list):
        for i, section in enumerate(data["sections"]):
            section_path = f"sections[{i}]"
            
            if not section.get("section_type"):
                errors.append(f"Missing {section_path}.section_type")
            
            if not section.get("section_name"):
                errors.append(f"Missing {section_path}.section_name")
            
            # Validate items
            if "items" in section and isinstance(section["items"], list):
                for j, item in enumerate(section["items"]):
                    item_path = f"{section_path}.items[{j}]"
                    
                    if not item.get("description") and not item.get("category"):
                        warnings.append(f"Warning: No description at {item_path}")
                    
                    # Check for sum insured or limit
                    if item.get("sum_insured") is None and item.get("limit_of_indemnity") is None:
                        warnings.append(f"Warning: No sum_insured or limit_of_indemnity at {item_path}")
    
    # Validate motor section if present
    if data.get("motor_section") and data["motor_section"].get("vehicles"):
        for i, vehicle in enumerate(data["motor_section"]["vehicles"]):
            v_path = f"motor_section.vehicles[{i}]"
            
            if not vehicle.get("description"):
                warnings.append(f"Warning: No description at {v_path}")
            
            # VIN validation
            vin = vehicle.get("vin_number")
            if vin and vin.upper() != "TBA":
                if len(vin) != 17:
                    warnings.append(f"Warning: Invalid VIN length at {v_path}: {vin}")
    
    # Validate premium summary
    if data.get("premium_summary"):
        ps = data["premium_summary"]
        if ps.get("total_premium") is None:
            warnings.append("Warning: Missing premium_summary.total_premium")
    
    # Print warnings
    for warning in warnings:
        print(warning, file=sys.stderr)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_against_schema(data: dict, schema_path: str) -> Tuple[bool, List[str]]:
    """
    Validate data against JSON schema using jsonschema library.
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    try:
        import jsonschema
        from jsonschema import validate, ValidationError
        
        schema = load_json(schema_path)
        
        try:
            validate(instance=data, schema=schema)
            return True, []
        except ValidationError as e:
            return False, [f"Schema validation error: {e.message} at {'/'.join(str(p) for p in e.absolute_path)}"]
        
    except ImportError:
        print("Warning: jsonschema not installed. Running basic validation only.", file=sys.stderr)
        return validate_policy_data(data)


def print_summary(data: dict):
    """Print a summary of extracted data."""
    print("\n=== EXTRACTION SUMMARY ===")
    
    # Policy info
    pd = data.get("policy_details", {})
    print(f"\nPolicy Number: {pd.get('policy_number', 'N/A')}")
    print(f"Insurer: {pd.get('insurer_name', 'N/A')}")
    print(f"Policy Type: {pd.get('policy_type', 'N/A')}")
    
    # Policyholder
    ph = data.get("policyholder", {})
    print(f"\nPolicyholder: {ph.get('name', 'N/A')}")
    
    # Sections
    sections = data.get("sections", [])
    print(f"\nSections Extracted: {len(sections)}")
    for section in sections:
        item_count = len(section.get("items", []))
        premium = section.get("total_section_premium")
        premium_str = f"R {premium:,.2f}" if premium else "N/A"
        print(f"  - {section.get('section_name', 'Unknown')}: {item_count} items, Premium: {premium_str}")
    
    # Motor vehicles
    motor = data.get("motor_section", {})
    if motor and motor.get("vehicles"):
        print(f"\nMotor Vehicles: {len(motor['vehicles'])}")
    
    # Premium summary
    ps = data.get("premium_summary", {})
    if ps.get("total_premium"):
        print(f"\nTotal Premium: R {ps['total_premium']:,.2f}")
    
    # Risk addresses
    addresses = data.get("risk_addresses", [])
    if addresses:
        print(f"\nRisk Addresses: {len(addresses)}")
        for addr in addresses[:3]:  # Show first 3
            print(f"  - {addr.get('full_address', 'N/A')[:50]}...")
    
    print("\n" + "=" * 30)


def main():
    parser = argparse.ArgumentParser(
        description="Validate extracted policy JSON against schema"
    )
    parser.add_argument("json_file", help="JSON file to validate")
    parser.add_argument("--schema", help="JSON schema file (optional)")
    parser.add_argument("--summary", action="store_true", help="Print extraction summary")
    parser.add_argument("--quiet", action="store_true", help="Suppress output except errors")
    
    args = parser.parse_args()
    
    # Load JSON file
    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: File not found: {args.json_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        data = load_json(str(json_path))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate
    if args.schema:
        is_valid, errors = validate_against_schema(data, args.schema)
    else:
        is_valid, errors = validate_policy_data(data)
    
    # Output results
    if not args.quiet:
        if is_valid:
            print("✓ Validation passed")
        else:
            print("✗ Validation failed")
            for error in errors:
                print(f"  - {error}")
    
    if args.summary:
        print_summary(data)
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
