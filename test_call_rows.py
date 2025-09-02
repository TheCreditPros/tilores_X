#!/usr/bin/env python3
import asyncio
import json
from direct_credit_api_with_phone import DirectCreditAPIWithPhone

async def test_call_rows():
    api = DirectCreditAPIWithPhone()
    email = 'astoddard112@comcast.net'
    
    print('🔍 TESTING CALL ROWS BY EMAIL')
    print('=' * 50)
    
    query = '''
    query CallRowsByEmail($email: String!) {
      search(input: { parameters: { EMAIL: $email } }) {
        entities {
          id
          recordInsights {
            emails: valuesDistinct(field: "EMAIL")
            agents: valuesDistinct(field: "AGENT_USERNAME")
            call_ids: valuesDistinct(field: "CALL_ID")
          }
          records {
            id
            CALL_ID
            AGENT_USERNAME
            CALL_DURATION
            CALL_START_TIME
            CALL_HANGUP_TIME
            CALL_TYPE
            CAMPAIGN_NAME
            PHONE_NUMBER
          }
        }
      }
    }
    '''
    
    try:
        result = await api.query_tilores(query, {'email': email})
        entities = result.get('data', {}).get('search', {}).get('entities', [])
        
        if entities:
            entity = entities[0]
            entity_id = entity.get('id')
            records = entity.get('records', [])
            record_insights = entity.get('recordInsights', {})
            
            print(f'✅ Found entity: {entity_id}')
            print(f'📊 Total records: {len(records)}')
            
            # Show record insights
            print(f'\n📋 RECORD INSIGHTS:')
            for field, values in record_insights.items():
                if values:
                    print(f'  {field}: {values}')
            
            # Filter to call records only
            call_records = [r for r in records if r.get('CALL_ID')]
            print(f'\n📞 CALL RECORDS FOUND: {len(call_records)}')
            
            if call_records:
                print('\n🎯 CALL DETAILS:')
                for i, record in enumerate(call_records):
                    print(f'  Call {i+1}:')
                    print(f'    CALL_ID: {record.get("CALL_ID")}')
                    print(f'    AGENT_USERNAME: {record.get("AGENT_USERNAME")}')
                    print(f'    CALL_DURATION: {record.get("CALL_DURATION")}')
                    print(f'    CALL_START_TIME: {record.get("CALL_START_TIME")}')
                    print(f'    CALL_HANGUP_TIME: {record.get("CALL_HANGUP_TIME")}')
                    print(f'    CALL_TYPE: {record.get("CALL_TYPE")}')
                    print(f'    CAMPAIGN_NAME: {record.get("CAMPAIGN_NAME")}')
                    print(f'    PHONE_NUMBER: {record.get("PHONE_NUMBER")}')
                    print()
            else:
                print('❌ No call records found (all CALL_ID fields are null)')
                
                # Show sample of all records to see what we have
                print('\n📋 SAMPLE RECORDS (first 3):')
                for i, record in enumerate(records[:3]):
                    print(f'  Record {i+1}:')
                    print(f'    ID: {record.get("id")}')
                    print(f'    CALL_ID: {record.get("CALL_ID")}')
                    print(f'    EMAIL: {record.get("EMAIL")}')
                    print(f'    FIRST_NAME: {record.get("FIRST_NAME")}')
                    print(f'    LAST_NAME: {record.get("LAST_NAME")}')
                    print()
        else:
            print('❌ No entities found')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_call_rows())
