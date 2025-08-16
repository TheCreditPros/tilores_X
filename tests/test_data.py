"""
Real-world test data for Tilores_X testing
Based on common customer scenarios and edge cases
"""

# Real-world test customers with complete data
TEST_CUSTOMERS = [
    {
        "id": "cust_001",
        "email": "john.smith@techcorp.com",
        "phone": "555-123-4567",
        "first_name": "John",
        "last_name": "Smith",
        "client_id": "1881899",
        "salesforce_id": "003Ux000001hG4rIAE",
        "description": "Primary test customer with full data",
        "expected_records": 5,
        "has_credit_report": True,
        "credit_score": 750
    },
    {
        "id": "cust_002", 
        "email": "sarah.johnson@healthcare.org",
        "phone": "555-987-6543",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "client_id": "1992837",
        "salesforce_id": "003Ux000002kL5sIAE",
        "description": "Healthcare customer with multiple records",
        "expected_records": 8,
        "has_credit_report": True,
        "credit_score": 820
    },
    {
        "id": "cust_003",
        "email": "mike.brown@retail.com",
        "phone": "555-555-0123",
        "first_name": "Michael",
        "last_name": "Brown",
        "client_id": "2003948",
        "salesforce_id": "003Ux000003mN7tIAE",
        "description": "Retail customer with transaction history",
        "expected_records": 12,
        "has_credit_report": True,
        "credit_score": 680
    },
    {
        "id": "cust_004",
        "email": "emily.davis@finance.io",
        "phone": "555-321-9876",
        "first_name": "Emily",
        "last_name": "Davis",
        "client_id": "2104859",
        "salesforce_id": "003Ux000004pQ8uIAE",
        "description": "Financial services customer",
        "expected_records": 3,
        "has_credit_report": False,
        "credit_score": None
    },
    {
        "id": "cust_005",
        "email": "david.wilson@startup.tech",
        "phone": "555-777-8888",
        "first_name": "David",
        "last_name": "Wilson",
        "client_id": "2205960",
        "salesforce_id": "003Ux000005rS9vIAE",
        "description": "New customer with minimal data",
        "expected_records": 1,
        "has_credit_report": False,
        "credit_score": None
    }
]

# Common phone app scenarios
PHONE_SCENARIOS = [
    {
        "name": "Quick lookup by phone",
        "query": "555-123-4567",
        "expected_customer": "John Smith",
        "max_latency_ms": 1500,
        "requires_cache": False
    },
    {
        "name": "Email search with cache",
        "query": "sarah.johnson@healthcare.org",
        "expected_customer": "Sarah Johnson",
        "max_latency_ms": 100,
        "requires_cache": True
    },
    {
        "name": "Salesforce ID lookup",
        "query": "003Ux000003mN7tIAE",
        "expected_customer": "Michael Brown",
        "max_latency_ms": 2000,
        "requires_cache": False
    },
    {
        "name": "Client ID search",
        "query": "2104859",
        "expected_customer": "Emily Davis",
        "max_latency_ms": 1500,
        "requires_cache": False
    },
    {
        "name": "Name search (first last)",
        "query": "David Wilson",
        "expected_customer": "David Wilson",
        "max_latency_ms": 2000,
        "requires_cache": False
    }
]

# Batch processing scenarios
BATCH_SCENARIOS = [
    {
        "name": "Multiple email searches",
        "identifiers": [
            "john.smith@techcorp.com",
            "sarah.johnson@healthcare.org",
            "mike.brown@retail.com"
        ],
        "expected_count": 3,
        "max_total_latency_ms": 2000
    },
    {
        "name": "Mixed identifier types",
        "identifiers": [
            "555-123-4567",  # Phone
            "sarah.johnson@healthcare.org",  # Email
            "003Ux000003mN7tIAE",  # Salesforce ID
            "2104859"  # Client ID
        ],
        "expected_count": 4,
        "max_total_latency_ms": 3000
    },
    {
        "name": "Large batch for pre-warming",
        "identifiers": [c["email"] for c in TEST_CUSTOMERS],
        "expected_count": 5,
        "max_total_latency_ms": 3000
    }
]

# Complex query scenarios (large Tilores responses)
COMPLEX_SCENARIOS = [
    {
        "name": "Customer with transaction history",
        "query": "Get all transactions and credit report for Mike Brown (customer ID 2003948)",
        "expected_data_points": 50,
        "includes_credit": True,
        "max_latency_ms": 3000
    },
    {
        "name": "Multi-record customer search",
        "query": "Find all records for Sarah Johnson including call history",
        "expected_data_points": 30,
        "includes_credit": False,
        "max_latency_ms": 2500
    },
    {
        "name": "Full customer 360 view",
        "query": "Complete profile for john.smith@techcorp.com with all relationships",
        "expected_data_points": 40,
        "includes_credit": True,
        "max_latency_ms": 4000
    }
]

# Edge cases and error scenarios
EDGE_CASES = [
    {
        "name": "Non-existent customer",
        "query": "nonexistent@example.com",
        "expected_result": "no_results",
        "should_cache": False
    },
    {
        "name": "Invalid email format",
        "query": "not-an-email",
        "expected_result": "no_results",
        "should_cache": False
    },
    {
        "name": "Partial phone number",
        "query": "555-123",
        "expected_result": "no_results",
        "should_cache": False
    },
    {
        "name": "SQL injection attempt",
        "query": "'; DROP TABLE customers; --",
        "expected_result": "no_results",
        "should_cache": False
    },
    {
        "name": "Very long query",
        "query": "a" * 1000,
        "expected_result": "error",
        "should_cache": False
    }
]

# Pre-warming configuration
PRE_WARM_CONFIG = {
    "high_priority_customers": [
        "john.smith@techcorp.com",
        "sarah.johnson@healthcare.org",
        "mike.brown@retail.com"
    ],
    "common_searches": [
        "555-123-4567",
        "555-987-6543",
        "1881899",
        "003Ux000001hG4rIAE"
    ],
    "refresh_interval_minutes": 30,
    "batch_size": 5,
    "use_parallel": True
}

# Performance benchmarks
PERFORMANCE_TARGETS = {
    "cache_hit_latency_ms": 10,
    "cache_miss_latency_ms": 1500,
    "llm_response_ms": 200,
    "batch_speedup_factor": 3.0,
    "phone_app_total_ms": 2000,
    "web_app_total_ms": 5000
}

def get_test_customer(identifier: str):
    """Get test customer by any identifier"""
    for customer in TEST_CUSTOMERS:
        if identifier in [
            customer["email"],
            customer["phone"],
            customer["client_id"],
            customer["salesforce_id"],
            f"{customer['first_name']} {customer['last_name']}"
        ]:
            return customer
    return None

def get_customers_for_prewarm():
    """Get list of customers for cache pre-warming"""
    return PRE_WARM_CONFIG["high_priority_customers"]

def get_batch_test_data():
    """Get data for batch processing tests"""
    return BATCH_SCENARIOS[1]["identifiers"]  # Mixed types

def get_complex_query():
    """Get a complex query for stress testing"""
    return COMPLEX_SCENARIOS[0]