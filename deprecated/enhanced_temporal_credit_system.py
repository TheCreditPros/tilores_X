#!/usr/bin/env python3
"""
Enhanced Temporal Credit System
Uses built-in summary parameters instead of manual calculations
Leverages CREDIT_SUMMARY.DATA_SET for rollup information
"""

from dotenv import load_dotenv
load_dotenv()

def enhanced_temporal_credit_system():
    """Enhanced temporal credit system using summary parameters"""

    print("🚀 ENHANCED TEMPORAL CREDIT SYSTEM - USING SUMMARY PARAMETERS")
    print("=" * 70)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working entity ID
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print(f"\n🔍 ENHANCED TEMPORAL ANALYSIS: {entity_id}")
    print("-" * 50)

    # Query with summary parameters
    enhanced_query = """
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
              CREDIT_SUMMARY {
                BorrowerID
                Name
                DATA_SET {
                  ID
                  Name
                  Value
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        resp = tilores_api.gql(enhanced_query, {"id": entity_id})
        data = resp.get("data") or {}
        entity = data.get('entity', {}).get('entity', {})

        if entity:
            records = entity.get('records', [])
            print("📊 ENHANCED TEMPORAL ANALYSIS RESULTS:")
            print(f"   Total records: {len(records)}")

            # Extract credit data with summary parameters
            enhanced_data = extract_enhanced_temporal_data(records)

            if enhanced_data:
                print("✅ Enhanced temporal credit data extracted successfully!")
                display_enhanced_analysis(enhanced_data)
            else:
                print("❌ No enhanced temporal credit data found")

        else:
            print("❌ No entity data returned")

    except Exception as e:
        print(f"❌ Enhanced temporal system failed: {e}")

    print("\n🎯 ENHANCED TEMPORAL CREDIT SYSTEM COMPLETE")
    print("=" * 70)

def extract_enhanced_temporal_data(records):
    """Extract temporal credit data using summary parameters"""

    try:
        # Collect all credit data with temporal context and summary parameters
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
                            'summary_parameters': {},
                            'utilization': {},
                            'inquiries': {},
                            'accounts': {},
                            'payments': {},
                            'delinquencies': {}
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

                    # Extract summary parameters from DATA_SET
                    summary = credit_response.get('CREDIT_SUMMARY', {})
                    data_set = summary.get('DATA_SET', [])

                    for param in data_set:
                        param_id = param.get('ID')
                        param_name = param.get('Name')
                        param_value = param.get('Value')

                        if param_name and param_value:
                            # Store the raw parameter
                            temporal_data[bureau][report_date]['summary_parameters'][param_name] = {
                                'id': param_id,
                                'value': param_value
                            }

                            # Categorize and extract key metrics
                            categorize_summary_parameter(
                                temporal_data[bureau][report_date],
                                param_name,
                                param_value
                            )

        if temporal_data:
            # Build comprehensive enhanced temporal analysis
            analysis = {
                'bureaus': {},
                'cross_bureau_comparison': {}
            }

            # Process each bureau
            for bureau, dates in temporal_data.items():
                analysis['bureaus'][bureau] = {
                    'total_reports': len(dates),
                    'date_range': sorted(dates.keys()),
                    'score_progression': [],
                    'utilization_trend': [],
                    'inquiry_trend': [],
                    'account_trend': [],
                    'payment_trend': [],
                    'delinquency_trend': []
                }

                # Sort dates chronologically
                sorted_dates = sorted(dates.keys())

                # Build score progression
                for date in sorted_dates:
                    scores = dates[date]['scores']
                    if scores:
                        score_values = [int(s['value']) for s in scores if s['value'].isdigit()]
                        if score_values:
                            analysis['bureaus'][bureau]['score_progression'].append({
                                'date': date,
                                'average_score': sum(score_values) / len(score_values),
                                'score_count': len(scores)
                            })

                # Build utilization trend using summary parameters
                for date in sorted_dates:
                    utilization = dates[date]['utilization']
                    if utilization:
                        analysis['bureaus'][bureau]['utilization_trend'].append({
                            'date': date,
                            'revolving_utilization': utilization.get('revolving', 'N/A'),
                            'overall_utilization': utilization.get('overall', 'N/A'),
                            'credit_card_utilization': utilization.get('credit_card', 'N/A')
                        })

                # Build inquiry trend using summary parameters
                for date in sorted_dates:
                    inquiries = dates[date]['inquiries']
                    if inquiries:
                        analysis['bureaus'][bureau]['inquiry_trend'].append({
                            'date': date,
                            'total_inquiries': inquiries.get('total', 'N/A'),
                            'recent_inquiries': inquiries.get('recent', 'N/A'),
                            'months_since_inquiry': inquiries.get('months_since', 'N/A')
                        })

                # Build account trend using summary parameters
                for date in sorted_dates:
                    accounts = dates[date]['accounts']
                    if accounts:
                        analysis['bureaus'][bureau]['account_trend'].append({
                            'date': date,
                            'total_tradelines': accounts.get('total', 'N/A'),
                            'open_trades': accounts.get('open', 'N/A'),
                            'credit_cards': accounts.get('credit_cards', 'N/A'),
                            'installment_accounts': accounts.get('installment', 'N/A')
                        })

                # Build payment trend using summary parameters
                for date in sorted_dates:
                    payments = dates[date]['payments']
                    if payments:
                        analysis['bureaus'][bureau]['payment_trend'].append({
                            'date': date,
                            'total_payments': payments.get('total', 'N/A'),
                            'satisfactory_trades': payments.get('satisfactory', 'N/A'),
                            'never_delinquent': payments.get('never_delinquent', 'N/A')
                        })

                # Build delinquency trend using summary parameters
                for date in sorted_dates:
                    delinquencies = dates[date]['delinquencies']
                    if delinquencies:
                        analysis['bureaus'][bureau]['delinquency_trend'].append({
                            'date': date,
                            'minor_delinqs': delinquencies.get('minor', 'N/A'),
                            'major_derogatory': delinquencies.get('major', 'N/A'),
                            'months_since_delinquency': delinquencies.get('months_since', 'N/A')
                        })

            # Build cross-bureau comparison
            all_dates = set()
            for bureau_data in analysis['bureaus'].values():
                all_dates.update(bureau_data['date_range'])

            for date in sorted(all_dates):
                analysis['cross_bureau_comparison'][date] = {}
                for bureau in temporal_data.keys():
                    if date in temporal_data[bureau]:
                        analysis['cross_bureau_comparison'][date][bureau] = {
                            'scores': temporal_data[bureau][date]['scores'],
                            'utilization': temporal_data[bureau][date]['utilization'],
                            'inquiries': temporal_data[bureau][date]['inquiries'],
                            'accounts': temporal_data[bureau][date]['accounts'],
                            'payments': temporal_data[bureau][date]['payments'],
                            'delinquencies': temporal_data[bureau][date]['delinquencies']
                        }

            return analysis

        return None

    except Exception as e:
        print(f"❌ Enhanced temporal credit extraction failed: {e}")
        return None

def categorize_summary_parameter(record_data, param_name, param_value):
    """Categorize summary parameters into logical groups"""

    param_name_lower = param_name.lower()

    # Utilization parameters
    if any(keyword in param_name_lower for keyword in ['utilization', 'util']):
        if 'revolving' in param_name_lower:
            record_data['utilization']['revolving'] = param_value
        elif 'credit card' in param_name_lower:
            record_data['utilization']['credit_card'] = param_value
        elif 'overall' in param_name_lower or 'all' in param_name_lower:
            record_data['utilization']['overall'] = param_value

    # Inquiry parameters
    elif any(keyword in param_name_lower for keyword in ['inquiry', 'inquiries']):
        if 'hard' in param_name_lower:
            record_data['inquiries']['total'] = param_value
        elif 'months since' in param_name_lower:
            record_data['inquiries']['months_since'] = param_value
        elif 'past 6 months' in param_name_lower:
            record_data['inquiries']['recent'] = param_value

    # Account parameters
    elif any(keyword in param_name_lower for keyword in ['tradeline', 'trade', 'account']):
        if 'number of tradelines' in param_name_lower:
            record_data['accounts']['total'] = param_value
        elif 'open trade' in param_name_lower:
            record_data['accounts']['open'] = param_value
        elif 'credit card' in param_name_lower:
            record_data['accounts']['credit_cards'] = param_value
        elif 'installment' in param_name_lower:
            record_data['accounts']['installment'] = param_value

    # Payment parameters
    elif any(keyword in param_name_lower for keyword in ['payment', 'satisfactory']):
        if 'number of payments' in param_name_lower:
            record_data['payments']['total'] = param_value
        elif 'satisfactory' in param_name_lower:
            record_data['payments']['satisfactory'] = param_value
        elif 'never delinquent' in param_name_lower:
            record_data['payments']['never_delinquent'] = param_value

    # Delinquency parameters
    elif any(keyword in param_name_lower for keyword in ['delinquency', 'delinq', 'derogatory']):
        if 'minor delinq' in param_name_lower:
            record_data['delinquencies']['minor'] = param_value
        elif 'major derogatory' in param_name_lower:
            record_data['delinquencies']['major'] = param_value
        elif 'months since' in param_name_lower and 'delinquency' in param_name_lower:
            record_data['delinquencies']['months_since'] = param_value

def display_enhanced_analysis(credit_data):
    """Display enhanced temporal credit analysis"""

    print("\n📊 ENHANCED TEMPORAL CREDIT ANALYSIS:")
    print("=" * 70)

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

            # Utilization trend using summary parameters
            if data['utilization_trend']:
                print("     💳 Utilization trend (from summary parameters):")
                for util_data in data['utilization_trend']:
                    print(f"       {util_data['date']}: Revolving={util_data['revolving_utilization']}%, Overall={util_data['overall_utilization']}%")

            # Inquiry trend using summary parameters
            if data['inquiry_trend']:
                print("     🔍 Inquiry trend (from summary parameters):")
                for inq_data in data['inquiry_trend']:
                    print(f"       {util_data['date']}: Total={inq_data['total_inquiries']}, Recent={inq_data['recent_inquiries']}")

            # Account trend using summary parameters
            if data['account_trend']:
                print("     🏦 Account trend (from summary parameters):")
                for acc_data in data['account_trend']:
                    print(f"       {acc_data['date']}: Tradelines={acc_data['total_tradelines']}, Open={acc_data['open_trades']}")

        # Cross-bureau comparison
        if cross_bureau:
            print("\n   🔄 CROSS-BUREAU COMPARISON:")
            print("-" * 40)

            for date in sorted(cross_bureau.keys()):
                print(f"\n     📅 {date}:")
                date_data = cross_bureau[date]

                for bureau, bureau_data in date_data.items():
                    print(f"       {bureau}:")

                    # Show key summary parameters
                    utilization = bureau_data['utilization']
                    if utilization.get('revolving'):
                        print(f"         Revolving utilization: {utilization['revolving']}%")

                    inquiries = bureau_data['inquiries']
                    if inquiries.get('total'):
                        print(f"         Total inquiries: {inquiries['total']}")

                    accounts = bureau_data['accounts']
                    if accounts.get('total'):
                        print(f"         Total tradelines: {accounts['total']}")

        print("\n✅ ENHANCED ANALYSIS COMPLETE!")
        print("   🎯 System now uses built-in summary parameters for:")
        print("      • Utilization rates (no manual calculation)")
        print("      • Inquiry counts (no manual counting)")
        print("      • Account totals (no manual aggregation)")
        print("      • Payment history (no manual analysis)")
        print("      • Delinquency patterns (no manual detection)")

    else:
        print("   ❌ No bureau data found")

if __name__ == "__main__":
    enhanced_temporal_credit_system()
