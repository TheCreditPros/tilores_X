#!/usr/bin/env python3
"""
Investigate Credit Score Dates - Find why dates are missing in CREDIT_SCORE
Critical for temporal analysis and answering user queries about score changes
"""

from dotenv import load_dotenv
load_dotenv()

def investigate_score_date_fields():
    """Investigate the CREDIT_SCORE structure to find date fields"""

    print("🔍 INVESTIGATING CREDIT SCORE DATE FIELDS")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Focused query on CREDIT_SCORE fields
        score_query = """
        query InvestigateScoreDates {{
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

                  # Detailed CREDIT_SCORE investigation
                  CREDIT_SCORE {{
                    # All possible date fields
                    Date
                    CreditReportFirstIssuedDate
                    CreditReportIdentifier

                    # Score information
                    Value
                    ModelNameType
                    CreditRepositorySourceType
                    CreditScoreID

                    # Additional fields that might contain dates
                    BorrowerID
                    CreditFileID

                    # Factors
                    FACTOR {{
                      Code
                      Text
                      Factor_Type
                    }}
                  }}

                  # Also check CREDIT_FILE for dates
                  CREDIT_FILE {{
                    CreditFileID
                    CreditRepositorySourceType
                    InfileDate
                    ResultStatusType
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing focused score date investigation...")
        result = tilores_api.gql(score_query)

        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            print(f"✅ Query successful! Found {len(records)} records")

            # Analyze each record for score date information
            for i, record in enumerate(records):
                credit_response = record.get("CREDIT_RESPONSE")
                if credit_response:
                    print(f"\n📊 Record {i + 1} - CREDIT_RESPONSE Analysis:")

                    # Check report-level dates
                    print(f"   📅 Report Date: {credit_response.get('CreditReportFirstIssuedDate')}")
                    print(f"   🆔 Report ID: {credit_response.get('CreditReportIdentifier')}")
                    print(f"   🏢 Bureau: {credit_response.get('CREDIT_BUREAU')}")

                    # Check credit file dates
                    credit_file = credit_response.get("CREDIT_FILE")
                    if credit_file:
                        print(f"   📁 Credit File ID: {credit_file.get('CreditFileID')}")
                        print(f"   📅 Infile Date: {credit_file.get('InfileDate')}")
                        print(f"   🏢 Repository: {credit_file.get('CreditRepositorySourceType')}")

                    # Check credit scores
                    scores = credit_response.get("CREDIT_SCORE")
                    if scores:
                        if isinstance(scores, list):
                            print(f"   📈 Found {len(scores)} credit scores:")
                            for j, score in enumerate(scores):
                                print(f"      Score {j + 1}:")
                                print(f"         Value: {score.get('Value')}")
                                print(f"         Date: {score.get('Date')}")
                                print(f"         Model: {score.get('ModelNameType')}")
                                print(f"         Score ID: {score.get('CreditScoreID')}")
                                print(f"         File ID: {score.get('CreditFileID')}")
                                print(f"         Repository: {score.get('CreditRepositorySourceType')}")
                        elif isinstance(scores, dict):
                            print("   📈 Single credit score:")
                            print(f"      Value: {scores.get('Value')}")
                            print(f"      Date: {scores.get('Date')}")
                            print(f"      Model: {scores.get('ModelNameType')}")
                            print(f"      Score ID: {scores.get('CreditScoreID')}")
                            print(f"      File ID: {scores.get('CreditFileID')}")
                            print(f"      Repository: {scores.get('CreditRepositorySourceType')}")

                    print("   " + "-" * 40)

            return True

        else:
            print(f"❌ Query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Score date investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def investigate_alternative_date_fields():
    """Investigate alternative fields that might contain score dates"""

    print("\n🔍 INVESTIGATING ALTERNATIVE DATE FIELDS")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Look for any date-related fields in the schema
        alternative_query = """
        query AlternativeDateFields {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                # Look for any date fields that might be related to scores
                CREDIT_RESPONSE {{
                  # All possible date fields
                  CreditReportFirstIssuedDate
                  CreditReportIdentifier
                  Report_ID
                  Report_Type
                  Vendor

                  # Check if there are other date fields
                  CREDIT_SCORE {{
                    Value
                    ModelNameType
                    CreditRepositorySourceType
                    CreditScoreID
                    CreditFileID
                    BorrowerID
                    RiskBasedPricingMax
                    RiskBasedPricingMin
                    RiskBasedPricingPercent
                    InquiriesAffectedScore

                    # Look for any date-related fields
                    Date
                    ScoreDate
                    ReportDate
                    GeneratedDate
                    CalculatedDate
                  }}

                  # Check other sections for dates
                  CREDIT_FILE {{
                    CreditFileID
                    CreditRepositorySourceType
                    InfileDate
                    ResultStatusType
                    BorrowerID
                    CreditScoreID
                  }}

                  # Check if there are date fields in other sections
                  CREDIT_INQUIRY {{
                    Date
                    Name
                    PurposeType
                  }}

                  CREDIT_LIABILITY {{
                    AccountOpenedDate
                    AccountClosedDate
                    LastPaymentDate
                    LastActivityDate
                    ChargeOffDate
                    CollectionDate
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing alternative date field investigation...")
        result = tilores_api.gql(alternative_query)

        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            print(f"✅ Alternative query successful! Found {len(records)} records")

            # Look for any date fields that contain data
            date_fields_found = {}

            for i, record in enumerate(records):
                credit_response = record.get("CREDIT_RESPONSE")
                if credit_response:
                    print(f"\n📊 Record {i + 1} - Date Field Analysis:")

                    # Check all possible date fields
                    date_fields = [
                        ("CreditReportFirstIssuedDate", credit_response.get("CreditReportFirstIssuedDate")),
                        ("Report_ID", credit_response.get("Report_ID")),
                        ("Vendor", credit_response.get("Vendor"))
                    ]

                    for field_name, value in date_fields:
                        if value:
                            print(f"   ✅ {field_name}: {value}")
                            if field_name not in date_fields_found:
                                date_fields_found[field_name] = []
                            date_fields_found[field_name].append(value)
                        else:
                            print(f"   ❌ {field_name}: No data")

                    # Check credit file dates
                    credit_file = credit_response.get("CREDIT_FILE")
                    if credit_file:
                        infile_date = credit_file.get("InfileDate")
                        if infile_date:
                            print(f"   ✅ CREDIT_FILE.InfileDate: {infile_date}")
                            if "InfileDate" not in date_fields_found:
                                date_fields_found["InfileDate"] = []
                            date_fields_found["InfileDate"].append(infile_date)
                        else:
                            print("   ❌ CREDIT_FILE.InfileDate: No data")

                    # Check inquiry dates
                    inquiries = credit_response.get("CREDIT_INQUIRY")
                    if inquiries:
                        if isinstance(inquiries, list):
                            for inquiry in inquiries:
                                inquiry_date = inquiry.get("Date")
                                if inquiry_date:
                                    print(f"   ✅ CREDIT_INQUIRY.Date: {inquiry_date}")
                                    if "InquiryDate" not in date_fields_found:
                                        date_fields_found["InquiryDate"] = []
                                    date_fields_found["InquiryDate"].append(inquiry_date)
                        elif isinstance(inquiries, dict):
                            inquiry_date = inquiries.get("Date")
                            if inquiry_date:
                                print(f"   ✅ CREDIT_INQUIRY.Date: {inquiry_date}")
                                if "InquiryDate" not in date_fields_found:
                                    date_fields_found["InquiryDate"] = []
                                date_fields_found["InquiryDate"].append(inquiry_date)

                    # Check liability dates
                    liabilities = credit_response.get("CREDIT_LIABILITY")
                    if liabilities:
                        if isinstance(liabilities, list):
                            for liability in liabilities:
                                for date_field in ["AccountOpenedDate", "AccountClosedDate", "LastPaymentDate"]:
                                    date_value = liability.get(date_field)
                                    if date_value:
                                        print(f"   ✅ CREDIT_LIABILITY.{date_field}: {date_value}")
                                        if date_field not in date_fields_found:
                                            date_fields_found[date_field] = []
                                        date_fields_found[date_field].append(date_value)
                        elif isinstance(liabilities, dict):
                            for date_field in ["AccountOpenedDate", "AccountClosedDate", "LastPaymentDate"]:
                                date_value = liabilities.get(date_field)
                                if date_value:
                                    print(f"   ✅ CREDIT_LIABILITY.{date_field}: {date_value}")
                                    if date_field not in date_fields_found:
                                        date_fields_found[date_field] = []
                                    date_fields_found[date_field].append(date_value)

            # Summary of date fields found
            print("\n📊 DATE FIELD SUMMARY:")
            print("=" * 40)
            for field_name, values in date_fields_found.items():
                unique_values = list(set(values))
                print(f"   📅 {field_name}: {len(unique_values)} unique values")
                print(f"      Values: {unique_values[:5]}{'...' if len(unique_values) > 5 else ''}")

            return True

        else:
            print(f"❌ Alternative query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Alternative date investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def investigate_score_date_mapping():
    """Investigate how to map scores to dates using available fields"""

    print("\n🔍 INVESTIGATING SCORE-DATE MAPPING STRATEGIES")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Try to find relationships between scores and dates
        mapping_query = """
        query ScoreDateMapping {{
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

                  # Get scores with all possible identifiers
                  CREDIT_SCORE {{
                    Value
                    ModelNameType
                    CreditRepositorySourceType
                    CreditScoreID
                    CreditFileID
                    BorrowerID
                    CreditReportIdentifier
                    RiskBasedPricingMax
                    RiskBasedPricingMin
                    RiskBasedPricingPercent
                    InquiriesAffectedScore
                  }}

                  # Get credit file with dates
                  CREDIT_FILE {{
                    CreditFileID
                    CreditRepositorySourceType
                    InfileDate
                    ResultStatusType
                    BorrowerID
                    CreditScoreID
                  }}

                  # Get inquiries with dates
                  CREDIT_INQUIRY {{
                    Date
                    Name
                    PurposeType
                    CreditFileID
                    BorrowerID
                  }}

                  # Get liabilities with dates
                  CREDIT_LIABILITY {{
                    AccountOpenedDate
                    AccountClosedDate
                    LastPaymentDate
                    CreditFileID
                    BorrowerID
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing score-date mapping investigation...")
        result = tilores_api.gql(mapping_query)

        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            print(f"✅ Mapping query successful! Found {len(records)} records")

            # Analyze relationships between scores and dates
            for i, record in enumerate(records):
                credit_response = record.get("CREDIT_RESPONSE")
                if credit_response:
                    print(f"\n📊 Record {i + 1} - Score-Date Relationship Analysis:")

                    bureau = credit_response.get("CREDIT_BUREAU")
                    report_date = credit_response.get("CreditReportFirstIssuedDate")
                    report_id = credit_response.get("CreditReportIdentifier")

                    print(f"   🏢 Bureau: {bureau}")
                    print(f"   📅 Report Date: {report_date}")
                    print(f"   🆔 Report ID: {report_id}")

                    # Check credit scores
                    scores = credit_response.get("CREDIT_SCORE")
                    if scores:
                        if isinstance(scores, list):
                            print(f"   📈 Found {len(scores)} credit scores:")
                            for j, score in enumerate(scores):
                                print(f"      Score {j + 1}:")
                                print(f"         Value: {score.get('Value')}")
                                print(f"         Score ID: {score.get('CreditScoreID')}")
                                print(f"         File ID: {score.get('CreditFileID')}")
                                print(f"         Borrower ID: {score.get('BorrowerID')}")
                                print(f"         Repository: {score.get('CreditRepositorySourceType')}")
                        elif isinstance(scores, dict):
                            print("   📈 Single credit score:")
                            print(f"      Value: {scores.get('Value')}")
                            print(f"      Score ID: {scores.get('CreditScoreID')}")
                            print(f"      File ID: {scores.get('CreditFileID')}")
                            print(f"      Borrower ID: {scores.get('BorrowerID')}")
                            print(f"      Repository: {scores.get('CreditRepositorySourceType')}")

                    # Check credit file
                    credit_file = credit_response.get("CREDIT_FILE")
                    if credit_file:
                        print("   📁 Credit File:")
                        print(f"      File ID: {credit_file.get('CreditFileID')}")
                        print(f"      Infile Date: {credit_file.get('InfileDate')}")
                        print(f"      Repository: {credit_file.get('CreditRepositorySourceType')}")
                        print(f"      Borrower ID: {credit_file.get('BorrowerID')}")
                        print(f"      Score ID: {credit_file.get('CreditScoreID')}")

                    print("   " + "-" * 40)

            return True

        else:
            print(f"❌ Mapping query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Score-date mapping investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INVESTIGATING CREDIT SCORE DATE FIELDS")
    print("=" * 70)

    # Run all investigations
    test1_success = investigate_score_date_fields()
    test2_success = investigate_alternative_date_fields()
    test3_success = investigate_score_date_mapping()

    print("\n" + "=" * 70)
    print("📊 INVESTIGATION RESULTS:")
    print(f"   • Score Date Fields: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
    print(f"   • Alternative Date Fields: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")
    print(f"   • Score-Date Mapping: {'✅ SUCCESS' if test3_success else '❌ FAILED'}")

    overall_success = test1_success or test2_success or test3_success
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("🎉 Score date investigation successful!")
        print("   • Date field structure understood")
        print("   • Ready to implement date mapping")
        print("   • Temporal analysis can be enhanced")
    else:
        print("⚠️  Score date investigation needs more work")
