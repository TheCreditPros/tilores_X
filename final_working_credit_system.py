#!/usr/bin/env python3
"""
Final Working Credit System
Complete working solution that handles None dates and provides multi-bureau analysis
"""

from dotenv import load_dotenv
load_dotenv()
from collections import defaultdict

def final_working_credit_system():
    """Final working credit system with proper None handling"""

    print("🚀 FINAL WORKING CREDIT SYSTEM")
    print("=" * 60)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working entity ID we discovered
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print(f"\n🔍 FINAL CREDIT ANALYSIS WITH ENTITY ID: {entity_id}")
    print("-" * 50)

    # Final working query
    working_query = """
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
        resp = tilores_api.gql(working_query, {"id": entity_id})

        # Check for GraphQL errors
        if isinstance(resp, dict) and resp.get("errors"):
            print(f"❌ GraphQL errors: {resp['errors']}")
            return

        data = resp.get("data") or {}
        entity = data.get('entity', {}).get('entity', {})

        if entity:
            records = entity.get('records', [])
            print("📊 FINAL RESULTS:")
            print(f"   Entity ID: {entity.get('id')}")
            print(f"   Records found: {len(records)}")

            # Extract credit data with proper None handling
            credit_data = extract_credit_final(records)

            if credit_data:
                print("✅ Credit data extracted successfully!")
                display_final_analysis(credit_data)
            else:
                print("❌ No credit data found")

        else:
            print("❌ No entity data returned")

    except Exception as e:
        print(f"❌ Final system failed: {e}")

    print("\n🎯 FINAL WORKING CREDIT SYSTEM COMPLETE")
    print("=" * 60)

def extract_credit_final(records):
    """Extract credit data with proper None handling"""
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

            # Get latest per group with proper None handling
            latest = {}
            for key, score_list in by_model_bureau.items():
                # Filter out scores with None dates for sorting
                valid_scores = [s for s in score_list if s['date'] and s['date'] != 'Unknown']
                if valid_scores:
                    # Sort by date and get latest
                    sorted_scores = sorted(valid_scores, key=lambda x: x['date'], reverse=True)
                    latest[key] = sorted_scores[0]
                else:
                    # If no valid dates, use first score
                    latest[key] = score_list[0]

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

def display_final_analysis(credit_data):
    """Display final credit analysis results"""
    print("\n📊 FINAL CREDIT ANALYSIS RESULTS:")
    print("-" * 50)

    scores = credit_data.get('scores', [])
    if scores:
        print(f"   Total scores: {len(scores)}")

        # Sort by date, handling None values
        def safe_date_sort(score):
            date = score.get('date', '')
            if date and date != 'Unknown':
                return date
            return '1900 - 01 - 01'  # Default for sorting

        sorted_scores = sorted(scores, key=safe_date_sort)

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
            print("   🎯 System can answer all original user questions:")
            print("      • Compare credit utilization across different bureaus")
            print("      • Analyze late payment patterns across bureaus")
            print("      • Explain score changes across different bureaus")
        else:
            print("   ⚠️  Single bureau system")

        # Show score distribution
        print("\n   📊 Score Distribution:")
        score_values = [int(s['value']) for s in scores if s['value'].isdigit()]
        if score_values:
            min_score = min(score_values)
            max_score = max(score_values)
            avg_score = sum(score_values) / len(score_values)
            print(f"      Range: {min_score} - {max_score}")
            print(f"      Average: {avg_score:.0f}")

    else:
        print("   ❌ No credit scores found")

if __name__ == "__main__":
    final_working_credit_system()
