#!/usr/bin/env python3
"""
Test Credit Data in Records Array with Correct Field Names
Using the working field structure from debug_available_fields.py
"""

from dotenv import load_dotenv
load_dotenv()

def test_records_array_with_correct_fields():
    """Test records array access using fields that actually exist"""
    
    print("🔍 TESTING RECORDS ARRAY WITH CORRECT FIELD NAMES")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        # Use the known working entity ID
        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"
        print(f"🎯 Testing entity: {entity_id}")
        
        # Test 1: Access records array with fields that actually exist
        print("\n🔍 TEST 1: Records Array with Working Fields")
        working_records_query = """
        query WorkingRecordsAccess {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              records {{
                id
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
                PHONE_EXTERNAL
                CUSTOMER_AGE
                DATE_OF_BIRTH
                ENROLL_DATE
                STATUS
                PRODUCT_NAME
                AMOUNT
                TRANSACTION_AMOUNT
                CARD_TYPE
                PAYMENT_METHOD
                # Check for any additional fields that might contain credit data
                __typename
              }}
            }}
          }}
        }}
        """
        
        try:
            result = tilores_api.gql(working_records_query)
            if result and 'data' in result:
                records = result['data']['entity']['entity']['records']
                print(f"   📊 Found {len(records)} records")
                
                # Check each record for credit-related data
                credit_data_found = False
                for i, record in enumerate(records):
                    print(f"   📄 Record {i + 1}:")
                    
                    # Check for credit-related data in known fields
                    credit_indicators = []
                    
                    # Check if any field values contain credit-related information
                    for key, value in record.items():
                        if value is not None:
                            value_str = str(value).upper()
                            if any(term in value_str for term in ['CREDIT', 'SCORE', 'BUREAU', 'EXPERIAN', 'TRANSUNION', 'EQUIFAX']):
                                credit_indicators.append(f"{key}: {value}")
                    
                    if credit_indicators:
                        credit_data_found = True
                        print(f"      ✅ Credit indicators found: {credit_indicators}")
                    else:
                        print("      ❌ No credit indicators")
                    
                    # Show record summary
                    email = record.get('EMAIL', 'N/A')
                    name = record.get('FIRST_NAME', 'N/A')
                    product = record.get('PRODUCT_NAME', 'N/A')
                    amount = record.get('AMOUNT', 'N/A')
                    print(f"      Summary: {name} | {email} | {product} | ${amount}")
                
                if credit_data_found:
                    print("\n🎉 SUCCESS: Credit-related data found in records!")
                    return True
                else:
                    print("\n📊 Records analyzed: No credit data found in known fields")
                    print("   This suggests credit data may be in different field names")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Working records query failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_available_fields():
    """Test to see all available fields in records"""
    
    print("\n🔍 TEST 2: Discover All Available Fields in Records")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"
        
        # Get all available fields from records
        all_fields_query = """
        query AllAvailableFields {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                id
                # Get all available fields to discover credit data
                __typename
                # Include known working fields
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
                PHONE_EXTERNAL
                CUSTOMER_AGE
                DATE_OF_BIRTH
                ENROLL_DATE
                STATUS
                PRODUCT_NAME
                AMOUNT
                TRANSACTION_AMOUNT
                CARD_TYPE
                PAYMENT_METHOD
              }}
            }}
          }}
        }}
        """
        
        try:
            result = tilores_api.gql(all_fields_query)
            if result and 'data' in result:
                records = result['data']['entity']['entity']['records']
                print(f"   📊 Found {len(records)} records")
                
                if records:
                    # Get all unique field names from all records
                    all_fields = set()
                    for record in records:
                        all_fields.update(record.keys())
                    
                    print(f"   📋 Total unique fields found: {len(all_fields)}")
                    
                    # Look for credit-related fields
                    credit_fields = [f for f in all_fields if any(term in f.upper() for term in ['CREDIT', 'SCORE', 'BUREAU', 'EXPERIAN', 'TRANSUNION', 'EQUIFAX'])]
                    
                    if credit_fields:
                        print(f"   ✅ Credit-related fields found: {credit_fields}")
                        return True
                    else:
                        print("   ❌ No credit-related fields found")
                        print(f"   📋 All available fields: {sorted(list(all_fields))}")
                        return False
                else:
                    print("   ❌ No records found")
                    return False
                    
        except Exception as e:
            print(f"   ❌ All fields query failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Field discovery failed: {e}")
        return False

def test_search_entities_structure():
    """Test the search entities structure to understand where credit data is"""
    
    print("\n🔍 TEST 3: Search Entities Structure Analysis")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        # Test the search structure that was shown in the image
        search_query = """
        query SearchEntitiesStructure {
          search(input: { parameters: { EMAIL: "e.j.price1986@gmail.com" } }) {
            entities {
              id
              hits
              duplicates
              edges
              recordInsights {
                __typename
              }
              records {
                id
                __typename
              }
            }
          }
        }
        """
        
        try:
            result = tilores_api.gql(search_query)
            if result and 'data' in result:
                entities = result['data']['search']['entities']
                print(f"   📊 Found {len(entities)} entities")
                
                if entities:
                    entity = entities[0]
                    print(f"   🎯 Entity ID: {entity.get('id', 'Unknown')}")
                    
                    # Check for records array
                    records = entity.get('records', [])
                    print(f"   📄 Records: {len(records)} records found")
                    
                    # Check for recordInsights
                    record_insights = entity.get('recordInsights', {})
                    print(f"   🔍 Record Insights: {len(record_insights) if record_insights else 0} fields")
                    
                    # Check for hits and duplicates
                    hits = entity.get('hits', {})
                    duplicates = entity.get('duplicates', {})
                    print(f"   🎯 Hits: {len(hits)} hit groups")
                    print(f"   🔄 Duplicates: {len(duplicates)} duplicate groups")
                    
                    return len(records) > 0
                else:
                    print("   ❌ No entities found")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Search structure query failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Search structure analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING RECORDS ARRAY WITH CORRECT FIELD NAMES")
    print("=" * 70)
    
    # Run all tests
    test1_success = test_records_array_with_correct_fields()
    test2_success = test_all_available_fields()
    test3_success = test_search_entities_structure()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS:")
    print(f"   • Records with Working Fields: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
    print(f"   • Field Discovery: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")
    print(f"   • Search Structure Analysis: {'✅ SUCCESS' if test3_success else '❌ FAILED'}")
    
    overall_success = any([test1_success, test2_success, test3_success])
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        print("🎉 Records array access working!")
        print("   Next: Analyze discovered fields for credit data")
    else:
        print("⚠️  Records array access needs investigation")
