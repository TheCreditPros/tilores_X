#!/usr/bin/env python3
"""
Date Availability Check
Check what date fields are available for credit reports and scores
"""

from dotenv import load_dotenv
load_dotenv()

def date_availability_check():
    """Check date availability for credit reports and scores"""

    print("📅 DATE AVAILABILITY CHECK FOR CREDIT DATA")
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

    print(f"\n🔍 CHECKING DATES FOR ENTITY: {entity_id}")
    print("-" * 50)

    # Comprehensive date field query
    date_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              Report_Type
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
                Date
                CreditRepositorySourceType
              }
            }
          }
        }
      }
    }
    """

    try:
        resp = tilores_api.gql(date_query, {"id": entity_id})
        data = resp.get("data") or {}
        entity = data.get('entity', {}).get('entity', {})

        if entity:
            records = entity.get('records', [])
            print("📊 DATE ANALYSIS RESULTS:")
            print(f"   Total records: {len(records)}")

            # Analyze date availability
            date_fields = {
                'CreditReportFirstIssuedDate': [],
                'CREDIT_SCORE.Date': [],
                'Report_ID': [],
                'Report_Type': []
            }

            bureau_date_data = {}

            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    report_date = credit_response.get('CreditReportFirstIssuedDate')
                    report_id = credit_response.get('Report_ID')
                    report_type = credit_response.get('Report_Type')

                    if bureau:
                        if bureau not in bureau_date_data:
                            bureau_date_data[bureau] = []

                        # Collect date information
                        record_info = {
                            'record_index': i,
                            'report_date': report_date,
                            'report_id': report_id,
                            'report_type': report_type,
                            'scores': []
                        }

                        # Get score dates
                        credit_scores = credit_response.get('CREDIT_SCORE', [])
                        for score in credit_scores:
                            score_value = score.get('Value')
                            score_date = score.get('Date')
                            score_model = score.get('ModelNameType')
                            score_source = score.get('CreditRepositorySourceType')

                            if score_value and score_value != "None":
                                record_info['scores'].append({
                                    'value': score_value,
                                    'date': score_date,
                                    'model': score_model,
                                    'source': score_source
                                })

                        bureau_date_data[bureau].append(record_info)

                        # Collect date field data
                        if report_date:
                            date_fields['CreditReportFirstIssuedDate'].append(report_date)
                        if report_id:
                            date_fields['Report_ID'].append(report_id)
                        if report_type:
                            date_fields['Report_Type'].append(report_type)

                        for score in credit_scores:
                            score_date = score.get('Date')
                            if score_date:
                                date_fields['CREDIT_SCORE.Date'].append(score_date)

            # Display date field availability
            print("\n📅 DATE FIELD AVAILABILITY:")
            print("-" * 40)
            for field, values in date_fields.items():
                unique_values = list(set(values))
                print(f"   {field}:")
                print(f"     Total values: {len(values)}")
                print(f"     Unique values: {len(unique_values)}")
                if unique_values:
                    print(f"     Sample values: {unique_values[:5]}")
                else:
                    print("     No values found")

            # Display bureau-specific date analysis
            print("\n🏛️  BUREAU-SPECIFIC DATE ANALYSIS:")
            print("-" * 40)
            for bureau, records in bureau_date_data.items():
                print(f"\n   📋 {bureau}:")
                print(f"     Records: {len(records)}")

                for record in records:
                    report_date = record['report_date']
                    scores = record['scores']

                    print(f"     Record {record['record_index']}:")
                    print(f"       Report Date: {report_date}")
                    print(f"       Scores: {len(scores)}")

                    for score in scores:
                        date_str = score['date'] if score['date'] else 'None'
                        print(f"         {score['value']} | {score['model']} | Date: {date_str}")

            # Summary
            print("\n📊 DATE AVAILABILITY SUMMARY:")
            print("-" * 40)

            total_reports = sum(len(records) for records in bureau_date_data.values())
            reports_with_dates = len([d for d in date_fields['CreditReportFirstIssuedDate'] if d])
            scores_with_dates = len([d for d in date_fields['CREDIT_SCORE.Date'] if d])

            print(f"   Total credit reports: {total_reports}")
            print(f"   Reports with dates: {reports_with_dates}")
            print(f"   Scores with dates: {scores_with_dates}")

            if reports_with_dates > 0:
                print(f"   ✅ Report dates available: {reports_with_dates}/{total_reports}")
            else:
                print("   ❌ No report dates available")

            if scores_with_dates > 0:
                print(f"   ✅ Score dates available: {scores_with_dates}")
            else:
                print("   ❌ No score dates available")

        else:
            print("❌ No entity data returned")

    except Exception as e:
        print(f"❌ Date availability check failed: {e}")

    print("\n🎯 DATE AVAILABILITY CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    date_availability_check()
