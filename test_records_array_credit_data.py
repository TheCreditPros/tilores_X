#!/usr/bin/env python3
"""
Test Credit Data in Records Array
Based on user insight that credit reports appear in the records array
"""

from dotenv import load_dotenv
load_dotenv()

def test_credit_data_in_records_array():
    """Test for credit data in the records array structure"""
    
    print("🔍 TESTING CREDIT DATA IN RECORDS ARRAY")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        # Use the known working entity ID
        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"
        print(f"🎯 Testing entity: {entity_id}")
        
        # Test 1: Access records array directly to find credit data
        print("\n🔍 TEST 1: Direct Records Array Access")
        records_query = """
        query RecordsArrayCreditData {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                id
                # Check for credit-related fields in each record
                CREDIT_RESPONSE
                CREDIT_SCORE
                CREDIT_INQUIRY
                CREDIT_LIABILITY
                Bureau
                CreditScore
                CreditReport
                Experian
                TransUnion
                Equifax
                # Check for any fields that might contain credit data
                __typename
              }}
            }}
          }}
        }}
        """
        
        try:
            result = tilores_api.gql(records_query)
            if result and 'data' in result:
                records = result['data']['entity']['entity']['records']
                print(f"   📊 Found {len(records)} records")
                
                # Check each record for credit data
                credit_records = []
                for i, record in enumerate(records):
                    credit_fields = {}
                    for key, value in record.items():
                        if value is not None and any(term in str(key).upper() for term in ['CREDIT', 'SCORE', 'BUREAU', 'EXPERIAN', 'TRANSUNION', 'EQUIFAX']):
                            credit_fields[key] = value
                    
                    if credit_fields:
                        credit_records.append((i, credit_fields))
                        print(f"   📄 Record {i + 1}: ✅ Credit fields found")
                        for field, val in credit_fields.items():
                            print(f"      {field}: {val}")
                    else:
                        print(f"   📄 Record {i + 1}: ❌ No credit fields")
                
                if credit_records:
                    print(f"\n🎉 SUCCESS: Found {len(credit_records)} records with credit data!")
                    return True
                else:
                    print("\n❌ No credit data found in records array")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Records query failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_records_array_structure():
    """Test the structure of the records array to understand credit data layout"""
    
    print("\n🔍 TEST 2: Records Array Structure Analysis")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"
        
        # Get a sample record to analyze its structure
        sample_record_query = """
        query SampleRecordStructure {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records(limit: 1) {{
                id
                # Get all available fields to understand structure
                __typename
                # Check for any nested credit objects
                CREDIT_RESPONSE
                CREDIT_SCORE
                CREDIT_INQUIRY
                CREDIT_LIABILITY
                # Check for bureau-specific data
                Experian
                TransUnion
                Equifax
                # Check for credit report data
                CreditReport
                CreditScore
                Bureau
                # Check for any other fields that might contain credit data
                __typename
              }}
            }}
          }}
        }}
        """
        
        try:
            result = tilores_api.gql(sample_record_query)
            if result and 'data' in result:
                records = result['data']['entity']['entity']['records']
                if records:
                    record = records[0]
                    print("   📊 Sample Record Analysis:")
                    print(f"   Record ID: {record.get('id', 'Unknown')}")
                    print(f"   Type: {record.get('__typename', 'Unknown')}")
                    
                    # Check for credit-related fields
                    credit_fields = []
                    all_fields = []
                    
                    for key, value in record.items():
                        all_fields.append(key)
                        if value is not None and any(term in str(key).upper() for term in ['CREDIT', 'SCORE', 'BUREAU', 'EXPERIAN', 'TRANSUNION', 'EQUIFAX']):
                            credit_fields.append((key, value))
                    
                    print(f"   Total fields: {len(all_fields)}")
                    print(f"   Credit-related fields: {len(credit_fields)}")
                    
                    if credit_fields:
                        print("   ✅ Credit fields found:")
                        for field, val in credit_fields:
                            print(f"      {field}: {val}")
                    else:
                        print("   ❌ No credit fields in sample record")
                        print(f"   📋 All available fields: {all_fields[:20]}...")  # Show first 20
                    
                    return len(credit_fields) > 0
                else:
                    print("   ❌ No records found")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Sample record query failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Structure analysis failed: {e}")
        return False

def test_credit_data_extraction():
    """Test extracting credit data from the records array"""
    
    print("\n🔍 TEST 3: Credit Data Extraction from Records")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"
        
        # Try to extract credit data from records array
        credit_extraction_query = """
        query CreditDataExtraction {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                id
                # Try to access nested credit data
                CREDIT_RESPONSE {{
                  CREDIT_SCORE {{
                    Value
                    ModelNameType
                  }}
                  Bureau
                  Date
                  CREDIT_INQUIRY {{
                    Name
                    Date
                  }}
                  CREDIT_LIABILITY {{
                    AccountType
                    Balance
                    CreditLimit
                    PaymentPattern
                  }}
                }}
                # Alternative credit data paths
                Experian
                TransUnion
                Equifax
                CreditReport
                CreditScore
                Bureau
              }}
            }}
          }}
        }}
        """
        
        try:
            result = tilores_api.gql(credit_extraction_query)
            if result and 'data' in result:
                records = result['data']['entity']['entity']['records']
                print(f"   📊 Extracted data from {len(records)} records")
                
                credit_data_found = False
                for i, record in enumerate(records):
                    if record.get('CREDIT_RESPONSE'):
                        credit_data_found = True
                        credit_response = record['CREDIT_RESPONSE']
                        print(f"   📄 Record {i + 1}: Credit data found")
                        
                        if credit_response.get('CREDIT_SCORE'):
                            scores = credit_response['CREDIT_SCORE']
                            print(f"      Credit Scores: {scores}")
                        
                        if credit_response.get('Bureau'):
                            bureau = credit_response['Bureau']
                            print(f"      Bureau: {bureau}")
                        
                        if credit_response.get('Date'):
                            date = credit_response['Date']
                            print(f"      Date: {date}")
                
                if credit_data_found:
                    print("\n🎉 SUCCESS: Credit data extracted from records array!")
                    return True
                else:
                    print("\n❌ No credit data found in records array")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Credit extraction query failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Credit data extraction failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING CREDIT DATA IN RECORDS ARRAY")
    print("=" * 70)
    
    # Run all tests
    test1_success = test_credit_data_in_records_array()
    test2_success = test_records_array_structure()
    test3_success = test_credit_data_extraction()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS:")
    print(f"   • Records Array Access: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
    print(f"   • Structure Analysis: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")
    print(f"   • Credit Data Extraction: {'✅ SUCCESS' if test3_success else '❌ FAILED'}")
    
    overall_success = any([test1_success, test2_success, test3_success])
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        print("🎉 Credit data found in records array!")
        print("   The user's insight was correct - credit reports are in records, not recordInsights")
        print("   Next: Update enhanced credit tool to use records array")
    else:
        print("⚠️  Credit data not found in records array")
        print("   May need to investigate different field paths or data structure")
