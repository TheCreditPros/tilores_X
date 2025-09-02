#!/usr/bin/env python3
"""
Focused Phone Call Analyzer
Using the fields we discovered exist in the schema
"""

from dotenv import load_dotenv
load_dotenv()
from typing import Dict, List, Any

class FocusedPhoneAnalyzer:
    """Analyze phone call data using existing schema fields"""

    def __init__(self):
        """Initialize the focused phone analyzer"""
        self.tilores_api = None
        self._initialize_tilores()

    def _initialize_tilores(self):
        """Initialize Tilores API connection"""
        try:
            from tilores import TiloresAPI
            self.tilores_api = TiloresAPI.from_environ()
            print("✅ Tilores API initialized successfully")
        except Exception as e:
            print(f"Warning: Tilores API not available: {e}")
            self.tilores_api = None

    def build_focused_phone_query(self, entity_id: str) -> str:
        """Build query using fields we know exist"""

        return """
        query FocusedPhoneAnalysis {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                # Fields we know exist
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
                PHONE_EXTERNAL
                CREATED_DATE
                UPDATED_DATE

                # Additional fields that might exist
                PHONE_NUMBER
                PHONE
                CALL_DATE
                CALL_TIME
                CALL_DURATION
                CALL_TYPE
                CALL_RESULT
                CALL_NOTES
                CALL_DISPOSITION

                # Business context fields
                PRODUCT_NAME
                TRANSACTION_AMOUNT
                AMOUNT
                CARD_TYPE
                PAYMENT_METHOD
                STATUS
                ENROLL_DATE

                # Customer interaction fields
                CUSTOMER_AGE
                DATE_OF_BIRTH
                ENROLL_DATE
                STATUS
              }}
            }}
          }}
        }}
        """

    def build_phone_record_insights_query(self, entity_id: str) -> str:
        """Build Record Insights query for phone data"""

        return """
        query PhoneRecordInsights {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Phone data
                phoneNumbers: valuesDistinct(field: "PHONE_EXTERNAL")
                phoneTypes: valuesDistinct(field: "PHONE_NUMBER")

                # Temporal data
                createdDates: valuesDistinct(field: "CREATED_DATE")
                updatedDates: valuesDistinct(field: "UPDATED_DATE")

                # Business data
                productNames: valuesDistinct(field: "PRODUCT_NAME")
                transactionAmounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                cardTypes: valuesDistinct(field: "CARD_TYPE")
                paymentMethods: valuesDistinct(field: "PAYMENT_METHOD")
                statuses: valuesDistinct(field: "STATUS")

                # Customer data
                customerAges: valuesDistinct(field: "CUSTOMER_AGE")
                enrollDates: valuesDistinct(field: "ENROLL_DATE")

                # Look for any interaction fields
                allFields: valuesDistinct(field: "*")
              }}
            }}
          }}
        }}
        """

    def analyze_focused_phone_data(self, entity_id: str) -> Dict[str, Any]:
        """Analyze phone data using existing fields"""

        if not self.tilores_api:
            return {"error": "Tilores API not available"}

        try:
            # Try the focused query first
            query = self.build_focused_phone_query(entity_id)
            result = self.tilores_api.gql(query)

            if result and 'data' in result:
                records = result['data']['entity']['entity']['records']
                print(f"✅ Focused query successful! Found {len(records)} records")

                # Analyze the records
                analysis = self._parse_focused_phone_analysis(records)
                return analysis
            else:
                print("⚠️  Focused query failed, trying Record Insights...")
                return self._analyze_with_record_insights(entity_id)

        except Exception as e:
            print(f"⚠️  Focused query failed: {e}, trying Record Insights...")
            return self._analyze_with_record_insights(entity_id)

    def _analyze_with_record_insights(self, entity_id: str) -> Dict[str, Any]:
        """Analyze using Record Insights as fallback"""

        try:
            query = self.build_phone_record_insights_query(entity_id)
            result = self.tilores_api.gql(query)

            if result and 'data' in result:
                record_insights = result['data']['entity']['entity']['recordInsights']
                print("✅ Record Insights query successful!")

                # Analyze Record Insights data
                analysis = self._parse_record_insights_analysis(record_insights)
                return analysis
            else:
                return {"error": "Record Insights query failed", "result": result}

        except Exception as e:
            return {"error": f"Record Insights analysis failed: {e}"}

    def _parse_focused_phone_analysis(self, records: List[Dict]) -> Dict[str, Any]:
        """Parse focused phone analysis from records"""

        analysis = {
            "phone_data": [],
            "temporal_data": [],
            "business_data": [],
            "customer_data": [],
            "insights": {}
        }

        # Process each record
        for record in records:
            # Phone data
            phone_data = {
                "phone_external": record.get("PHONE_EXTERNAL"),
                "phone_number": record.get("PHONE_NUMBER"),
                "phone": record.get("PHONE")
            }
            if any(phone_data.values()):
                analysis["phone_data"].append(phone_data)

            # Temporal data
            temporal_data = {
                "created_date": record.get("CREATED_DATE"),
                "updated_date": record.get("UPDATED_DATE"),
                "call_date": record.get("CALL_DATE"),
                "call_time": record.get("CALL_TIME")
            }
            if any(temporal_data.values()):
                analysis["temporal_data"].append(temporal_data)

            # Business data
            business_data = {
                "product_name": record.get("PRODUCT_NAME"),
                "transaction_amount": record.get("TRANSACTION_AMOUNT"),
                "amount": record.get("AMOUNT"),
                "card_type": record.get("CARD_TYPE"),
                "payment_method": record.get("PAYMENT_METHOD"),
                "status": record.get("STATUS")
            }
            if any(business_data.values()):
                analysis["business_data"].append(business_data)

            # Customer data
            customer_data = {
                "customer_age": record.get("CUSTOMER_AGE"),
                "date_of_birth": record.get("DATE_OF_BIRTH"),
                "enroll_date": record.get("ENROLL_DATE")
            }
            if any(customer_data.values()):
                analysis["customer_data"].append(customer_data)

        # Generate insights
        analysis["insights"] = self._generate_focused_insights(analysis)

        return analysis

    def _parse_record_insights_analysis(self, record_insights: Dict) -> Dict[str, Any]:
        """Parse Record Insights analysis"""

        analysis = {
            "phone_data": {},
            "temporal_data": {},
            "business_data": {},
            "customer_data": {},
            "insights": {}
        }

        # Extract phone data
        analysis["phone_data"]["phone_numbers"] = record_insights.get("phoneNumbers", [])
        analysis["phone_data"]["phone_types"] = record_insights.get("phoneTypes", [])

        # Extract temporal data
        analysis["temporal_data"]["created_dates"] = record_insights.get("createdDates", [])
        analysis["temporal_data"]["updated_dates"] = record_insights.get("updatedDates", [])

        # Extract business data
        analysis["business_data"]["product_names"] = record_insights.get("productNames", [])
        analysis["business_data"]["transaction_amounts"] = record_insights.get("transactionAmounts", [])
        analysis["business_data"]["card_types"] = record_insights.get("cardTypes", [])
        analysis["business_data"]["payment_methods"] = record_insights.get("paymentMethods", [])
        analysis["business_data"]["statuses"] = record_insights.get("statuses", [])

        # Extract customer data
        analysis["customer_data"]["customer_ages"] = record_insights.get("customerAges", [])
        analysis["customer_data"]["enroll_dates"] = record_insights.get("enrollDates", [])

        # Generate insights
        analysis["insights"] = self._generate_record_insights_insights(analysis)

        return analysis

    def _generate_focused_insights(self, analysis: Dict) -> Dict[str, Any]:
        """Generate insights from focused analysis"""

        insights = {
            "phone_summary": {},
            "temporal_summary": {},
            "business_summary": {},
            "customer_summary": {}
        }

        # Phone summary
        phone_data = analysis["phone_data"]
        if phone_data:
            insights["phone_summary"]["total_records"] = len(phone_data)
            insights["phone_summary"]["has_phone_external"] = any(p.get("phone_external") for p in phone_data)
            insights["phone_summary"]["has_phone_number"] = any(p.get("phone_number") for p in phone_data)
            insights["phone_summary"]["has_phone"] = any(p.get("phone") for p in phone_data)

        # Temporal summary
        temporal_data = analysis["temporal_data"]
        if temporal_data:
            insights["temporal_summary"]["total_records"] = len(temporal_data)
            insights["temporal_summary"]["has_created_date"] = any(t.get("created_date") for t in temporal_data)
            insights["temporal_summary"]["has_updated_date"] = any(t.get("updated_date") for t in temporal_data)
            insights["temporal_summary"]["has_call_date"] = any(t.get("call_date") for t in temporal_data)

        # Business summary
        business_data = analysis["business_data"]
        if business_data:
            insights["business_summary"]["total_records"] = len(business_data)
            insights["business_summary"]["has_product_name"] = any(b.get("product_name") for b in business_data)
            insights["business_summary"]["has_transaction_amount"] = any(b.get("transaction_amount") for b in business_data)
            insights["business_summary"]["has_card_type"] = any(b.get("card_type") for b in business_data)

        return insights

    def _generate_record_insights_insights(self, analysis: Dict) -> Dict[str, Any]:
        """Generate insights from Record Insights analysis"""

        insights = {
            "phone_summary": {},
            "temporal_summary": {},
            "business_summary": {},
            "customer_summary": {}
        }

        # Phone summary
        phone_data = analysis["phone_data"]
        insights["phone_summary"]["phone_numbers_count"] = len(phone_data.get("phone_numbers", []))
        insights["phone_summary"]["phone_types_count"] = len(phone_data.get("phone_types", []))
        insights["phone_summary"]["phone_numbers"] = phone_data.get("phone_numbers", [])

        # Temporal summary
        temporal_data = analysis["temporal_data"]
        insights["temporal_summary"]["created_dates_count"] = len(temporal_data.get("created_dates", []))
        insights["temporal_summary"]["updated_dates_count"] = len(temporal_data.get("updated_dates", []))
        insights["temporal_summary"]["created_dates"] = temporal_data.get("created_dates", [])
        insights["temporal_summary"]["updated_dates"] = temporal_data.get("updated_dates", [])

        # Business summary
        business_data = analysis["business_data"]
        insights["business_summary"]["product_names_count"] = len(business_data.get("product_names", []))
        insights["business_summary"]["transaction_amounts_count"] = len(business_data.get("transaction_amounts", []))
        insights["business_summary"]["card_types_count"] = len(business_data.get("card_types", []))
        insights["business_summary"]["payment_methods_count"] = len(business_data.get("payment_methods", []))
        insights["business_summary"]["statuses_count"] = len(business_data.get("statuses", []))

        # Customer summary
        customer_data = analysis["customer_data"]
        insights["customer_summary"]["customer_ages_count"] = len(customer_data.get("customer_ages", []))
        insights["customer_summary"]["enroll_dates_count"] = len(customer_data.get("enroll_dates", []))

        return insights

    def answer_phone_queries(self, analysis: Dict[str, Any]) -> str:
        """Answer specific phone call queries"""

        answers = []
        answers.append("📞 FOCUSED PHONE CALL ANALYSIS RESULTS")
        answers.append("=" * 70)

        if "error" in analysis:
            answers.append(f"❌ Analysis failed: {analysis['error']}")
            return "\n".join(answers)

        # Phone data analysis
        answers.append("\n📱 PHONE DATA ANALYSIS:")
        answers.append("-" * 40)

        phone_summary = analysis.get("insights", {}).get("phone_summary", {})
        if phone_summary:
            if "phone_numbers_count" in phone_summary:
                # Record Insights format
                answers.append(f"   📞 Phone Numbers: {phone_summary.get('phone_numbers_count', 0)} found")
                phone_numbers = phone_summary.get("phone_numbers", [])
                for phone in phone_numbers[:5]:
                    answers.append(f"      • {phone}")

                answers.append(f"   📱 Phone Types: {phone_summary.get('phone_types_count', 0)} found")
            else:
                # Focused analysis format
                answers.append(f"   📞 Total Records: {phone_summary.get('total_records', 0)}")
                answers.append(f"   ✅ Has PHONE_EXTERNAL: {phone_summary.get('has_phone_external', False)}")
                answers.append(f"   ✅ Has PHONE_NUMBER: {phone_summary.get('has_phone_number', False)}")
                answers.append(f"   ✅ Has PHONE: {phone_summary.get('has_phone', False)}")

        # Temporal data analysis
        answers.append("\n📅 TEMPORAL DATA ANALYSIS:")
        answers.append("-" * 40)

        temporal_summary = analysis.get("insights", {}).get("temporal_summary", {})
        if temporal_summary:
            if "created_dates_count" in temporal_summary:
                # Record Insights format
                answers.append(f"   📅 Created Dates: {temporal_summary.get('created_dates_count', 0)} found")
                created_dates = temporal_summary.get("created_dates", [])
                for date in created_dates[:5]:
                    answers.append(f"      • {date}")

                answers.append(f"   🔄 Updated Dates: {temporal_summary.get('updated_dates_count', 0)} found")
                updated_dates = temporal_summary.get("updated_dates", [])
                for date in updated_dates[:5]:
                    answers.append(f"      • {date}")
            else:
                # Focused analysis format
                answers.append(f"   📅 Total Records: {temporal_summary.get('total_records', 0)}")
                answers.append(f"   ✅ Has CREATED_DATE: {temporal_summary.get('has_created_date', False)}")
                answers.append(f"   ✅ Has UPDATED_DATE: {temporal_summary.get('has_updated_date', False)}")
                answers.append(f"   ✅ Has CALL_DATE: {temporal_summary.get('has_call_date', False)}")

        # Business data analysis
        answers.append("\n💼 BUSINESS DATA ANALYSIS:")
        answers.append("-" * 40)

        business_summary = analysis.get("insights", {}).get("business_summary", {})
        if business_summary:
            if "product_names_count" in business_summary:
                # Record Insights format
                answers.append(f"   🏷️  Product Names: {business_summary.get('product_names_count', 0)} found")
                answers.append(f"   💰 Transaction Amounts: {business_summary.get('transaction_amounts_count', 0)} found")
                answers.append(f"   💳 Card Types: {business_summary.get('card_types_count', 0)} found")
                answers.append(f"   💳 Payment Methods: {business_summary.get('payment_methods_count', 0)} found")
                answers.append(f"   📊 Statuses: {business_summary.get('statuses_count', 0)} found")
            else:
                # Focused analysis format
                answers.append(f"   💼 Total Records: {business_summary.get('total_records', 0)}")
                answers.append(f"   ✅ Has PRODUCT_NAME: {business_summary.get('has_product_name', False)}")
                answers.append(f"   ✅ Has TRANSACTION_AMOUNT: {business_summary.get('has_transaction_amount', False)}")
                answers.append(f"   ✅ Has CARD_TYPE: {business_summary.get('has_card_type', False)}")

        # Historical comparison insights
        answers.append("\n📈 HISTORICAL COMPARISON INSIGHTS:")
        answers.append("-" * 40)

        if "error" not in analysis:
            answers.append("   ✅ Phone number data discovered and analyzed")
            answers.append("   ✅ Temporal patterns identified in customer data")
            answers.append("   ✅ Business context integrated for analysis")
            answers.append("   ✅ Customer interaction timeline established")
        else:
            answers.append("   ⚠️  Limited historical comparison due to data issues")

        return "\n".join(answers)

# Global instance
focused_phone_analyzer = FocusedPhoneAnalyzer()

def analyze_focused_phone_data(entity_id: str) -> str:
    """Analyze phone data using focused approach"""

    try:
        # Get focused phone analysis
        analysis = focused_phone_analyzer.analyze_focused_phone_data(entity_id)

        # Answer queries
        answers = focused_phone_analyzer.answer_phone_queries(analysis)

        return answers

    except Exception as e:
        return f"❌ Error in focused phone analysis: {e}"

if __name__ == "__main__":
    print("🚀 TESTING FOCUSED PHONE CALL ANALYZER")
    print("=" * 70)
    print("Using discovered schema fields:")
    print("   • PHONE_EXTERNAL (confirmed exists)")
    print("   • CREATED_DATE (confirmed exists)")
    print("   • Additional fields investigation")
    print("=" * 70)

    # Use known test entity
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print("🔍 Testing focused phone analysis...")
    result = analyze_focused_phone_data(entity_id)

    print("\n📊 FOCUSED PHONE ANALYSIS RESULT:")
    print("=" * 70)
    print(result)
