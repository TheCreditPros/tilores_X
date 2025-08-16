"""
Comprehensive unit tests for utils/context_extraction.py
Tests advanced customer context extraction utilities
"""

from unittest.mock import patch

# Import the module under test
from utils.context_extraction import (
    IDPatterns,
    extract_customer_context_from_messages,
    parse_customer_query
)


class TestIDPatterns:
    """Test the IDPatterns class static methods."""

    def test_extract_client_id_simple_pattern(self):
        """Test extracting client ID from simple numeric patterns."""
        # Test 7-digit ID
        assert IDPatterns.extract_client_id("Customer 1234567 needs help") == "1234567"

        # Test 8-digit ID
        assert IDPatterns.extract_client_id("The client 12345678 called") == "12345678"

        # Test 10-digit ID
        assert IDPatterns.extract_client_id("ID: 1234567890") == "1234567890"

    def test_extract_client_id_labeled_patterns(self):
        """Test extracting client ID from labeled patterns."""
        # Test "client id" pattern
        assert IDPatterns.extract_client_id("client id: 1881899") == "1881899"
        assert IDPatterns.extract_client_id("client_id 1881899") == "1881899"
        assert IDPatterns.extract_client_id("clientid:1881899") == "1881899"

        # Test "customer id" pattern
        assert IDPatterns.extract_client_id("customer id: 2345678") == "2345678"
        assert IDPatterns.extract_client_id("customer_id 2345678") == "2345678"

        # Test case insensitive
        assert IDPatterns.extract_client_id("CLIENT ID: 1881899") == "1881899"
        assert IDPatterns.extract_client_id("Customer ID 1881899") == "1881899"

    def test_extract_client_id_no_match(self):
        """Test client ID extraction when no match found."""
        assert IDPatterns.extract_client_id("No ID here") is None
        assert IDPatterns.extract_client_id("Short 123") is None  # Too short
        assert IDPatterns.extract_client_id("Too long 12345678901") is None  # Too long
        assert IDPatterns.extract_client_id("") is None

    def test_extract_email_valid(self):
        """Test extracting valid email addresses."""
        assert IDPatterns.extract_email("Contact john.doe@example.com") == "john.doe@example.com"
        assert IDPatterns.extract_email("Email: user+test@domain.co.uk") == "user+test@domain.co.uk"
        assert IDPatterns.extract_email("Send to test123@gmail.com please") == "test123@gmail.com"
        assert IDPatterns.extract_email("customer_email@company-name.org") == "customer_email@company-name.org"

    def test_extract_email_no_match(self):
        """Test email extraction when no valid email found."""
        assert IDPatterns.extract_email("No email here") is None
        assert IDPatterns.extract_email("invalid@") is None
        assert IDPatterns.extract_email("@invalid.com") is None
        assert IDPatterns.extract_email("not.an.email") is None
        assert IDPatterns.extract_email("") is None

    def test_extract_salesforce_id_valid(self):
        """Test extracting valid Salesforce Contact IDs."""
        assert IDPatterns.extract_salesforce_id("Contact ID: 003Ux00004c99SQ") == "003Ux00004c99SQ"
        assert IDPatterns.extract_salesforce_id("SF ID 003ABC123DEF456") == "003ABC123DEF456"
        # Test with exact 15-character ID (003 + 12 chars)
        assert IDPatterns.extract_salesforce_id("Find customer 003ABC123DEF456") == "003ABC123DEF456"

    def test_extract_salesforce_id_no_match(self):
        """Test Salesforce ID extraction when no match found."""
        assert IDPatterns.extract_salesforce_id("No SF ID here") is None
        assert IDPatterns.extract_salesforce_id("004Ux00004c99SQ") is None  # Wrong prefix
        assert IDPatterns.extract_salesforce_id("003Ux") is None  # Too short
        assert IDPatterns.extract_salesforce_id("") is None

    def test_extract_phone_10_digit(self):
        """Test extracting and normalizing 10-digit phone numbers."""
        assert IDPatterns.extract_phone("Call 5551234567") == "15551234567"
        assert IDPatterns.extract_phone("Phone: (555) 123-4567") == "15551234567"
        assert IDPatterns.extract_phone("555.123.4567") == "15551234567"
        assert IDPatterns.extract_phone("555 123 4567") == "15551234567"

    def test_extract_phone_11_digit(self):
        """Test extracting 11-digit phone numbers with country code."""
        assert IDPatterns.extract_phone("15551234567") == "15551234567"
        assert IDPatterns.extract_phone("1-555-123-4567") == "15551234567"
        assert IDPatterns.extract_phone("+1 555 123 4567") == "15551234567"

    def test_extract_phone_formatted(self):
        """Test extracting phone numbers with various formatting."""
        assert IDPatterns.extract_phone("(555) 123-4567") == "15551234567"
        assert IDPatterns.extract_phone("555-123-4567") == "15551234567"
        assert IDPatterns.extract_phone("+1 (555) 123-4567") == "15551234567"
        assert IDPatterns.extract_phone("1.555.123.4567") == "15551234567"

    def test_extract_phone_no_match(self):
        """Test phone extraction when no valid phone found."""
        assert IDPatterns.extract_phone("No phone here") is None
        assert IDPatterns.extract_phone("123") is None  # Too short
        # Test with text that has no 10+ digit sequences starting with valid patterns
        assert IDPatterns.extract_phone("abc def ghi") is None  # No digits
        assert IDPatterns.extract_phone("") is None

    def test_extract_phone_edge_cases(self):
        """Test phone extraction edge cases."""
        # Test exactly 10 digits
        text_with_10_digits = "abc1234567890def"
        result = IDPatterns.extract_phone(text_with_10_digits)
        assert result == "11234567890"

        # Test exactly 11 digits starting with 1
        text_with_11_digits = "abc11234567890def"
        result = IDPatterns.extract_phone(text_with_11_digits)
        assert result == "11234567890"


class TestExtractCustomerContextFromMessages:
    """Test the extract_customer_context_from_messages function."""

    def test_extract_context_empty_messages(self):
        """Test extracting context from empty message list."""
        result = extract_customer_context_from_messages([])
        assert result == {}

    def test_extract_context_no_identifiers(self):
        """Test extracting context when no identifiers present."""
        messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm fine, thank you!"}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result == {}

    def test_extract_context_client_id_from_user(self):
        """Test extracting client ID from user messages."""
        messages = [
            {"role": "user", "content": "Help me with client 1881899"},
            {"role": "assistant", "content": "I'll help you with that client."}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["client_id"] == "1881899"

    def test_extract_context_client_id_from_assistant(self):
        """Test extracting client ID from assistant responses."""
        messages = [
            {"role": "user", "content": "Find my customer"},
            {"role": "assistant", "content": "Found customer_id: 1881899 in system"}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["client_id"] == "1881899"

    def test_extract_context_email(self):
        """Test extracting email from messages."""
        messages = [
            {"role": "user", "content": "Look up john.doe@example.com"},
            {"role": "assistant", "content": "I'll search for that email."}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["email"] == "john.doe@example.com"

    def test_extract_context_salesforce_id(self):
        """Test extracting Salesforce Contact ID."""
        messages = [
            {"role": "user", "content": "Find contact 003Ux00004c99SQ"},
            {"role": "assistant", "content": "Searching for that contact."}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["customer_id"] == "003Ux00004c99SQ"

    def test_extract_context_phone(self):
        """Test extracting phone number."""
        messages = [
            {"role": "user", "content": "Customer with phone (555) 123-4567"},
            {"role": "assistant", "content": "I'll find that customer."}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["phone"] == "15551234567"

    def test_extract_context_names(self):
        """Test extracting customer names."""
        messages = [
            {"role": "user", "content": "Find customer John Smith"},
            {"role": "assistant", "content": "Searching for John Smith."}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["first_name"] == "John"
        assert result["last_name"] == "Smith"

    def test_extract_context_names_patterns(self):
        """Test extracting names with different patterns."""
        # Test "find" pattern
        messages = [{"role": "user", "content": "find Jane Doe"}]
        result = extract_customer_context_from_messages(messages)
        assert result["first_name"] == "Jane"
        assert result["last_name"] == "Doe"

        # Test "customer" pattern
        messages = [{"role": "user", "content": "customer named Bob Wilson"}]
        result = extract_customer_context_from_messages(messages)
        assert result["first_name"] == "Bob"
        assert result["last_name"] == "Wilson"

        # Test "lookup" pattern
        messages = [{"role": "user", "content": "lookup Alice Johnson"}]
        result = extract_customer_context_from_messages(messages)
        assert result["first_name"] == "Alice"
        assert result["last_name"] == "Johnson"

    def test_extract_context_multiple_identifiers(self):
        """Test extracting multiple types of identifiers."""
        messages = [
            {"role": "user", "content": "Find client 1881899 with email john@example.com"},
            {"role": "assistant", "content": "I found the customer."}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["client_id"] == "1881899"
        assert result["email"] == "john@example.com"

    def test_extract_context_priority_order(self):
        """Test that extraction respects priority order (most recent first)."""
        messages = [
            {"role": "user", "content": "Old client 1111111"},
            {"role": "user", "content": "Current client 1881899"}
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["client_id"] == "1881899"  # Most recent

    def test_extract_context_early_exit(self):
        """Test processing in reverse order (most recent first)."""
        messages = [
            {"role": "user", "content": "client 1881899 with email john@example.com"},
            {"role": "user", "content": "Another client 9999999"}  # More recent, processed first
        ]
        result = extract_customer_context_from_messages(messages)
        # Since processing in reverse order, the more recent client ID is found first
        assert result["client_id"] == "9999999"
        assert result["email"] == "john@example.com"

    def test_extract_context_malformed_messages(self):
        """Test handling malformed messages."""
        messages = [
            {"role": "user"},  # Missing content
            {"content": "No role here"},  # Missing role
            {"role": "user", "content": "client 1881899"}  # Valid message
        ]
        result = extract_customer_context_from_messages(messages)
        assert result["client_id"] == "1881899"

    def test_extract_context_exception_handling(self):
        """Test exception handling in context extraction."""
        # Test with invalid message structure that might cause exceptions
        invalid_messages = [
            None,
            {"role": "user", "content": "client 1881899"}
        ]

        with patch('builtins.print'):
            result = extract_customer_context_from_messages(invalid_messages)
            # Should handle gracefully and still extract from valid message
            assert result["client_id"] == "1881899"


class TestParseCustomerQuery:
    """Test the parse_customer_query function."""

    def test_parse_query_empty(self):
        """Test parsing empty query."""
        result = parse_customer_query("")
        assert result == {}

    def test_parse_query_email(self):
        """Test parsing query with email."""
        result = parse_customer_query("Find customer john.doe@example.com")
        assert result["email"] == "john.doe@example.com"

    def test_parse_query_client_id(self):
        """Test parsing query with client ID."""
        result = parse_customer_query("Look up client 1881899")
        assert result["client_id"] == "1881899"

    def test_parse_query_salesforce_id(self):
        """Test parsing query with Salesforce ID."""
        result = parse_customer_query("Find contact 003Ux00004c99SQ")
        assert result["customer_id"] == "003Ux00004c99SQ"

    def test_parse_query_phone(self):
        """Test parsing query with phone number."""
        result = parse_customer_query("Customer with phone (555) 123-4567")
        assert result["phone"] == "15551234567"

    def test_parse_query_multiple_identifiers(self):
        """Test parsing query with multiple identifiers."""
        result = parse_customer_query("Client 1881899 email john@example.com phone 555-123-4567")
        assert result["email"] == "john@example.com"
        assert result["client_id"] == "1881899"
        assert result["phone"] == "15551234567"

    def test_parse_query_name_fallback(self):
        """Test parsing query falls back to name when no other identifiers."""
        # The regex pattern matches first two capitalized words
        result = parse_customer_query("Find John Smith")
        assert result["first_name"] == "Find"
        assert result["last_name"] == "John"

        # Test with just names (no keywords)
        result = parse_customer_query("John Smith")
        assert result["first_name"] == "John"
        assert result["last_name"] == "Smith"

    def test_parse_query_name_with_identifiers(self):
        """Test that name is not extracted when other identifiers present."""
        result = parse_customer_query("Find John Smith with ID 1881899")
        assert result["client_id"] == "1881899"
        # Should not extract name when other identifiers are present
        assert "first_name" not in result
        assert "last_name" not in result

    def test_parse_query_no_name_match(self):
        """Test parsing query with no recognizable patterns."""
        result = parse_customer_query("just some random text")
        assert result == {}

    def test_parse_query_complex_patterns(self):
        """Test parsing complex queries with mixed content."""
        query = "I need help with customer jane.doe@company.com who has ID 1881899"
        result = parse_customer_query(query)
        assert result["email"] == "jane.doe@company.com"
        assert result["client_id"] == "1881899"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_extract_client_id_boundary_lengths(self):
        """Test client ID extraction at boundary lengths."""
        # Exactly 7 digits (minimum)
        assert IDPatterns.extract_client_id("ID 1234567") == "1234567"

        # Exactly 10 digits (maximum)
        assert IDPatterns.extract_client_id("ID 1234567890") == "1234567890"

        # 6 digits (too short)
        assert IDPatterns.extract_client_id("ID 123456") is None

        # 11 digits (too long)
        assert IDPatterns.extract_client_id("ID 12345678901") is None

    def test_phone_extraction_edge_cases(self):
        """Test phone number extraction edge cases."""
        # Multiple phone numbers in text
        text = "Call 555-123-4567 or 555-987-6543"
        result = IDPatterns.extract_phone(text)
        assert result == "15551234567"  # Should get first match

        # Phone with extensions
        assert IDPatterns.extract_phone("555-123-4567 x123") == "15551234567"

        # International format
        assert IDPatterns.extract_phone("+1 555 123 4567") == "15551234567"

    def test_email_extraction_edge_cases(self):
        """Test email extraction edge cases."""
        # Multiple emails
        text = "Contact john@example.com or jane@company.org"
        result = IDPatterns.extract_email(text)
        assert result == "john@example.com"  # Should get first match

        # Email with plus addressing
        assert IDPatterns.extract_email("user+tag@domain.com") == "user+tag@domain.com"

        # Email with subdomain
        assert IDPatterns.extract_email("test@mail.company.com") == "test@mail.company.com"

    def test_salesforce_id_variations(self):
        """Test Salesforce ID extraction with variations."""
        # 15-character ID
        assert IDPatterns.extract_salesforce_id("003ABC123DEF456") == "003ABC123DEF456"

        # 18-character ID
        assert IDPatterns.extract_salesforce_id("003ABC123DEF456GHI") == "003ABC123DEF456GHI"

        # Mixed case
        assert IDPatterns.extract_salesforce_id("003aBc123dEf456") == "003aBc123dEf456"

    def test_context_extraction_message_content_variations(self):
        """Test context extraction with various message content formats."""
        # JSON-like content
        messages = [{"role": "assistant", "content": '{"customer_id": "1881899", "status": "found"}'}]
        result = extract_customer_context_from_messages(messages)
        assert result["client_id"] == "1881899"

        # Mixed content
        messages = [{"role": "user", "content": "Find customer with ID: 1881899 and email: john@example.com"}]
        result = extract_customer_context_from_messages(messages)
        assert result["client_id"] == "1881899"
        assert result["email"] == "john@example.com"


class TestIntegration:
    """Test integration scenarios combining multiple functions."""

    def test_full_context_extraction_workflow(self):
        """Test complete workflow of context extraction."""
        # Simulate a conversation
        messages = [
            {"role": "user", "content": "I need help with a customer"},
            {"role": "assistant", "content": "I can help. Can you provide customer details?"},
            {"role": "user", "content": "The customer is John Smith with email john.smith@company.com"},
            {"role": "assistant", "content": "Found customer_id: 1881899 for john.smith@company.com"},
            {"role": "user", "content": "Great, what's their phone number?"}
        ]

        context = extract_customer_context_from_messages(messages)

        # Should extract both email and client_id
        assert context["email"] == "john.smith@company.com"
        assert context["client_id"] == "1881899"
        # Names are only extracted with specific trigger patterns (find/search/lookup etc.)
        # "The customer is John Smith" doesn't match the patterns for name extraction

    def test_query_parsing_comprehensive(self):
        """Test comprehensive query parsing scenarios."""
        queries = [
            "Find client 1881899",
            "Look up john@example.com",
            "Search for 003Ux00004c99SQ",
            "Customer with phone 555-123-4567",
            "John Smith",  # Simple name without keywords
            "Complex query with client 1881899 and email john@example.com"
        ]

        results = [parse_customer_query(q) for q in queries]

        # Verify each query produces expected results
        assert results[0]["client_id"] == "1881899"
        assert results[1]["email"] == "john@example.com"
        assert results[2]["customer_id"] == "003Ux00004c99SQ"
        assert results[3]["phone"] == "15551234567"
        assert results[4]["first_name"] == "John" and results[4]["last_name"] == "Smith"
        assert results[5]["client_id"] == "1881899" and results[5]["email"] == "john@example.com"
