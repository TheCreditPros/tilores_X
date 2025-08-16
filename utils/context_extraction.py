"""
Advanced Customer Context Extraction Utilities
Extracted from tilores-unified-api for enhanced query routing
"""

import re
from typing import Any, Dict, List, Optional


class IDPatterns:
    """Centralized ID pattern extraction utilities"""

    @staticmethod
    def extract_client_id(text: str) -> Optional[str]:
        """Extract client ID (numeric pattern like 1881899)"""
        patterns = [
            r"\b(\d{7,10})\b",  # 7-10 digit number
            r"client[_\s]?id[:\s]+(\d{7,10})",
            r"customer[_\s]?id[:\s]+(\d{7,10})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        return None

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_salesforce_id(text: str) -> Optional[str]:
        """Extract Salesforce Contact ID (003Ux... format)"""
        # Salesforce Contact IDs start with 003 and are 15 or 18 chars
        pattern = r"\b003[A-Za-z0-9]{12,15}\b"
        match = re.search(pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract and normalize phone number"""
        # Remove all non-digit characters
        digits = re.sub(r"\D", "", text)

        # Look for 10-11 digit phone numbers
        if len(digits) >= 10:
            if len(digits) == 11 and digits[0] == "1":
                return digits  # US number with country code
            elif len(digits) == 10:
                return "1" + digits  # Add US country code

        # Try to find phone pattern in original text
        patterns = [
            r"(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})",
            r"(\b[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # Normalize the match
                phone = re.sub(r"\D", "", match.group(0))
                if len(phone) == 10:
                    return "1" + phone
                elif len(phone) == 11:
                    return phone

        return None


def extract_customer_context_from_messages(messages: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extract customer context from chat message history for follow-up queries.
    Prioritizes explicit info: client_id > email > phone > name

    Args:
        messages: List of chat messages with role and content

    Returns:
        Dictionary containing extracted customer identifiers
    """
    context = {}

    try:
        # Process messages in reverse order (most recent first)
        for msg in reversed(messages):
            # Skip if we already have all key identifiers
            if all(context.get(k) for k in ["client_id", "email"]):
                break

            # Check assistant messages for function calls
            if msg.get("role") == "assistant":
                # Check for function call results in content
                content = msg.get("content", "")
                if "customer_id" in content or "client_id" in content:
                    # Try to extract from structured responses
                    if not context.get("client_id"):
                        client_id = IDPatterns.extract_client_id(content)
                        if client_id:
                            context["client_id"] = client_id

            # Check user messages for explicit customer mentions
            if msg.get("role") == "user":
                content = msg.get("content", "")

                # Extract Salesforce Contact ID
                if not context.get("customer_id"):
                    customer_id = IDPatterns.extract_salesforce_id(content)
                    if customer_id:
                        context["customer_id"] = customer_id

                # Extract client ID
                if not context.get("client_id"):
                    client_id = IDPatterns.extract_client_id(content)
                    if client_id:
                        context["client_id"] = client_id

                # Extract email
                if not context.get("email"):
                    email = IDPatterns.extract_email(content)
                    if email:
                        context["email"] = email

                # Extract phone
                if not context.get("phone"):
                    phone = IDPatterns.extract_phone(content)
                    if phone:
                        context["phone"] = phone

                # Extract name (simple pattern)
                if not context.get("first_name"):
                    # Look for "find John Smith" or "customer John Smith" patterns
                    name_patterns = [
                        r"(?:find|search|lookup|get|show|customer|client)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)",
                        r"(?:name|called|named)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)",
                    ]
                    for pattern in name_patterns:
                        match = re.search(pattern, content)
                        if match:
                            context["first_name"] = match.group(1)
                            context["last_name"] = match.group(2)
                            break

    except Exception as e:
        print(f"⚠️ Error extracting customer context: {e}")

    return context


def parse_customer_query(query: str) -> Dict[str, Any]:
    """
    Parse a customer query to extract structured search parameters

    Args:
        query: User query string

    Returns:
        Dictionary of extracted parameters
    """
    params = {}

    # Extract all possible identifiers
    email = IDPatterns.extract_email(query)
    if email:
        params["email"] = email

    client_id = IDPatterns.extract_client_id(query)
    if client_id:
        params["client_id"] = client_id

    salesforce_id = IDPatterns.extract_salesforce_id(query)
    if salesforce_id:
        params["customer_id"] = salesforce_id

    phone = IDPatterns.extract_phone(query)
    if phone:
        params["phone"] = phone

    # Extract name if no other identifiers found
    if not params:
        # Simple name extraction
        name_match = re.search(r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b", query)
        if name_match:
            params["first_name"] = name_match.group(1)
            params["last_name"] = name_match.group(2)

    return params
