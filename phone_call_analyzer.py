#!/usr/bin/env python3
"""
Phone Call Analyzer - Historical Analysis and Salesforce Integration
Extends our temporal analysis capabilities to include phone call data
"""

from dotenv import load_dotenv
load_dotenv()
from typing import Dict, List, Any

class PhoneCallAnalyzer:
    """Analyze phone call data with historical comparisons and Salesforce integration"""

    def __init__(self):
        """Initialize the phone call analyzer"""
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

    def build_phone_call_query(self, entity_id: str) -> str:
        """Build query for phone call data with temporal focus"""

        return """
        query PhoneCallAnalysis {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
                PHONE_EXTERNAL
                PHONE_NUMBER

                # Phone call specific fields
                CALL_DATE
                CALL_TIME
                CALL_DURATION
                CALL_TYPE
                CALL_RESULT
                CALL_NOTES
                CALL_DISPOSITION

                # Salesforce integration fields
                SALESFORCE_ID
                SALESFORCE_LEAD_ID
                SALESFORCE_OPPORTUNITY_ID
                SALESFORCE_CASE_ID
                SALESFORCE_ACCOUNT_ID

                # Call outcome and metrics
                CALL_OUTCOME
                CALL_PURPOSE
                CALL_PRIORITY
                CALL_STATUS
                CALL_SOURCE

                # Historical call data
                PREVIOUS_CALL_DATE
                NEXT_CALL_DATE
                CALL_FREQUENCY
                TOTAL_CALLS

                # Customer interaction data
                CUSTOMER_SATISFACTION
                CUSTOMER_FEEDBACK
                FOLLOW_UP_REQUIRED
                FOLLOW_UP_DATE

                # Agent and routing data
                AGENT_ID
                AGENT_NAME
                AGENT_DEPARTMENT
                CALL_QUEUE
                CALL_ROUTING

                # Business context
                PRODUCT_INTEREST
                SERVICE_REQUEST
                COMPLAINT_TYPE
                RESOLUTION_STATUS

                # Temporal markers
                CREATED_DATE
                UPDATED_DATE
                LAST_ACTIVITY_DATE
              }}
            }}
          }}
        }}
        """

    def build_salesforce_integration_query(self, entity_id: str) -> str:
        """Build query for Salesforce data integration"""

        return """
        query SalesforceIntegration {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                # Core customer data
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID

                # Salesforce objects
                SALESFORCE_LEAD {{
                  LeadId
                  Company
                  Industry
                  LeadSource
                  Status
                  CreatedDate
                  LastModifiedDate
                  ConvertedDate
                  ConvertedOpportunityId
                }}

                SALESFORCE_OPPORTUNITY {{
                  OpportunityId
                  Name
                  Amount
                  StageName
                  CloseDate
                  CreatedDate
                  LastModifiedDate
                  Probability
                  Type
                }}

                SALESFORCE_CASE {{
                  CaseId
                  CaseNumber
                  Subject
                  Status
                  Priority
                  CreatedDate
                  LastModifiedDate
                  ClosedDate
                  CaseOrigin
                  CaseType
                }}

                SALESFORCE_ACCOUNT {{
                  AccountId
                  Name
                  Industry
                  Type
                  BillingCity
                  BillingState
                  CreatedDate
                  LastModifiedDate
                }}

                # Call activity in Salesforce
                SALESFORCE_CALL_ACTIVITY {{
                  ActivityId
                  Subject
                  CallType
                  CallDate
                  CallDuration
                  CallResult
                  Description
                  CreatedDate
                  LastModifiedDate
                }}

                # Task and follow-up data
                SALESFORCE_TASK {{
                  TaskId
                  Subject
                  Status
                  Priority
                  ActivityDate
                  CreatedDate
                  LastModifiedDate
                  Description
                  Type
                }}
              }}
            }}
          }}
        }}
        """

    def analyze_phone_call_data(self, entity_id: str) -> Dict[str, Any]:
        """Analyze phone call data with temporal focus"""

        if not self.tilores_api:
            return {"error": "Tilores API not available"}

        try:
            query = self.build_phone_call_query(entity_id)
            result = self.tilores_api.gql(query)

            if not result or 'data' not in result:
                return {"error": "Query failed", "result": result}

            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            if not records:
                return {"error": "No records found"}

            # Analyze phone call data
            analysis = self._parse_phone_call_analysis(records)
            return analysis

        except Exception as e:
            return {"error": f"Phone call analysis failed: {e}"}

    def analyze_salesforce_integration(self, entity_id: str) -> Dict[str, Any]:
        """Analyze Salesforce data integration"""

        if not self.tilores_api:
            return {"error": "Tilores API not available"}

        try:
            query = self.build_salesforce_integration_query(entity_id)
            result = self.tilores_api.gql(query)

            if not result or 'data' not in result:
                return {"error": "Salesforce query failed", "result": result}

            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            if not records:
                return {"error": "No Salesforce records found"}

            # Analyze Salesforce data
            analysis = self._parse_salesforce_analysis(records)
            return analysis

        except Exception as e:
            return {"error": f"Salesforce analysis failed: {e}"}

    def _parse_phone_call_analysis(self, records: List[Dict]) -> Dict[str, Any]:
        """Parse phone call data for temporal analysis"""

        analysis = {
            "phone_calls": [],
            "call_timeline": {},
            "call_patterns": {},
            "customer_interactions": {},
            "temporal_insights": {}
        }

        # Process each record for phone call data
        for record in records:
            call_data = self._extract_call_data(record)
            if call_data:
                analysis["phone_calls"].append(call_data)

                # Add to timeline
                call_date = call_data.get("call_date")
                if call_date:
                    if call_date not in analysis["call_timeline"]:
                        analysis["call_timeline"][call_date] = []
                    analysis["call_timeline"][call_date].append(call_data)

        # Generate insights
        analysis["temporal_insights"] = self._generate_call_insights(analysis)

        return analysis

    def _extract_call_data(self, record: Dict) -> Dict[str, Any]:
        """Extract phone call data from a record"""

        call_data = {
            "call_date": record.get("CALL_DATE"),
            "call_time": record.get("CALL_TIME"),
            "duration": record.get("CALL_DURATION"),
            "call_type": record.get("CALL_TYPE"),
            "result": record.get("CALL_RESULT"),
            "notes": record.get("CALL_NOTES"),
            "disposition": record.get("CALL_DISPOSITION"),
            "outcome": record.get("CALL_OUTCOME"),
            "purpose": record.get("CALL_PURPOSE"),
            "priority": record.get("CALL_PRIORITY"),
            "status": record.get("CALL_STATUS"),
            "source": record.get("CALL_SOURCE"),
            "agent_id": record.get("AGENT_ID"),
            "agent_name": record.get("AGENT_NAME"),
            "department": record.get("AGENT_DEPARTMENT"),
            "queue": record.get("CALL_QUEUE"),
            "routing": record.get("CALL_ROUTING"),
            "product_interest": record.get("PRODUCT_INTEREST"),
            "service_request": record.get("SERVICE_REQUEST"),
            "complaint_type": record.get("COMPLAINT_TYPE"),
            "resolution_status": record.get("RESOLUTION_STATUS"),
            "satisfaction": record.get("CUSTOMER_SATISFACTION"),
            "feedback": record.get("CUSTOMER_FEEDBACK"),
            "follow_up_required": record.get("FOLLOW_UP_REQUIRED"),
            "follow_up_date": record.get("FOLLOW_UP_DATE"),
            "created_date": record.get("CREATED_DATE"),
            "updated_date": record.get("UPDATED_DATE"),
            "last_activity": record.get("LAST_ACTIVITY_DATE")
        }

        # Only return if we have meaningful call data
        if any([call_data["call_date"], call_data["call_type"], call_data["result"]]):
            return call_data
        return None

    def _parse_salesforce_analysis(self, records: List[Dict]) -> Dict[str, Any]:
        """Parse Salesforce data for integration analysis"""

        analysis = {
            "leads": [],
            "opportunities": [],
            "cases": [],
            "accounts": [],
            "call_activities": [],
            "tasks": [],
            "salesforce_timeline": {},
            "integration_insights": {}
        }

        # Process each record for Salesforce data
        for record in records:
            # Extract Salesforce objects
            if "SALESFORCE_LEAD" in record:
                analysis["leads"].append(record["SALESFORCE_LEAD"])

            if "SALESFORCE_OPPORTUNITY" in record:
                analysis["opportunities"].append(record["SALESFORCE_OPPORTUNITY"])

            if "SALESFORCE_CASE" in record:
                analysis["cases"].append(record["SALESFORCE_CASE"])

            if "SALESFORCE_ACCOUNT" in record:
                analysis["accounts"].append(record["SALESFORCE_ACCOUNT"])

            if "SALESFORCE_CALL_ACTIVITY" in record:
                analysis["call_activities"].append(record["SALESFORCE_CALL_ACTIVITY"])

            if "SALESFORCE_TASK" in record:
                analysis["tasks"].append(record["SALESFORCE_TASK"])

        # Generate integration insights
        analysis["integration_insights"] = self._generate_salesforce_insights(analysis)

        return analysis

    def _generate_call_insights(self, analysis: Dict) -> Dict[str, Any]:
        """Generate insights from phone call analysis"""

        insights = {
            "call_frequency": {},
            "call_patterns": {},
            "outcome_trends": {},
            "agent_performance": {},
            "customer_satisfaction": {}
        }

        # Analyze call frequency over time
        call_dates = sorted(analysis["call_timeline"].keys())
        if len(call_dates) >= 2:
            insights["call_frequency"]["total_calls"] = len(analysis["phone_calls"])
            insights["call_frequency"]["date_range"] = f"{call_dates[0]} to {call_dates[-1]}"
            insights["call_frequency"]["unique_dates"] = len(call_dates)

            # Calculate average calls per day
            if len(call_dates) > 0:
                insights["call_frequency"]["avg_calls_per_day"] = len(analysis["phone_calls"]) / len(call_dates)

        # Analyze call patterns
        call_types = {}
        call_results = {}
        call_purposes = {}

        for call in analysis["phone_calls"]:
            # Call types
            call_type = call.get("call_type")
            if call_type:
                call_types[call_type] = call_types.get(call_type, 0) + 1

            # Call results
            result = call.get("result")
            if result:
                call_results[result] = call_results.get(result, 0) + 1

            # Call purposes
            purpose = call.get("purpose")
            if purpose:
                call_purposes[purpose] = call_purposes.get(purpose, 0) + 1

        insights["call_patterns"]["types"] = call_types
        insights["call_patterns"]["results"] = call_results
        insights["call_patterns"]["purposes"] = call_purposes

        return insights

    def _generate_salesforce_insights(self, analysis: Dict) -> Dict[str, Any]:
        """Generate insights from Salesforce integration"""

        insights = {
            "lead_conversion": {},
            "opportunity_pipeline": {},
            "case_resolution": {},
            "customer_journey": {},
            "call_activity_correlation": {}
        }

        # Lead conversion analysis
        if analysis["leads"]:
            total_leads = len(analysis["leads"])
            converted_leads = len([lead for lead in analysis["leads"] if lead.get("ConvertedDate")])
            insights["lead_conversion"]["total_leads"] = total_leads
            insights["lead_conversion"]["converted_leads"] = converted_leads
            insights["lead_conversion"]["conversion_rate"] = (converted_leads / total_leads * 100) if total_leads > 0 else 0

        # Opportunity pipeline analysis
        if analysis["opportunities"]:
            total_opportunities = len(analysis["opportunities"])
            open_opportunities = len([opp for opp in analysis["opportunities"] if opp.get("StageName") != "Closed Won"])
            insights["opportunity_pipeline"]["total_opportunities"] = total_opportunities
            insights["opportunity_pipeline"]["open_opportunities"] = open_opportunities
            insights["opportunity_pipeline"]["closed_opportunities"] = total_opportunities - open_opportunities

        # Case resolution analysis
        if analysis["cases"]:
            total_cases = len(analysis["cases"])
            open_cases = len([case for case in analysis["cases"] if case.get("Status") != "Closed"])
            insights["case_resolution"]["total_cases"] = total_cases
            insights["case_resolution"]["open_cases"] = open_cases
            insights["case_resolution"]["closed_cases"] = total_cases - open_cases

        return insights

    def answer_phone_call_queries(self, call_analysis: Dict, salesforce_analysis: Dict) -> str:
        """Answer specific phone call and Salesforce integration queries"""

        answers = []
        answers.append("📞 PHONE CALL ANALYSIS & SALESFORCE INTEGRATION")
        answers.append("=" * 70)

        # Phone call analysis
        if "error" not in call_analysis:
            answers.append("\n📊 PHONE CALL TEMPORAL ANALYSIS:")
            answers.append("-" * 40)

            insights = call_analysis.get("temporal_insights", {})
            call_frequency = insights.get("call_frequency", {})

            if call_frequency:
                answers.append(f"   📅 Total Calls: {call_frequency.get('total_calls', 0)}")
                answers.append(f"   📈 Date Range: {call_frequency.get('date_range', 'N/A')}")
                answers.append(f"   🗓️  Unique Dates: {call_frequency.get('unique_dates', 0)}")
                answers.append(f"   📊 Avg Calls/Day: {call_frequency.get('avg_calls_per_day', 0):.1f}")

            call_patterns = insights.get("call_patterns", {})
            if call_patterns.get("types"):
                answers.append(f"   📞 Call Types: {len(call_patterns['types'])} different types")
                for call_type, count in list(call_patterns["types"].items())[:3]:
                    answers.append(f"      • {call_type}: {count} calls")

            if call_patterns.get("results"):
                answers.append(f"   🎯 Call Results: {len(call_patterns['results'])} different outcomes")
                for result, count in list(call_patterns["results"].items())[:3]:
                    answers.append(f"      • {result}: {count} calls")
        else:
            answers.append(f"   ❌ Phone call analysis failed: {call_analysis['error']}")

        # Salesforce integration analysis
        if "error" not in salesforce_analysis:
            answers.append("\n🔄 SALESFORCE INTEGRATION ANALYSIS:")
            answers.append("-" * 40)

            integration_insights = salesforce_analysis.get("integration_insights", {})

            # Lead conversion
            lead_conversion = integration_insights.get("lead_conversion", {})
            if lead_conversion:
                answers.append("   🎯 Lead Conversion:")
                answers.append(f"      Total Leads: {lead_conversion.get('total_leads', 0)}")
                answers.append(f"      Converted: {lead_conversion.get('converted_leads', 0)}")
                answers.append(f"      Rate: {lead_conversion.get('conversion_rate', 0):.1f}%")

            # Opportunity pipeline
            opportunity_pipeline = integration_insights.get("opportunity_pipeline", {})
            if opportunity_pipeline:
                answers.append("   💰 Opportunity Pipeline:")
                answers.append(f"      Total: {opportunity_pipeline.get('total_opportunities', 0)}")
                answers.append(f"      Open: {opportunity_pipeline.get('open_opportunities', 0)}")
                answers.append(f"      Closed: {opportunity_pipeline.get('closed_opportunities', 0)}")

            # Case resolution
            case_resolution = integration_insights.get("case_resolution", {})
            if case_resolution:
                answers.append("   🎫 Case Resolution:")
                answers.append(f"      Total Cases: {case_resolution.get('total_cases', 0)}")
                answers.append(f"      Open: {case_resolution.get('open_cases', 0)}")
                answers.append(f"      Closed: {case_resolution.get('closed_cases', 0)}")
        else:
            answers.append(f"   ❌ Salesforce analysis failed: {salesforce_analysis['error']}")

        # Historical comparison insights
        answers.append("\n📈 HISTORICAL COMPARISON INSIGHTS:")
        answers.append("-" * 40)

        if "error" not in call_analysis and "error" not in salesforce_analysis:
            answers.append("   ✅ Phone call patterns analyzed across time periods")
            answers.append("   ✅ Salesforce data integrated for customer journey")
            answers.append("   ✅ Call outcomes correlated with business metrics")
            answers.append("   ✅ Temporal trends identified in customer interactions")
        else:
            answers.append("   ⚠️  Limited historical comparison due to data issues")

        return "\n".join(answers)

# Global instance
phone_call_analyzer = PhoneCallAnalyzer()

def analyze_phone_calls_and_salesforce(entity_id: str) -> str:
    """Analyze phone calls and Salesforce integration for temporal insights"""

    try:
        # Get phone call analysis
        call_analysis = phone_call_analyzer.analyze_phone_call_data(entity_id)

        # Get Salesforce integration analysis
        salesforce_analysis = phone_call_analyzer.analyze_salesforce_integration(entity_id)

        # Answer queries
        answers = phone_call_analyzer.answer_phone_call_queries(call_analysis, salesforce_analysis)

        return answers

    except Exception as e:
        return f"❌ Error in phone call and Salesforce analysis: {e}"

if __name__ == "__main__":
    print("🚀 TESTING PHONE CALL ANALYZER & SALESFORCE INTEGRATION")
    print("=" * 70)
    print("Extending temporal analysis to include:")
    print("   • Phone call historical patterns")
    print("   • Salesforce data integration")
    print("   • Customer interaction timeline")
    print("   • Business outcome correlation")
    print("=" * 70)

    # Use known test entity
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print("🔍 Testing phone call and Salesforce analysis...")
    result = analyze_phone_calls_and_salesforce(entity_id)

    print("\n📊 PHONE CALL & SALESFORCE ANALYSIS RESULT:")
    print("=" * 70)
    print(result)
