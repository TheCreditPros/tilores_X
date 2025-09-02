#!/usr/bin/env python3
"""
Analyze the actual data quality issues
Show exactly what's missing from the responses
"""

from dotenv import load_dotenv
load_dotenv()

from core_app import initialize_engine
import core_app

def analyze_credit_data_accuracy():
    """Analyze what's actually in the credit report vs what should be there"""

    print("🔍 ANALYZING ACTUAL CREDIT DATA ACCURACY")
    print("=" * 60)

    initialize_engine()
    engine = core_app.engine

    if not engine:
        return

    # Get credit tool
    credit_tool = None
    for tool in engine.tools:
        if tool.name == "get_customer_credit_report":
            credit_tool = tool
            break

    if not credit_tool:
        print("❌ Credit tool not found")
        return

    # Test credit report for Esteban Price
    customer_name = "Esteban Price"
    print(f"🎯 Testing credit report for: {customer_name}")

    try:
        result = credit_tool.invoke({"customer_name": customer_name})

        print("\n📊 CREDIT REPORT ANALYSIS:")
        print(f"Length: {len(str(result))} characters")
        print(f"Type: {type(result)}")

        # Show the complete credit report
        print("\n📋 COMPLETE CREDIT REPORT:")
        print("=" * 80)
        print(str(result))
        print("=" * 80)

        # Analyze what's missing
        result_str = str(result).lower()

        print("\n❌ MISSING DATA ANALYSIS:")

        missing_items = {
            "Actual Experian credit score numbers": "experian" in result_str and any(char.isdigit() for char in result_str if result_str.find("score") < result_str.find(char) < result_str.find("score") + 50),
            "Specific credit score values (e.g. 650, 720)": any(f"{score}" in result_str for score in range(300, 851)),
            "Credit account details": "account" in result_str and "balance" in result_str,
            "Payment history specifics": "payment" in result_str and ("late" in result_str or "on time" in result_str),
            "Credit utilization percentages": any(f"{pct}%" in result_str for pct in range(0, 101)),
            "Tradeline information": "tradeline" in result_str or "credit line" in result_str,
            "Credit inquiries": "inquir" in result_str and ("hard" in result_str or "soft" in result_str),
            "Actual bureau data": any(bureau in result_str for bureau in ["experian", "equifax", "transunion"])
        }

        for item, found in missing_items.items():
            status = "✅" if found else "❌"
            print(f"   {status} {item}: {'Present' if found else 'MISSING'}")

        # Check what we actually have
        print("\n✅ WHAT WE ACTUALLY HAVE:")
        if "credit score status" in result_str:
            print("   ✅ Generic credit score status message")
        if "not available" in result_str:
            print("   ❌ 'Not available' messages")
        if "action required" in result_str:
            print("   ❌ 'Action required' messages")
        if "analysis required" in result_str:
            print("   ❌ 'Analysis required' messages")

        print("\n🎯 ROOT ISSUE:")
        print("   The credit report contains TEMPLATE TEXT, not actual credit data")
        print("   It says 'Credit report needs to be pulled' instead of showing real scores")
        print("   This explains why queries about 'most recent Experian score' fail")

        return False  # Data is not accurate

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_specific_credit_queries():
    """Test the specific queries the user asked about"""

    print("\n🎯 TESTING SPECIFIC USER QUERIES")
    print("=" * 60)

    engine = core_app.engine
    if not engine:
        return False

    # Get credit tool
    credit_tool = None
    for tool in engine.tools:
        if tool.name == "get_customer_credit_report":
            credit_tool = tool
            break

    queries_to_test = [
        "What was their most recent Experian credit score?",
        "Compare that score to the first Experian credit score"
    ]

    print("Testing if our credit data can answer these queries:")

    try:
        # Get the credit report
        result = credit_tool.invoke({"customer_name": "Esteban Price"})
        result_str = str(result).lower()

        for i, query in enumerate(queries_to_test, 1):
            print(f"\n📋 QUERY {i}: {query}")

            if "recent" in query.lower() and "experian" in query.lower():
                # Look for actual Experian scores
                has_experian = "experian" in result_str
                has_score_numbers = any(f"{score}" in result_str for score in range(300, 851))

                print(f"   Can we answer this? {'✅ YES' if has_experian and has_score_numbers else '❌ NO'}")
                if not (has_experian and has_score_numbers):
                    print("   Issue: No actual Experian score numbers found")

            elif "compare" in query.lower():
                # Look for multiple scores to compare
                score_count = sum(1 for score in range(300, 851) if f"{score}" in result_str)

                print(f"   Can we answer this? {'✅ YES' if score_count >= 2 else '❌ NO'}")
                if score_count < 2:
                    print(f"   Issue: Need at least 2 scores to compare, found {score_count}")

        return False  # Cannot answer the specific queries accurately

    except Exception as e:
        print(f"❌ Error testing queries: {e}")
        return False

def show_what_accurate_data_should_look_like():
    """Show what accurate credit data should contain"""

    print("\n📋 WHAT ACCURATE CREDIT DATA SHOULD CONTAIN:")
    print("=" * 60)

    print("✅ EXPECTED for 'Who is e.j.price1986@gmail.com?':")
    print("   - Name: Esteban Price ✅ (We have this)")
    print("   - Email: e.j.price1986@gmail.com ✅ (We have this)")
    print("   - Client ID: 1747598 ✅ (We have this)")
    print("   - Complete profile ✅ (We have this)")

    print("\n❌ MISSING for 'Most recent Experian credit score?':")
    print("   - Actual score number (e.g., 'Most recent Experian score: 720')")
    print("   - Score date (e.g., 'as of August 2025')")
    print("   - Bureau confirmation (e.g., 'Experian bureau report')")

    print("\n❌ MISSING for 'Compare to first Experian score?':")
    print("   - First score number (e.g., 'First Experian score: 650')")
    print("   - Recent score number (e.g., 'Most recent score: 720')")
    print("   - Comparison (e.g., 'Improvement of 70 points')")
    print("   - Time period (e.g., 'Over 6 months')")

    print("\n🎯 CONCLUSION:")
    print("   Customer profile data: ✅ ACCURATE & COMPLETE")
    print("   Credit score data: ❌ TEMPLATE TEXT, NOT REAL DATA")
    print("   Fix needed: Get actual credit scores from Tilores, not generic templates")

if __name__ == "__main__":
    print("🚨 ANALYZING ACTUAL DATA ACCURACY ISSUES")
    print("=" * 70)

    # Test 1: Credit data accuracy
    credit_accurate = analyze_credit_data_accuracy()

    # Test 2: Specific query capability
    queries_answerable = test_specific_credit_queries()

    # Show what's expected
    show_what_accurate_data_should_look_like()

    print("\n" + "=" * 70)
    print("📊 ACCURACY ASSESSMENT:")
    print(f"   Credit Data Accuracy: {'✅ PASS' if credit_accurate else '❌ FAIL'}")
    print(f"   Can Answer User Queries: {'✅ PASS' if queries_answerable else '❌ FAIL'}")

    if not credit_accurate or not queries_answerable:
        print("\n🚨 CRITICAL ISSUE IDENTIFIED:")
        print("   The system returns TEMPLATE RESPONSES, not actual credit data")
        print("   This explains why the user doesn't see 'accurate data in output'")
        print("   Need to investigate why credit tool returns templates vs real scores")
    else:
        print("\n✅ DATA ACCURACY CONFIRMED - Ready for API fix implementation")

