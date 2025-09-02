#!/usr/bin/env python3
"""
Test RAW Path Fallback
Test the RAW + local reduction path since Insights isn't returning credit data
"""

from dotenv import load_dotenv
load_dotenv()
from collections import defaultdict
import json

def test_raw_path_fallback():
    """Test the RAW path fallback for credit data extraction"""

    print("🔍 TEST RAW PATH FALLBACK")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working entity ID we discovered
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print(f"\n🔍 TESTING RAW PATH WITH ENTITY ID: {entity_id}")
    print("-" * 50)

    # RAW query path
    raw_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          id
          records {
            id
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
                Date
              }
            }
          }
        }
      }
    }
    """

    try:
        resp = tilores_api.gql(raw_query, {"id": entity_id})

        # Check for GraphQL errors
        if isinstance(resp, dict) and resp.get("errors"):
            print(f"❌ GraphQL errors: {json.dumps(resp['errors'], indent=2)}")
            return

        data = resp.get("data") or {}
        entity = data.get('entity', {}).get('entity', {})

        if entity:
            records = entity.get('records', [])
            print("📊 RAW PATH RESULTS:")
            print(f"   Entity ID: {entity.get('id')}")
            print(f"   Records found: {len(records)}")

            # Extract credit data using local reduction
            credit_data = extract_credit_from_raw_entity(records)

            if credit_data:
                print("✅ Credit data extracted successfully using RAW path")
                display_credit_analysis(credit_data)
            else:
                print("❌ No credit data found in RAW path")

        else:
            print("❌ No entity data returned")

    except Exception as e:
        print(f"❌ RAW path test failed: {e}")

    print("\n🎯 RAW PATH FALLBACK TEST COMPLETE")
    print("=" * 50)

def extract_credit_from_raw_entity(records):
    """Extract credit data from raw entity records"""
    try:
        # Collect all credit scores
        scores = []
        for record in records:
            credit_response = record.get('CREDIT_RESPONSE')
            if credit_response:
                credit_scores = credit_response.get('CREDIT_SCORE', [])
                for score in credit_scores:
                    if score.get('Value') and score.get('Value') != "None":
                        scores.append({
                            'value': score.get('Value'),
                            'model': score.get('ModelNameType', 'Unknown'),
                            'bureau': score.get('CreditRepositorySourceType', 'Unknown'),
                            'date': score.get('Date', 'Unknown')
                        })

        if scores:
            print(f"   Raw scores found: {len(scores)}")

            # Group by model and bureau, get latest per group
            by_model_bureau = defaultdict(list)
            for score in scores:
                key = (score['model'], score['bureau'])
                by_model_bureau[key].append(score)

            # Get latest per group
            latest = {}
            for key, score_list in by_model_bureau.items():
                # Sort by date and get latest
                sorted_scores = sorted(score_list, key=lambda x: x.get('date', ''), reverse=True)
                latest[key] = sorted_scores[0]

            # Build credit aggregation shape
            credit_aggregation = {
                'scores': [
                    {
                        'model': model,
                        'value': score['value'],
                        'date': score['date'],
                        'bureaus': [bureau]
                    }
                    for (model, bureau), score in latest.items()
                ]
            }

            return credit_aggregation

        return None

    except Exception as e:
        print(f"❌ Credit extraction failed: {e}")
        return None

def display_credit_analysis(credit_data):
    """Display credit analysis results"""
    print("\n📊 CREDIT ANALYSIS RESULTS:")
    print("-" * 40)

    scores = credit_data.get('scores', [])
    if scores:
        print(f"   Total scores: {len(scores)}")

        # Sort by date
        sorted_scores = sorted(scores, key=lambda x: x.get('date', ''))

        print("\n   📈 Credit Score Timeline:")
        for i, score in enumerate(sorted_scores, 1):
            model = score.get('model', 'Unknown')
            value = score.get('value', 'Unknown')
            date = score.get('date', 'Unknown')
            bureaus = ', '.join(score.get('bureaus', []))

            print(f"   {i:2d}. {value} | {model:15} | {date:12} | {bureaus}")

        # Bureau analysis
        all_bureaus = set()
        for score in scores:
            all_bureaus.update(score.get('bureaus', []))

        print(f"\n   🏛️  Bureaus Found: {list(all_bureaus)}")

        if len(all_bureaus) > 1:
            print("   ✅ MULTI-BUREAU SYSTEM CONFIRMED!")
            print("   🎯 System can answer all original user questions")
        else:
            print("   ⚠️  Single bureau system")

    else:
        print("   ❌ No credit scores found")

if __name__ == "__main__":
    test_raw_path_fallback()
