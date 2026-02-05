---
name: hollard-agri-data-extractor
description: |
  Extract structured data from insurance policy schedules into JSON format. Use this skill when:
  (1) User provides an insurance policy schedule PDF or text and wants data extraction
  (2) User needs policyholder details, risk addresses, insured items, premiums, or endorsements extracted
  (3) User wants to convert policy documents into structured/machine-readable format
  (4) User mentions "policy schedule", "insurance extraction", "policy JSON", or similar terms
  Supports: Fire, Motor, Liability, Goods in Transit, Business All Risks, and other commercial insurance sections.
---

# Insurance Policy Extractor

Extract comprehensive data from insurance policy schedules into structured JSON format.

## Quick Start

```bash
# Extract from PDF
python scripts/extract_policy.py /path/to/policy.pdf -o output.json

# Extract from text file
python scripts/extract_policy.py /path/to/policy.txt -o output.json

# Validate extracted JSON against schema
python scripts/validate_policy_json.py output.json
```

## Workflow

1. **Load the policy document** - Read PDF/text into memory
2. **Run extraction script** - `scripts/extract_policy.py` handles parsing
3. **Review and validate** - Check output against `references/schema.json`
4. **Export** - Save final JSON to user's desired location

## Output Schema

The extraction produces JSON conforming to `references/schema.json`. Key sections:

- `policy_details` - Policy number, dates, insurer info
- `policyholder` - Name, registration, addresses, contacts
- `broker` - Broker company and contact details
- `premium_summary` - Section premiums, SASRIA, fees, totals
- `sections` - Array of insured sections (Fire, Motor, Liability, etc.)
- `general_endorsements` - Policy-wide clauses and exclusions
- `first_amounts_payable` - Standard excess schedules

## Section Types

Each section in `sections[]` follows a type-specific structure:

| Section Type | Key Fields |
|--------------|------------|
| Fire | buildings, stock, miscellaneous items, column references |
| Motor | vehicles array with VIN, registration, cover type, extras |
| Liability | public/products liability, retroactive date, basis |
| Goods in Transit | load limit, conveyance type, hijacking cover |
| Business All Risks | portable equipment, serial numbers |
| Accidental Damage | total value at risk, defined events |

## Sum Insured Text Detection

Items and vehicles include fields to detect text-based sum insured values:

| Field | Description |
|-------|-------------|
| `sum_insured` | Numeric value (may be null for text-based) |
| `sum_insured_text` | Original text when sum is text-based (e.g., "Agreed Value", "Retail Value") |
| `sum_insured_is_text_based` | `true` if sum contains text like "Agreed Value" or "Retail Value" |
| `basis_of_valuation` | Inferred valuation basis: `AGREED_VALUE`, `RETAIL_VALUE`, `MARKET_VALUE`, `REPLACEMENT_VALUE` |

**Detected text patterns:**
- Agreed Value, Retail Value, Market Value, Replacement Value
- Trade Value, Book Value, Invoice Value
- As per valuation, As valued, TBA, N/A

## Scripts Reference

### `scripts/extract_policy.py`
Main extraction script. Parses policy documents and outputs JSON.

```bash
python scripts/extract_policy.py <input_file> [-o output.json] [--format pretty|compact]
```

### `scripts/validate_policy_json.py`
Validates extracted JSON against the schema.

```bash
python scripts/validate_policy_json.py <json_file>
```

### `scripts/policy_utils.py`
Utility functions for currency parsing, date normalization, and field extraction.
Import in custom scripts: `from policy_utils import parse_currency, normalize_date`

## Manual Extraction Guidelines

When automated extraction fails or for complex documents, extract manually following `references/extraction_rules.md`:

1. Start with policyholder identification
2. Extract policy metadata (numbers, dates, territorial limits)
3. Process each section sequentially
4. Capture all endorsements and clauses
5. Record first amounts payable (excesses)
6. Validate completeness against schema

## Files

- `references/schema.json` - Complete JSON schema definition
- `references/extraction_rules.md` - Detailed field-by-field extraction rules
- `scripts/extract_policy.py` - Main extraction script
- `scripts/validate_policy_json.py` - Schema validation
- `scripts/policy_utils.py` - Shared utility functions
