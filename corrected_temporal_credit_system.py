#!/usr/bin/env python3
"""
Corrected Temporal Credit System
Updated to use CreditReportFirstIssuedDate for temporal analysis
Credit scores inherit dates from their parent credit reports
"""

from dotenv import load_dotenv
load_dotenv()
# from collections import defaultdict  # Not currently used

def corrected_temporal_credit_system():
    """Corrected temporal credit system using report dates"""

    print("🚀 CORRECTED TEMPORAL CREDIT SYSTEM")
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

    print(f"\n🔍 CORRECTED TEMPORAL ANALYSIS: {entity_id}")
    print("-" * 50)

    # Query with proper date fields
    temporal_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
              }
              CREDIT_LIABILITY {
                AccountType
                CreditLimitAmount
                CreditBalance
                UnpaidBalanceAmount
                LateCount {
                  Days30
                  Days60
                  Days90
                }
                CurrentRating {
                  Code
                  Type
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        resp = tilores_api.gql(temporal_query, {"id": entity_id})
        data = resp.get("data") or {}
        entity = data.get('entity', {}).get('entity', {})

        if entity:
            records = entity.get('records', [])
            print("📊 TEMPORAL ANALYSIS RESULTS:")
            print(f"   Total records: {len(records)}")

            # Extract credit data with proper temporal context
            credit_data = extract_temporal_credit_data(records)

            if credit_data:
                print("✅ Temporal credit data extracted successfully!")
                display_temporal_analysis(credit_data)
            else:
                print("❌ No temporal credit data found")

        else:
            print("❌ No entity data returned")

    except Exception as e:
        print(f"❌ Temporal system failed: {e}")

    print("\n🎯 CORRECTED TEMPORAL CREDIT SYSTEM COMPLETE")
    print("=" * 60)

def extract_temporal_credit_data(records):
    """Extract credit data with proper temporal context using report dates"""
    try:
        # Collect all credit data with temporal context
        temporal_data = {}

        for record in records:
            credit_response = record.get('CREDIT_RESPONSE')
            if credit_response:
                bureau = credit_response.get('CREDIT_BUREAU')
                report_date = credit_response.get('CreditReportFirstIssuedDate')
                report_id = credit_response.get('Report_ID')

                if bureau and report_date:
                    # Initialize bureau data structure
                    if bureau not in temporal_data:
                        temporal_data[bureau] = {}

                    if report_date not in temporal_data[bureau]:
                        temporal_data[bureau][report_date] = {
                            'report_id': report_id,
                            'scores': [],
                            'liabilities': [],
                            'utilization': {'limit': 0, 'balance': 0, 'accounts': 0},
                            'late_payments': {'30': 0, '60': 0, '90': 0}
                        }

                    # Get credit scores (inherit date from report)
                    credit_scores = credit_response.get('CREDIT_SCORE', [])
                    for score in credit_scores:
                        if score.get('Value') and score.get('Value') != "None":
                            temporal_data[bureau][report_date]['scores'].append({
                                'value': score.get('Value'),
                                'model': score.get('ModelNameType', 'Unknown'),
                                'source': score.get('CreditRepositorySourceType', 'Unknown'),
                                'date': report_date  # Inherit from report
                            })

                    # Get liabilities and utilization
                    liabilities = credit_response.get('CREDIT_LIABILITY', [])
                    for liability in liabilities:
                        account_type = liability.get('AccountType')
                        limit = liability.get('CreditLimitAmount')
                        balance = liability.get('CreditBalance')

                        if account_type:
                            temporal_data[bureau][report_date]['liabilities'].append({
                                'type': account_type,
                                'limit': limit,
                                'balance': balance
                            })

                            # Calculate utilization
                            if limit and limit != "None":
                                try:
                                    temporal_data[bureau][report_date]['utilization']['limit'] += float(limit)
                                except (ValueError, TypeError):
                                    pass

                            if balance and balance != "None":
                                try:
                                    temporal_data[bureau][report_date]['utilization']['balance'] += float(balance)
                                except (ValueError, TypeError):
                                    pass

                            temporal_data[bureau][report_date]['utilization']['accounts'] += 1

                        # Get late payment counts
                        late_count = liability.get('LateCount', {})
                        for days, count in late_count.items():
                            if count and count != "None":
                                try:
                                    count_val = int(str(count))
                                    if days == 'Days30':
                                        temporal_data[bureau][report_date]['late_payments']['30'] += count_val
                                    elif days == 'Days60':
                                        temporal_data[bureau][report_date]['late_payments']['60'] += count_val
                                    elif days == 'Days90':
                                        temporal_data[bureau][report_date]['late_payments']['90'] += count_val
                                except (ValueError, TypeError):
                                    pass

        if temporal_data:
            # Build comprehensive temporal analysis
            analysis = {
                'bureaus': {},
                'temporal_timeline': [],
                'cross_bureau_comparison': {}
            }

            # Process each bureau
            for bureau, dates in temporal_data.items():
                analysis['bureaus'][bureau] = {
                    'total_reports': len(dates),
                    'date_range': sorted(dates.keys()),
                    'score_progression': [],
                    'utilization_trend': [],
                    'late_payment_trend': []
                }

                # Sort dates chronologically
                sorted_dates = sorted(dates.keys())

                # Build score progression
                for date in sorted_dates:
                    scores = dates[date]['scores']
                    if scores:
                        avg_score = sum(int(s['value']) for s in scores if s['value'].isdigit()) / len(scores)
                        analysis['bureaus'][bureau]['score_progression'].append({
                            'date': date,
                            'average_score': avg_score,
                            'score_count': len(scores)
                        })

                # Build utilization trend
                for date in sorted_dates:
                    util = dates[date]['utilization']
                    if util['limit'] > 0:
                        utilization_pct = (util['balance'] / util['limit']) * 100
                        analysis['bureaus'][bureau]['utilization_trend'].append({
                            'date': date,
                            'utilization': utilization_pct,
                            'accounts': util['accounts']
                        })

                # Build late payment trend
                for date in sorted_dates:
                    late = dates[date]['late_payments']
                    analysis['bureaus'][bureau]['late_payment_trend'].append({
                        'date': date,
                        'late_30': late['30'],
                        'late_60': late['60'],
                        'late_90': late['90']
                    })

            # Build cross-bureau comparison
            all_dates = set()
            for bureau_data in analysis['bureaus'].values():
                all_dates.update(bureau_data['date_range'])

            for date in sorted(all_dates):
                analysis['cross_bureau_comparison'][date] = {}
                for bureau in analysis['bureaus']:
                    if date in temporal_data[bureau]:
                        analysis['cross_bureau_comparison'][date][bureau] = {
                            'scores': temporal_data[bureau][date]['scores'],
                            'utilization': temporal_data[bureau][date]['utilization'],
                            'late_payments': temporal_data[bureau][date]['late_payments']
                        }

            return analysis

        return None

    except Exception as e:
        print(f"❌ Temporal credit extraction failed: {e}")
        return None

def display_temporal_analysis(credit_data):
    """Display comprehensive temporal credit analysis"""
    print("\n📊 COMPREHENSIVE TEMPORAL CREDIT ANALYSIS:")
    print("=" * 60)

    bureaus = credit_data.get('bureaus', {})
    cross_bureau = credit_data.get('cross_bureau_comparison', {})

    if bureaus:
        print("   📈 BUREAU ANALYSIS:")
        print("-" * 40)

        for bureau, data in bureaus.items():
            print(f"\n   🏛️  {bureau}:")
            print(f"     Total reports: {data['total_reports']}")
            print(f"     Date range: {data['date_range'][0]} to {data['date_range'][-1]}")

            # Score progression
            if data['score_progression']:
                print("     📊 Score progression:")
                for score_data in data['score_progression']:
                    print(f"       {score_data['date']}: {score_data['average_score']:.0f} ({score_data['score_count']} scores)")

            # Utilization trend
            if data['utilization_trend']:
                print("     💳 Utilization trend:")
                for util_data in data['utilization_trend']:
                    print(f"       {util_data['date']}: {util_data['utilization']:.1f}% ({util_data['accounts']} accounts)")

        # Cross-bureau comparison
        if cross_bureau:
            print("\n   🔄 CROSS-BUREAU COMPARISON:")
            print("-" * 40)

            for date in sorted(cross_bureau.keys()):
                print(f"\n     📅 {date}:")
                date_data = cross_bureau[date]

                for bureau, bureau_data in date_data.items():
                    scores = bureau_data['scores']
                    utilization = bureau_data['utilization']
                    late_payments = bureau_data['late_payments']

                    print(f"       {bureau}:")
                    if scores:
                        score_values = [s['value'] for s in scores]
                        print(f"         Scores: {', '.join(score_values)}")

                    if utilization['limit'] > 0:
                        util_pct = (utilization['balance'] / utilization['limit']) * 100
                        print(f"         Utilization: {util_pct:.1f}% ({utilization['accounts']} accounts)")

                    if any(late_payments.values()):
                        print(f"         Late payments: 30+:{late_payments['30']}, 60+:{late_payments['60']}, 90+:{late_payments['90']}")

        print("\n✅ TEMPORAL ANALYSIS COMPLETE!")
        print("   🎯 System can answer all temporal credit questions:")
        print("      • Compare utilization across bureaus over time")
        print("      • Analyze late payment patterns across bureaus")
        print("      • Explain score changes across bureaus with temporal context")

    else:
        print("   ❌ No bureau data found")

if __name__ == "__main__":
    corrected_temporal_credit_system()
