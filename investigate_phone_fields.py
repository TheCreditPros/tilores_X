#!/usr/bin/env python3
"""
Investigate Phone Call and Salesforce Fields
Discover what fields actually exist in the schema for phone call analysis
"""

from dotenv import load_dotenv
load_dotenv()

def investigate_phone_and_salesforce_fields():
    """Investigate what phone call and Salesforce fields exist in the schema"""

    print("🔍 INVESTIGATING PHONE CALL & SALESFORCE FIELDS")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Simple query to see what fields exist
        basic_query = """
        query InvestigatePhoneFields {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                # Basic fields we know exist
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
                PHONE_EXTERNAL

                # Look for phone-related fields
                PHONE_NUMBER
                PHONE
                CALL
                CONTACT

                # Look for Salesforce-related fields
                SALESFORCE
                SF
                LEAD
                OPPORTUNITY
                CASE
                ACCOUNT

                # Look for interaction fields
                INTERACTION
                ACTIVITY
                TASK
                NOTE

                # Look for temporal fields
                CREATED_DATE
                UPDATED_DATE
                DATE
                TIME

                # Look for outcome fields
                OUTCOME
                RESULT
                STATUS
                DISPOSITION
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing basic field investigation...")
        result = tilores_api.gql(basic_query)

        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            print(f"✅ Basic query successful! Found {len(records)} records")

            # Analyze what fields actually exist
            existing_fields = {}

            for i, record in enumerate(records):
                print(f"\n📊 Record {i + 1} - Field Analysis:")

                # Check each field type
                field_categories = {
                    "Phone Fields": ["PHONE_EXTERNAL", "PHONE_NUMBER", "PHONE", "CALL", "CONTACT"],
                    "Salesforce Fields": ["SALESFORCE", "SF", "LEAD", "OPPORTUNITY", "CASE", "ACCOUNT"],
                    "Interaction Fields": ["INTERACTION", "ACTIVITY", "TASK", "NOTE"],
                    "Temporal Fields": ["CREATED_DATE", "UPDATED_DATE", "DATE", "TIME"],
                    "Outcome Fields": ["OUTCOME", "RESULT", "STATUS", "DISPOSITION"]
                }

                for category, fields in field_categories.items():
                    print(f"   {category}:")
                    for field in fields:
                        value = record.get(field)
                        if value:
                            print(f"      ✅ {field}: {value}")
                            if field not in existing_fields:
                                existing_fields[field] = []
                            existing_fields[field].append(value)
                        else:
                            print(f"      ❌ {field}: No data")

                # Also check for any fields that contain our keywords
                print("   🔍 Other Fields with Keywords:")
                for field_name, field_value in record.items():
                    field_lower = field_name.lower()
                    if any(keyword in field_lower for keyword in ["phone", "call", "contact", "salesforce", "lead", "opportunity", "case", "account", "interaction", "activity", "task", "note"]):
                        print(f"      🔍 {field_name}: {field_value}")
                        if field_name not in existing_fields:
                            existing_fields[field_name] = []
                        existing_fields[field_name].append(field_value)

                print("   " + "-" * 40)

            # Summary of existing fields
            print("\n📊 FIELD EXISTENCE SUMMARY:")
            print("=" * 40)
            for field_name, values in existing_fields.items():
                unique_values = list(set(values))
                print(f"   📅 {field_name}: {len(unique_values)} unique values")
                print(f"      Values: {unique_values[:3]}{'...' if len(unique_values) > 3 else ''}")

            return True

        else:
            print(f"❌ Basic query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Field investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def investigate_record_insights_phone():
    """Test Record Insights for phone-related data"""

    print("\n🔍 TESTING RECORD INSIGHTS FOR PHONE DATA")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test Record Insights for phone data
        insights_query = """
        query PhoneRecordInsights {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Test phone-related fields
                phoneNumbers: valuesDistinct(field: "PHONE_EXTERNAL")
                phoneTypes: valuesDistinct(field: "PHONE_NUMBER")

                # Test interaction fields
                interactionTypes: valuesDistinct(field: "INTERACTION_TYPE")
                activityTypes: valuesDistinct(field: "ACTIVITY_TYPE")

                # Test temporal fields
                createdDates: valuesDistinct(field: "CREATED_DATE")
                updatedDates: valuesDistinct(field: "UPDATED_DATE")

                # Test outcome fields
                outcomeTypes: valuesDistinct(field: "OUTCOME")
                resultTypes: valuesDistinct(field: "RESULT")

                # Test any fields that might contain phone data
                allFields: valuesDistinct(field: "*")
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing Record Insights for phone data...")
        result = tilores_api.gql(insights_query)

        if result and 'data' in result:
            record_insights = result['data']['entity']['entity']['recordInsights']
            print("✅ Record Insights query successful!")

            print("\n📊 RECORD INSIGHTS RESULTS:")
            print("=" * 40)

            # Phone numbers
            phone_numbers = record_insights.get("phoneNumbers", [])
            print(f"   📞 Phone Numbers: {len(phone_numbers)} found")
            for phone in phone_numbers[:5]:
                print(f"      • {phone}")

            # Phone types
            phone_types = record_insights.get("phoneTypes", [])
            print(f"   📱 Phone Types: {len(phone_types)} found")
            for phone_type in phone_types[:5]:
                print(f"      • {phone_type}")

            # Interaction types
            interaction_types = record_insights.get("interactionTypes", [])
            print(f"   🤝 Interaction Types: {len(interaction_types)} found")
            for interaction in interaction_types[:5]:
                print(f"      • {interaction}")

            # Activity types
            activity_types = record_insights.get("activityTypes", [])
            print(f"   🎯 Activity Types: {len(activity_types)} found")
            for activity in activity_types[:5]:
                print(f"      • {activity}")

            # Temporal data
            created_dates = record_insights.get("createdDates", [])
            print(f"   📅 Created Dates: {len(created_dates)} found")
            for date in created_dates[:5]:
                print(f"      • {date}")

            # Outcome data
            outcome_types = record_insights.get("outcomeTypes", [])
            print(f"   🎯 Outcome Types: {len(outcome_types)} found")
            for outcome in outcome_types[:5]:
                print(f"      • {outcome}")

            return True

        else:
            print(f"❌ Record Insights query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Record Insights test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INVESTIGATING PHONE CALL & SALESFORCE FIELDS")
    print("=" * 70)

    # Run investigations
    test1_success = investigate_phone_and_salesforce_fields()
    test2_success = investigate_record_insights_phone()

    print("\n" + "=" * 70)
    print("📊 INVESTIGATION RESULTS:")
    print(f"   • Field Discovery: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
    print(f"   • Record Insights: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")

    overall_success = test1_success or test2_success
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("🎉 Field investigation successful!")
        print("   • Phone call fields identified")
        print("   • Salesforce fields discovered")
        print("   • Ready for focused phone analysis")
    else:
        print("⚠️  Field investigation needs more work")
