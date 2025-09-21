#!/usr / bin / env python3
"""
Deep Credit Data Extractor
Attempts to extract the nested credit report arrays (scores, liabilities, inquiries, etc.)
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class DeepCreditDataExtractor:
    """Extracts deep nested credit report data"""

    def __init__(self):
        self.tilores_api = None
        self.test_customer_email = "e.j.price1986@gmail.com"
        self.entity_id = "dc93a2cd - de0a - 444f - ad47 - 3003ba998cd3"

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

    def extract_deep_credit_data(self) -> Optional[Dict[str, Any]]:
        """Extract deep nested credit data using specific queries"""

        print(f"🔍 Extracting DEEP credit data for entity {self.entity_id}...")

        # Try comprehensive credit query with all nested structures
        deep_credit_query = """
        query DeepCreditData {{
          entity(input: {{ id: "{self.entity_id}" }}) {{
            entity {{
              records {{
                id
                CREDIT_RESPONSE {{
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  CreditReportIdentifier
                  Report_ID
                  Report_Type
                  Vendor

                  # Borrower Information
                  BORROWER {{
                    FirstName
                    LastName
                    SSN
                    BirthDate
                    UnparsedName
                    RESIDENCE {{
                      City
                      State
                      PostalCode
                      StreetAddress
                      BorrowerResidencyType
                    }}
                  }}

                  # Credit Scores
                  CREDIT_SCORE {{
                    Value
                    Date
                    CreditRepositorySourceType
                    ModelNameType
                    RiskBasedPricingPercent
                    FACTOR {{
                      Code
                      Text
                      Factor_Type
                    }}
                  }}

                  # Credit Liabilities (Accounts)
                  CREDIT_LIABILITY {{
                    AccountIdentifier
                    AccountType
                    AccountStatusType
                    CreditLimitAmount
                    UnpaidBalanceAmount
                    MonthlyPaymentAmount
                    AccountOpenedDate
                    LastActivityDate
                    AccountClosedDate
                    HighBalanceAmount
                    OriginalBalanceAmount
                    PastDueAmount

                    CurrentRating {{
                      Code
                      Type
                    }}

                    HighestAdverseRating {{
                      Code
                      Type
                    }}

                    Creditor {{
                      Name
                      City
                      State
                      PostalCode
                      StreetAddress
                    }}

                    LateCount {{
                      Days30
                      Days60
                      Days90
                    }}

                    PaymentPattern {{
                      Data
                      StartDate
                    }}
                  }}

                  # Credit Inquiries
                  CREDIT_INQUIRY {{
                    Name
                    Date
                    PurposeType
                    City
                    State
                    PostalCode
                    StreetAddress
                    Phone
                    CreditBusinessType
                  }}

                  # Credit File Information
                  CREDIT_FILE {{
                    CreditRepositorySourceType
                    InfileDate
                    ResultStatusType

                    BORROWER {{
                      FirstName
                      LastName
                      SSN
                      BirthDate
                      UnparsedName

                      RESIDENCE {{
                        City
                        State
                        PostalCode
                        StreetAddress
                        BorrowerResidencyType
                        DateReported
                      }}

                      EMPLOYER {{
                        Name
                        CurrentEmploymentStartDate
                        EmploymentCurrentIndicator
                      }}

                      ALIAS {{
                        FirstName
                        LastName
                        MiddleName
                      }}
                    }}

                    ALERT_MESSAGE {{
                      CategoryType
                      Code
                      Text
                      Type
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(deep_credit_query)

            if result and 'data' in result and result['data']['entity']['entity']['records']:
                records = result['data']['entity']['entity']['records']
                print(f"✅ Retrieved {len(records)} records")
                return records
            else:
                print("❌ No records returned")
                return None

        except Exception as e:
            print(f"❌ Deep credit query failed: {e}")
            return None

    def try_record_insights_approach(self) -> Optional[Dict[str, Any]]:
        """Try using Record Insights to get aggregated credit data"""

        print(f"🔍 Trying Record Insights approach for entity {self.entity_id}...")

        insights_query = """
        query CreditInsights {{
          entity(input: {{ id: "{self.entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Credit Scores
                creditScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                creditScoreModels: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.ModelNameType")
                creditScoreDates: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Date")

                # Credit Accounts
                accountTypes: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.AccountType")
                accountStatuses: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.AccountStatusType")
                creditLimits: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.CreditLimitAmount")
                balances: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.UnpaidBalanceAmount")
                creditorNames: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.Creditor.Name")

                # Credit Inquiries
                inquiryNames: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_INQUIRY.Name")
                inquiryDates: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_INQUIRY.Date")
                inquiryPurposes: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_INQUIRY.PurposeType")

                # Borrower Info
                borrowerNames: valuesDistinct(field: "CREDIT_RESPONSE.BORROWER.FirstName")
                borrowerSSN: valuesDistinct(field: "CREDIT_RESPONSE.BORROWER.SSN")

                # Counts
                totalCreditScores: count(filter: {{field: "CREDIT_RESPONSE.CREDIT_SCORE.Value", exists: true}})
                totalAccounts: count(filter: {{field: "CREDIT_RESPONSE.CREDIT_LIABILITY.AccountIdentifier", exists: true}})
                totalInquiries: count(filter: {{field: "CREDIT_RESPONSE.CREDIT_INQUIRY.Name", exists: true}})
              }}
            }}
          }}
        }}
        """

        try:
            result = self.tilores_api.gql(insights_query)

            if result and 'data' in result and result['data']['entity']['entity']['recordInsights']:
                insights = result['data']['entity']['entity']['recordInsights']
                print("✅ Retrieved record insights")
                return insights
            else:
                print("❌ No insights returned")
                return None

        except Exception as e:
            print(f"❌ Record insights query failed: {e}")
            return None

    def analyze_credit_data_availability(self, records: List[Dict], insights: Dict) -> Dict[str, Any]:
        """Analyze what credit data is actually available"""

        analysis = {
            'records_with_credit': 0,
            'nested_data_found': {
                'credit_scores': 0,
                'credit_liabilities': 0,
                'credit_inquiries': 0,
                'borrower_info': 0,
                'credit_file': 0
            },
            'insights_data': insights or {},
            'sample_nested_structures': {},
            'data_availability_summary': {}
        }

        if records:
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    analysis['records_with_credit'] += 1

                    # Check for nested structures
                    if credit_response.get('CREDIT_SCORE'):
                        analysis['nested_data_found']['credit_scores'] += 1
                        if 'CREDIT_SCORE' not in analysis['sample_nested_structures']:
                            analysis['sample_nested_structures']['CREDIT_SCORE'] = credit_response['CREDIT_SCORE']

                    if credit_response.get('CREDIT_LIABILITY'):
                        analysis['nested_data_found']['credit_liabilities'] += 1
                        if 'CREDIT_LIABILITY' not in analysis['sample_nested_structures']:
                            analysis['sample_nested_structures']['CREDIT_LIABILITY'] = credit_response['CREDIT_LIABILITY']

                    if credit_response.get('CREDIT_INQUIRY'):
                        analysis['nested_data_found']['credit_inquiries'] += 1
                        if 'CREDIT_INQUIRY' not in analysis['sample_nested_structures']:
                            analysis['sample_nested_structures']['CREDIT_INQUIRY'] = credit_response['CREDIT_INQUIRY']

                    if credit_response.get('BORROWER'):
                        analysis['nested_data_found']['borrower_info'] += 1
                        if 'BORROWER' not in analysis['sample_nested_structures']:
                            analysis['sample_nested_structures']['BORROWER'] = credit_response['BORROWER']

                    if credit_response.get('CREDIT_FILE'):
                        analysis['nested_data_found']['credit_file'] += 1
                        if 'CREDIT_FILE' not in analysis['sample_nested_structures']:
                            analysis['sample_nested_structures']['CREDIT_FILE'] = credit_response['CREDIT_FILE']

        # Summarize availability
        analysis['data_availability_summary'] = {
            'has_credit_reports': analysis['records_with_credit'] > 0,
            'has_nested_credit_data': any(count > 0 for count in analysis['nested_data_found'].values()),
            'has_insights_data': bool(insights and any(insights.values())),
            'total_nested_structures': sum(analysis['nested_data_found'].values())
        }

        return analysis

def main():
    """Main execution"""
    print("🚀 DEEP CREDIT DATA EXTRACTION")
    print("=" * 60)

    extractor = DeepCreditDataExtractor()

    # Initialize API
    if not extractor.initialize_tilores():
        return

    # Try deep credit data extraction
    print("\n🔍 ATTEMPT 1: Deep Credit Query")
    print("-" * 40)
    deep_records = extractor.extract_deep_credit_data()

    # Try record insights approach
    print("\n🔍 ATTEMPT 2: Record Insights Approach")
    print("-" * 40)
    insights = extractor.try_record_insights_approach()

    # Analyze what we found
    analysis = extractor.analyze_credit_data_availability(deep_records or [], insights or {})

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"deep_credit_analysis_{timestamp}.json"

    results = {
        'metadata': {
            'extraction_timestamp': datetime.now().isoformat(),
            'customer_email': extractor.test_customer_email,
            'entity_id': extractor.entity_id
        },
        'deep_records': deep_records,
        'record_insights': insights,
        'analysis': analysis
    }

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Saved deep credit analysis to {filename}")

    # Print analysis summary
    print("\n📊 DEEP CREDIT DATA ANALYSIS")
    print("-" * 50)

    summary = analysis['data_availability_summary']
    nested_found = analysis['nested_data_found']

    print(f"Records with Credit Response: {analysis['records_with_credit']}")
    print(f"Has Nested Credit Data: {'✅' if summary['has_nested_credit_data'] else '❌'}")
    print(f"Has Insights Data: {'✅' if summary['has_insights_data'] else '❌'}")
    print(f"Total Nested Structures: {summary['total_nested_structures']}")

    print("\nNested Data Breakdown:")
    for data_type, count in nested_found.items():
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {data_type}: {count} records")

    if insights:
        print("\nRecord Insights Summary:")
        for key, value in insights.items():
            if value:
                print(f"  • {key}: {value}")

    if analysis['sample_nested_structures']:
        print("\nSample Nested Structures Found:")
        for structure_type in analysis['sample_nested_structures'].keys():
            print(f"  ✅ {structure_type}")

    return filename

if __name__ == "__main__":
    main()


