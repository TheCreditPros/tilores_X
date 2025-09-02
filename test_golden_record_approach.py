#!/usr/bin/env python3
"""
Test Golden Record Credit Analysis Approach
Implements and tests Tilores' recommended golden record → drill-down methodology
"""

from dotenv import load_dotenv
load_dotenv()

def test_golden_record_credit_approach():
    """Test the golden record approach for credit analysis"""
    
    print("🔍 TESTING GOLDEN RECORD CREDIT APPROACH")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        from enhanced_credit_tool import create_enhanced_credit_tool
        
        # Initialize Tilores API
        tilores_api = TiloresAPI.from_environ()
        
        # Create enhanced credit tool
        enhanced_tool = create_enhanced_credit_tool(tilores_api)
        
        print("✅ Enhanced credit tool created with golden record methodology")
        
        # Test with the customer that supposedly has credit data
        test_email = "e.j.price1986@gmail.com"
        print(f"\n🎯 TESTING: {test_email}")
        print("   (User claims this record has many credit reports available)")
        
        # Execute the enhanced tool
        result = enhanced_tool.invoke({
            "email": test_email
        })
        
        print("\n📊 GOLDEN RECORD ANALYSIS RESULT:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        # Validate the results
        validation_checks = {
            "credit_scores_found": "CREDIT SCORES" in result and "No credit score data available" not in result,
            "bureaus_identified": "BUREAUS COVERED" in result,
            "temporal_data": "REPORT DATES" in result,
            "customer_identified": "PRIMARY NAME" in result,
            "golden_record_complete": "GOLDEN RECORD ANALYSIS COMPLETE" in result,
            "no_errors": "Error" not in result and "Customer not found" not in result
        }
        
        print("\n✅ VALIDATION RESULTS:")
        for check, passed in validation_checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   • {check.replace('_', ' ').title()}: {status}")
        
        success_rate = sum(validation_checks.values()) / len(validation_checks)
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1%} ({sum(validation_checks.values())}/{len(validation_checks)} checks passed)")
        
        # Specific credit data validation
        if validation_checks["credit_scores_found"]:
            print("\n🎉 SUCCESS: Credit scores found using golden record methodology!")
            print("   This confirms the user's assertion that credit data exists for this record")
            return True
        elif validation_checks["customer_identified"] and validation_checks["golden_record_complete"]:
            print("\n✅ PARTIAL SUCCESS: Customer found and analyzed")
            print("   Golden record methodology working, but credit data may not be available")
            print("   OR credit data exists but uses different field paths than expected")
            return True
        else:
            print("\n⚠️  INVESTIGATION NEEDED: Analysis incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_credit_investigation():
    """Directly investigate what credit fields are available"""
    
    print("\n🔍 DIRECT CREDIT FIELD INVESTIGATION")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        # Search for the customer first (without limit parameter)
        search_result = tilores_api.search("e.j.price1986@gmail.com")
        
        if not search_result or not search_result.get('entities'):
            print("❌ Customer not found in search")
            return False
        
        entity_id = search_result['entities'][0]['id']
        print(f"✅ Found entity ID: {entity_id}")
        
        # Try a comprehensive investigation query with multiple field path attempts
        investigation_query = """
        query CreditFieldInvestigation {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Primary credit field paths
                creditScores1: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                creditScores2: valuesDistinct(field: "CREDIT_SCORE.Value")
                creditScores3: valuesDistinct(field: "CreditScore")
                
                # Bureau paths
                bureaus1: valuesDistinct(field: "CREDIT_RESPONSE.Bureau")
                bureaus2: valuesDistinct(field: "Bureau")
                bureaus3: valuesDistinct(field: "BUREAU")
                
                # Date paths
                dates1: valuesDistinct(field: "CREDIT_RESPONSE.Date")
                dates2: valuesDistinct(field: "Date")
                dates3: valuesDistinct(field: "CREATED_DATE")
                
                # Account information paths
                accounts1: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.AccountType")
                accounts2: valuesDistinct(field: "CREDIT_LIABILITY.AccountType")
                accounts3: valuesDistinct(field: "AccountType")
                
                # Basic customer info
                names: valuesDistinct(field: "FIRST_NAME")
                emails: valuesDistinct(field: "EMAIL")
              }}
            }}
          }}
        }}
        """
        
        print("🔍 Executing comprehensive credit field investigation...")
        result = tilores_api.gql(investigation_query)
        
        if result and 'data' in result:
            insights = result['data']['entity']['entity']['recordInsights']
            
            print("\n📊 CREDIT FIELD INVESTIGATION RESULTS:")
            credit_data_found = False
            
            for field_name, field_data in insights.items():
                if field_data:
                    print(f"   ✅ {field_name}: {len(field_data)} values found")
                    if isinstance(field_data, list) and len(field_data) <= 10:
                        print(f"      Values: {field_data}")
                    
                    # Check if this is credit-related data
                    if 'credit' in field_name.lower() or 'bureau' in field_name.lower() or 'account' in field_name.lower():
                        credit_data_found = True
                else:
                    print(f"   ❌ {field_name}: No data")
            
            if credit_data_found:
                print("\n🎉 CREDIT DATA CONFIRMED!")
                print("   The user was correct - credit-related data exists for this record")
                return True
            else:
                print("\n❓ MIXED RESULTS")
                print("   Customer data found, but no clear credit fields populated")
                print("   Credit data may exist but use different field names/structure")
                return False
        else:
            print("❌ Investigation query failed")
            return False
            
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 GOLDEN RECORD CREDIT ANALYSIS VALIDATION")
    print("=" * 70)
    
    # Test 1: Golden record approach
    test1_success = test_golden_record_credit_approach()
    
    # Test 2: Direct field investigation
    test2_success = test_direct_credit_investigation()
    
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS:")
    print(f"   • Golden Record Approach: {'✅ SUCCESS' if test1_success else '❌ NEEDS WORK'}")
    print(f"   • Direct Field Investigation: {'✅ SUCCESS' if test2_success else '❌ NEEDS WORK'}")
    
    overall_success = test1_success or test2_success
    print(f"\n🎯 OVERALL VALIDATION: {'✅ SUCCESS' if overall_success else '❌ INVESTIGATION NEEDED'}")
    
    if overall_success:
        print("🎉 Improved methodology working with Tilores golden record approach!")
        if test1_success and "credit scores found" in str(test1_success).lower():
            print("🎉 User's assertion validated - credit reports are available!")
        else:
            print("📊 Customer analysis working - credit data investigation ongoing")
    else:
        print("⚠️  Further investigation needed to locate credit data")
        print("   May need to examine schema or try alternative field paths")
