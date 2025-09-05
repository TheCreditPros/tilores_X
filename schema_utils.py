#!/usr/bin/env python3
"""
GraphQL Schema Utilities for Tilores API
Practical utilities for working with the complete schema
"""

import json
from typing import Dict, List, Any, Optional

class TiloresSchemaUtils:
    """Utility class for working with Tilores GraphQL schema"""

    def __init__(self, schema_file: str = "tilores_graphql_schema.json"):
        with open(schema_file, 'r') as f:
            self.schema = json.load(f)

    # Standard query templates
    BASIC_CUSTOMER_QUERY = """
    query GetCustomerBasics($id: ID!) {
        entity(input: { id: $id }) {
            entity {
                id
                records {
                    id
                    STATUS
                    FIRST_NAME
                    LAST_NAME
                    EMAIL
                    CLIENT_ID
                    PRODUCT_NAME
                    CURRENT_PRODUCT
                    ENROLL_DATE
                }
            }
        }
    }
    """

    COMPREHENSIVE_CREDIT_QUERY = """
    query GetComprehensiveCreditData($id: ID!) {
        entity(input: { id: $id }) {
            entity {
                id
                records {
                    id
                    STATUS
                    FIRST_NAME
                    LAST_NAME
                    EMAIL
                    CLIENT_ID
                    CURRENT_PRODUCT
                    ENROLL_DATE

                    CREDIT_RESPONSE {
                        CREDIT_BUREAU
                        CreditReportFirstIssuedDate

                        CREDIT_SCORE {
                            Value
                            ModelNameType
                            CreditRepositorySourceType
                        }

                        CREDIT_LIABILITY {
                            AccountType
                            CreditLimitAmount
                            CreditBalance
                            AccountOpenedDate
                            AccountClosedDate
                            CurrentRating {
                                Code
                                Type
                            }
                            HighestAdverseRating {
                                Code
                                Type
                            }
                            LateCount {
                                Days30
                                Days60
                                Days90
                            }
                        }

                        CREDIT_INQUIRY {
                            InquiryDate
                            SubscriberName
                            CreditBusinessType
                        }
                    }
                }
            }
        }
    }
    """

    MULTI_DATA_ANALYSIS_QUERY = """
    query GetMultiDataAnalysis($id: ID!) {
        entity(input: { id: $id }) {
            entity {
                id

                # Customer data
                recordInsights {
                    filter(condition: { field: "STATUS", operator: "EXISTS" }) {
                        first {
                            STATUS
                            FIRST_NAME
                            LAST_NAME
                            EMAIL
                            CLIENT_ID
                            CURRENT_PRODUCT
                            ENROLL_DATE
                        }
                    }
                }

                # Credit data
                recordInsights {
                    filter(condition: { field: "CREDIT_RESPONSE", operator: "EXISTS" }) {
                        records {
                            CREDIT_RESPONSE {
                                CREDIT_BUREAU
                                CreditReportFirstIssuedDate
                                CREDIT_SCORE {
                                    Value
                                    CreditRepositorySourceType
                                }
                                CREDIT_LIABILITY {
                                    AccountType
                                    CreditLimitAmount
                                    CreditBalance
                                }
                            }
                        }
                    }
                }

                # Transaction data
                recordInsights {
                    filter(condition: { field: "TRANSACTION_AMOUNT", operator: "EXISTS" }) {
                        records {
                            TRANSACTION_AMOUNT
                            PAYMENT_METHOD
                            GATEWAY_RESPONSE
                            TRANSACTION_CREATED_DATE
                        }
                        count
                    }
                }

                # Support tickets
                recordInsights {
                    filter(condition: { field: "TICKETNUMBER", operator: "EXISTS" }) {
                        records {
                            TICKETNUMBER
                            SUBJECT
                            ZOHO_STATUS
                            CATEGORY
                            SENTIMENT
                            CREATEDTIME
                        }
                        count
                    }
                }
            }
        }
    }
    """

    TEMPORAL_CREDIT_QUERY = """
    query GetTemporalCreditAnalysis($id: ID!) {
        entity(input: { id: $id }) {
            entity {
                id
                recordInsights {
                    filter(condition: { field: "CREDIT_RESPONSE", operator: "EXISTS" }) {
                        sort(criteria: { field: "CREDIT_RESPONSE.CreditReportFirstIssuedDate", direction: ASC }) {
                            records {
                                CREDIT_RESPONSE {
                                    CREDIT_BUREAU
                                    CreditReportFirstIssuedDate
                                    CREDIT_SCORE {
                                        Value
                                        CreditRepositorySourceType
                                    }
                                    CREDIT_LIABILITY {
                                        AccountType
                                        CreditLimitAmount
                                        CreditBalance
                                    }
                                }
                            }
                            first {
                                CREDIT_RESPONSE {
                                    CreditReportFirstIssuedDate
                                    CREDIT_SCORE { Value CreditRepositorySourceType }
                                }
                            }
                            newest {
                                CREDIT_RESPONSE {
                                    CreditReportFirstIssuedDate
                                    CREDIT_SCORE { Value CreditRepositorySourceType }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    @classmethod
    def get_query_template(cls, query_type: str) -> str:
        """Get a standard query template by type"""
        templates = {
            "basic": cls.BASIC_CUSTOMER_QUERY,
            "credit": cls.COMPREHENSIVE_CREDIT_QUERY,
            "multi_data": cls.MULTI_DATA_ANALYSIS_QUERY,
            "temporal": cls.TEMPORAL_CREDIT_QUERY
        }
        return templates.get(query_type, cls.BASIC_CUSTOMER_QUERY)

    def get_bureau_specific_query(self, bureau: str) -> str:
        """Generate bureau-specific credit query"""
        return f"""
        query GetBureauSpecificCredit($id: ID!) {{
            entity(input: {{ id: $id }}) {{
                entity {{
                    id
                    recordInsights {{
                        filter(condition: {{
                            field: "CREDIT_RESPONSE.CREDIT_BUREAU",
                            operator: "EQUALS",
                            value: "{bureau}"
                        }}) {{
                            records {{
                                CREDIT_RESPONSE {{
                                    CREDIT_BUREAU
                                    CreditReportFirstIssuedDate
                                    CREDIT_SCORE {{
                                        Value
                                        ModelNameType
                                        CreditRepositorySourceType
                                    }}
                                    CREDIT_LIABILITY {{
                                        AccountType
                                        CreditLimitAmount
                                        CreditBalance
                                        CurrentRating {{
                                            Code
                                            Type
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """

    def get_date_range_query(self, start_date: str, end_date: Optional[str] = None) -> str:
        """Generate date range filtered query"""
        date_filter = f'field: "CREDIT_RESPONSE.CreditReportFirstIssuedDate", operator: "GREATER_THAN", value: "{start_date}"'
        if end_date:
            date_filter = f'field: "CREDIT_RESPONSE.CreditReportFirstIssuedDate", operator: "BETWEEN", value: ["{start_date}", "{end_date}"]'

        return f"""
        query GetCreditByDateRange($id: ID!) {{
            entity(input: {{ id: $id }}) {{
                entity {{
                    id
                    recordInsights {{
                        filter(condition: {{ {date_filter} }}) {{
                            records {{
                                CREDIT_RESPONSE {{
                                    CREDIT_BUREAU
                                    CreditReportFirstIssuedDate
                                    CREDIT_SCORE {{
                                        Value
                                        CreditRepositorySourceType
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """

    def get_field_info(self, type_name: str, field_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific field"""
        type_info = self.schema["types"].get(type_name)
        if not type_info or not type_info.get("fields"):
            return None

        for field in type_info["fields"]:
            if field["name"] == field_name:
                return field
        return None

    def list_credit_fields(self) -> List[str]:
        """List all available credit-related fields"""
        credit_response = self.schema["types"].get("CreditResponse", {})
        if not credit_response.get("fields"):
            return []

        return [field["name"] for field in credit_response["fields"]]

    def list_record_fields(self) -> List[str]:
        """List all available record fields"""
        record = self.schema["types"].get("Record", {})
        if not record.get("fields"):
            return []

        return [field["name"] for field in record["fields"]]

    def get_credit_score_fields(self) -> List[str]:
        """Get all fields available in CreditScore"""
        credit_score = self.schema["types"].get("CreditResponseCreditScore", {})
        if not credit_score.get("fields"):
            return []

        return [field["name"] for field in credit_score["fields"]]

    def get_credit_liability_fields(self) -> List[str]:
        """Get all fields available in CreditLiability"""
        credit_liability = self.schema["types"].get("CreditResponseCreditLiability", {})
        if not credit_liability.get("fields"):
            return []

        return [field["name"] for field in credit_liability["fields"]]

    def build_custom_query(self, entity_id_var: str = "$id",
                          include_basic: bool = True,
                          include_credit: bool = False,
                          include_transactions: bool = False,
                          include_tickets: bool = False,
                          credit_fields: Optional[List[str]] = None,
                          record_fields: Optional[List[str]] = None) -> str:
        """Build a custom query based on requirements"""

        query_parts = [f"query CustomQuery({entity_id_var}: ID!) {{"]
        query_parts.append(f"  entity(input: {{ id: {entity_id_var} }}) {{")
        query_parts.append("    entity {")
        query_parts.append("      id")

        if include_basic or include_credit or include_transactions or include_tickets:
            query_parts.append("      records {")
            query_parts.append("        id")

            # Basic fields
            if include_basic:
                basic_fields = record_fields or [
                    "STATUS", "FIRST_NAME", "LAST_NAME", "EMAIL",
                    "CLIENT_ID", "CURRENT_PRODUCT", "ENROLL_DATE"
                ]
                for field in basic_fields:
                    query_parts.append(f"        {field}")

            # Credit data
            if include_credit:
                query_parts.append("        CREDIT_RESPONSE {")
                credit_query_fields = credit_fields or [
                    "CREDIT_BUREAU", "CreditReportFirstIssuedDate"
                ]
                for field in credit_query_fields:
                    query_parts.append(f"          {field}")

                # Always include credit scores and liabilities
                query_parts.append("          CREDIT_SCORE {")
                query_parts.append("            Value")
                query_parts.append("            ModelNameType")
                query_parts.append("            CreditRepositorySourceType")
                query_parts.append("          }")

                query_parts.append("          CREDIT_LIABILITY {")
                query_parts.append("            AccountType")
                query_parts.append("            CreditLimitAmount")
                query_parts.append("            CreditBalance")
                query_parts.append("          }")

                query_parts.append("        }")

            # Transaction fields
            if include_transactions:
                transaction_fields = [
                    "TRANSACTION_AMOUNT", "PAYMENT_METHOD",
                    "GATEWAY_RESPONSE", "TRANSACTION_CREATED_DATE"
                ]
                for field in transaction_fields:
                    query_parts.append(f"        {field}")

            # Ticket fields
            if include_tickets:
                ticket_fields = [
                    "TICKETNUMBER", "SUBJECT", "ZOHO_STATUS",
                    "CATEGORY", "SENTIMENT", "CREATEDTIME"
                ]
                for field in ticket_fields:
                    query_parts.append(f"        {field}")

            query_parts.append("      }")

        query_parts.append("    }")
        query_parts.append("  }")
        query_parts.append("}")

        return "\n".join(query_parts)

# Convenience functions for common operations
def get_basic_customer_query() -> str:
    """Get basic customer data query"""
    return TiloresSchemaUtils.get_query_template("basic")

def get_comprehensive_credit_query() -> str:
    """Get comprehensive credit analysis query"""
    return TiloresSchemaUtils.get_query_template("credit")

def get_multi_data_query() -> str:
    """Get multi-data analysis query"""
    return TiloresSchemaUtils.get_query_template("multi_data")

def get_temporal_credit_query() -> str:
    """Get temporal credit analysis query"""
    return TiloresSchemaUtils.get_query_template("temporal")

def get_experian_only_query() -> str:
    """Get Experian-specific credit query"""
    utils = TiloresSchemaUtils()
    return utils.get_bureau_specific_query("Experian")

def get_transunion_only_query() -> str:
    """Get TransUnion-specific credit query"""
    utils = TiloresSchemaUtils()
    return utils.get_bureau_specific_query("TransUnion")

def get_equifax_only_query() -> str:
    """Get Equifax-specific credit query"""
    utils = TiloresSchemaUtils()
    return utils.get_bureau_specific_query("Equifax")

if __name__ == "__main__":
    # Example usage
    utils = TiloresSchemaUtils()

    print("📋 Available Record Fields:")
    record_fields = utils.list_record_fields()
    for i, field in enumerate(record_fields[:20]):  # Show first 20
        print(f"  {i+1}. {field}")
    print(f"  ... and {len(record_fields) - 20} more")

    print("\n💳 Available Credit Fields:")
    credit_fields = utils.list_credit_fields()
    for i, field in enumerate(credit_fields):
        print(f"  {i+1}. {field}")

    print("\n📊 Credit Score Fields:")
    score_fields = utils.get_credit_score_fields()
    for i, field in enumerate(score_fields):
        print(f"  {i+1}. {field}")

    print("\n🏦 Credit Liability Fields:")
    liability_fields = utils.get_credit_liability_fields()
    for i, field in enumerate(liability_fields[:15]):  # Show first 15
        print(f"  {i+1}. {field}")
    print(f"  ... and {len(liability_fields) - 15} more")

    print("\n🔧 Custom Query Example:")
    custom_query = utils.build_custom_query(
        include_basic=True,
        include_credit=True,
        include_transactions=True
    )
    print(custom_query)
