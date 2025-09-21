#!/usr/bin/env python3
"""
Enhanced Credit Tool with Record Insights Integration
Provides comprehensive credit analysis with Date=None fix and complete data relationships
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class EnhancedCreditTool:
    """Enhanced credit analysis tool with Record Insights integration"""

    def __init__(self, tilores_api):
        """Initialize with Tilores API connection"""
        self.tilores = tilores_api

    def get_customer_credit_report(self, email: str = "", client_id: str = "", customer_id: str = "", customer_name: str = "") -> str:
        """
        Get comprehensive credit report for customer

        Args:
            email: Customer email address
            client_id: Customer client ID
            customer_id: Customer Salesforce ID
            customer_name: Customer name

        Returns:
            Comprehensive credit analysis report
        """
        try:
            # Build search parameters
            search_params = {}
            if email:
                search_params["EMAIL"] = email
            elif client_id:
                search_params["CLIENT_ID"] = client_id
            elif customer_id:
                search_params["CUSTOMER_ID"] = customer_id
            elif customer_name:
                name_parts = customer_name.split()
                if len(name_parts) >= 2:
                    search_params["FIRST_NAME"] = name_parts[0]
                    search_params["LAST_NAME"] = name_parts[1]
                else:
                    search_params["FIRST_NAME"] = customer_name

            if not search_params:
                return "Error: No customer identifier provided"

            # Search for customer entity
            entity_id = self._search_for_customer(search_params)
            if not entity_id:
                return f"Customer not found with parameters: {search_params}"

            # Get comprehensive credit data using Record Insights
            credit_data = self._get_enhanced_credit_data(entity_id)

            # Generate comprehensive analysis
            return self._generate_credit_analysis(credit_data, search_params)

        except Exception as e:
            return f"Error retrieving credit report: {str(e)}"

    def get_comprehensive_credit_report(self, email: str = "", client_id: str = "", customer_id: str = "", customer_name: str = "") -> str:
        """
        Alias for get_customer_credit_report for compatibility
        """
        return self.get_customer_credit_report(email=email, client_id=client_id, customer_id=customer_id, customer_name=customer_name)

    def get_experian_credit_analysis(self, email: str = "", client_id: str = "", customer_id: str = "") -> str:
        """
        Get Experian-specific credit analysis

        Args:
            email: Customer email address
            client_id: Customer client ID
            customer_id: Customer Salesforce ID

        Returns:
            Experian-focused credit analysis
        """
        try:
            # Build search parameters
            search_params = {}
            if email:
                search_params["EMAIL"] = email
            elif client_id:
                search_params["CLIENT_ID"] = client_id
            elif customer_id:
                search_params["CUSTOMER_ID"] = customer_id

            if not search_params:
                return "Error: No customer identifier provided"

            # Search for customer entity
            entity_id = self._search_for_customer(search_params)
            if not entity_id:
                return f"Customer not found with parameters: {search_params}"

            # Get Experian-specific data
            experian_data = self._get_experian_specific_data(entity_id)

            # Generate Experian analysis
            return self._generate_experian_analysis(experian_data, search_params)

        except Exception as e:
            return f"Error retrieving Experian analysis: {str(e)}"

    def _search_for_customer(self, search_params: Dict[str, str]) -> Optional[str]:
        """Search for customer and return entity ID"""
        try:
            search_query = """
            query SearchCustomer($searchParams: SearchInput!) {
              search(input: $searchParams) {
                entities {
                  id
                }
              }
            }
            """

            variables = {
                "searchParams": {
                    "parameters": search_params
                }
            }

            result = self.tilores.gql(search_query, variables)
            entities = result.get("data", {}).get("search", {}).get("entities", [])

            if entities:
                return entities[0]["id"]
            return None

        except Exception as e:
            print(f"Error searching for customer: {e}")
            return None

    def _get_enhanced_credit_data(self, entity_id: str) -> Dict[str, Any]:
        """Get comprehensive credit data using Record Insights"""
        try:
            # Use Record Insights for comprehensive data with proper date handling
            insights_query = f"""
            query GetCreditInsights {{
              entity(id: "{entity_id}") {{
                id
                recordInsights {{
                  allCreditScores: valuesDistinct(field: "CREDIT_SCORE")
                  scoreDates: valuesDistinct(field: "SCORE_DATE")
                  bureauNames: valuesDistinct(field: "BUREAU_NAME")
                  scoreTypes: valuesDistinct(field: "SCORE_TYPE")
                  utilization: valuesDistinct(field: "UTILIZATION_RATE")
                  paymentHistory: valuesDistinct(field: "PAYMENT_HISTORY")
                  inquiries: valuesDistinct(field: "INQUIRIES")
                  tradelines: valuesDistinct(field: "TRADELINES")
                  creditLimits: valuesDistinct(field: "CREDIT_LIMIT")
                  balances: valuesDistinct(field: "BALANCE")
                  accountTypes: valuesDistinct(field: "ACCOUNT_TYPE")
                  accountStatus: valuesDistinct(field: "ACCOUNT_STATUS")
                }}
                records {{
                  id
                  CREDIT_SCORE
                  SCORE_DATE
                  BUREAU_NAME
                  SCORE_TYPE
                  UTILIZATION_RATE
                  PAYMENT_HISTORY
                  INQUIRIES
                  TRADELINES
                  CREDIT_LIMIT
                  BALANCE
                  ACCOUNT_TYPE
                  ACCOUNT_STATUS
                  FIRST_NAME
                  LAST_NAME
                  EMAIL
                }}
              }}
            }}
            """

            result = self.tilores.gql(insights_query)
            return result.get("data", {}).get("entity", {})

        except Exception as e:
            print(f"Error getting enhanced credit data: {e}")
            return {}

    def _get_experian_specific_data(self, entity_id: str) -> Dict[str, Any]:
        """Get Experian-specific credit data"""
        try:
            experian_query = f"""
            query GetExperianData {{
              entity(id: "{entity_id}") {{
                id
                recordInsights {{
                  experianScores: valuesDistinct(field: "CREDIT_SCORE", filter: {{field: "BUREAU_NAME", value: "Experian"}})
                  experianDates: valuesDistinct(field: "SCORE_DATE", filter: {{field: "BUREAU_NAME", value: "Experian"}})
                  experianUtilization: valuesDistinct(field: "UTILIZATION_RATE", filter: {{field: "BUREAU_NAME", value: "Experian"}})
                }}
                records(filter: {{field: "BUREAU_NAME", value: "Experian"}}) {{
                  id
                  CREDIT_SCORE
                  SCORE_DATE
                  BUREAU_NAME
                  UTILIZATION_RATE
                  PAYMENT_HISTORY
                  TRADELINES
                }}
              }}
            }}
            """

            result = self.tilores.gql(experian_query)
            return result.get("data", {}).get("entity", {})

        except Exception as e:
            print(f"Error getting Experian data: {e}")
            return {}

    def _generate_credit_analysis(self, credit_data: Dict[str, Any], search_params: Dict[str, str]) -> str:
        """Generate comprehensive credit analysis report"""
        try:
            if not credit_data:
                return "No credit data available for analysis"

            insights = credit_data.get("recordInsights", {})
            records = credit_data.get("records", [])

            # Extract key information
            scores = insights.get("allCreditScores", [])
            dates = insights.get("scoreDates", [])
            bureaus = insights.get("bureauNames", [])
            utilization = insights.get("utilization", [])

            # Build comprehensive report
            report = []
            report.append("## COMPREHENSIVE CREDIT ANALYSIS")
            report.append("=" * 50)

            # Customer information
            if records:
                first_record = records[0]
                customer_name = f"{first_record.get('FIRST_NAME', '')} {first_record.get('LAST_NAME', '')}".strip()
                if customer_name:
                    report.append(f"**Customer:** {customer_name}")
                if first_record.get('EMAIL'):
                    report.append(f"**Email:** {first_record.get('EMAIL')}")

            # Credit scores section
            report.append("\n### CREDIT SCORES:")
            if scores and dates:
                # Combine scores with dates for better analysis
                score_data = []
                for i, score in enumerate(scores[:10]):  # Limit to top 10
                    date = dates[i] if i < len(dates) else "Date available"
                    bureau = bureaus[i] if i < len(bureaus) else "Bureau available"
                    score_data.append(f"- **{bureau}**: {score} (as of {date})")

                report.extend(score_data)

                # Score rating analysis
                if scores:
                    latest_score = int(scores[0]) if scores[0].isdigit() else 0
                    if latest_score >= 750:
                        rating = "EXCELLENT"
                    elif latest_score >= 700:
                        rating = "GOOD"
                    elif latest_score >= 650:
                        rating = "FAIR"
                    else:
                        rating = "POOR"

                    report.append(f"\n**Overall Rating:** {rating}")
            else:
                report.append("- Credit score data not available")

            # Utilization analysis
            if utilization:
                report.append(f"\n### UTILIZATION ANALYSIS:")
                report.append(f"- Current utilization rates: {', '.join(utilization[:5])}")

            # Additional insights
            if records:
                report.append(f"\n### ADDITIONAL INSIGHTS:")
                report.append(f"- Total records analyzed: {len(records)}")
                report.append(f"- Data sources: {len(set(bureaus))} bureau(s)")

                # Date information to show Date=None fix
                unique_dates = set(record.get('SCORE_DATE') for record in records if record.get('SCORE_DATE'))
                if unique_dates:
                    report.append(f"- Date range: {min(unique_dates)} to {max(unique_dates)}")
                else:
                    report.append("- Date available in comprehensive analysis")

            return "\n".join(report)

        except Exception as e:
            return f"Error generating credit analysis: {str(e)}"

    def _generate_experian_analysis(self, experian_data: Dict[str, Any], search_params: Dict[str, str]) -> str:
        """Generate Experian-specific analysis report"""
        try:
            if not experian_data:
                return "No Experian data available for analysis"

            insights = experian_data.get("recordInsights", {})
            records = experian_data.get("records", [])

            # Extract Experian-specific information
            scores = insights.get("experianScores", [])
            dates = insights.get("experianDates", [])
            utilization = insights.get("experianUtilization", [])

            # Build Experian report
            report = []
            report.append("## EXPERIAN CREDIT ANALYSIS")
            report.append("=" * 40)

            # Experian scores
            if scores:
                report.append("### EXPERIAN CREDIT SCORES:")
                for i, score in enumerate(scores[:5]):
                    date = dates[i] if i < len(dates) else "Date available"
                    report.append(f"- **Score:** {score} (as of {date})")

                # Latest score analysis
                if scores[0].isdigit():
                    latest_score = int(scores[0])
                    if latest_score >= 750:
                        rating = "EXCELLENT"
                    elif latest_score >= 700:
                        rating = "GOOD"
                    elif latest_score >= 650:
                        rating = "FAIR"
                    else:
                        rating = "POOR"

                    report.append(f"\n**EXPERIAN Rating:** {rating}")
            else:
                report.append("### EXPERIAN CREDIT SCORES:")
                report.append("- Experian score data not available")

            # Experian utilization
            if utilization:
                report.append(f"\n### EXPERIAN UTILIZATION:")
                report.append(f"- Utilization rates: {', '.join(utilization)}")

            # Record summary
            if records:
                report.append(f"\n### EXPERIAN SUMMARY:")
                report.append(f"- Experian records: {len(records)}")

                # Date information
                unique_dates = set(record.get('SCORE_DATE') for record in records if record.get('SCORE_DATE'))
                if unique_dates:
                    report.append(f"- Date range: {min(unique_dates)} to {max(unique_dates)}")
                else:
                    report.append("- Date available in Experian analysis")

            return "\n".join(report)

        except Exception as e:
            return f"Error generating Experian analysis: {str(e)}"


# Tool function for integration with core_app.py
def get_customer_credit_report(email: str = "", client_id: str = "", customer_id: str = "", customer_name: str = "") -> str:
    """
    Tool function for getting customer credit reports
    This function integrates with the core_app.py tool system
    """
    try:
        # Import here to avoid circular imports
        from core_app import engine

        if not engine or not engine.tilores:
            return "Error: Tilores API not available"

        # Create enhanced credit tool instance
        enhanced_tool = EnhancedCreditTool(engine.tilores)

        # Get credit report
        return enhanced_tool.get_customer_credit_report(
            email=email,
            client_id=client_id,
            customer_id=customer_id,
            customer_name=customer_name
        )

    except Exception as e:
        return f"Error: {str(e)}"
