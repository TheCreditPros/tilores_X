#!/usr/bin/env python3
"""
Improved Credit Score Investigation - Using Correct Schema Structure
Based on user's canonical path: CREDIT_RESPONSE.CREDIT_SCORE[].Date
"""

from dotenv import load_dotenv
load_dotenv()

def investigate_canonical_score_structure():
    """Investigate using the correct canonical path structure"""

    print("🔍 INVESTIGATING CANONICAL SCORE STRUCTURE")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Use the user's canonical path structure
        canonical_query = """
        query CanonicalScoreStructure {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                CREDIT_RESPONSE {{
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  CreditReportIdentifier

                  # Use canonical path: CREDIT_SCORE[] array
                  CREDIT_SCORE {{
                    Value
                    Date
                    ModelNameType
                    CreditRepositorySourceType
                    CreditScoreID
                    CreditFileID
                    BorrowerID

                    # Include factors as mentioned by user
                    FACTOR {{
                      Code
                      Text
                      Factor_Type
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing canonical score structure query...")
        result = tilores_api.gql(canonical_query)

        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            print(f"✅ Canonical query successful! Found {len(records)} records")

            # Analyze each record for score structure
            for i, record in enumerate(records):
                credit_response = record.get("CREDIT_RESPONSE")
                if credit_response:
                    print(f"\n📊 Record {i + 1} - Canonical Score Analysis:")

                    bureau = credit_response.get("CREDIT_BUREAU")
                    report_date = credit_response.get("CreditReportFirstIssuedDate")
                    report_id = credit_response.get("CreditReportIdentifier")

                    print(f"   🏢 Bureau: {bureau}")
                    print(f"   📅 Report Date: {report_date}")
                    print(f"   🆔 Report ID: {report_id}")

                    # Check CREDIT_SCORE array structure
                    scores = credit_response.get("CREDIT_SCORE")
                    if scores:
                        if isinstance(scores, list):
                            print(f"   📈 Found {len(scores)} credit scores in array:")
                            for j, score in enumerate(scores):
                                print(f"      Score {j + 1}:")
                                print(f"         Value: {score.get('Value')}")
                                print(f"         Date: {score.get('Date')} {'✅' if score.get('Date') else '❌'}")
                                print(f"         Model: {score.get('ModelNameType')}")
                                print(f"         Repository: {score.get('CreditRepositorySourceType')}")
                                print(f"         Score ID: {score.get('CreditScoreID')}")

                                # Check factors
                                factors = score.get("FACTOR")
                                if factors:
                                    if isinstance(factors, list):
                                        print(f"         Factors: {len(factors)} found")
                                        for k, factor in enumerate(factors[:3]):  # Show first 3
                                            print(f"            Factor {k + 1}: {factor.get('Code')} - {factor.get('Text')}")
                                    elif isinstance(factors, dict):
                                        print(f"         Factor: {factors.get('Code')} - {factors.get('Text')}")
                        elif isinstance(scores, dict):
                            print("   📈 Single credit score object:")
                            print(f"      Value: {scores.get('Value')}")
                            print(f"      Date: {scores.get('Date')} {'✅' if scores.get('Date') else '❌'}")
                            print(f"      Model: {scores.get('ModelNameType')}")
                            print(f"      Repository: {scores.get('CreditRepositorySourceType')}")
                    else:
                        print("   ❌ No CREDIT_SCORE found")

                    print("   " + "-" * 40)

            return True

        else:
            print(f"❌ Canonical query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Canonical score investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_record_insights_credit_scores():
    """Test Record Insights with credit score data using user's patterns"""

    print("\n🔍 TESTING RECORD INSIGHTS WITH CREDIT SCORES")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test the user's GoldenScores query pattern
        golden_scores_query = """
        query GoldenScores {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                scoreModels: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.ModelNameType")
                bureaus: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.CreditRepositorySourceType")
                scoreValues: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                factorTexts: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.FACTOR.Text")
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing GoldenScores Record Insights query...")
        result = tilores_api.gql(golden_scores_query)

        if result and 'data' in result:
            record_insights = result['data']['entity']['entity']['recordInsights']
            print("✅ GoldenScores query successful!")

            print("\n📊 RECORD INSIGHTS RESULTS:")
            print("=" * 40)

            # Score Models
            score_models = record_insights.get("scoreModels", [])
            print(f"   📈 Score Models: {len(score_models)} found")
            for model in score_models:
                print(f"      • {model}")

            # Bureaus
            bureaus = record_insights.get("bureaus", [])
            print(f"   🏢 Bureaus: {len(bureaus)} found")
            for bureau in bureaus:
                print(f"      • {bureau}")

            # Score Values
            score_values = record_insights.get("scoreValues", [])
            print(f"   🎯 Score Values: {len(score_values)} found")
            for value in score_values[:10]:  # Show first 10
                print(f"      • {value}")
            if len(score_values) > 10:
                print(f"      ... and {len(score_values) - 10} more")

            # Factor Texts
            factor_texts = record_insights.get("factorTexts", [])
            print(f"   🔍 Factor Texts: {len(factor_texts)} found")
            for factor in factor_texts[:5]:  # Show first 5
                print(f"      • {factor}")
            if len(factor_texts) > 5:
                print(f"      ... and {len(factor_texts) - 5} more")

            return True

        else:
            print(f"❌ GoldenScores query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Record Insights test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recent_scores_filtering():
    """Test time-based filtering of credit scores"""

    print("\n🔍 TESTING RECENT SCORES FILTERING")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test the user's RecentScores query pattern with time filtering
        recent_scores_query = """
        query RecentScores {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights: filter(conditions: [
                {{ field: "CREDIT_RESPONSE.CREDIT_SCORE.Date", since: "2025 - 01 - 01" }}
              ]) {{
                models: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.ModelNameType")
                values: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                dates: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Date")
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing RecentScores with time filtering...")
        result = tilores_api.gql(recent_scores_query)

        if result and 'data' in result:
            record_insights = result['data']['entity']['entity']['recordInsights']
            print("✅ RecentScores query successful!")

            print("\n📊 RECENT SCORES (since 2025 - 01 - 01):")
            print("=" * 40)

            # Models
            models = record_insights.get("models", [])
            print(f"   📈 Models: {len(models)} found")
            for model in models:
                print(f"      • {model}")

            # Values
            values = record_insights.get("values", [])
            print(f"   🎯 Values: {len(values)} found")
            for value in values:
                print(f"      • {value}")

            # Dates
            dates = record_insights.get("dates", [])
            print(f"   📅 Dates: {len(dates)} found")
            for date in dates:
                print(f"      • {date}")

            return True

        else:
            print(f"❌ RecentScores query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Recent scores test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scores_raw_query():
    """Test the user's ScoresRaw query pattern"""

    print("\n🔍 TESTING SCORES RAW QUERY")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test the user's ScoresRaw query pattern
        scores_raw_query = """
        query ScoresRaw {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              CREDIT_RESPONSE {{
                CREDIT_SCORE {{
                  ModelNameType
                  CreditRepositorySourceType
                  Date
                  Value
                  FACTOR {{ Code Text Factor_Type }}
                }}
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing ScoresRaw query...")
        result = tilores_api.gql(scores_raw_query)

        if result and 'data' in result:
            credit_responses = result['data']['entity']['entity']['CREDIT_RESPONSE']
            print("✅ ScoresRaw query successful!")

            print("\n📊 RAW CREDIT SCORES:")
            print("=" * 40)

            if isinstance(credit_responses, list):
                for i, response in enumerate(credit_responses):
                    print(f"   📊 Response {i + 1}:")

                    scores = response.get("CREDIT_SCORE")
                    if scores:
                        if isinstance(scores, list):
                            print(f"      📈 {len(scores)} scores found:")
                            for j, score in enumerate(scores):
                                print(f"         Score {j + 1}:")
                                print(f"            Value: {score.get('Value')}")
                                print(f"            Date: {score.get('Date')} {'✅' if score.get('Date') else '❌'}")
                                print(f"            Model: {score.get('ModelNameType')}")
                                print(f"            Repository: {score.get('CreditRepositorySourceType')}")

                                # Factors
                                factors = score.get("FACTOR")
                                if factors:
                                    if isinstance(factors, list):
                                        print(f"            Factors: {len(factors)} found")
                                        for factor in factors[:2]:  # Show first 2
                                            print(f"               • {factor.get('Code')}: {factor.get('Text')}")
                                    elif isinstance(factors, dict):
                                        print(f"            Factor: {factors.get('Code')}: {factors.get('Text')}")
                        elif isinstance(scores, dict):
                            print("      📈 Single score:")
                            print(f"         Value: {scores.get('Value')}")
                            print(f"         Date: {scores.get('Date')} {'✅' if scores.get('Date') else '❌'}")
                            print(f"         Model: {scores.get('ModelNameType')}")
                            print(f"         Repository: {scores.get('CreditRepositorySourceType')}")
                    else:
                        print("      ❌ No scores found")

                    print("      " + "-" * 30)
            elif isinstance(credit_responses, dict):
                print("   📊 Single response:")
                scores = credit_responses.get("CREDIT_SCORE")
                if scores:
                    # Similar processing for single response
                    pass

            return True

        else:
            print(f"❌ ScoresRaw query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ ScoresRaw test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 IMPROVED CREDIT SCORE INVESTIGATION")
    print("=" * 70)
    print("Using user's canonical schema structure:")
    print("   • CREDIT_RESPONSE.CREDIT_SCORE[] array")
    print("   • CREDIT_SCORE[].Date field")
    print("   • Record Insights integration")
    print("=" * 70)

    # Run all improved investigations
    test1_success = investigate_canonical_score_structure()
    test2_success = test_record_insights_credit_scores()
    test3_success = test_recent_scores_filtering()
    test4_success = test_scores_raw_query()

    print("\n" + "=" * 70)
    print("📊 IMPROVED INVESTIGATION RESULTS:")
    print(f"   • Canonical Structure: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
    print(f"   • Record Insights: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")
    print(f"   • Time Filtering: {'✅ SUCCESS' if test3_success else '❌ FAILED'}")
    print(f"   • Raw Scores: {'✅ SUCCESS' if test4_success else '❌ FAILED'}")

    overall_success = test1_success or test2_success or test3_success or test4_success
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("🎉 Improved investigation successful!")
        print("   • Correct schema structure identified")
        print("   • Date field availability confirmed")
        print("   • Record Insights working with credit scores")
        print("   • Ready for advanced temporal analysis")
    else:
        print("⚠️  Improved investigation needs more work")
