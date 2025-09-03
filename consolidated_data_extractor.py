#!/usr / bin / env python3
"""
Consolidated Data Extractor
Properly consolidates data from multiple records to build complete customer profile
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

def load_data_map(filename: str) -> Dict[str, Any]:
    """Load the comprehensive data map"""
    with open(filename, 'r') as f:
        return json.load(f)

def consolidate_customer_data(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Consolidate data from multiple records into complete customer profile"""

    print("🔄 Consolidating data from multiple records...")

    consolidated = {
        'identity': {},
        'credit_reports': [],
        'transactions': [],
        'cards': [],
        'phone_calls': [],
        'tickets': [],
        'business_data': {},
        'system_data': {},
        'all_unique_values': defaultdict(set)
    }

    # Process each record
    for i, record in enumerate(records):
        print(f"Processing record {i}...")

        # Collect identity data (first non - null wins)
        identity_fields = ['EMAIL', 'FIRST_NAME', 'LAST_NAME', 'MIDDLE_NAME', 'PHONE_NUMBER', 'CLIENT_ID']
        for field in identity_fields:
            value = record.get(field)
            if value and not consolidated['identity'].get(field.lower()):
                consolidated['identity'][field.lower()] = value

        # Collect credit data
        credit_response = record.get('CREDIT_RESPONSE')
        if credit_response:
            credit_report = {
                'record_id': record.get('id'),
                'credit_bureau': credit_response.get('CREDIT_BUREAU'),
                'report_date': credit_response.get('CreditReportFirstIssuedDate'),
                'report_id': credit_response.get('Report_ID'),
                'report_identifier': credit_response.get('CreditReportIdentifier'),
                'vendor': credit_response.get('Vendor')
            }
            consolidated['credit_reports'].append(credit_report)

        # Collect transaction data
        if record.get('TRANSACTION_AMOUNT'):
            transaction = {
                'record_id': record.get('id'),
                'amount': record.get('TRANSACTION_AMOUNT'),
                'payment_method': record.get('PAYMENT_METHOD'),
                'response_status': record.get('RESPONSE_STATUS'),
                'response_message': record.get('RESPONSE_MESSAGE'),
                'gateway_date': record.get('GATEWAY_DATE'),
                'type': record.get('TYPE'),
                'recurring': record.get('RECURRING'),
                'chargeback': record.get('CHARGEBACK')
            }
            consolidated['transactions'].append(transaction)

        # Collect card data
        if record.get('CARD_LAST_4'):
            card = {
                'record_id': record.get('id'),
                'last_4': record.get('CARD_LAST_4'),
                'first_6': record.get('CARD_FIRST_6_DIGIT'),
                'card_type': record.get('CARD_TYPE'),
                'expired': record.get('CARD_EXPIRED'),
                'expiration_month': record.get('EXPIRATION_MONTH'),
                'expiration_year': record.get('EXPIRATION_YEAR')
            }
            consolidated['cards'].append(card)

        # Collect phone data
        if record.get('CALL_ID'):
            call = {
                'record_id': record.get('id'),
                'call_id': record.get('CALL_ID'),
                'start_time': record.get('CALL_START_TIME'),
                'duration': record.get('CALL_DURATION'),
                'call_type': record.get('CALL_TYPE'),
                'contact_type': record.get('CONTACT_TYPE')
            }
            consolidated['phone_calls'].append(call)

        # Collect ticket data
        if record.get('TICKETNUMBER'):
            ticket = {
                'record_id': record.get('id'),
                'ticket_number': record.get('TICKETNUMBER'),
                'zoho_id': record.get('ZOHO_ID'),
                'zoho_status': record.get('ZOHO_STATUS'),
                'category': record.get('CATEGORY'),
                'priority': record.get('PRIORITY')
            }
            consolidated['tickets'].append(ticket)

        # Collect business data (first non - null wins)
        business_fields = ['CURRENT_PRODUCT', 'STATUS', 'ACTIVE', 'ENROLL_DATE', 'ENROLLMENT_FEE', 'OPPORTUNITY_ID']
        for field in business_fields:
            value = record.get(field)
            if value is not None and not consolidated['business_data'].get(field.lower()):
                consolidated['business_data'][field.lower()] = value

        # Collect all unique values for analysis
        for field, value in record.items():
            if value is not None and value != '':
                consolidated['all_unique_values'][field].add(str(value))

    # Convert sets to lists for JSON serialization
    consolidated['all_unique_values'] = {
        field: list(values) for field, values in consolidated['all_unique_values'].items()
    }

    return consolidated

def extract_detailed_credit_data(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract detailed credit analysis"""

    credit_analysis = {
        'total_credit_reports': 0,
        'credit_bureaus': set(),
        'report_dates': [],
        'vendors': set(),
        'report_timeline': []
    }

    for record in records:
        credit_response = record.get('CREDIT_RESPONSE')
        if credit_response:
            credit_analysis['total_credit_reports'] += 1

            bureau = credit_response.get('CREDIT_BUREAU')
            if bureau:
                credit_analysis['credit_bureaus'].add(bureau)

            date = credit_response.get('CreditReportFirstIssuedDate')
            if date:
                credit_analysis['report_dates'].append(date)

            vendor = credit_response.get('Vendor')
            if vendor:
                credit_analysis['vendors'].add(vendor)

            credit_analysis['report_timeline'].append({
                'date': date,
                'bureau': bureau,
                'report_id': credit_response.get('Report_ID'),
                'vendor': vendor
            })

    # Sort timeline by date
    credit_analysis['report_timeline'].sort(key=lambda x: x['date'] or '')

    # Convert sets to lists
    credit_analysis['credit_bureaus'] = list(credit_analysis['credit_bureaus'])
    credit_analysis['vendors'] = list(credit_analysis['vendors'])

    return credit_analysis

def build_complete_ground_truth(data_map: Dict[str, Any]) -> Dict[str, Any]:
    """Build complete ground truth from consolidated data"""

    records = data_map['raw_records']
    consolidated = consolidate_customer_data(records)
    credit_analysis = extract_detailed_credit_data(records)

    # Build comprehensive ground truth
    ground_truth = {
        'metadata': {
            'customer_email': data_map['metadata']['customer_email'],
            'entity_id': data_map['metadata']['entity_id'],
            'total_records': len(records),
            'consolidation_timestamp': datetime.now().isoformat()
        },

        'customer_identity': consolidated['identity'],

        'credit_profile': {
            'has_credit_data': len(consolidated['credit_reports']) > 0,
            'total_reports': len(consolidated['credit_reports']),
            'bureaus': credit_analysis['credit_bureaus'],
            'vendors': credit_analysis['vendors'],
            'date_range': {
                'earliest': min(credit_analysis['report_dates']) if credit_analysis['report_dates'] else None,
                'latest': max(credit_analysis['report_dates']) if credit_analysis['report_dates'] else None
            },
            'reports': consolidated['credit_reports'],
            'timeline': credit_analysis['report_timeline']
        },

        'transaction_profile': {
            'has_transactions': len(consolidated['transactions']) > 0,
            'total_transactions': len(consolidated['transactions']),
            'transactions': consolidated['transactions']
        },

        'card_profile': {
            'has_cards': len(consolidated['cards']) > 0,
            'total_cards': len(consolidated['cards']),
            'cards': consolidated['cards']
        },

        'communication_profile': {
            'has_phone_calls': len(consolidated['phone_calls']) > 0,
            'has_tickets': len(consolidated['tickets']) > 0,
            'phone_calls': consolidated['phone_calls'],
            'tickets': consolidated['tickets']
        },

        'business_profile': consolidated['business_data'],

        'data_completeness': {
            'identity_complete': bool(consolidated['identity'].get('email') and
                                    consolidated['identity'].get('first_name') and
                                    consolidated['identity'].get('last_name')),
            'credit_available': len(consolidated['credit_reports']) > 0,
            'transactions_available': len(consolidated['transactions']) > 0,
            'cards_available': len(consolidated['cards']) > 0,
            'contact_available': len(consolidated['phone_calls']) > 0 or len(consolidated['tickets']) > 0
        },

        'field_inventory': consolidated['all_unique_values']
    }

    return ground_truth

def main():
    """Main execution"""
    print("🚀 CONSOLIDATED DATA EXTRACTION")
    print("=" * 50)

    # Load the data map
    data_map = load_data_map('complete_live_data_map_20250902_152235.json')

    # Build complete ground truth
    ground_truth = build_complete_ground_truth(data_map)

    # Save consolidated data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"consolidated_ground_truth_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(ground_truth, f, indent=2, default=str)

    print(f"✅ Saved consolidated data to {filename}")

    # Print summary
    print("\n📊 CONSOLIDATED DATA SUMMARY")
    print("-" * 40)

    identity = ground_truth['customer_identity']
    print(f"Customer: {identity.get('first_name')} {identity.get('last_name')}")
    print(f"Email: {identity.get('email')}")
    print(f"Client ID: {identity.get('client_id')}")
    print(f"Phone: {identity.get('phone_number')}")

    credit = ground_truth['credit_profile']
    print(f"\nCredit Reports: {credit['total_reports']}")
    print(f"Credit Bureaus: {credit['bureaus']}")
    print(f"Date Range: {credit['date_range']['earliest']} to {credit['date_range']['latest']}")

    transactions = ground_truth['transaction_profile']
    print(f"\nTransactions: {transactions['total_transactions']}")

    cards = ground_truth['card_profile']
    print(f"Cards: {cards['total_cards']}")

    completeness = ground_truth['data_completeness']
    print("\nData Completeness:")
    print(f"  Identity: {'✅' if completeness['identity_complete'] else '❌'}")
    print(f"  Credit: {'✅' if completeness['credit_available'] else '❌'}")
    print(f"  Transactions: {'✅' if completeness['transactions_available'] else '❌'}")
    print(f"  Cards: {'✅' if completeness['cards_available'] else '❌'}")

    return filename

if __name__ == "__main__":
    main()


