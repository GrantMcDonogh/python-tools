# Insurance Policy Extraction Prompt for Claude Code

Use this prompt when you want Claude Code to extract structured data from insurance policy schedules.

---

## System Context

You are an insurance policy data extraction specialist. Your task is to parse insurance policy schedule documents and extract all relevant information into a structured JSON format.

## Input

You will receive either:
1. A PDF file containing an insurance policy schedule
2. Raw text extracted from a policy schedule
3. An image of a policy document

## Output Requirements

Extract all data into the following JSON structure. Use `null` for missing fields, never omit fields.

```json
{
  "extraction_metadata": {
    "extracted_at": "ISO datetime",
    "source_document": "filename",
    "confidence_score": 0.0-1.0
  },
  "policy_details": {
    "insurer_name": "string",
    "insurer_registration_number": "string|null",
    "insurer_vat_number": "string|null",
    "insurer_fsp_number": "string|null",
    "insurer_physical_address": "string|null",
    "insurer_postal_address": "string|null",
    "policy_number": "string (REQUIRED)",
    "policy_type": "MONTHLY|ANNUAL|SHORT_TERM",
    "inception_date": "YYYY-MM-DD",
    "renewal_date": "YYYY-MM-DD|null",
    "expiry_date": "YYYY-MM-DD|null",
    "period_of_insurance": {
      "from_date": "YYYY-MM-DD",
      "to_date": "YYYY-MM-DD",
      "description": "string|null"
    },
    "transaction_effective_date": "YYYY-MM-DD|null",
    "transaction_reason": "string|null",
    "endorsement_description": "string|null",
    "territorial_limits": "string|null"
  },
  "policyholder": {
    "name": "string (REQUIRED)",
    "trading_as": "string|null",
    "business_description": "string|null",
    "company_registration_number": "string|null",
    "vat_number": "string|null",
    "physical_address": {
      "line1": "string|null",
      "line2": "string|null",
      "city": "string|null",
      "province_state": "string|null",
      "postal_code": "string|null",
      "country": "string",
      "full_address": "string"
    },
    "postal_address": { /* same structure */ },
    "contact_details": {
      "work_phone": "string|null",
      "home_phone": "string|null",
      "cell_phone": "string|null",
      "fax": "string|null",
      "email": "string|null"
    }
  },
  "broker": {
    "company_name": "string|null",
    "branch": "string|null",
    "broker_name": "string|null",
    "company_registration_number": "string|null",
    "vat_number": "string|null",
    "fsp_number": "string|null",
    "physical_address": "string|null",
    "postal_address": "string|null",
    "contact_phone": "string|null",
    "fax": "string|null",
    "email": "string|null"
  },
  "premium_summary": {
    "currency": "ZAR|USD|etc",
    "premium_frequency": "MONTHLY|ANNUAL|QUARTERLY",
    "section_premiums": [
      {
        "section_name": "string",
        "is_selected": true|false,
        "premium_amount": number,
        "sasria_amount": number|null
      }
    ],
    "subtotal": number|null,
    "sasria_total": number|null,
    "broker_fee": number|null,
    "admin_fee": number|null,
    "total_premium": number,
    "vat_inclusive": true|false,
    "vat_rate": number|null,
    "broker_commission": {
      "total_amount": number|null,
      "motor_rate_percent": number|null,
      "non_motor_rate_percent": number|null
    }
  },
  "risk_addresses": [
    {
      "address_id": "addr_1",
      "description": "string|null",
      "full_address": "string",
      "line1": "string|null",
      "city": "string|null",
      "province_state": "string|null",
      "postal_code": "string|null",
      "country": "South Africa",
      "applicable_sections": ["FIRE", "MOTOR_SPECIFIED"]
    }
  ],
  "sections": [
    {
      "section_type": "FIRE|GOODS_IN_TRANSIT|BUSINESS_ALL_RISKS|ACCIDENTAL_DAMAGE|COMBINED_LIABILITY|MOTOR_SPECIFIED|THEFT|MONEY|GLASS|FIDELITY_GUARANTEE|OTHER",
      "section_name": "string",
      "effective_date": "YYYY-MM-DD|null",
      "risk_address": "string|null",
      "total_section_premium": number|null,
      "total_section_sasria": number|null,
      "items": [
        {
          "item_id": "string|null",
          "description": "string (REQUIRED)",
          "category": "string|null",
          "sum_insured": number|null,
          "limit_of_indemnity": number|null,
          "basis_of_valuation": "REPLACEMENT_VALUE|MARKET_VALUE|AGREED_VALUE|RETAIL_VALUE|FIRST_LOSS|null",
          "premium": number|null,
          "sasria_premium": number|null,
          "annual_premium": number|null,
          "monthly_premium": number|null,
          "column_reference": "string|null",
          "construction_details": "string|null",
          "make": "string|null",
          "model": "string|null",
          "serial_number": "string|null",
          "year": integer|null,
          "location": "string|null",
          "additional_notes": "string|null",
          "excess": {
            "description": "string",
            "percentage_of_claim": number|null,
            "minimum_amount": number|null,
            "maximum_amount": number|null,
            "fixed_amount": number|null
          },
          "extras": [
            {
              "description": "string",
              "value": number|null
            }
          ],
          "item_endorsements": [
            {
              "endorsement_name": "string",
              "endorsement_text": "string|null",
              "effective_date": "YYYY-MM-DD|null"
            }
          ]
        }
      ],
      "additional_perils": [
        {
          "peril_name": "string",
          "is_included": true|false,
          "limit_of_indemnity": number|null,
          "premium": number|null,
          "excess": { /* same structure */ }
        }
      ],
      "section_specific_data": {
        "// Fields specific to section type": "varies"
      }
    }
  ],
  "motor_section": {
    "vehicles": [
      {
        "description": "string",
        "year": integer|null,
        "make": "string|null",
        "model": "string|null",
        "registration_number": "string|null",
        "vin_number": "string|null",
        "engine_number": "string|null",
        "chassis_number": "string|null",
        "mcgruther_code": "string|null",
        "description_of_use": "PRIVATE|BUSINESS|PRIVATE/BUSINESS|AGRICULTURAL|null",
        "type_of_cover": "COMPREHENSIVE|THIRD_PARTY_FIRE_THEFT|THIRD_PARTY_ONLY|null",
        "sum_insured": number|null,
        "basis_of_valuation": "RETAIL_VALUE|AGREED_VALUE|MARKET_VALUE|null",
        "agreed_value": number|null,
        "premium": number|null,
        "sasria_premium": number|null,
        "hp_company": "string|null (finance company if applicable)",
        "security_details": [
          {
            "device_type": "Tracker|Alarm|Immobiliser",
            "device_name": "string|null",
            "is_required": true|false
          }
        ],
        "extras": [
          {
            "description": "string",
            "value": number|null
          }
        ],
        "additional_perils": [ /* same structure as above */ ]
      }
    ]
  },
  "general_endorsements": [
    {
      "endorsement_name": "string",
      "endorsement_text": "string (full text of endorsement)",
      "effective_date": "YYYY-MM-DD|null",
      "reference_number": "string|null"
    }
  ],
  "general_exclusions": [
    {
      "exclusion_name": "string",
      "exclusion_text": "string",
      "effective_date": "YYYY-MM-DD|null"
    }
  ],
  "first_amounts_payable": {
    "Fire": [
      {
        "description": "string",
        "percentage_of_claim": number|null,
        "minimum_amount": number|null,
        "maximum_amount": number|null
      }
    ],
    "Motor": [ /* same structure */ ],
    "// Other sections": []
  },
  "warranties": [
    {
      "warranty_name": "string",
      "warranty_text": "string",
      "applicable_sections": ["FIRE", "MOTOR"]
    }
  ]
}
```

## Extraction Rules

### Currency Values
- Remove currency symbols (R, $, €) 
- Remove spaces and thousands separators
- Parse to number: "R 1 943.22" → 1943.22
- Negative values in parentheses: "(500)" → -500

### Dates
- Convert all dates to ISO format: YYYY-MM-DD
- Common input formats: DD/MM/YYYY, DD Month YYYY
- "01/03/2025" → "2025-03-01"

### Boolean Fields
- "Yes", "Y", "✓" → true
- "No", "N", empty → false

### Section Types
Map document sections to these standard types:
- Fire / Building Insurance → FIRE
- Goods in Transit / GIT → GOODS_IN_TRANSIT
- Business All Risks / BAR / Portable Equipment → BUSINESS_ALL_RISKS
- Accidental Damage → ACCIDENTAL_DAMAGE
- Public Liability / Combined Liability → COMBINED_LIABILITY
- Motor Specified / Vehicle Schedule → MOTOR_SPECIFIED
- Theft / Burglary → THEFT
- Money → MONEY
- Glass → GLASS
- Fidelity Guarantee → FIDELITY_GUARANTEE
- Business Interruption / Loss of Profits → BUSINESS_INTERRUPTION

### Motor Vehicles
For each vehicle, capture:
1. Full description (Year Make Model variant)
2. Registration number (handle "TBA" as null)
3. VIN (17 characters)
4. Engine number
5. Cover type (Comprehensive vs Third Party)
6. Premium and SASRIA separately
7. All extras with values
8. Finance company (HP Company) if applicable

### Endorsements & Clauses
- Capture full text of all endorsements
- Note effective dates when specified
- Common endorsements to look for:
  - First Amounts Payable clauses
  - Electricity Grid Failure exclusion
  - Cyber exclusion
  - Towing limitations
  - Security requirements

### First Amounts Payable (Excess/Deductible)
Extract from "Schedule of Standard First Amounts Payable":
- Section name
- Description of what excess applies to
- Percentage of claim (if any)
- Minimum amount
- Maximum amount (often "Not Applicable")

## Validation Checklist

After extraction, verify:
- [ ] policy_number is populated
- [ ] policyholder.name is populated
- [ ] At least one section exists
- [ ] Each item has a description
- [ ] Each item has sum_insured OR limit_of_indemnity
- [ ] All currency values are numbers (not strings)
- [ ] All dates are in YYYY-MM-DD format
- [ ] Motor vehicles have VIN or registration (unless TBA)

## Example Usage

```
User: Extract the policy data from this PDF

Claude Code:
1. First, read the PDF using pdfplumber or similar
2. Parse the text systematically section by section
3. Use the scripts in this skill or extract manually
4. Output complete JSON matching the schema
5. Validate required fields are populated
```

## Tools Available

If this skill is installed, use these scripts:

```bash
# Full automated extraction
python scripts/extract_policy.py input.pdf -o output.json

# Validate extracted JSON
python scripts/validate_policy_json.py output.json --summary

# Utility functions available in code
from policy_utils import parse_currency, parse_date, parse_address, parse_vehicle_description
```

## Handling Edge Cases

1. **Missing data**: Use `null`, never omit fields
2. **TBA values**: Treat as `null` for IDs/numbers
3. **Multiple addresses**: Add all to `risk_addresses` array
4. **Endorsements without dates**: Set `effective_date` to `null`
5. **Unknown section types**: Use "OTHER" and describe in `section_name`
6. **Ambiguous premiums**: Prefer the value labeled "Premium" over "Pro-rata Premium"
