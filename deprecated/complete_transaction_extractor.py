#!/usr / bin / env python3
"""
Complete Transaction Extractor
Extracts ALL transaction data with comprehensive filtering
"""

import json
from datetime import datetime
from typing import Dict, List, Any

def extract_complete_transactions(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract ALL transaction data from records"""

    print("💰 EXTRACTING COMPLETE TRANSACTION DATA")
    print("=" * 50)

    transactions = []
    payment_schedule = {}
    financial_summary = {}

    # Transaction fields to check
    transaction_fields = [
        'TRANSACTION_AMOUNT', 'LAST_APPROVED_TRANSACTION', 'LAST_APPROVED_TRANSACTION_AMOUNT',
        'LAST_FAILED_TRANSACTION', 'PAYMENT_METHOD', 'PAYMENT_START_DATE', 'PAYMENT_END_DATE',
        'UPCOMING_SCHEDULED_PAYMENT', 'UPCOMING_SCHEDULED_PAYMENT_AMOUNT', 'CHARGEBACK',
        'REFUND_CONFIRMATION_SENT', 'DEBT_PAYMENT', 'DEBT_PAYMENT_DATE', 'AMOUNT',
        'ENROLLMENT_FEE', 'ENROLLMENT_BALANCE', 'NET_BALANCE_DUE', 'SETUP_FEE2_AMOUNT',
        'RECURRING_MONTHLY_FEE', 'DISCOUNT_AMOUNT', 'COUPON_AMOUNT', 'RESPONSE_STATUS',
        'RESPONSE_MESSAGE', 'GATEWAY_DATE', 'TYPE', 'RECURRING', 'NEXT_TRANSACTION_DATE'
    ]

    for i, record in enumerate(records):
        record_id = record.get('id')

        # Extract direct transactions (charges / credits)
        if record.get('TRANSACTION_AMOUNT'):
            transaction = {
                'record_index': i,
                'record_id': record_id,
                'type': 'direct_transaction',
                'amount': record.get('TRANSACTION_AMOUNT'),
                'payment_method': record.get('PAYMENT_METHOD'),
                'transaction_type': record.get('TYPE'),
                'status': record.get('RESPONSE_STATUS'),
                'message': record.get('RESPONSE_MESSAGE'),
                'gateway_date': record.get('GATEWAY_DATE'),
                'recurring': record.get('RECURRING'),
                'chargeback': record.get('CHARGEBACK'),
                'refund_sent': record.get('REFUND_CONFIRMATION_SENT')
            }
            transactions.append(transaction)
            print(f"✅ Direct Transaction - Record {i}: ${transaction['amount']} ({transaction['transaction_type']})")

        # Extract payment history data
        if record.get('LAST_APPROVED_TRANSACTION') or record.get('LAST_APPROVED_TRANSACTION_AMOUNT'):
            payment_history = {
                'record_index': i,
                'record_id': record_id,
                'type': 'payment_history',
                'last_transaction_date': record.get('LAST_APPROVED_TRANSACTION'),
                'last_transaction_amount': record.get('LAST_APPROVED_TRANSACTION_AMOUNT'),
                'days_since_last_transaction': record.get('DAYS_SINCE_LAST_APPROVED_TRANSACTION'),
                'enrollment_balance': record.get('ENROLLMENT_BALANCE'),
                'net_balance_due': record.get('NET_BALANCE_DUE')
            }
            transactions.append(payment_history)
            print(f"✅ Payment History - Record {i}: Last transaction ${payment_history['last_transaction_amount']}")

        # Extract payment schedule data
        if record.get('UPCOMING_SCHEDULED_PAYMENT') or record.get('RECURRING_MONTHLY_FEE'):
            schedule = {
                'record_index': i,
                'record_id': record_id,
                'type': 'payment_schedule',
                'payment_start_date': record.get('PAYMENT_START_DATE'),
                'next_payment_date': record.get('UPCOMING_SCHEDULED_PAYMENT'),
                'next_payment_amount': record.get('UPCOMING_SCHEDULED_PAYMENT_AMOUNT'),
                'recurring_monthly_fee': record.get('RECURRING_MONTHLY_FEE'),
                'setup_fee': record.get('SETUP_FEE2_AMOUNT'),
                'next_transaction_date': record.get('NEXT_TRANSACTION_DATE')
            }
            transactions.append(schedule)
            print(f"✅ Payment Schedule - Record {i}: Next payment ${schedule['next_payment_amount']} on {schedule['next_payment_date']}")

        # Extract any other financial data
        financial_data = {}
        for field in transaction_fields:
            value = record.get(field)
            if value is not None and value != '' and value is not False:
                financial_data[field] = value

        if financial_data and not any(record.get(key) for key in ['TRANSACTION_AMOUNT', 'LAST_APPROVED_TRANSACTION', 'UPCOMING_SCHEDULED_PAYMENT']):
            other_financial = {
                'record_index': i,
                'record_id': record_id,
                'type': 'other_financial',
                'data': financial_data
            }
            transactions.append(other_financial)
            print(f"✅ Other Financial - Record {i}: {list(financial_data.keys())}")

    # Build comprehensive transaction profile
    transaction_profile = {
        'total_transaction_records': len(transactions),
        'transactions_by_type': {
            'direct_transactions': [t for t in transactions if t['type'] == 'direct_transaction'],
            'payment_history': [t for t in transactions if t['type'] == 'payment_history'],
            'payment_schedule': [t for t in transactions if t['type'] == 'payment_schedule'],
            'other_financial': [t for t in transactions if t['type'] == 'other_financial']
        },
        'all_transactions': transactions,
        'financial_summary': {
            'direct_charges': [float(t['amount']) for t in transactions if t['type'] == 'direct_transaction' and t.get('amount')],
            'monthly_recurring': [float(t['recurring_monthly_fee']) for t in transactions if t['type'] == 'payment_schedule' and t.get('recurring_monthly_fee')],
            'upcoming_payments': [float(t['next_payment_amount']) for t in transactions if t['type'] == 'payment_schedule' and t.get('next_payment_amount')],
            'balances': {
                'enrollment_balance': [float(t['enrollment_balance']) for t in transactions if t['type'] == 'payment_history' and t.get('enrollment_balance') is not None],
                'net_balance_due': [float(t['net_balance_due']) for t in transactions if t['type'] == 'payment_history' and t.get('net_balance_due') is not None]
            }
        }
    }

    return transaction_profile

def main():
    """Main execution"""
    print("🚀 COMPLETE TRANSACTION EXTRACTION")
    print("=" * 50)

    # Load the raw data
    with open('complete_live_data_map_20250902_152235.json', 'r') as f:
        raw_data = json.load(f)

    records = raw_data['raw_records']

    # Extract complete transactions
    transaction_profile = extract_complete_transactions(records)

    # Save complete transaction data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"complete_transactions_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(transaction_profile, f, indent=2, default=str)

    print(f"\n✅ Saved complete transaction data to {filename}")

    # Print detailed summary
    print("\n💰 COMPLETE TRANSACTION SUMMARY")
    print("-" * 50)

    by_type = transaction_profile['transactions_by_type']
    summary = transaction_profile['financial_summary']

    print(f"Total Transaction Records: {transaction_profile['total_transaction_records']}")
    print(f"Direct Transactions: {len(by_type['direct_transactions'])}")
    print(f"Payment History Records: {len(by_type['payment_history'])}")
    print(f"Payment Schedule Records: {len(by_type['payment_schedule'])}")
    print(f"Other Financial Records: {len(by_type['other_financial'])}")

    print(f"\nDirect Charges: {summary['direct_charges']}")
    print(f"Monthly Recurring: {summary['monthly_recurring']}")
    print(f"Upcoming Payments: {summary['upcoming_payments']}")
    print(f"Current Balances: {summary['balances']}")

    # Show each transaction
    print("\n📋 DETAILED TRANSACTION BREAKDOWN")
    print("-" * 50)

    for i, transaction in enumerate(transaction_profile['all_transactions'], 1):
        print(f"{i}. {transaction['type'].upper()} (Record {transaction['record_index']}):")

        if transaction['type'] == 'direct_transaction':
            print(f"   Amount: ${transaction['amount']}")
            print(f"   Type: {transaction['transaction_type']}")
            print(f"   Method: {transaction['payment_method']}")
            print(f"   Status: {transaction['status']}")
            print(f"   Date: {transaction['gateway_date']}")

        elif transaction['type'] == 'payment_history':
            print(f"   Last Transaction: ${transaction['last_transaction_amount']} on {transaction['last_transaction_date']}")
            print(f"   Days Since: {transaction['days_since_last_transaction']}")
            print(f"   Balance: ${transaction['enrollment_balance']}")

        elif transaction['type'] == 'payment_schedule':
            print(f"   Monthly Fee: ${transaction['recurring_monthly_fee']}")
            print(f"   Next Payment: ${transaction['next_payment_amount']} on {transaction['next_payment_date']}")
            print(f"   Payment Start: {transaction['payment_start_date']}")

        print()

    return filename

if __name__ == "__main__":
    main()


