#!/usr/bin/env python3
"""
Test Enhanced Credit Tool with Record Insights
Validates Date=None fix and complete data relationships
"""

import json
from dotenv import load_dotenv
load_dotenv()

def test_enhanced_credit_tool():
    """Test enhanced credit tool with actual customer data"""

    print("🧪 TESTING ENHANCED CREDIT TOOL WITH RECORD INSIGHTS")
    print("=" * 70)

    try:
        # Initialize engine
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        if not engine or not engine.tools:
            print("❌ Engine not available")
            return False

        # Find enhanced credit tool
        enhanced_credit_tool = None
        for tool in engine.tools:
            if tool.name == "get_customer_credit_report":
                enhanced_credit_tool = tool
                break

        if not enhanced_credit_tool:
            print("❌ Enhanced credit tool not found")
            return False

        print("✅ Enhanced credit tool found")

        # Test with known customer
        print("\n🔍 Testing with e.j.price1986@gmail.com...")

        result = enhanced_credit_tool.invoke({
            "email": "e.j.price1986@gmail.com"
        })

        print("\n📊 ENHANCED CREDIT TOOL RESULT:")
        print("-" * 50)
        print(result)
        print("-" * 50)

        # Validate results
        success_indicators = [
            "Date available" in result or "2023" in result or "2024" in result,  # Date fix
            "CREDIT SCORES:" in result,  # Credit scores section
            "EXCELLENT" in result or "GOOD" in result or "FAIR" in result or "POOR" in result,  # Score ratings
            "Error" not in result or "template" not in result.lower()  # No errors/templates
        ]

        print("\n✅ VALIDATION RESULTS:")
        print(f"   • Date information present: {success_indicators[0]}")
        print(f"   • Credit scores section: {success_indicators[1]}")
        print(f"   • Score ratings present: {success_indicators[2]}")
        print(f"   • No errors/templates: {success_indicators[3]}")

        overall_success = sum(success_indicators) >= 3
        print(f"\n🎯 OVERALL SUCCESS: {overall_success} ({sum(success_indicators)}/4 checks passed)")

        return overall_success

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_experian_specific_query():
    """Test Experian-specific query functionality"""

    print("\n🧪 TESTING EXPERIAN-SPECIFIC FUNCTIONALITY")
    print("=" * 70)

    try:
        # Test direct enhanced tool
        from enhanced_credit_tool import EnhancedCreditTool
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        if not engine or not engine.tilores:
            print("❌ Tilores not available")
            return False

        # Create enhanced tool directly
        enhanced_tool = EnhancedCreditTool(engine.tilores)

        print("🔍 Testing Experian analysis for e.j.price1986@gmail.com...")

        result = enhanced_tool.get_experian_credit_analysis(
            email="e.j.price1986@gmail.com"
        )

        print("\n📊 EXPERIAN ANALYSIS RESULT:")
        print("-" * 50)
        print(result)
        print("-" * 50)

        # Validate Experian-specific results
        experian_indicators = [
            "EXPERIAN" in result.upper(),  # Experian mentioned
            "Date available" in result or "2023" in result or "2024" in result,  # Date info
            "Customer not found" not in result,  # Customer found
            "Error" not in result or len(result) > 100  # Substantial response
        ]

        print("\n✅ EXPERIAN VALIDATION:")
        print(f"   • Experian-specific: {experian_indicators[0]}")
        print(f"   • Date information: {experian_indicators[1]}")
        print(f"   • Customer found: {experian_indicators[2]}")
        print(f"   • Substantial response: {experian_indicators[3]}")

        experian_success = sum(experian_indicators) >= 3
        print(f"\n🎯 EXPERIAN SUCCESS: {experian_success} ({sum(experian_indicators)}/4 checks passed)")

        return experian_success

    except Exception as e:
        print(f"❌ Experian test failed: {e}")
        return False

def test_record_insights_queries():
    """Test Record Insights queries directly"""

    print("\n🧪 TESTING RECORD INSIGHTS QUERIES DIRECTLY")
    print("=" * 70)

    try:
        from enhanced_record_insights_queries import RecordInsightsQueryBuilder
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        if not engine or not engine.tilores:
            print("❌ Tilores not available")
            return False

        # Test entity search first
        search_query = """
        query GetEntityId($searchParams: SearchInput!) {
          search(input: $searchParams) {
            entities {
              id
            }
          }
        }
        """

        variables = {
            "searchParams": {
                "parameters": {"EMAIL": "e.j.price1986@gmail.com"}
            }
        }

        print("🔍 Getting entity ID for e.j.price1986@gmail.com...")

        search_result = engine.tilores.gql(search_query, variables)
        print(f"📊 Search result: {json.dumps(search_result, indent=2)}")

        entities = search_result.get("data", {}).get("search", {}).get("entities", [])
        if not entities:
            print("❌ No entities found")
            return False

        entity_id = entities[0]["id"]
        print(f"✅ Entity ID found: {entity_id}")

        # Test Record Insights query
        query_builder = RecordInsightsQueryBuilder()
        insights_query = query_builder.build_comprehensive_credit_query(entity_id)

        print("\n🔍 Executing Record Insights query...")
        print(f"Query preview: {insights_query[:200]}...")

        insights_result = engine.tilores.gql(insights_query)

        print("\n📊 RECORD INSIGHTS RESULT:")
        print(f"Result keys: {list(insights_result.keys())}")

        if "data" in insights_result:
            entity_data = insights_result["data"].get("entity", {})
            if entity_data:
                insights = entity_data.get("entity", {}).get("recordInsights", {})
                print(f"Record Insights keys: {list(insights.keys())}")

                # Check for credit score data
                all_scores = insights.get("allCreditScores", [])
                score_dates = insights.get("scoreDates", [])

                print(f"Credit scores found: {len(all_scores)}")
                print(f"Score dates found: {len(score_dates)}")

                if all_scores:
                    print(f"Sample scores: {all_scores[:3]}")
                if score_dates:
                    print(f"Sample dates: {score_dates[:3]}")

                insights_success = len(all_scores) > 0 or len(score_dates) > 0
                print(f"\n🎯 RECORD INSIGHTS SUCCESS: {insights_success}")

                return insights_success
            else:
                print("❌ No entity data in response")
                return False
        else:
            print(f"❌ No data in response: {insights_result}")
            return False

    except Exception as e:
        print(f"❌ Record Insights test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 STARTING ENHANCED CREDIT TOOL VALIDATION")
    print("=" * 70)

    # Run all tests
    test1_result = test_enhanced_credit_tool()
    test2_result = test_experian_specific_query()
    test3_result = test_record_insights_queries()

    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS:")
    print(f"   • Enhanced Credit Tool: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   • Experian Analysis: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"   • Record Insights Queries: {'✅ PASS' if test3_result else '❌ FAIL'}")

    overall_success = sum([test1_result, test2_result, test3_result]) >= 2
    print(f"\n🎯 OVERALL VALIDATION: {'✅ SUCCESS' if overall_success else '❌ NEEDS WORK'}")

    if overall_success:
        print("🎉 Enhanced credit tool is working with Record Insights!")
        print("🎉 Date=None issue should be resolved!")
    else:
        print("⚠️  Some tests failed - investigation needed")

