#!/usr / bin / env python3
"""
Comprehensive Live Data Mapper
Extracts EVERY field and element from the test customer's actual Tilores data
Creates a complete master map with all nested structures and real values
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

class ComprehensiveLiveDataMapper:
    """Maps every field and element from live customer data"""

    def __init__(self):
        self.tilores_api = None
        self.test_customer_email = "e.j.price1986@gmail.com"
        self.complete_data_map = {}
        self.field_inventory = defaultdict(list)
        self.nested_structures = {}

    def initialize_tilores(self) -> bool:
        """Initialize Tilores API connection"""
        try:
            from tilores import TiloresAPI
            self.tilores_api = TiloresAPI.from_environ()
            print("✅ Tilores API initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Tilores API: {e}")
            return False

    def extract_basic_customer_data(self) -> Optional[Dict[str, Any]]:
        """Extract basic customer data first"""

        print(f"🔍 Step 1: Extracting basic data for {self.test_customer_email}...")

        basic_query = """
        query BasicData {{
          search(input: {{ parameters: {{ EMAIL: "{self.test_customer_email}" }} }}) {{
            entities {{
              id
              records {{
                EMAIL
                FIRST_NAME
                LAST_NAME
                MIDDLE_NAME
                CLIENT_ID
                PHONE_NUMBER
                STATUS
                ACTIVE
                ENROLL_DATE
                CREATED_DATE
                TRANSACTION_AMOUNT
                PAYMENT_METHOD
                LAST_APPROVED_TRANSACTION
                LAST_APPROVED_TRANSACTION_AMOUNT
                CARD_LAST_4
                CARD_TYPE
                CALL_ID
                CALL_DURATION
                TICKETNUMBER
                ZOHO_STATUS
                CURRENT_PRODUCT
                ENROLLMENT_FEE
                CREDIT_RESPONSE {{
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(basic_query)
            if result and 'data' in result and result['data']['search']['entities']:
                return result['data']['search']['entities'][0]
            return None
        except Exception as e:
            print(f"❌ Basic data extraction failed: {e}")
            return None

    def extract_detailed_credit_data(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Extract detailed credit data using entity ID"""

        print(f"🔍 Step 2: Extracting detailed credit data for entity {entity_id}...")

        credit_query = """
        query DetailedCreditData {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                CREDIT_RESPONSE {{
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  CreditReportIdentifier
                  Report_ID
                  Report_Type
                  Vendor
                  BORROWER {{
                    FirstName
                    LastName
                    SSN
                    BirthDate
                    UnparsedName
                  }}
                  CREDIT_SCORE {{
                    Value
                    Date
                    CreditRepositorySourceType
                    ModelNameType
                  }}
                  CREDIT_LIABILITY {{
                    AccountIdentifier
                    AccountType
                    AccountStatusType
                    CreditLimitAmount
                    UnpaidBalanceAmount
                    MonthlyPaymentAmount
                    AccountOpenedDate
                    LastActivityDate
                    Creditor {{
                      Name
                      City
                      State
                    }}
                  }}
                  CREDIT_INQUIRY {{
                    Name
                    Date
                    PurposeType
                    City
                    State
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(credit_query)
            if result and 'data' in result and result['data']['entity']['entity']['records']:
                return result['data']['entity']['entity']['records']
            return None
        except Exception as e:
            print(f"❌ Credit data extraction failed: {e}")
            return None

    def extract_record_insights(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Extract record insights and aggregations"""

        print(f"🔍 Step 3: Extracting record insights for entity {entity_id}...")

        insights_query = """
        query RecordInsights {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Counts
                totalRecords: count
                activeRecords: count(filter: {{field: "ACTIVE", value: "true"}})

                # Credit insights
                creditScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                creditBureaus: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_BUREAU")

                # Transaction insights
                transactionAmounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                paymentMethods: valuesDistinct(field: "PAYMENT_METHOD")

                # Identity insights
                firstNames: valuesDistinct(field: "FIRST_NAME")
                lastNames: valuesDistinct(field: "LAST_NAME")
                emails: valuesDistinct(field: "EMAIL")
                clientIds: valuesDistinct(field: "CLIENT_ID")

                # Status insights
                statuses: valuesDistinct(field: "STATUS")
                products: valuesDistinct(field: "CURRENT_PRODUCT")

                # Temporal insights
                firstRecord: first {{
                  CREATED_DATE
                  ENROLL_DATE
                  EMAIL
                  FIRST_NAME
                  LAST_NAME
                  CLIENT_ID
                  STATUS
                }}
                latestRecord: newest {{
                  CREATED_DATE
                  LAST_APPROVED_TRANSACTION
                  STATUS
                  ACTIVE
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(insights_query)
            if result and 'data' in result and result['data']['entity']['entity']['recordInsights']:
                return result['data']['entity']['entity']['recordInsights']
            return None
        except Exception as e:
            print(f"❌ Record insights extraction failed: {e}")
            return None

    def extract_all_field_values(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Extract all possible field values using a comprehensive approach"""

        print(f"🔍 Step 4: Extracting ALL field values for entity {entity_id}...")

        # Use the complete field list from our schema analysis
        all_fields_query = """
        query AllFieldValues {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                # Identity fields
                EMAIL
                FIRST_NAME
                LAST_NAME
                MIDDLE_NAME
                PHONE_NUMBER
                AGENT_USERNAME
                CAMPAIGN_NAME
                PRODUCT_NAME
                SPOUSE_FULL_NAME
                STAGE_NAME

                # System fields
                CLIENT_ID
                STATUS
                ACTIVE
                GATHRR_CUSTOMER_ID
                OPPORTUNITY
                OPPORTUNITY_ID
                OPPORTUNITY_OWNER
                SOURCE
                SOURCE_TYPE
                PRIMARY

                # Dates
                CREATED_DATE
                CREATEDTIME
                ENROLL_DATE
                ENROLLMENT_CAPTURE_COMPLETED
                CANCELLATION_DATE
                CLOSE_DATE
                CLOSEDTIME

                # Financial fields
                AMOUNT
                CREDIT_AMOUNT
                ENROLLMENT_FEE
                ENROLLMENT_BALANCE
                NET_BALANCE_DUE
                SETUP_FEE2_AMOUNT
                RECURRING_MONTHLY_FEE
                DISCOUNT_AMOUNT
                COUPON_AMOUNT

                # Transaction fields
                TRANSACTION_AMOUNT
                LAST_APPROVED_TRANSACTION
                LAST_APPROVED_TRANSACTION_AMOUNT
                LAST_FAILED_TRANSACTION
                PAYMENT_METHOD
                PAYMENT_START_DATE
                PAYMENT_END_DATE
                DAYS_SINCE_LAST_APPROVED_TRANSACTION
                UPCOMING_SCHEDULED_PAYMENT
                UPCOMING_SCHEDULED_PAYMENT_AMOUNT
                CHARGEBACK
                REFUND_CONFIRMATION_SENT
                DEBT_PAYMENT
                DEBT_PAYMENT_DATE

                # Card fields
                CARD_NUMBER
                CARD_LAST_4
                CARD_FIRST_6_DIGIT
                CARD_TYPE
                EXPIRATION_MONTH
                EXPIRATION_YEAR
                CARD_EXPIRED
                INVALID_CARD
                BIN
                CVV

                # Phone fields
                CALL_ID
                CALL_START_TIME
                CALL_HANGUP_TIME
                CALL_DURATION
                CALL_TYPE
                CONTACT_TYPE
                PHONE_EXTERNAL
                ZOHO_CONTACT_ID
                ZOHO_PHONE
                CONTACT_NEW

                # Ticket fields
                TICKETNUMBER
                ZOHO_ID
                ZOHO_EMAIL
                ZOHO_STATUS
                CATEGORY
                SUBCATEGORY
                PRIORITY
                SUBJECT
                COMMENTCOUNT
                THREADCOUNT
                RESPONSEDUEDATE
                DUEDATE

                # Business fields
                CURRENT_PRODUCT
                CURRENT_PRODUCT_TYPE
                CONTRACT_SIGNED
                SUCCESS_PLUS_CONTRACT_SIGNED
                CANCEL_REASON
                CANCEL_REASONS
                CANCELLED_BY
                REENROLL_CLIENT
                RE_ENROLLMENT
                RE_ENROLL_DATE

                # Personal info
                DATE_OF_BIRTH
                CUSTOMER_AGE
                SPANISH_SPEAKER
                SPOUSE
                LANGUAGE
                SMS_OPT_OUT
                TCPA

                # Address fields
                MAILING_STREET
                MAILING_CITY
                MAILING_STATE
                MAILING_STATE_CODE
                MAILING_POSTAL_CODE

                # License fields
                DRIVING_LICENSE_NUMBER
                DRIVING_LICENSE_ISSUED_BY
                DRIVING_LICENSE_EXPIRY_DATE

                # System tracking
                id
                ORIGINAL_LEAD_ID
                REFERRED_BY_CLIENT
                GENERATE_REFERRAL_BY
                HOW_DID_YOU_HEAR_ABOUT_US
                WEB_ENROLLMENT
                WEB_ENROLLMENT_STATUS
                TCP_WEBSITE_ENROLLMENT

                # Status tracking
                KYC_STATUS
                TU_AUTHENTICATED
                VERIFY_IDENTITY
                ID_DOC_UPLOADED
                EMAIL_CONFIRMATION_DATE

                # Enrollment tracking
                DAYS_SINCE_ENROLL
                DAYS_SINCE_ENROLLED
                MONTHS_SINCE_ENROLL
                DAYS_SINCE_CREATED
                DAYS_SINCE_LAST_FAILED

                # Financial tracking
                PREPAID
                RECURRING
                NEXT_SUBSCRIPTION_DATE
                NEXT_TRANSACTION_DATE
                PAST_DUE_DATE
                IS_EB0_DATE

                # Response tracking
                RESPONSE_MESSAGE
                RESPONSE_STATUS
                GATEWAY_RESPONSE
                GATEWAY_DATE

                # Completion tracking
                CAP_COMPLETED
                CAP_COMPLETED_DATE
                CAP_MISSED
                ACE_CAP

                # Deal tracking
                DEAL_CLOSE_DATE
                DEAL_CLOSE_TIME
                COLD_LEAD_CREATED_DATE

                # Fee tracking
                SETUP_FEE2_DATE
                CLAWBACK_DATE
                CLAWBACK_REASONS

                # Age tracking
                AGE_OF_CANCELLATION

                # Portal
                CP_PORTAL_LINK

                # Additional system fields
                X18_CHAR_ID
                ID_18_CHAR
                SENTIMENT
                TYPE
                STATUSTYPE

                # Credit data (basic level)
                CREDIT_RESPONSE {{
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  CreditReportIdentifier
                  Report_ID
                  Report_Type
                  Vendor
                }}
                CHARGEBACK_CREDITED
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(all_fields_query)
            if result and 'data' in result and result['data']['entity']['entity']['records']:
                return result['data']['entity']['entity']['records']
            return None
        except Exception as e:
            print(f"❌ All fields extraction failed: {e}")
            return None

    def analyze_field_coverage(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze field coverage across all records"""

        print("📊 Analyzing field coverage...")

        field_stats = defaultdict(lambda: {'count': 0, 'non_null_count': 0, 'values': set(), 'sample_values': []})

        for record in records:
            self._analyze_record_fields(record, field_stats, "")

        # Convert to regular dict and process
        coverage_analysis = {}
        for field_path, stats in field_stats.items():
            coverage_analysis[field_path] = {
                'appears_in_records': stats['count'],
                'has_non_null_values': stats['non_null_count'],
                'coverage_percentage': round((stats['non_null_count'] / len(records)) * 100, 2) if records else 0,
                'unique_values': len(stats['values']),
                'sample_values': list(stats['sample_values'])[:5]  # First 5 unique values
            }

        return coverage_analysis

    def _analyze_record_fields(self, obj: Any, stats: Dict, path: str):
        """Recursively analyze fields in a record"""

        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                stats[current_path]['count'] += 1

                if value is not None:
                    stats[current_path]['non_null_count'] += 1
                    stats[current_path]['values'].add(str(value)[:100])  # Limit string length
                    if len(stats[current_path]['sample_values']) < 10:
                        stats[current_path]['sample_values'].append(value)

                # Recurse into nested objects
                if isinstance(value, (dict, list)):
                    self._analyze_record_fields(value, stats, current_path)

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    self._analyze_record_fields(item, stats, path)

    def build_complete_data_map(self) -> Dict[str, Any]:
        """Build the complete data map with all fields and elements"""

        print("🚀 BUILDING COMPLETE LIVE DATA MAP")
        print("=" * 60)

        # Step 1: Get basic data
        basic_data = self.extract_basic_customer_data()
        if not basic_data:
            print("❌ Failed to extract basic data")
            return {}

        entity_id = basic_data['id']
        basic_records = basic_data.get('records', [])

        print(f"✅ Found entity {entity_id} with {len(basic_records)} records")

        # Step 2: Get detailed credit data
        credit_records = self.extract_detailed_credit_data(entity_id)

        # Step 3: Get record insights
        insights = self.extract_record_insights(entity_id)

        # Step 4: Get all field values
        all_records = self.extract_all_field_values(entity_id)

        # Use the most comprehensive record set
        final_records = all_records or basic_records

        # Step 5: Analyze field coverage
        field_coverage = self.analyze_field_coverage(final_records)

        # Build complete data map
        complete_map = {
            'metadata': {
                'customer_email': self.test_customer_email,
                'entity_id': entity_id,
                'extraction_timestamp': datetime.now().isoformat(),
                'total_records': len(final_records),
                'total_fields_found': len(field_coverage),
                'fields_with_data': len([f for f, stats in field_coverage.items() if stats['has_non_null_values'] > 0])
            },
            'customer_summary': self._build_customer_summary(final_records, insights),
            'raw_records': final_records,
            'record_insights': insights,
            'field_coverage_analysis': field_coverage,
            'data_source_breakdown': self._categorize_data_sources(field_coverage),
            'complete_field_inventory': self._build_field_inventory(field_coverage)
        }

        return complete_map

    def _build_customer_summary(self, records: List[Dict], insights: Dict) -> Dict[str, Any]:
        """Build customer summary from records"""

        if not records:
            return {}

        # Get primary record (first one)
        primary = records[0]

        summary = {
            'identity': {
                'email': primary.get('EMAIL'),
                'first_name': primary.get('FIRST_NAME'),
                'last_name': primary.get('LAST_NAME'),
                'phone': primary.get('PHONE_NUMBER'),
                'client_id': primary.get('CLIENT_ID')
            },
            'account': {
                'status': primary.get('STATUS'),
                'active': primary.get('ACTIVE'),
                'enrollment_date': primary.get('ENROLL_DATE'),
                'created_date': primary.get('CREATED_DATE'),
                'current_product': primary.get('CURRENT_PRODUCT')
            },
            'financial': {
                'enrollment_fee': primary.get('ENROLLMENT_FEE'),
                'transaction_amount': primary.get('TRANSACTION_AMOUNT'),
                'payment_method': primary.get('PAYMENT_METHOD'),
                'last_transaction': primary.get('LAST_APPROVED_TRANSACTION')
            },
            'aggregated_insights': insights or {}
        }

        return summary

    def _categorize_data_sources(self, field_coverage: Dict) -> Dict[str, Dict]:
        """Categorize fields by data source"""

        categories = {
            'identity': [],
            'credit': [],
            'transaction': [],
            'card': [],
            'phone': [],
            'ticket': [],
            'business': [],
            'system': []
        }

        for field_path, stats in field_coverage.items():
            if stats['has_non_null_values'] == 0:
                continue  # Skip empty fields

            field_upper = field_path.upper()

            if any(term in field_upper for term in ['EMAIL', 'NAME', 'PHONE', 'ADDRESS', 'SSN', 'DOB']):
                categories['identity'].append({'field': field_path, 'stats': stats})
            elif any(term in field_upper for term in ['CREDIT', 'SCORE', 'BUREAU', 'LIABILITY', 'INQUIRY']):
                categories['credit'].append({'field': field_path, 'stats': stats})
            elif any(term in field_upper for term in ['TRANSACTION', 'PAYMENT', 'BILLING', 'CHARGE', 'REFUND']):
                categories['transaction'].append({'field': field_path, 'stats': stats})
            elif any(term in field_upper for term in ['CARD', 'BIN', 'EXPIR', 'CVV']):
                categories['card'].append({'field': field_path, 'stats': stats})
            elif any(term in field_upper for term in ['CALL', 'PHONE', 'CONTACT', 'ZOHO_PHONE']):
                categories['phone'].append({'field': field_path, 'stats': stats})
            elif any(term in field_upper for term in ['TICKET', 'ZOHO_ID', 'ZOHO_STATUS', 'CATEGORY']):
                categories['ticket'].append({'field': field_path, 'stats': stats})
            elif any(term in field_upper for term in ['PRODUCT', 'CAMPAIGN', 'ENROLLMENT', 'CONTRACT']):
                categories['business'].append({'field': field_path, 'stats': stats})
            else:
                categories['system'].append({'field': field_path, 'stats': stats})

        return categories

    def _build_field_inventory(self, field_coverage: Dict) -> Dict[str, Any]:
        """Build complete field inventory"""

        inventory = {
            'total_fields': len(field_coverage),
            'fields_with_data': 0,
            'fields_by_coverage': {
                'high_coverage': [],      # >80% coverage
                'medium_coverage': [],    # 20 - 80% coverage
                'low_coverage': [],       # <20% coverage
                'no_data': []            # 0% coverage
            },
            'most_populated_fields': [],
            'unique_value_fields': [],
            'complete_field_list': []
        }

        coverage_list = []

        for field_path, stats in field_coverage.items():
            coverage_pct = stats['coverage_percentage']

            if coverage_pct > 80:
                inventory['fields_by_coverage']['high_coverage'].append(field_path)
            elif coverage_pct > 20:
                inventory['fields_by_coverage']['medium_coverage'].append(field_path)
            elif coverage_pct > 0:
                inventory['fields_by_coverage']['low_coverage'].append(field_path)
            else:
                inventory['fields_by_coverage']['no_data'].append(field_path)

            if stats['has_non_null_values'] > 0:
                inventory['fields_with_data'] += 1
                coverage_list.append((field_path, coverage_pct, stats))

            inventory['complete_field_list'].append({
                'field': field_path,
                'coverage_percentage': coverage_pct,
                'non_null_count': stats['has_non_null_values'],
                'unique_values': stats['unique_values'],
                'sample_values': stats['sample_values']
            })

        # Sort by coverage
        coverage_list.sort(key=lambda x: x[1], reverse=True)
        inventory['most_populated_fields'] = [
            {'field': field, 'coverage': cov, 'unique_values': stats['unique_values']}
            for field, cov, stats in coverage_list[:20]
        ]

        return inventory

    def save_complete_data_map(self, data_map: Dict[str, Any], filename: str = None) -> str:
        """Save complete data map to file"""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complete_live_data_map_{timestamp}.json"

        print(f"💾 Saving complete data map to {filename}...")

        with open(filename, 'w') as f:
            json.dump(data_map, f, indent=2, default=str)

        print(f"✅ Saved complete data map to {filename}")
        return filename

    def generate_data_map_report(self, data_map: Dict[str, Any]) -> str:
        """Generate comprehensive data map report"""

        metadata = data_map.get('metadata', {})
        summary = data_map.get('customer_summary', {})
        field_coverage = data_map.get('field_coverage_analysis', {})
        data_sources = data_map.get('data_source_breakdown', {})
        inventory = data_map.get('complete_field_inventory', {})

        report = []
        report.append("🎯 COMPREHENSIVE LIVE DATA MAP REPORT")
        report.append("=" * 70)
        report.append(f"Customer: {metadata.get('customer_email')}")
        report.append(f"Entity ID: {metadata.get('entity_id')}")
        report.append(f"Generated: {metadata.get('extraction_timestamp')}")
        report.append("")

        # Overview
        report.append("📊 DATA OVERVIEW")
        report.append("-" * 40)
        report.append(f"Total Records: {metadata.get('total_records')}")
        report.append(f"Total Fields Found: {metadata.get('total_fields_found')}")
        report.append(f"Fields with Data: {metadata.get('fields_with_data')}")
        report.append(f"Data Coverage: {round((metadata.get('fields_with_data', 0) / metadata.get('total_fields_found', 1)) * 100, 1)}%")
        report.append("")

        # Customer Summary
        report.append("👤 CUSTOMER SUMMARY")
        report.append("-" * 40)
        identity = summary.get('identity', {})
        account = summary.get('account', {})
        financial = summary.get('financial', {})

        report.append(f"Name: {identity.get('first_name')} {identity.get('last_name')}")
        report.append(f"Email: {identity.get('email')}")
        report.append(f"Client ID: {identity.get('client_id')}")
        report.append(f"Phone: {identity.get('phone')}")
        report.append(f"Status: {account.get('status')}")
        report.append(f"Active: {account.get('active')}")
        report.append(f"Product: {account.get('current_product')}")
        report.append(f"Enrollment Date: {account.get('enrollment_date')}")
        report.append("")

        # Data Source Breakdown
        report.append("🗂️ DATA SOURCE BREAKDOWN")
        report.append("-" * 40)
        for source_name, fields in data_sources.items():
            if fields:
                report.append(f"{source_name.upper()}: {len(fields)} fields with data")
                for field_info in fields[:5]:  # Show top 5
                    field = field_info['field']
                    coverage = field_info['stats']['coverage_percentage']
                    report.append(f"  • {field}: {coverage}% coverage")
                if len(fields) > 5:
                    report.append(f"  ... and {len(fields) - 5} more fields")
                report.append("")

        # Field Coverage Analysis
        report.append("📈 FIELD COVERAGE ANALYSIS")
        report.append("-" * 40)
        coverage_breakdown = inventory.get('fields_by_coverage', {})
        report.append(f"High Coverage (>80%): {len(coverage_breakdown.get('high_coverage', []))} fields")
        report.append(f"Medium Coverage (20 - 80%): {len(coverage_breakdown.get('medium_coverage', []))} fields")
        report.append(f"Low Coverage (<20%): {len(coverage_breakdown.get('low_coverage', []))} fields")
        report.append(f"No Data (0%): {len(coverage_breakdown.get('no_data', []))} fields")
        report.append("")

        # Most Populated Fields
        report.append("🔥 MOST POPULATED FIELDS")
        report.append("-" * 40)
        most_populated = inventory.get('most_populated_fields', [])
        for i, field_info in enumerate(most_populated[:15], 1):
            field = field_info['field']
            coverage = field_info['coverage']
            unique = field_info['unique_values']
            report.append(f"{i:2d}. {field}: {coverage}% coverage, {unique} unique values")

        return "\n".join(report)

def main():
    """Main execution function"""
    print("🚀 COMPREHENSIVE LIVE DATA MAPPER")
    print("=" * 60)

    mapper = ComprehensiveLiveDataMapper()

    # Initialize Tilores API
    if not mapper.initialize_tilores():
        return

    # Build complete data map
    data_map = mapper.build_complete_data_map()
    if not data_map:
        print("❌ Failed to build data map")
        return

    # Save data map
    map_file = mapper.save_complete_data_map(data_map)

    # Generate report
    report = mapper.generate_data_map_report(data_map)

    # Save report
    report_file = map_file.replace('.json', '_report.txt')
    with open(report_file, 'w') as f:
        f.write(report)

    print("\n" + report)

    print("\n🎯 COMPREHENSIVE DATA MAP COMPLETE!")
    print(f"📊 Data Map: {map_file}")
    print(f"📄 Report: {report_file}")
    print("\n✅ Master map with ALL fields and elements ready!")

if __name__ == "__main__":
    main()


