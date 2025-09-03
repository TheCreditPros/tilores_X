#!/usr / bin / env python3
"""
Comprehensive Phone Call Data Extractor
Extracts ALL phone call data with complete fields and entities
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class ComprehensivePhoneCallExtractor:
    """Extracts complete phone call data from Tilores"""

    def __init__(self):
        self.tilores_api = None
        self.test_customer_email = "e.j.price1986@gmail.com"
        self.entity_id = "dc93a2cd - de0a - 444f - ad47 - 3003ba998cd3"

    def initialize_tilores(self) -> bool:
        """Initialize Tilores API connection"""
        try:
            from tilores import TiloresAPI
            self.tilores_api = TiloresAPI.from_environ()
            print("✅ Tilores API initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Tilores API: {e}")
            return False

    def extract_comprehensive_phone_data(self) -> Optional[Dict[str, Any]]:
        """Extract comprehensive phone call data using detailed query"""

        print(f"📞 Extracting comprehensive phone data for entity {self.entity_id}...")

        # Comprehensive phone call query with all possible fields
        phone_query = """
        query ComprehensivePhoneData {{
          entity(input: {{ id: "{self.entity_id}" }}) {{
            entity {{
              records {{
                id

                # Basic phone fields
                PHONE_NUMBER
                PHONE_EXTERNAL

                # Call data fields
                CALL_ID
                CALL_START_TIME
                CALL_HANGUP_TIME
                CALL_DURATION
                CALL_TYPE

                # Contact fields
                CONTACT_TYPE
                CONTACT_NEW

                # Zoho integration fields
                ZOHO_CONTACT_ID
                ZOHO_PHONE
                ZOHO_ID
                ZOHO_EMAIL
                ZOHO_STATUS

                # Agent and campaign fields
                AGENT_USERNAME
                CAMPAIGN_NAME

                # Additional phone - related fields that might exist
                PHONE_CONFIRMED
                PHONE_VERIFIED
                PHONE_PRIMARY
                PHONE_MOBILE
                PHONE_HOME
                PHONE_WORK
                PHONE_OTHER

                # Call outcome fields
                CALL_OUTCOME
                CALL_RESULT
                CALL_STATUS
                CALL_NOTES
                CALL_DISPOSITION

                # Call quality fields
                CALL_QUALITY
                CALL_RATING
                CALL_FEEDBACK

                # Call routing fields
                CALL_QUEUE
                CALL_DEPARTMENT
                CALL_TRANSFERRED

                # Timing fields
                CALL_WAIT_TIME
                CALL_TALK_TIME
                CALL_HOLD_TIME

                # System fields that might relate to calls
                SOURCE
                SOURCE_TYPE
                CREATED_DATE
                CREATEDTIME

                # Customer service fields
                TICKETNUMBER
                CATEGORY
                SUBCATEGORY
                PRIORITY
                SUBJECT

                # Identity fields for context
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(phone_query)

            if result and 'data' in result and result['data']['entity']['entity']['records']:
                records = result['data']['entity']['entity']['records']
                print(f"✅ Retrieved {len(records)} records for phone analysis")
                return records
            else:
                print("❌ No records returned")
                return None

        except Exception as e:
            print(f"❌ Phone data query failed: {e}")
            return None

    def try_phone_insights_approach(self) -> Optional[Dict[str, Any]]:
        """Try using Record Insights to get aggregated phone data"""

        print("📞 Trying Record Insights approach for phone data...")

        insights_query = """
        query PhoneInsights {{
          entity(input: {{ id: "{self.entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Phone number insights
                phoneNumbers: valuesDistinct(field: "PHONE_NUMBER")
                externalPhones: valuesDistinct(field: "PHONE_EXTERNAL")
                zohoPhones: valuesDistinct(field: "ZOHO_PHONE")

                # Call insights
                callIds: valuesDistinct(field: "CALL_ID")
                callTypes: valuesDistinct(field: "CALL_TYPE")
                callDurations: valuesDistinct(field: "CALL_DURATION")

                # Contact insights
                contactTypes: valuesDistinct(field: "CONTACT_TYPE")
                zohoContactIds: valuesDistinct(field: "ZOHO_CONTACT_ID")

                # Agent insights
                agents: valuesDistinct(field: "AGENT_USERNAME")
                campaigns: valuesDistinct(field: "CAMPAIGN_NAME")

                # Counts
                totalCallRecords: count(filter: {{field: "CALL_ID", exists: true}})
                totalPhoneRecords: count(filter: {{field: "PHONE_NUMBER", exists: true}})
                totalContactRecords: count(filter: {{field: "CONTACT_TYPE", exists: true}})

                # Temporal analysis
                firstCallRecord: first(filter: {{field: "CALL_ID", exists: true}}) {{
                  CALL_ID
                  CALL_START_TIME
                  CALL_DURATION
                  CALL_TYPE
                }}

                latestCallRecord: newest(filter: {{field: "CALL_ID", exists: true}}) {{
                  CALL_ID
                  CALL_START_TIME
                  CALL_DURATION
                  CALL_TYPE
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(insights_query)

            if result and 'data' in result and result['data']['entity']['entity']['recordInsights']:
                insights = result['data']['entity']['entity']['recordInsights']
                print("✅ Retrieved phone insights")
                return insights
            else:
                print("❌ No phone insights returned")
                return None

        except Exception as e:
            print(f"❌ Phone insights query failed: {e}")
            return None

    def analyze_phone_data(self, records: List[Dict], insights: Dict) -> Dict[str, Any]:
        """Analyze phone data comprehensively"""

        print("📊 Analyzing phone data...")

        phone_analysis = {
            'total_records': len(records) if records else 0,
            'phone_call_records': [],
            'contact_records': [],
            'phone_number_records': [],
            'zoho_integration_records': [],
            'agent_interaction_records': [],
            'phone_field_coverage': {},
            'insights_summary': insights or {},
            'data_availability': {}
        }

        # Phone - related fields to check
        phone_fields = [
            'PHONE_NUMBER', 'PHONE_EXTERNAL', 'CALL_ID', 'CALL_START_TIME',
            'CALL_HANGUP_TIME', 'CALL_DURATION', 'CALL_TYPE', 'CONTACT_TYPE',
            'CONTACT_NEW', 'ZOHO_CONTACT_ID', 'ZOHO_PHONE', 'AGENT_USERNAME',
            'CAMPAIGN_NAME', 'ZOHO_ID', 'ZOHO_EMAIL', 'ZOHO_STATUS'
        ]

        if records:
            for i, record in enumerate(records):
                record_id = record.get('id')

                # Check for call data
                if record.get('CALL_ID'):
                    call_record = {
                        'record_index': i,
                        'record_id': record_id,
                        'call_id': record.get('CALL_ID'),
                        'start_time': record.get('CALL_START_TIME'),
                        'hangup_time': record.get('CALL_HANGUP_TIME'),
                        'duration': record.get('CALL_DURATION'),
                        'call_type': record.get('CALL_TYPE'),
                        'phone_number': record.get('PHONE_NUMBER'),
                        'agent': record.get('AGENT_USERNAME'),
                        'campaign': record.get('CAMPAIGN_NAME')
                    }
                    phone_analysis['phone_call_records'].append(call_record)

                # Check for contact data
                if record.get('CONTACT_TYPE') or record.get('CONTACT_NEW'):
                    contact_record = {
                        'record_index': i,
                        'record_id': record_id,
                        'contact_type': record.get('CONTACT_TYPE'),
                        'contact_new': record.get('CONTACT_NEW'),
                        'phone_number': record.get('PHONE_NUMBER'),
                        'email': record.get('EMAIL'),
                        'name': f"{record.get('FIRST_NAME', '')} {record.get('LAST_NAME', '')}".strip()
                    }
                    phone_analysis['contact_records'].append(contact_record)

                # Check for phone number data
                if record.get('PHONE_NUMBER') or record.get('PHONE_EXTERNAL'):
                    phone_record = {
                        'record_index': i,
                        'record_id': record_id,
                        'phone_number': record.get('PHONE_NUMBER'),
                        'phone_external': record.get('PHONE_EXTERNAL'),
                        'zoho_phone': record.get('ZOHO_PHONE')
                    }
                    phone_analysis['phone_number_records'].append(phone_record)

                # Check for Zoho integration
                if record.get('ZOHO_CONTACT_ID') or record.get('ZOHO_ID'):
                    zoho_record = {
                        'record_index': i,
                        'record_id': record_id,
                        'zoho_contact_id': record.get('ZOHO_CONTACT_ID'),
                        'zoho_id': record.get('ZOHO_ID'),
                        'zoho_email': record.get('ZOHO_EMAIL'),
                        'zoho_status': record.get('ZOHO_STATUS'),
                        'zoho_phone': record.get('ZOHO_PHONE')
                    }
                    phone_analysis['zoho_integration_records'].append(zoho_record)

                # Check for agent interactions
                if record.get('AGENT_USERNAME') or record.get('CAMPAIGN_NAME'):
                    agent_record = {
                        'record_index': i,
                        'record_id': record_id,
                        'agent_username': record.get('AGENT_USERNAME'),
                        'campaign_name': record.get('CAMPAIGN_NAME'),
                        'source': record.get('SOURCE'),
                        'created_date': record.get('CREATED_DATE')
                    }
                    phone_analysis['agent_interaction_records'].append(agent_record)

                # Track field coverage
                for field in phone_fields:
                    value = record.get(field)
                    if value is not None and value != '':
                        if field not in phone_analysis['phone_field_coverage']:
                            phone_analysis['phone_field_coverage'][field] = []
                        phone_analysis['phone_field_coverage'][field].append({
                            'record_index': i,
                            'value': value
                        })

        # Data availability summary
        phone_analysis['data_availability'] = {
            'has_call_records': len(phone_analysis['phone_call_records']) > 0,
            'has_contact_records': len(phone_analysis['contact_records']) > 0,
            'has_phone_numbers': len(phone_analysis['phone_number_records']) > 0,
            'has_zoho_integration': len(phone_analysis['zoho_integration_records']) > 0,
            'has_agent_interactions': len(phone_analysis['agent_interaction_records']) > 0,
            'total_phone_related_records': (
                len(phone_analysis['phone_call_records']) +
                len(phone_analysis['contact_records']) +
                len(phone_analysis['phone_number_records']) +
                len(phone_analysis['zoho_integration_records']) +
                len(phone_analysis['agent_interaction_records'])
            )
        }

        return phone_analysis

def main():
    """Main execution"""
    print("🚀 COMPREHENSIVE PHONE CALL DATA EXTRACTION")
    print("=" * 70)

    extractor = ComprehensivePhoneCallExtractor()

    # Initialize API
    if not extractor.initialize_tilores():
        return

    # Extract comprehensive phone data
    print("\n📞 ATTEMPT 1: Comprehensive Phone Query")
    print("-" * 50)
    phone_records = extractor.extract_comprehensive_phone_data()

    # Try insights approach
    print("\n📞 ATTEMPT 2: Phone Insights Approach")
    print("-" * 50)
    phone_insights = extractor.try_phone_insights_approach()

    # Analyze phone data
    phone_analysis = extractor.analyze_phone_data(phone_records or [], phone_insights or {})

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comprehensive_phone_data_{timestamp}.json"

    results = {
        'metadata': {
            'extraction_timestamp': datetime.now().isoformat(),
            'customer_email': extractor.test_customer_email,
            'entity_id': extractor.entity_id
        },
        'raw_phone_records': phone_records,
        'phone_insights': phone_insights,
        'phone_analysis': phone_analysis
    }

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Saved comprehensive phone data to {filename}")

    # Print analysis summary
    print("\n📊 COMPREHENSIVE PHONE DATA ANALYSIS")
    print("-" * 60)

    analysis = phone_analysis
    availability = analysis['data_availability']

    print(f"Total Records Analyzed: {analysis['total_records']}")
    print(f"Phone Call Records: {len(analysis['phone_call_records'])}")
    print(f"Contact Records: {len(analysis['contact_records'])}")
    print(f"Phone Number Records: {len(analysis['phone_number_records'])}")
    print(f"Zoho Integration Records: {len(analysis['zoho_integration_records'])}")
    print(f"Agent Interaction Records: {len(analysis['agent_interaction_records'])}")

    print("\nData Availability:")
    print(f"  📞 Call Records: {'✅' if availability['has_call_records'] else '❌'}")
    print(f"  👥 Contact Records: {'✅' if availability['has_contact_records'] else '❌'}")
    print(f"  📱 Phone Numbers: {'✅' if availability['has_phone_numbers'] else '❌'}")
    print(f"  🔗 Zoho Integration: {'✅' if availability['has_zoho_integration'] else '❌'}")
    print(f"  👨‍💼 Agent Interactions: {'✅' if availability['has_agent_interactions'] else '❌'}")

    print("\nField Coverage:")
    for field, occurrences in analysis['phone_field_coverage'].items():
        print(f"  • {field}: {len(occurrences)} records")

    if phone_insights:
        print("\nInsights Summary:")
        for key, value in phone_insights.items():
            if value:
                print(f"  • {key}: {value}")

    return filename

if __name__ == "__main__":
    main()


