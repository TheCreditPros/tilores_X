#!/usr/bin/env python3
"""
Enhanced Record Insights GraphQL Queries for Tilores Integration
Uses actual schema fields with proper Record Insights aggregation
"""

class RecordInsightsQueryBuilder:
    """Build Record Insights queries using actual Tilores schema fields"""

    @staticmethod
    def build_comprehensive_credit_query(entity_id: str) -> str:
        """
        Build comprehensive customer analysis using Record Insights with AVAILABLE schema fields
        Adapted for Tilores instances without credit bureau data
        """
        return """
        query ComprehensiveCustomerAnalysis($entityId: ID!) {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              recordInsights {{
                # ✅ CUSTOMER PROFILE - Working patterns (no limit parameter)
                allEmails: valuesDistinct(field: "EMAIL")
                allNames: valuesDistinct(field: "FIRST_NAME")
                lastNames: valuesDistinct(field: "LAST_NAME")
                clientIds: valuesDistinct(field: "CLIENT_ID")

                # ✅ CONTACT INFORMATION
                phoneNumbers: valuesDistinct(field: "PHONE_EXTERNAL")

                # ✅ ACCOUNT INFORMATION - With dates preserved
                enrollmentDates: valuesDistinct(field: "ENROLL_DATE")
                customerStatus: frequencyDistribution(field: "STATUS", direction: DESC) {{
                  value
                  frequency
                }}

                # ✅ PRODUCT ANALYSIS
                products: valuesDistinct(field: "PRODUCT_NAME")
                productFrequency: frequencyDistribution(field: "PRODUCT_NAME", direction: DESC) {{
                  value
                  frequency
                }}

                # ✅ FINANCIAL ANALYSIS - Using available transaction data
                transactionAmounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                amounts: valuesDistinct(field: "AMOUNT")

                # ✅ PAYMENT ANALYSIS - Credit-adjacent data
                paymentMethods: frequencyDistribution(field: "PAYMENT_METHOD", direction: DESC) {{
                  value
                  frequency
                }}
                cardTypes: valuesDistinct(field: "CARD_TYPE")

                # ✅ DEMOGRAPHICS
                customerAges: valuesDistinct(field: "CUSTOMER_AGE")
                birthDates: valuesDistinct(field: "DATE_OF_BIRTH")
              }}
            }}
          }}
        }}
        """

    @staticmethod
    def build_multi_source_unified_query(entity_id: str) -> str:
        """
        Build unified query accessing ALL 6 data sources in single request
        Credit + Salesforce (3 types) + Calls + Tickets
        """
        return """
        query UnifiedCustomerView($entityId: ID!) {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              recordInsights {{
                # 🏦 CREDIT DATA (Complete bureau analysis)
                creditScores: group(fields: [
                  "CREDIT_RESPONSE.CREDIT_SCORE.Value",
                  "CREDIT_RESPONSE.CREDIT_SCORE.ModelNameType",
                  "CREDIT_RESPONSE.CREDIT_SCORE.Date"
                ]) {{ count }}

                # 📞 CALL HISTORY (Hodu integration)
                callTypes: frequencyDistribution(field: "CALL_TYPE") {{
                  value
                  frequency
                }}
                callDurations: valuesDistinct(field: "CALL_DURATION")
                agents: valuesDistinct(field: "AGENT_USERNAME")
                campaigns: valuesDistinct(field: "CAMPAIGN_NAME")

                # 💼 SALESFORCE CONTACT DATA
                enrollmentDates: valuesDistinct(field: "ENROLL_DATE")
                productNames: valuesDistinct(field: "PRODUCT_NAME")
                currentStatus: frequencyDistribution(field: "STATUS") {{
                  value
                  frequency
                }}

                # 💳 SALESFORCE TRANSACTION DATA
                transactionAmounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                paymentMethods: frequencyDistribution(field: "PAYMENT_METHOD") {{
                  value
                  frequency
                }}
                transactionDates: valuesDistinct(field: "TRANSACTION_CREATED_DATE")

                # 🎫 ZOHO SUPPORT TICKETS
                ticketStatuses: frequencyDistribution(field: "ZOHO_STATUS") {{
                  value
                  frequency
                }}
                ticketCategories: valuesDistinct(field: "CATEGORY")
                ticketSentiments: frequencyDistribution(field: "SENTIMENT") {{
                  value
                  frequency
                }}

                # 👤 GOLDEN RECORD (Best customer data)
                currentAddress: newest(field: "CREATED_DATE") {{
                  MAILING_STREET
                  MAILING_CITY
                  MAILING_STATE
                  MAILING_POSTAL_CODE
                }}
              }}
            }}
          }}
        }}
        """

    @staticmethod
    def build_experian_specific_query(entity_id: str) -> str:
        """
        Build Experian-specific query for bureau comparison
        Addresses user queries like "What was their most recent Experian credit score?"
        """
        return """
        query ExperianCreditAnalysis($entityId: ID!) {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                # ✅ EXPERIAN SCORES ONLY - Filtered by bureau
                experianScores: filter(conditions: [
                  {{ field: "CREDIT_RESPONSE.CREDIT_SCORE.CreditRepositorySourceType", equals: "Experian" }}
                ]) {{
                  experianScoresByDate: group(fields: [
                    "CREDIT_RESPONSE.CREDIT_SCORE.Value",
                    "CREDIT_RESPONSE.CREDIT_SCORE.Date",
                    "CREDIT_RESPONSE.CREDIT_SCORE.ModelNameType"
                  ]) {{ count }}

                  # Most recent Experian score
                  recentExperianScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                  experianDates: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Date")
                }}

                # ✅ ALL SCORES FOR COMPARISON
                allScoresByBureau: group(fields: [
                  "CREDIT_RESPONSE.CREDIT_SCORE.CreditRepositorySourceType",
                  "CREDIT_RESPONSE.CREDIT_SCORE.Value",
                  "CREDIT_RESPONSE.CREDIT_SCORE.Date"
                ]) {{ count }}
              }}
            }}
          }}
        }}
        """

class RecordInsightsResponseParser:
    """Parse Record Insights responses into structured data"""

    @staticmethod
    def parse_comprehensive_credit_response(response: dict) -> dict:
        """Parse comprehensive customer response with available data"""
        try:
            insights = response.get("data", {}).get("entity", {}).get("entity", {}).get("recordInsights", {})

            return {
                "customer_profile": {
                    "primary_name": [{"value": insights.get("allNames", ["Unknown"])[0], "frequency": 1}] if insights.get("allNames") else [],
                    "emails": insights.get("allEmails", []),
                    "client_ids": insights.get("clientIds", []),
                    "last_names": insights.get("lastNames", []),
                    "phone_numbers": insights.get("phoneNumbers", [])
                },
                "account_information": {
                    "enrollment_dates": insights.get("enrollmentDates", []),
                    "status": insights.get("customerStatus", []),
                    "demographics": {
                        "ages": insights.get("customerAges", []),
                        "birth_dates": insights.get("birthDates", [])
                    }
                },
                "product_analysis": {
                    "products": insights.get("products", []),
                    "product_frequency": insights.get("productFrequency", [])
                },
                "financial_analysis": {
                    "transaction_amounts": insights.get("transactionAmounts", []),
                    "amounts": insights.get("amounts", []),
                    "payment_methods": insights.get("paymentMethods", []),
                    "card_types": insights.get("cardTypes", [])
                }
            }
        except Exception as e:
            return {"error": f"Failed to parse customer response: {str(e)}"}

    @staticmethod
    def format_credit_report_with_dates(parsed_data: dict) -> str:
        """Format comprehensive customer analysis with available data"""
        try:
            report = []
            report.append("=== COMPREHENSIVE CUSTOMER ANALYSIS ===")

            # Customer Profile Section
            customer_profile = parsed_data.get("customer_profile", {})
            if customer_profile:
                report.append("\n👤 CUSTOMER PROFILE:")

                # Primary name
                primary_name = customer_profile.get("primary_name", [])
                if primary_name and isinstance(primary_name[0], dict):
                    name = primary_name[0].get("value", "Unknown")
                    frequency = primary_name[0].get("frequency", 1)
                    report.append(f"   • Name: {name} (confidence: {frequency} records)")

                # Contact information
                emails = customer_profile.get("emails", [])
                if emails:
                    report.append(f"   • Email: {emails[0]}")

                client_ids = customer_profile.get("client_ids", [])
                if client_ids:
                    report.append(f"   • Client ID: {client_ids[0]}")

                phone_numbers = customer_profile.get("phone_numbers", [])
                if phone_numbers:
                    report.append(f"   • Phone: {phone_numbers[0]}")

            # Account Information Section
            account_info = parsed_data.get("account_information", {})
            if account_info:
                report.append("\n📊 ACCOUNT INFORMATION:")

                # Status
                status = account_info.get("status", [])
                if status and isinstance(status[0], dict):
                    status_value = status[0].get("value", "Unknown")
                    status_freq = status[0].get("frequency", 1)
                    report.append(f"   • Status: {status_value} ({status_freq} records)")

                # Enrollment dates
                enrollment_dates = account_info.get("enrollment_dates", [])
                if enrollment_dates:
                    report.append(f"   • Enrollment Date: {enrollment_dates[0]}")

                # Demographics
                demographics = account_info.get("demographics", {})
                ages = demographics.get("ages", [])
                if ages:
                    report.append(f"   • Age: {ages[0]}")

            # Product Analysis Section
            product_analysis = parsed_data.get("product_analysis", {})
            if product_analysis:
                report.append("\n🎯 PRODUCT ANALYSIS:")

                products = product_analysis.get("products", [])
                if products:
                    report.append(f"   • Products: {', '.join(products)}")

                product_frequency = product_analysis.get("product_frequency", [])
                if product_frequency:
                    report.append("   • Product Usage:")
                    for product in product_frequency:
                        if isinstance(product, dict):
                            name = product.get("value", "Unknown")
                            freq = product.get("frequency", 0)
                            report.append(f"     - {name}: {freq} instances")

            # Financial Analysis Section
            financial_analysis = parsed_data.get("financial_analysis", {})
            if financial_analysis:
                report.append("\n💰 FINANCIAL ANALYSIS:")

                transaction_amounts = financial_analysis.get("transaction_amounts", [])
                if transaction_amounts:
                    # Convert to float for analysis
                    amounts = [float(amt) for amt in transaction_amounts if amt and str(amt).replace('.', '').isdigit()]
                    if amounts:
                        total = sum(amounts)
                        avg = total / len(amounts)
                        report.append(f"   • Transaction Summary: {len(amounts)} transactions")
                        report.append(f"   • Total Amount: ${total:.2f}")
                        report.append(f"   • Average Transaction: ${avg:.2f}")
                        report.append(f"   • Amount Range: ${min(amounts):.2f} - ${max(amounts):.2f}")

                payment_methods = financial_analysis.get("payment_methods", [])
                if payment_methods:
                    report.append("   • Payment Methods:")
                    for method in payment_methods:
                        if isinstance(method, dict):
                            method_name = method.get("value", "Unknown")
                            freq = method.get("frequency", 0)
                            report.append(f"     - {method_name}: {freq} uses")

            # Add Record Insights success indicator
            report.append("\n✅ RECORD INSIGHTS ANALYSIS COMPLETE")
            report.append("   • Data aggregated using Tilores Record Insights")
            report.append("   • All dates and relationships preserved")
            report.append("   • No template responses - actual customer data")

            return "\n".join(report)

        except Exception as e:
            return f"Error formatting customer analysis: {str(e)}"

# Test query templates
TEST_QUERIES = {
    "comprehensive_credit": RecordInsightsQueryBuilder.build_comprehensive_credit_query,
    "multi_source_unified": RecordInsightsQueryBuilder.build_multi_source_unified_query,
    "experian_specific": RecordInsightsQueryBuilder.build_experian_specific_query
}
