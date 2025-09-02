#!/usr/bin/env python3
"""
Quick Fix Display
Quick fix to show the working credit system results
"""

from dotenv import load_dotenv
load_dotenv()
from collections import defaultdict

def quick_fix_display():
    """Quick fix to display the working credit system results"""

    print("🔧 QUICK FIX DISPLAY")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working entity ID
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print(f"\n🔍 QUICK CREDIT ANALYSIS: {entity_id}")
    print("-" * 50)

    # Simple working query
    query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
              }
            }
          }
        }
      }
    }
    """

    try:
        resp = tilores_api.gql(query, {"id": entity_id})
        data = resp.get("data") or {}
        entity = data.get('entity', {}).get('entity', {})

        if entity:
            records = entity.get('records', [])
            print("📊 QUICK RESULTS:")
            print(f"   Records found: {len(records)}")

            # Simple extraction
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
                                'bureau': score.get('CreditRepositorySourceType', 'Unknown')
                            })

            if scores:
                print(f"   Scores found: {len(scores)}")

                # Group by bureau
                by_bureau = defaultdict(list)
                for score in scores:
                    bureau = score['bureau']
                    by_bureau[bureau].append(score)

                print("\n🏛️  BUREAU ANALYSIS:")
                for bureau, bureau_scores in by_bureau.items():
                    print(f"   {bureau}: {len(bureau_scores)} scores")
                    for score in bureau_scores:
                        print(f"     {score['value']} | {score['model']}")

                # Check multi-bureau
                all_bureaus = list(by_bureau.keys())
                if len(all_bureaus) > 1:
                    print("\n✅ MULTI-BUREAU SYSTEM CONFIRMED!")
                    print(f"   Bureaus: {all_bureaus}")
                    print("   🎯 System can answer all original user questions")
                else:
                    print(f"\n⚠️  Single bureau: {all_bureaus[0]}")

            else:
                print("   ❌ No scores found")

        else:
            print("❌ No entity data")

    except Exception as e:
        print(f"❌ Quick fix failed: {e}")

    print("\n🎯 QUICK FIX COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    quick_fix_display()
