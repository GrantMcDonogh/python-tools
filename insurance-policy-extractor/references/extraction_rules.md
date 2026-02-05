# Insurance Policy Extraction Rules

Field-by-field extraction guidance for insurance policy schedules.

## 1. Policyholder Details

Extract from "POLICYHOLDER DETAILS" section:

| Field | Source Pattern | Notes |
|-------|---------------|-------|
| `name` | "Policyholder" line | Company/individual name |
| `business_description` | "Business description" | e.g., "Farmer", "Retailer" |
| `vat_number` | "Vat number" | May be empty |
| `company_registration_number` | "Company registration number" | Format: YYYY/NNNNNN/NN |
| `physical_address` | "Physical address" block | Multi-line, parse into components |
| `postal_address` | "Postal address" block | May match physical |
| `contact_details.work_phone` | "Work" | Phone number |
| `contact_details.cell_phone` | "Cell" | Mobile number |
| `contact_details.email` | "Email" | Email address |

## 2. Policy Details

Extract from "POLICY DETAILS" section:

| Field | Source Pattern | Format |
|-------|---------------|--------|
| `insurer_name` | "Insurer" | Full company name |
| `policy_number` | "Policy number" | Alphanumeric |
| `policy_type` | "Type of policy" | MONTHLY/ANNUAL |
| `inception_date` | "Inception date" | DD/MM/YYYY → YYYY-MM-DD |
| `renewal_date` | "Renewal date" | DD/MM/YYYY → YYYY-MM-DD |
| `transaction_effective_date` | "Transaction effective date" | DD/MM/YYYY |
| `transaction_reason` | "Transaction reason" | Text description |
| `endorsement_description` | "Endorsement Description" | Text description |
| `period_of_insurance.from_date` | "From DD/MM/YYYY" | Extract start date |
| `period_of_insurance.to_date` | "to DD/MM/YYYY" | Extract end date |
| `territorial_limits` | "Territorial Limits" | Full text, countries list |

## 3. Broker Details

Extract from "BROKER DETAILS" section:

| Field | Source Pattern |
|-------|---------------|
| `company_name` | "Company" |
| `branch` | "Branch" |
| `broker_name` | "Broker" (under Contact details) |
| `fsp_number` | "FSB/FSP number" or "Licence Number" |
| `company_registration_number` | "Company registration number" |
| `vat_number` | "VAT number" |

## 4. Premium Summary

Extract from "PREMIUM SUMMARY" section:

### Section Premiums Table
Parse the table with columns: Section Name | Selected (Yes/No) | Premium | Pro-rata Premium

```
For each row:
{
  "section_name": "Fire",
  "is_selected": true,
  "premium_amount": 1943.22,
  "sasria_amount": null  // Extract if separate SASRIA line exists
}
```

### Summary Fields
| Field | Source Pattern | Notes |
|-------|---------------|-------|
| `subtotal` | "Sub Total" | Sum before fees |
| `sasria_total` | "Sasria" | Total SASRIA levy |
| `broker_fee` | "Broker Fee" | Service fee |
| `total_premium` | "TOTAL" | Final amount |
| `broker_commission.total_amount` | "broker commission of RXXXX" | Parse from text |
| `broker_commission.motor_rate_percent` | "motor classes is XX%" | Percentage |
| `broker_commission.non_motor_rate_percent` | "non-motor classes is XX%" | Percentage |

## 5. Section Extraction

### 5.1 Fire Section

Header pattern: `FIRE SECTION`

Fields:
- `effective_date`: "Effective Date" line
- `risk_address`: "Physical Location" line
- `total_section_premium`: "Total Section Premium" (R value)

#### Items Table Columns:
- Description
- Column Reference (1-6)
- Escalator Clause Specific Percentage
- Sum Insured
- Premium
- SASRIA (separate line below item)

Column Reference Meanings (extract from endorsements):
- 1: Buildings and outbuildings
- 2: Rent/rental value
- 3: Plant, machinery, fixtures
- 4: Stock and materials in trade
- 5: Miscellaneous as described
- 6: Combined contents and stock

### 5.2 Goods in Transit Section

Header pattern: `GOODS IN TRANSIT SECTION`

Fields:
- `section_specific_data.cover_selected`: "Cover selected" (e.g., "Single Transit")
- `section_specific_data.basis_of_cover`: "Basis of Cover" (e.g., "All Risk")
- `section_specific_data.means_of_conveyance`: "Means of Conveyance" (e.g., "Rail, Air, Road")

Items:
- `sum_insured`: Main sum insured
- `load_limit`: Load limit per transit
- `additional_notes`: e.g., "Including Livestock"

### 5.3 Business All Risks Section

Header pattern: `BUSINESS ALL RISKS SECTION`

For each item extract:
- `description`: Full item description
- `sum_insured`: R value
- `premium`: R value
- `make`: If specified
- `model`: If specified
- `serial_number`: "Serial number/IMEI number" value
- `sasria_premium`: SASRIA line below item

### 5.4 Accidental Damage Section

Header pattern: `ACCIDENTAL DAMAGE SECTION`

Fields:
- `section_specific_data.total_value_at_risk`: "Total Value at Risk"
- `items[0].description`: Defined Events type
- `items[0].sum_insured`: Coverage amount

### 5.5 Combined Liability Section

Header pattern: `COMBINED LIABILITY SECTION`

Fields:
- `section_specific_data.retroactive_date`: "Retroactive Date"
- `section_specific_data.basis_of_cover`: "Basis of Cover" (e.g., "Claims Made")
- `section_specific_data.industry`: "Industry" field if present

Sub-sections:
- `items[].description`: e.g., "Sub-Section 1 - Public Liability"
- `items[].sum_insured`: Limit of indemnity

### 5.6 Motor Specified Section

Header pattern: `MOTOR SPECIFIED SECTION` or `MOTOR SPECIFIED SUMMARY`

#### Vehicle Details Block
For each vehicle, extract:

```json
{
  "description": "2021 MERCEDES-BENZ ACTROS 2645LS/33 PURE 6X4 A/T T/T C/C",
  "year": 2021,
  "make": "MERCEDES-BENZ",
  "model": "ACTROS 2645LS/33 PURE 6X4 A/T T/T C/C",
  "registration_number": "KVL678NW",
  "vin_number": "ABJ96342460470662",
  "engine_number": "460972U1067343",
  "chassis_number": null,
  "mcgruther_code": "44080902",
  "description_of_use": "PRIVATE/BUSINESS",
  "type_of_cover": "COMPREHENSIVE",
  "sum_insured": null,
  "basis_of_valuation": "RETAIL_VALUE",
  "agreed_value": null,
  "premium": 3625.20,
  "sasria_premium": 892.84,
  "hp_company": null
}
```

#### Security Details
Extract from "Security Details" sub-section:
```json
{
  "device_type": "Tracker",
  "device_name": null,
  "is_required": true
}
```

#### Vehicle Extras
Parse from "Additional Notes" section:
```json
{
  "extras": [
    { "description": "Aerokit", "value": 40000.00 },
    { "description": "Hydraulics", "value": 35000.00 }
  ]
}
```

#### Additional Perils
Parse the Yes/No table:
```json
{
  "peril_name": "Unauthorised passenger's personal injury liability",
  "is_included": true,
  "limit_of_indemnity": 2500000.00,
  "excess": { "percentage_of_claim": 0, "description": "0% of Retail Value" }
}
```

## 6. General Endorsements

Extract from "GENERAL ENDORSEMENTS" section and any "ENDORSEMENT FORMING PART OF THIS POLICY" blocks.

For each endorsement:
```json
{
  "endorsement_name": "Electricity Grid Failure exclusion",
  "endorsement_text": "[Full text of the endorsement]",
  "effective_date": "2023-04-01",
  "reference_number": "General Exception 8"
}
```

Key endorsements to capture:
- First Amounts Payable clauses
- Towing and Release Fees Limitation
- Electricity Grid Failure exclusion
- Cyber Exclusion
- Non-Physical Damage Business Interruption exclusion

## 7. First Amounts Payable (Excesses)

Extract from "SCHEDULE OF STANDARD FIRST AMOUNTS PAYABLE" section.

Structure by section type:
```json
{
  "Fire": [
    {
      "description": "Standard",
      "percentage_of_claim": 0,
      "minimum_amount": 2500,
      "maximum_amount": null
    },
    {
      "description": "Lightning - No SABS approved surge devices installed",
      "percentage_of_claim": 10,
      "minimum_amount": 2500,
      "maximum_amount": null
    }
  ],
  "Motor_Private": [
    {
      "description": "Sub-section A (Basic)",
      "percentage_of_claim": 5,
      "minimum_amount": 3000,
      "maximum_amount": null
    }
  ]
}
```

## 8. Currency Parsing Rules

- Remove currency symbol (R, $, €, etc.)
- Remove thousands separators (spaces or commas)
- Convert to float: "R 1 943.22" → 1943.22
- Handle negative values in parentheses: "(500)" → -500

## 9. Date Parsing Rules

Input formats to handle:
- DD/MM/YYYY → YYYY-MM-DD
- DD Month YYYY → YYYY-MM-DD
- YYYY/MM/DD → YYYY-MM-DD

## 10. Address Parsing Rules

Split multi-line addresses into:
- `line1`: Street number and name
- `line2`: Suburb/area
- `city`: City/town name
- `province_state`: Province
- `postal_code`: Postal/ZIP code
- `country`: Default "South Africa" if not specified

Preserve `full_address` as original concatenated string.

## 11. Boolean Field Rules

- "Yes" → true
- "No" → false
- Empty/blank → null or false depending on context
- Check mark (✓) → true

## 12. Null Handling

Use `null` for:
- Missing optional fields
- Fields marked as "TBA" or "To Be Advised"
- Empty cells in tables
- Fields that don't apply to item type
