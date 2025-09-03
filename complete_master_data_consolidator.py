#!/usr / bin / env python3
"""
Complete Master Data Consolidator
Consolidates ALL data (credit, transactions, phone, etc.) into one contiguous master file
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

def load_all_data_files() -> Dict[str, Any]:
    """Load all existing data files"""

    print("📂 Loading all data files...")

    data_files = {}

    try:
        # Load deep credit analysis
        with open('deep_credit_analysis_20250902_153033.json', 'r') as f:
            data_files['credit_data'] = json.load(f)
        print("✅ Loaded credit data")
    except Exception as e:
        print(f"❌ Failed to load credit data: {e}")
        data_files['credit_data'] = None

    try:
        # Load transaction data
        with open('complete_transactions_20250902_152644.json', 'r') as f:
            data_files['transaction_data'] = json.load(f)
        print("✅ Loaded transaction data")
    except Exception as e:
        print(f"❌ Failed to load transaction data: {e}")
        data_files['transaction_data'] = None

    try:
        # Load consolidated ground truth
        with open('consolidated_ground_truth_20250902_152517.json', 'r') as f:
            data_files['consolidated_data'] = json.load(f)
        print("✅ Loaded consolidated data")
    except Exception as e:
        print(f"❌ Failed to load consolidated data: {e}")
        data_files['consolidated_data'] = None

    try:
        # Load raw data map
        with open('complete_live_data_map_20250902_152235.json', 'r') as f:
            data_files['raw_data'] = json.load(f)
        print("✅ Loaded raw data map")
    except Exception as e:
        print(f"❌ Failed to load raw data map: {e}")
        data_files['raw_data'] = None

    return data_files

def extract_phone_data_from_raw(raw_records: List[Dict]) -> Dict[str, Any]:
    """Extract comprehensive phone data from raw records"""

    print("📞 Extracting phone data from raw records...")

    phone_data = {
        'phone_call_records': [],
        'contact_records': [],
        'phone_number_records': [],
        'zoho_integration_records': [],
        'agent_interaction_records': [],
        'phone_field_coverage': {},
        'summary': {}
    }

    # All possible phone - related fields
    phone_fields = [
        'PHONE_NUMBER', 'PHONE_EXTERNAL', 'CALL_ID', 'CALL_START_TIME',
        'CALL_HANGUP_TIME', 'CALL_DURATION', 'CALL_TYPE', 'CONTACT_TYPE',
        'CONTACT_NEW', 'ZOHO_CONTACT_ID', 'ZOHO_PHONE', 'AGENT_USERNAME',
        'CAMPAIGN_NAME', 'ZOHO_ID', 'ZOHO_EMAIL', 'ZOHO_STATUS'
    ]

    for i, record in enumerate(raw_records):
        record_id = record.get('id')

        # Extract any phone - related data
        phone_related_data = {}
        for field in phone_fields:
            value = record.get(field)
            if value is not None and value != '':
                phone_related_data[field] = value

        if phone_related_data:
            # Categorize the record
            if record.get('CALL_ID'):
                phone_data['phone_call_records'].append({
                    'record_index': i,
                    'record_id': record_id,
                    'call_data': phone_related_data
                })

            if record.get('CONTACT_TYPE') or record.get('CONTACT_NEW'):
                phone_data['contact_records'].append({
                    'record_index': i,
                    'record_id': record_id,
                    'contact_data': phone_related_data
                })

            if record.get('PHONE_NUMBER') or record.get('PHONE_EXTERNAL'):
                phone_data['phone_number_records'].append({
                    'record_index': i,
                    'record_id': record_id,
                    'phone_data': phone_related_data
                })

            if any(field.startswith('ZOHO_') for field in phone_related_data.keys()):
                phone_data['zoho_integration_records'].append({
                    'record_index': i,
                    'record_id': record_id,
                    'zoho_data': phone_related_data
                })

            if record.get('AGENT_USERNAME') or record.get('CAMPAIGN_NAME'):
                phone_data['agent_interaction_records'].append({
                    'record_index': i,
                    'record_id': record_id,
                    'agent_data': phone_related_data
                })

            # Track field coverage
            for field, value in phone_related_data.items():
                if field not in phone_data['phone_field_coverage']:
                    phone_data['phone_field_coverage'][field] = []
                phone_data['phone_field_coverage'][field].append({
                    'record_index': i,
                    'record_id': record_id,
                    'value': value
                })

    # Generate summary
    phone_data['summary'] = {
        'total_phone_call_records': len(phone_data['phone_call_records']),
        'total_contact_records': len(phone_data['contact_records']),
        'total_phone_number_records': len(phone_data['phone_number_records']),
        'total_zoho_records': len(phone_data['zoho_integration_records']),
        'total_agent_records': len(phone_data['agent_interaction_records']),
        'fields_with_data': list(phone_data['phone_field_coverage'].keys()),
        'total_phone_related_records': sum([
            len(phone_data['phone_call_records']),
            len(phone_data['contact_records']),
            len(phone_data['phone_number_records']),
            len(phone_data['zoho_integration_records']),
            len(phone_data['agent_interaction_records'])
        ])
    }

    return phone_data

def build_master_consolidated_file(data_files: Dict[str, Any]) -> Dict[str, Any]:
    """Build the complete master consolidated file"""

    print("🏗️ Building master consolidated file...")

    # Extract phone data from raw records
    phone_data = {}
    if data_files['raw_data'] and data_files['raw_data'].get('raw_records'):
        phone_data = extract_phone_data_from_raw(data_files['raw_data']['raw_records'])

    # Build master file structure
    master_file = {
        'metadata': {
            'consolidation_timestamp': datetime.now().isoformat(),
            'customer_email': 'e.j.price1986@gmail.com',
            'entity_id': 'dc93a2cd - de0a - 444f - ad47 - 3003ba998cd3',
            'data_sources_included': [],
            'total_records_analyzed': 0,
            'completeness_score': 0.0
        },

        # Customer Identity (from consolidated data)
        'customer_identity': {},

        # Complete Credit Profile (from deep credit analysis)
        'complete_credit_profile': {},

        # Complete Transaction Profile (from transaction analysis)
        'complete_transaction_profile': {},

        # Complete Phone Profile (extracted from raw data)
        'complete_phone_profile': phone_data,

        # Card Profile
        'complete_card_profile': {},

        # Ticket Profile
        'complete_ticket_profile': {},

        # Raw Data (all original records)
        'complete_raw_data': {},

        # Data Quality Assessment
        'data_quality_assessment': {},

        # Field Inventory (complete list of all fields)
        'complete_field_inventory': {}
    }

    # Populate from consolidated data
    if data_files['consolidated_data']:
        master_file['customer_identity'] = data_files['consolidated_data'].get('customer_identity', {})
        master_file['complete_card_profile'] = data_files['consolidated_data'].get('card_profile', {})
        master_file['complete_ticket_profile'] = data_files['consolidated_data'].get('communication_profile', {})
        master_file['metadata']['data_sources_included'].append('consolidated_identity_data')

    # Populate credit data
    if data_files['credit_data']:
        credit_records = [r for r in data_files['credit_data']['deep_records'] if r.get('CREDIT_RESPONSE')]
        master_file['complete_credit_profile'] = {
            'total_credit_reports': len(credit_records),
            'credit_reports': credit_records,
            'credit_analysis': data_files['credit_data'].get('analysis', {}),
            'credit_metadata': data_files['credit_data'].get('metadata', {})
        }
        master_file['metadata']['data_sources_included'].append('deep_credit_analysis')

    # Populate transaction data
    if data_files['transaction_data']:
        master_file['complete_transaction_profile'] = data_files['transaction_data']
        master_file['metadata']['data_sources_included'].append('complete_transaction_analysis')

    # Populate raw data
    if data_files['raw_data']:
        master_file['complete_raw_data'] = data_files['raw_data']
        master_file['metadata']['total_records_analyzed'] = len(data_files['raw_data'].get('raw_records', []))
        master_file['complete_field_inventory'] = data_files['raw_data'].get('complete_field_inventory', {})
        master_file['metadata']['data_sources_included'].append('complete_raw_data_map')

    # Calculate completeness score
    completeness_factors = []

    if master_file['customer_identity']:
        identity_complete = bool(
            master_file['customer_identity'].get('email') and
            master_file['customer_identity'].get('first_name') and
            master_file['customer_identity'].get('last_name')
        )
        completeness_factors.append(1.0 if identity_complete else 0.5)

    if master_file['complete_credit_profile']:
        credit_complete = master_file['complete_credit_profile'].get('total_credit_reports', 0) > 0
        completeness_factors.append(1.0 if credit_complete else 0.0)

    if master_file['complete_transaction_profile']:
        transaction_complete = master_file['complete_transaction_profile'].get('total_transaction_records', 0) > 0
        completeness_factors.append(1.0 if transaction_complete else 0.0)

    if master_file['complete_phone_profile']:
        phone_complete = master_file['complete_phone_profile']['summary'].get('total_phone_related_records', 0) > 0
        completeness_factors.append(1.0 if phone_complete else 0.0)

    master_file['metadata']['completeness_score'] = sum(completeness_factors) / len(completeness_factors) if completeness_factors else 0.0

    # Data quality assessment
    master_file['data_quality_assessment'] = {
        'identity_data_quality': 'complete' if master_file['customer_identity'] else 'missing',
        'credit_data_quality': 'complete' if master_file['complete_credit_profile'].get('total_credit_reports', 0) > 0 else 'missing',
        'transaction_data_quality': 'complete' if master_file['complete_transaction_profile'].get('total_transaction_records', 0) > 0 else 'missing',
        'phone_data_quality': 'partial' if master_file['complete_phone_profile']['summary'].get('total_phone_related_records', 0) > 0 else 'missing',
        'overall_quality_score': master_file['metadata']['completeness_score']
    }

    return master_file

def generate_master_summary_report(master_file: Dict[str, Any]) -> str:
    """Generate comprehensive summary report"""

    metadata = master_file['metadata']
    identity = master_file['customer_identity']
    credit = master_file['complete_credit_profile']
    transactions = master_file['complete_transaction_profile']
    phone = master_file['complete_phone_profile']
    quality = master_file['data_quality_assessment']

    report = []
    report.append("🎯 COMPLETE MASTER DATA CONSOLIDATION REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {metadata['consolidation_timestamp']}")
    report.append(f"Customer: {metadata['customer_email']}")
    report.append(f"Entity ID: {metadata['entity_id']}")
    report.append(f"Completeness Score: {metadata['completeness_score']:.1%}")
    report.append("")

    # Data Sources
    report.append("📂 DATA SOURCES INCLUDED")
    report.append("-" * 40)
    for source in metadata['data_sources_included']:
        report.append(f"  ✅ {source}")
    report.append("")

    # Customer Identity
    report.append("👤 CUSTOMER IDENTITY")
    report.append("-" * 40)
    report.append(f"Name: {identity.get('first_name')} {identity.get('last_name')}")
    report.append(f"Email: {identity.get('email')}")
    report.append(f"Client ID: {identity.get('client_id')}")
    report.append(f"Phone: {identity.get('phone_number', 'Not available')}")
    report.append("")

    # Credit Profile
    report.append("💳 CREDIT PROFILE")
    report.append("-" * 40)
    if credit:
        report.append(f"Total Credit Reports: {credit.get('total_credit_reports', 0)}")
        if credit.get('credit_reports'):
            report.append("Credit Report Timeline:")
            for i, cr_record in enumerate(credit['credit_reports'][:5]):  # Show first 5
                cr = cr_record.get('CREDIT_RESPONSE', {})
                report.append(f"  {i + 1}. {cr.get('CreditReportFirstIssuedDate')} - {cr.get('CREDIT_BUREAU')} (Report {cr.get('Report_ID')})")
            if len(credit['credit_reports']) > 5:
                report.append(f"  ... and {len(credit['credit_reports']) - 5} more reports")
    else:
        report.append("No credit data available")
    report.append("")

    # Transaction Profile
    report.append("💰 TRANSACTION PROFILE")
    report.append("-" * 40)
    if transactions:
        report.append(f"Total Transaction Records: {transactions.get('total_transaction_records', 0)}")
        by_type = transactions.get('transactions_by_type', {})
        report.append(f"Direct Transactions: {len(by_type.get('direct_transactions', []))}")
        report.append(f"Payment History: {len(by_type.get('payment_history', []))}")
        report.append(f"Payment Schedule: {len(by_type.get('payment_schedule', []))}")
    else:
        report.append("No transaction data available")
    report.append("")

    # Phone Profile
    report.append("📞 PHONE PROFILE")
    report.append("-" * 40)
    if phone and phone.get('summary'):
        summary = phone['summary']
        report.append(f"Total Phone - Related Records: {summary.get('total_phone_related_records', 0)}")
        report.append(f"Phone Call Records: {summary.get('total_phone_call_records', 0)}")
        report.append(f"Contact Records: {summary.get('total_contact_records', 0)}")
        report.append(f"Phone Number Records: {summary.get('total_phone_number_records', 0)}")
        report.append(f"Zoho Integration Records: {summary.get('total_zoho_records', 0)}")
        report.append(f"Agent Interaction Records: {summary.get('total_agent_records', 0)}")

        if summary.get('fields_with_data'):
            report.append(f"Phone Fields with Data: {', '.join(summary['fields_with_data'])}")
    else:
        report.append("No phone data available")
    report.append("")

    # Data Quality
    report.append("📊 DATA QUALITY ASSESSMENT")
    report.append("-" * 40)
    report.append(f"Identity Data: {quality.get('identity_data_quality', 'unknown').upper()}")
    report.append(f"Credit Data: {quality.get('credit_data_quality', 'unknown').upper()}")
    report.append(f"Transaction Data: {quality.get('transaction_data_quality', 'unknown').upper()}")
    report.append(f"Phone Data: {quality.get('phone_data_quality', 'unknown').upper()}")
    report.append(f"Overall Quality Score: {quality.get('overall_quality_score', 0):.1%}")

    return "\\n".join(report)

def main():
    """Main execution"""
    print("🚀 COMPLETE MASTER DATA CONSOLIDATION")
    print("=" * 70)

    # Load all data files
    data_files = load_all_data_files()

    # Build master consolidated file
    master_file = build_master_consolidated_file(data_files)

    # Save master file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    master_filename = f"MASTER_COMPLETE_DATA_{timestamp}.json"

    with open(master_filename, 'w') as f:
        json.dump(master_file, f, indent=2, default=str)

    print(f"\\n✅ Saved complete master file to {master_filename}")

    # Generate and save report
    report = generate_master_summary_report(master_file)
    report_filename = master_filename.replace('.json', '_REPORT.txt')

    with open(report_filename, 'w') as f:
        f.write(report)

    print(f"✅ Saved master report to {report_filename}")

    # Display report
    print("\\n" + report)

    print("\\n🎯 MASTER CONSOLIDATION COMPLETE!")
    print(f"📊 Master File: {master_filename}")
    print(f"📄 Master Report: {report_filename}")
    print("\\n✅ ALL DATA CONSOLIDATED INTO ONE CONTIGUOUS FILE!")

    return master_filename

if __name__ == "__main__":
    main()


