"""
Data Expansion Engine for Tilores Entity Processing
Normalizes, enriches, and provides insights on customer data
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class DataExpansionEngine:
    """Process and enhance Tilores entity data with normalization and insights"""
    
    def __init__(self, enable_pii_detection: bool = True):
        """
        Initialize the data expansion engine
        
        Args:
            enable_pii_detection: Whether to detect PII in records
        """
        self.enable_pii_detection = enable_pii_detection
        
        # PII field patterns
        self.pii_fields = {
            "EMAIL", "PHONE_EXTERNAL", "PHONE", "MOBILE_PHONE",
            "SOCIAL_SECURITY_NUMBER", "SSN", "DATE_OF_BIRTH", "DOB",
            "MAILING_STREET", "HOME_ADDRESS", "BILLING_ADDRESS",
            "CREDIT_CARD", "BANK_ACCOUNT", "ROUTING_NUMBER"
        }
        
        # Fields to normalize
        self.phone_fields = {"PHONE_EXTERNAL", "PHONE", "MOBILE_PHONE", "HOME_PHONE", "WORK_PHONE"}
        self.email_fields = {"EMAIL", "CONTACT_EMAIL", "BUSINESS_EMAIL", "PERSONAL_EMAIL"}
        self.name_fields = {"FIRST_NAME", "LAST_NAME", "FULL_NAME", "MIDDLE_NAME"}
        
    def expand_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand a single entity with normalization and insights
        
        Args:
            entity: Entity data from Tilores
            
        Returns:
            Enhanced entity with metadata and insights
        """
        if not entity:
            return entity
            
        expanded = entity.copy()
        
        # Add expansion metadata
        expanded["_expansion"] = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # Process records if available
        if "records" in entity and entity["records"]:
            expanded["records"] = self.process_records(entity["records"])
            expanded["_expansion"]["records_processed"] = len(entity["records"])
        
        # Generate insights
        expanded["_insights"] = self.generate_insights(expanded)
        
        # Add data quality score
        expanded["_data_quality"] = self.calculate_data_quality(expanded)
        
        return expanded
    
    def process_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and normalize records within an entity
        
        Args:
            records: List of records to process
            
        Returns:
            Processed records with normalization
        """
        processed = []
        
        for record in records:
            processed_record = record.copy()
            
            # Normalize phone numbers
            for field in self.phone_fields:
                if field in processed_record and processed_record[field]:
                    processed_record[field] = self.normalize_phone(processed_record[field])
            
            # Normalize emails
            for field in self.email_fields:
                if field in processed_record and processed_record[field]:
                    processed_record[field] = self.normalize_email(processed_record[field])
            
            # Normalize names
            for field in self.name_fields:
                if field in processed_record and processed_record[field]:
                    processed_record[field] = self.normalize_name(processed_record[field])
            
            # Add record metadata
            processed_record["_metadata"] = {
                "normalized": True,
                "has_pii": self.detect_pii(processed_record) if self.enable_pii_detection else None,
                "field_count": len([k for k, v in processed_record.items() 
                                   if v is not None and not k.startswith("_")])
            }
            
            processed.append(processed_record)
        
        return processed
    
    def normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number to consistent format
        
        Args:
            phone: Phone number string
            
        Returns:
            Normalized phone number
        """
        if not phone:
            return phone
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        
        # Handle US phone numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        elif len(digits) == 7:
            return f"{digits[:3]}-{digits[3:]}"
        
        # Return original if can't normalize
        return phone
    
    def normalize_email(self, email: str) -> str:
        """
        Normalize email address
        
        Args:
            email: Email address string
            
        Returns:
            Normalized email
        """
        if not email:
            return email
        
        # Convert to lowercase and strip whitespace
        normalized = str(email).lower().strip()
        
        # Remove any mailto: prefix
        if normalized.startswith("mailto:"):
            normalized = normalized[7:]
        
        # Basic validation
        if '@' in normalized and '.' in normalized.split('@')[1]:
            return normalized
        
        return email  # Return original if invalid
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize name to proper case
        
        Args:
            name: Name string
            
        Returns:
            Normalized name
        """
        if not name:
            return name
        
        # Strip whitespace and convert to title case
        normalized = str(name).strip()
        
        # Handle special cases (McDonald, O'Brien, etc.)
        words = normalized.split()
        normalized_words = []
        
        for word in words:
            if word.upper() in ['II', 'III', 'IV', 'JR', 'SR', 'PHD', 'MD']:
                normalized_words.append(word.upper())
            elif word.lower() in ['de', 'von', 'van', 'der', 'la', 'le']:
                normalized_words.append(word.lower())
            elif "'" in word:  # Handle O'Brien, D'Angelo
                parts = word.split("'")
                normalized_words.append("'".join(p.capitalize() for p in parts))
            elif word.startswith("Mc") and len(word) > 2:
                normalized_words.append(f"Mc{word[2:].capitalize()}")
            else:
                normalized_words.append(word.capitalize())
        
        return ' '.join(normalized_words)
    
    def detect_pii(self, record: Dict[str, Any]) -> bool:
        """
        Detect if record contains PII
        
        Args:
            record: Record to check
            
        Returns:
            True if PII detected
        """
        for field in record:
            if field.upper() in self.pii_fields and record[field]:
                return True
        return False
    
    def generate_insights(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights about an entity
        
        Args:
            entity: Entity to analyze
            
        Returns:
            Dictionary of insights
        """
        insights = {
            "has_contact_info": False,
            "has_financial_data": False,
            "primary_identifier": None,
            "record_count": 0,
            "unique_emails": [],
            "unique_phones": [],
            "data_completeness": 0.0
        }
        
        if "records" not in entity or not entity["records"]:
            return insights
        
        records = entity["records"]
        insights["record_count"] = len(records)
        
        # Collect unique identifiers
        emails = set()
        phones = set()
        all_fields = set()
        populated_fields = set()
        
        for record in records:
            for field, value in record.items():
                if field.startswith("_"):
                    continue
                    
                all_fields.add(field)
                if value is not None and value != "":
                    populated_fields.add(field)
                    
                    # Collect emails
                    if field.upper() in self.email_fields and value:
                        emails.add(str(value).lower())
                    
                    # Collect phones
                    if field.upper() in self.phone_fields and value:
                        phones.add(re.sub(r'\D', '', str(value)))
        
        # Set insights
        insights["unique_emails"] = list(emails)
        insights["unique_phones"] = list(phones)
        insights["has_contact_info"] = bool(emails or phones)
        
        # Check for financial fields
        financial_indicators = {
            "CREDIT_AMOUNT", "TRANSACTION_AMOUNT", "BALANCE",
            "PAYMENT", "CREDIT_SCORE", "LOAN", "MORTGAGE"
        }
        insights["has_financial_data"] = bool(financial_indicators & populated_fields)
        
        # Determine primary identifier
        if emails:
            insights["primary_identifier"] = "email"
        elif phones:
            insights["primary_identifier"] = "phone"
        elif "CLIENT_ID" in populated_fields:
            insights["primary_identifier"] = "client_id"
        else:
            insights["primary_identifier"] = "unknown"
        
        # Calculate completeness
        if all_fields:
            insights["data_completeness"] = len(populated_fields) / len(all_fields)
        
        return insights
    
    def calculate_data_quality(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate data quality metrics
        
        Args:
            entity: Entity to analyze
            
        Returns:
            Data quality metrics
        """
        quality = {
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        if "_insights" not in entity:
            return quality
        
        insights = entity["_insights"]
        score = 0.0
        max_score = 100.0
        
        # Check for contact info (30 points)
        if insights.get("has_contact_info"):
            score += 30
        else:
            quality["issues"].append("Missing contact information")
            quality["recommendations"].append("Add email or phone number")
        
        # Check data completeness (40 points)
        completeness = insights.get("data_completeness", 0.0)
        score += completeness * 40
        if completeness < 0.5:
            quality["issues"].append(f"Low data completeness: {completeness:.1%}")
            quality["recommendations"].append("Fill in missing fields")
        
        # Check for duplicate identifiers (20 points)
        if len(insights.get("unique_emails", [])) <= 1:
            score += 10
        else:
            quality["issues"].append("Multiple email addresses found")
        
        if len(insights.get("unique_phones", [])) <= 1:
            score += 10
        else:
            quality["issues"].append("Multiple phone numbers found")
        
        # Check for primary identifier (10 points)
        if insights.get("primary_identifier") != "unknown":
            score += 10
        else:
            quality["issues"].append("No primary identifier found")
            quality["recommendations"].append("Add client ID, email, or phone")
        
        quality["score"] = round(score, 2)
        
        # Add quality rating
        if score >= 80:
            quality["rating"] = "excellent"
        elif score >= 60:
            quality["rating"] = "good"
        elif score >= 40:
            quality["rating"] = "fair"
        else:
            quality["rating"] = "poor"
        
        return quality


# Global instance for convenience
data_expander = DataExpansionEngine()