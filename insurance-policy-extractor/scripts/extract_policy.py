#!/usr/bin/env python3
"""
extract_policy.py - Extract insurance policy data to JSON format.

Usage:
    python extract_policy.py <input_file> [-o output.json] [--format pretty|compact]

Supports PDF and text file inputs.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Import utilities
try:
    from policy_utils import (
        parse_currency, parse_date, parse_address, parse_boolean,
        parse_vehicle_description, parse_registration_number, parse_excess,
        parse_sum_insured, extract_field_value, clean_text,
        create_extraction_metadata, to_json
    )
except ImportError:
    # If running from different directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from policy_utils import (
        parse_currency, parse_date, parse_address, parse_boolean,
        parse_vehicle_description, parse_registration_number, parse_excess,
        parse_sum_insured, extract_field_value, clean_text,
        create_extraction_metadata, to_json
    )


class PolicyExtractor:
    """Extract structured data from insurance policy documents."""
    
    def __init__(self, text: str, source_name: str = "unknown"):
        self.text = text
        self.source_name = source_name
        self.data = self._create_empty_structure()
    
    def _create_empty_structure(self) -> dict:
        """Create empty policy data structure."""
        return {
            "extraction_metadata": create_extraction_metadata(self.source_name),
            "policy_details": {},
            "policyholder": {},
            "broker": None,
            "premium_summary": {},
            "risk_addresses": [],
            "sections": [],
            "motor_section": None,
            "general_endorsements": [],
            "general_exclusions": [],
            "first_amounts_payable": {},
            "special_conditions": [],
            "warranties": []
        }
    
    def extract_all(self) -> dict:
        """Run all extraction methods and return complete data."""
        self.extract_policyholder()
        self.extract_policy_details()
        self.extract_broker()
        self.extract_premium_summary()
        self.extract_sections()
        self.extract_general_endorsements()
        self.extract_first_amounts_payable()
        return self.data
    
    def extract_policyholder(self) -> dict:
        """Extract policyholder details."""
        section = self._find_section("POLICYHOLDER DETAILS", ["POLICY DETAILS", "BROKER DETAILS"])
        if not section:
            return {}
        
        holder = {
            "name": extract_field_value(section, "Policyholder"),
            "business_description": extract_field_value(section, "Business description"),
            "vat_number": extract_field_value(section, "Vat number"),
            "company_registration_number": extract_field_value(section, "Company registration number"),
        }
        
        # Extract addresses
        physical_match = re.search(
            r'Physical address\s*(.+?)(?=Postal address|Contact details|$)',
            section, re.DOTALL | re.IGNORECASE
        )
        if physical_match:
            holder["physical_address"] = parse_address(physical_match.group(1))
        
        postal_match = re.search(
            r'Postal address\s*(.+?)(?=Contact details|Work|$)',
            section, re.DOTALL | re.IGNORECASE
        )
        if postal_match:
            holder["postal_address"] = parse_address(postal_match.group(1))
        
        # Contact details
        holder["contact_details"] = {
            "work_phone": extract_field_value(section, "Work"),
            "home_phone": extract_field_value(section, "Home"),
            "cell_phone": extract_field_value(section, "Cell"),
            "fax": extract_field_value(section, "Fax"),
            "email": extract_field_value(section, "Email")
        }
        
        self.data["policyholder"] = holder
        return holder
    
    def extract_policy_details(self) -> dict:
        """Extract policy details."""
        section = self._find_section("POLICY DETAILS", ["BROKER DETAILS", "PREMIUM"])
        if not section:
            return {}
        
        details = {
            "insurer_name": extract_field_value(section, "Insurer"),
            "policy_number": extract_field_value(section, "Policy number"),
            "policy_type": extract_field_value(section, "Type of policy"),
            "inception_date": parse_date(extract_field_value(section, "Inception date") or ""),
            "renewal_date": parse_date(extract_field_value(section, "Renewal date") or ""),
            "transaction_effective_date": parse_date(extract_field_value(section, "Transaction effective date") or ""),
            "transaction_reason": extract_field_value(section, "Transaction reason"),
            "endorsement_description": extract_field_value(section, "Endorsement Description"),
            "territorial_limits": extract_field_value(section, "Territorial Limits"),
            "print_date": parse_date(extract_field_value(section, "Print date") or "")
        }
        
        # Extract period of insurance
        period_match = re.search(
            r'Period of insurance\s*(?:From\s*)?(\d{2}/\d{2}/\d{4})\s*to\s*(\d{2}/\d{2}/\d{4})',
            section, re.IGNORECASE
        )
        if period_match:
            details["period_of_insurance"] = {
                "from_date": parse_date(period_match.group(1)),
                "to_date": parse_date(period_match.group(2))
            }
        
        self.data["policy_details"] = details
        return details
    
    def extract_broker(self) -> dict:
        """Extract broker details."""
        section = self._find_section("BROKER DETAILS", ["INSURER DETAILS", "PREMIUM"])
        if not section:
            return None
        
        broker = {
            "company_name": extract_field_value(section, "Company"),
            "branch": extract_field_value(section, "Branch"),
            "broker_name": extract_field_value(section, "Broker"),
            "company_registration_number": extract_field_value(section, "Company registration number"),
            "vat_number": extract_field_value(section, "VAT number"),
            "fsp_number": extract_field_value(section, "Licence Number") or extract_field_value(section, "FSB/FSP number"),
            "contact_phone": extract_field_value(section, "Business"),
            "fax": extract_field_value(section, "Fax"),
            "email": extract_field_value(section, "Email")
        }
        
        self.data["broker"] = broker
        return broker
    
    def extract_premium_summary(self) -> dict:
        """Extract premium summary."""
        section = self._find_section("PREMIUM SUMMARY", ["GENERAL ENDORSEMENTS", "FIRE SECTION"])
        if not section:
            return {}
        
        summary = {
            "currency": "ZAR",
            "premium_frequency": self.data.get("policy_details", {}).get("policy_type", "MONTHLY"),
            "section_premiums": [],
            "subtotal": None,
            "sasria_total": None,
            "broker_fee": None,
            "total_premium": None,
            "vat_inclusive": True,
            "broker_commission": {}
        }
        
        # Extract section premiums
        sections = ["Fire", "Goods in Transit", "Business All Risks", "Accidental damage",
                   "Combined liability", "Motor specified", "Theft", "Money", "Glass"]
        
        for sec_name in sections:
            pattern = rf'{re.escape(sec_name)}\s+(?:Yes|No)\s+R\s*([\d\s,\.]+)'
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                summary["section_premiums"].append({
                    "section_name": sec_name,
                    "is_selected": "Yes" in match.group(0),
                    "premium_amount": parse_currency(match.group(1))
                })
        
        # Extract totals
        subtotal_match = re.search(r'Sub\s*Total\s+R?\s*([\d\s,\.]+)', section)
        if subtotal_match:
            summary["subtotal"] = parse_currency(subtotal_match.group(1))
        
        sasria_match = re.search(r'Sasria\s+R?\s*([\d\s,\.]+)', section)
        if sasria_match:
            summary["sasria_total"] = parse_currency(sasria_match.group(1))
        
        broker_fee_match = re.search(r'Broker Fee\s+R?\s*([\d\s,\.]+)', section)
        if broker_fee_match:
            summary["broker_fee"] = parse_currency(broker_fee_match.group(1))
        
        total_match = re.search(r'TOTAL\s+R?\s*([\d\s,\.]+)', section)
        if total_match:
            summary["total_premium"] = parse_currency(total_match.group(1))
        
        # Extract commission info
        comm_match = re.search(r'broker commission of R\s*([\d\s,\.]+)', section)
        if comm_match:
            summary["broker_commission"]["total_amount"] = parse_currency(comm_match.group(1))
        
        motor_rate_match = re.search(r'motor classes is (\d+(?:\.\d+)?)\s*%', section)
        if motor_rate_match:
            summary["broker_commission"]["motor_rate_percent"] = float(motor_rate_match.group(1))
        
        non_motor_rate_match = re.search(r'non-motor classes is (\d+(?:\.\d+)?)\s*%', section)
        if non_motor_rate_match:
            summary["broker_commission"]["non_motor_rate_percent"] = float(non_motor_rate_match.group(1))
        
        self.data["premium_summary"] = summary
        return summary
    
    def extract_sections(self) -> list:
        """Extract all insurance sections."""
        section_patterns = [
            ("FIRE SECTION", "FIRE"),
            ("GOODS IN TRANSIT SECTION", "GOODS_IN_TRANSIT"),
            ("BUSINESS ALL RISKS SECTION", "BUSINESS_ALL_RISKS"),
            ("ACCIDENTAL DAMAGE SECTION", "ACCIDENTAL_DAMAGE"),
            ("COMBINED LIABILITY SECTION", "COMBINED_LIABILITY"),
            ("MOTOR SPECIFIED SECTION", "MOTOR_SPECIFIED"),
            ("MOTOR SPECIFIED SUMMARY", "MOTOR_SPECIFIED"),
        ]
        
        for pattern, section_type in section_patterns:
            if pattern in self.text.upper():
                section_data = self._extract_section(pattern, section_type)
                if section_data:
                    # Check if section already exists
                    existing = next((s for s in self.data["sections"] 
                                   if s["section_type"] == section_type), None)
                    if existing:
                        # Merge items
                        existing["items"].extend(section_data.get("items", []))
                    else:
                        self.data["sections"].append(section_data)
        
        # Extract motor vehicles separately
        self._extract_motor_vehicles()
        
        return self.data["sections"]
    
    def _extract_section(self, header: str, section_type: str) -> dict:
        """Extract a specific section."""
        section_text = self._find_section(header, [
            "FIRE SECTION", "GOODS IN TRANSIT", "BUSINESS ALL RISKS",
            "ACCIDENTAL DAMAGE", "COMBINED LIABILITY", "MOTOR SPECIFIED",
            "GENERAL ENDORSEMENTS", "SCHEDULE OF STANDARD"
        ])
        
        if not section_text:
            return None
        
        section_data = {
            "section_type": section_type,
            "section_name": header.replace(" SECTION", "").title(),
            "effective_date": None,
            "risk_address": None,
            "total_section_premium": None,
            "items": [],
            "additional_perils": [],
            "section_endorsements": []
        }
        
        # Extract effective date
        eff_match = re.search(r'Effective Date\s+(\d{1,2}\s+\w+\s+\d{4}|\d{2}/\d{2}/\d{4})', section_text)
        if eff_match:
            section_data["effective_date"] = parse_date(eff_match.group(1))
        
        # Extract risk address
        addr_match = re.search(r'Physical Location\s+(.+?)(?=Total|Construction|Details|$)', section_text, re.DOTALL)
        if addr_match:
            section_data["risk_address"] = clean_text(addr_match.group(1))
            
            # Add to risk_addresses if not already present
            if section_data["risk_address"]:
                existing_addrs = [a["full_address"] for a in self.data["risk_addresses"]]
                if section_data["risk_address"] not in existing_addrs:
                    self.data["risk_addresses"].append({
                        "address_id": f"addr_{len(self.data['risk_addresses']) + 1}",
                        "full_address": section_data["risk_address"],
                        "applicable_sections": [section_type]
                    })
        
        # Extract total section premium
        premium_match = re.search(r'Total Section Premium\s+R\s*([\d\s,\.]+)', section_text)
        if premium_match:
            section_data["total_section_premium"] = parse_currency(premium_match.group(1))
        
        # Extract items based on section type
        if section_type == "FIRE":
            section_data["items"] = self._extract_fire_items(section_text)
        elif section_type == "GOODS_IN_TRANSIT":
            section_data["items"] = self._extract_transit_items(section_text)
        elif section_type == "BUSINESS_ALL_RISKS":
            section_data["items"] = self._extract_bar_items(section_text)
        elif section_type == "COMBINED_LIABILITY":
            section_data["items"] = self._extract_liability_items(section_text)
            # Extract retroactive date
            retro_match = re.search(r'Retroactive Date\s+(\d{2}/\d{2}/\d{4})', section_text)
            if retro_match:
                section_data["section_specific_data"] = {
                    "retroactive_date": parse_date(retro_match.group(1)),
                    "basis_of_cover": "Claims Made"
                }
        
        # Extract additional perils
        section_data["additional_perils"] = self._extract_additional_perils(section_text)
        
        return section_data
    
    def _extract_fire_items(self, section_text: str) -> list:
        """Extract items from fire section."""
        items = []

        # Pattern for fire items: Description, Column Ref, Sum Insured, Premium
        item_pattern = r'(Buildings as defined|Stock as defined|Miscellaneous Items as defined)\s+(?:R\s*)?([\d\s,\.]+)\s+(?:R\s*)?([\d\s,\.]+)\s*\n([^\n]+)'

        for match in re.finditer(item_pattern, section_text, re.IGNORECASE):
            sum_result = parse_sum_insured(match.group(2))
            item = {
                "category": match.group(1),
                "description": match.group(4).strip(),
                "sum_insured": sum_result["value"],
                "sum_insured_text": sum_result["text"],
                "sum_insured_is_text_based": sum_result["is_text_based"] or None,
                "basis_of_valuation": sum_result["basis_of_valuation"],
                "premium": parse_currency(match.group(3))
            }
            items.append(item)

        # Also try simpler pattern
        simple_pattern = r'([A-Z][^R\n]+?)\s+(\d)\s+R\s*([\d\s,\.]+)\s+R\s*([\d\s,\.]+)'
        for match in re.finditer(simple_pattern, section_text):
            desc = match.group(1).strip()
            if len(desc) > 5 and not any(d["description"] == desc for d in items):
                sum_result = parse_sum_insured(match.group(4))
                item = {
                    "description": desc,
                    "column_reference": match.group(2),
                    "premium": parse_currency(match.group(3)),
                    "sum_insured": sum_result["value"],
                    "sum_insured_text": sum_result["text"],
                    "sum_insured_is_text_based": sum_result["is_text_based"] or None,
                    "basis_of_valuation": sum_result["basis_of_valuation"]
                }
                items.append(item)

        return items
    
    def _extract_transit_items(self, section_text: str) -> list:
        """Extract items from goods in transit section."""
        items = []

        # Extract sum insured and premium
        sum_match = re.search(r'R\s*([\d\s,\.]+)\s+R\s*([\d\s,\.]+)\s*(?:\n|Sasria)', section_text)
        if sum_match:
            sum_result = parse_sum_insured(sum_match.group(1))
            item = {
                "description": "Goods in Transit",
                "sum_insured": sum_result["value"],
                "sum_insured_text": sum_result["text"],
                "sum_insured_is_text_based": sum_result["is_text_based"] or None,
                "basis_of_valuation": sum_result["basis_of_valuation"],
                "premium": parse_currency(sum_match.group(2))
            }

            # Check for livestock inclusion
            if "livestock" in section_text.lower():
                item["additional_notes"] = "Including Livestock"

            items.append(item)

        return items
    
    def _extract_bar_items(self, section_text: str) -> list:
        """Extract items from Business All Risks section."""
        items = []

        # Pattern for BAR items with serial numbers
        item_blocks = re.split(r'(?=Description\s+Sum Insured|(?:Make:|Model:|Serial number))', section_text)

        for block in item_blocks:
            if "R" in block and ("KVA" in block or "Generator" in block or "VSD" in block):
                item = {
                    "description": None,
                    "sum_insured": None,
                    "sum_insured_text": None,
                    "sum_insured_is_text_based": None,
                    "basis_of_valuation": None,
                    "premium": None
                }

                # Extract description
                desc_match = re.search(r'(\d+\s*KVA[^\n]+|VSD[^\n]+)', block)
                if desc_match:
                    item["description"] = desc_match.group(1).strip()

                # Extract sum insured and premium
                amounts = re.findall(r'R\s*([\d\s,\.]+)', block)
                if len(amounts) >= 2:
                    sum_result = parse_sum_insured(f"R {amounts[0]}")
                    item["sum_insured"] = sum_result["value"]
                    item["sum_insured_text"] = sum_result["text"]
                    item["sum_insured_is_text_based"] = sum_result["is_text_based"] or None
                    item["basis_of_valuation"] = sum_result["basis_of_valuation"]
                    item["premium"] = parse_currency(amounts[1])

                # Check for text-based sum insured in the block
                for pattern in ["Agreed Value", "Retail Value", "Market Value", "Replacement Value"]:
                    if re.search(pattern, block, re.IGNORECASE):
                        item["sum_insured_is_text_based"] = True
                        item["sum_insured_text"] = pattern
                        if "agreed" in pattern.lower():
                            item["basis_of_valuation"] = "AGREED_VALUE"
                        elif "retail" in pattern.lower():
                            item["basis_of_valuation"] = "RETAIL_VALUE"
                        elif "market" in pattern.lower():
                            item["basis_of_valuation"] = "MARKET_VALUE"
                        elif "replacement" in pattern.lower():
                            item["basis_of_valuation"] = "REPLACEMENT_VALUE"
                        break

                # Extract serial number
                serial_match = re.search(r'Serial number/IMEI number:\s*([^\n]+)', block)
                if serial_match:
                    item["serial_number"] = serial_match.group(1).strip()

                if item["description"]:
                    items.append(item)

        return items
    
    def _extract_liability_items(self, section_text: str) -> list:
        """Extract items from liability section."""
        items = []

        # Extract public liability
        pl_match = re.search(r'Public Liability[^\n]*\n[^\n]*R\s*([\d\s,\.]+)\s+R\s*([\d\s,\.]+)', section_text)
        if pl_match:
            sum_result = parse_sum_insured(pl_match.group(1))
            items.append({
                "description": "Public Liability",
                "sum_insured": sum_result["value"],
                "sum_insured_text": sum_result["text"],
                "sum_insured_is_text_based": sum_result["is_text_based"] or None,
                "basis_of_valuation": sum_result["basis_of_valuation"],
                "premium": parse_currency(pl_match.group(2))
            })

        return items
    
    def _extract_motor_vehicles(self):
        """Extract motor vehicle details."""
        motor_text = self._find_section("MOTOR SPECIFIED SECTION", ["AGRICULTURE POLICY WORDING", "SCHEDULE OF STANDARD"])
        if not motor_text:
            return
        
        vehicles = []
        
        # Split by vehicle blocks (look for registration patterns)
        vehicle_blocks = re.split(r'(?=Registration\s*\n|Details of Vehicle)', motor_text)
        
        for block in vehicle_blocks:
            if len(block) < 50:
                continue
            
            vehicle = self._parse_vehicle_block(block)
            if vehicle and vehicle.get("description"):
                vehicles.append(vehicle)
        
        if vehicles:
            self.data["motor_section"] = {"vehicles": vehicles}
            
            # Also add to sections
            motor_section = next((s for s in self.data["sections"] 
                                 if s["section_type"] == "MOTOR_SPECIFIED"), None)
            if motor_section:
                motor_section["items"] = vehicles
    
    def _parse_vehicle_block(self, block: str) -> dict:
        """Parse a single vehicle block."""
        vehicle = {
            "description": None,
            "year": None,
            "make": None,
            "model": None,
            "registration_number": None,
            "vin_number": None,
            "engine_number": None,
            "mcgruther_code": None,
            "description_of_use": None,
            "type_of_cover": None,
            "sum_insured": None,
            "sum_insured_text": None,
            "sum_insured_is_text_based": None,
            "basis_of_valuation": None,
            "premium": None,
            "sasria_premium": None,
            "extras": [],
            "additional_perils": []
        }
        
        # Extract registration number
        reg_match = re.search(r'([A-Z]{2,3}\d{3,4}[A-Z]{2}|TBA)', block)
        if reg_match:
            vehicle["registration_number"] = parse_registration_number(reg_match.group(1))
        
        # Extract VIN
        vin_match = re.search(r'VIN Number\s*([A-Z0-9]{17})', block, re.IGNORECASE)
        if vin_match:
            vehicle["vin_number"] = vin_match.group(1)
        
        # Extract engine number
        engine_match = re.search(r'Engine Number\s*([A-Z0-9]+)', block, re.IGNORECASE)
        if engine_match:
            vehicle["engine_number"] = engine_match.group(1)
        
        # Extract description (year make model)
        desc_match = re.search(r'(\d{4}\s+[A-Z][A-Z\-\s\d/]+(?:T/T|P/U|S/C|C/C|TRACTOR|BACKHOE|TRAILER|TIPPER)[^\n]*)', block, re.IGNORECASE)
        if desc_match:
            vehicle["description"] = desc_match.group(1).strip()
            parsed = parse_vehicle_description(vehicle["description"])
            vehicle.update(parsed)
        
        # Extract cover type
        if "Comprehensive" in block:
            vehicle["type_of_cover"] = "COMPREHENSIVE"
        elif "Third Party, Fire and Theft" in block:
            vehicle["type_of_cover"] = "THIRD_PARTY_FIRE_THEFT"
        elif "Third Party" in block:
            vehicle["type_of_cover"] = "THIRD_PARTY_ONLY"
        
        # Extract use
        if "Private/Business" in block:
            vehicle["description_of_use"] = "PRIVATE/BUSINESS"
        elif "Agricultural only" in block:
            vehicle["description_of_use"] = "AGRICULTURAL"
        
        # Extract sum insured (may be numeric or text-based like "Agreed Value", "Retail Value")
        sum_match = re.search(r'(?:Sum\s*Insured|Value)\s*[:\n]\s*([^\n]+)', block, re.IGNORECASE)
        if sum_match:
            sum_result = parse_sum_insured(sum_match.group(1))
            vehicle["sum_insured"] = sum_result["value"]
            vehicle["sum_insured_text"] = sum_result["text"]
            vehicle["sum_insured_is_text_based"] = sum_result["is_text_based"] or None
            if sum_result["basis_of_valuation"]:
                vehicle["basis_of_valuation"] = sum_result["basis_of_valuation"]

        # Also check for Agreed Value / Retail Value patterns elsewhere in block
        if not vehicle["sum_insured_is_text_based"]:
            for pattern in ["Agreed Value", "Retail Value", "Market Value"]:
                if re.search(pattern, block, re.IGNORECASE):
                    vehicle["sum_insured_is_text_based"] = True
                    vehicle["sum_insured_text"] = pattern
                    if "agreed" in pattern.lower():
                        vehicle["basis_of_valuation"] = "AGREED_VALUE"
                    elif "retail" in pattern.lower():
                        vehicle["basis_of_valuation"] = "RETAIL_VALUE"
                    elif "market" in pattern.lower():
                        vehicle["basis_of_valuation"] = "MARKET_VALUE"
                    break

        # Extract premium
        premium_match = re.search(r'Premium\s*\n[^\n]*R\s*([\d\s,\.]+)', block)
        if premium_match:
            vehicle["premium"] = parse_currency(premium_match.group(1))

        # Extract SASRIA
        sasria_match = re.search(r'Sasria\s+R\s*([\d\s,\.]+)', block)
        if sasria_match:
            vehicle["sasria_premium"] = parse_currency(sasria_match.group(1))
        
        # Extract extras from Additional Notes
        extras_match = re.search(r'Additional Notes\s*\n(.+?)(?=Registration|Details of|$)', block, re.DOTALL)
        if extras_match:
            extras_text = extras_match.group(1)
            for extra_match in re.finditer(r'([A-Za-z\s&]+)\s+R\s*([\d\s,\.]+)', extras_text):
                vehicle["extras"].append({
                    "description": extra_match.group(1).strip(),
                    "value": parse_currency(extra_match.group(2))
                })
        
        return vehicle
    
    def _extract_additional_perils(self, section_text: str) -> list:
        """Extract additional perils/extensions."""
        perils = []
        
        # Pattern for Yes/No perils table
        peril_pattern = r'([A-Za-z\s\-\(\)]+)\s+(Yes|No)\s*(?:R\s*([\d\s,\.]+))?'
        
        for match in re.finditer(peril_pattern, section_text):
            name = match.group(1).strip()
            # Filter out headers and noise
            if len(name) > 5 and name not in ["Description", "Limit of Indemnity", "Premium"]:
                peril = {
                    "peril_name": name,
                    "is_included": match.group(2).lower() == "yes",
                    "limit_of_indemnity": parse_currency(match.group(3)) if match.group(3) else None
                }
                perils.append(peril)
        
        return perils
    
    def extract_general_endorsements(self) -> list:
        """Extract general policy endorsements."""
        endorsements = []
        
        # Find GENERAL ENDORSEMENTS section
        section = self._find_section("GENERAL ENDORSEMENTS", ["FIRE SECTION", "PREMIUM SUMMARY"])
        if section:
            # Split by endorsement headers
            endo_blocks = re.split(r'(?=ENDORSEMENT FORMING PART|GENERAL EXCEPTION|GENERAL EXCLUSION)', section)
            
            for block in endo_blocks:
                if len(block) > 50:
                    # Extract endorsement name
                    name_match = re.search(r'^([A-Z][A-Z\s\-]+)(?:\n|:)', block)
                    if name_match:
                        endo = {
                            "endorsement_name": name_match.group(1).strip(),
                            "endorsement_text": clean_text(block[name_match.end():])[:500],  # Limit text length
                            "effective_date": None
                        }
                        
                        # Extract effective date if present
                        date_match = re.search(r'(?:EFFECT|effective)\s+(?:FROM\s+)?(\d{2}\s+\w+\s+\d{4}|\d{2}/\d{2}/\d{4})', block, re.IGNORECASE)
                        if date_match:
                            endo["effective_date"] = parse_date(date_match.group(1))
                        
                        endorsements.append(endo)
        
        self.data["general_endorsements"] = endorsements
        return endorsements
    
    def extract_first_amounts_payable(self) -> dict:
        """Extract first amounts payable (excesses)."""
        fap = {}
        
        section = self._find_section("SCHEDULE OF STANDARD FIRST AMOUNTS", ["DISCLOSURE NOTICE", "Sasria SOC"])
        if not section:
            return fap
        
        # Split by section headers
        current_section = None
        current_items = []
        
        for line in section.split('\n'):
            # Check for section header
            section_match = re.match(r'^(Fire|Motor|Theft|Glass|Money|Goods|Business|Combined|Electronic)', line, re.IGNORECASE)
            if section_match:
                if current_section and current_items:
                    fap[current_section] = current_items
                current_section = section_match.group(1)
                current_items = []
            elif current_section:
                # Try to parse FAP entry
                fap_match = re.match(r'(.+?)\s+(\d+)%\s+R\s*([\d\s,\.]+)\s+(.+)?', line)
                if fap_match:
                    entry = {
                        "description": fap_match.group(1).strip(),
                        "percentage_of_claim": float(fap_match.group(2)),
                        "minimum_amount": parse_currency(fap_match.group(3)),
                        "maximum_amount": None
                    }
                    current_items.append(entry)
        
        if current_section and current_items:
            fap[current_section] = current_items
        
        self.data["first_amounts_payable"] = fap
        return fap
    
    def _find_section(self, start_marker: str, end_markers: list) -> Optional[str]:
        """Find a section of text between markers."""
        start_idx = self.text.upper().find(start_marker.upper())
        if start_idx == -1:
            return None
        
        end_idx = len(self.text)
        for marker in end_markers:
            idx = self.text.upper().find(marker.upper(), start_idx + len(start_marker))
            if idx != -1 and idx < end_idx:
                end_idx = idx
        
        return self.text[start_idx:end_idx]


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file."""
    try:
        import pdfplumber
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except ImportError:
        print("Warning: pdfplumber not installed. Trying PyPDF2...")
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            raise ImportError("Please install pdfplumber or PyPDF2: pip install pdfplumber")


def main():
    parser = argparse.ArgumentParser(
        description="Extract insurance policy data to JSON format"
    )
    parser.add_argument("input_file", help="Input PDF or text file")
    parser.add_argument("-o", "--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--format", choices=["pretty", "compact"], default="pretty",
                       help="JSON output format")
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    if input_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(str(input_path))
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
    
    # Extract data
    extractor = PolicyExtractor(text, input_path.name)
    data = extractor.extract_all()
    
    # Output
    pretty = args.format == "pretty"
    json_output = to_json(data, pretty=pretty)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"Extracted data saved to: {args.output}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
