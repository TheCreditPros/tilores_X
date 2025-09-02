#!/usr/bin/env python3
"""
Test script to debug the comprehensive query issue
"""

import asyncio
import json
from direct_credit_api_with_phone import DirectCreditAPIWithPhone

async def test_comprehensive_query():
    """Test the comprehensive query step by step"""

    # Initialize the API
    api = DirectCreditAPIWithPhone()

    # Known entity ID for Esteban Price
    entity_id = "dc93a2cd-de0a-444f-ad47-3003ba998cd3"

    print("🔍 Testing comprehensive query...")

    try:
        # Test the comprehensive query
        result = await api.get_comprehensive_entity_data(entity_id)

        if result:
            print("✅ Comprehensive query successful!")
            print(f"📊 Total records: {len(result.get('records', []))}")
            print(f"📋 Record insights available: {bool(result.get('recordInsights'))}")

            # Check what data types we have
            records = result.get('records', [])
            data_types = {
                'credit_data': 0,
                'phone_data': 0,
                'transaction_data': 0,
                'opportunity_data': 0,
                'zoho_data': 0,
                'credit_card_data': 0
            }

            for record in records:
                if record.get('CREDIT_RESPONSE'):
                    data_types['credit_data'] += 1
                if record.get('PHONE_NUMBER') or record.get('CALL_ID'):
                    data_types['phone_data'] += 1
                if record.get('TRANSACTION_AMOUNT'):
                    data_types['transaction_data'] += 1
                if record.get('OPPORTUNITY_ID'):
                    data_types['opportunity_data'] += 1
                if record.get('ZOHO_ID'):
                    data_types['zoho_data'] += 1
                if record.get('CARD_NUMBER'):
                    data_types['credit_card_data'] += 1

            print("📈 Data type counts:")
            for data_type, count in data_types.items():
                print(f"  - {data_type}: {count} records")

        else:
            print("❌ Comprehensive query failed - no data returned")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_query())
