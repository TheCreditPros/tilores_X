#!/usr/bin/env python3
"""
Correct Bureau Field Query
Query the CreditResponseCreditRepositoryIncluded field for multi-bureau data
"""

from dotenv import load_dotenv
load_dotenv()

def correct_bureau_field_query():
    """Query the correct bureau field structure"""

    print("🔍 CORRECT BUREAU FIELD QUERY")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"  # Example entity ID for reference

    # Test 1: Query the CreditResponseCreditRepositoryIncluded field
    print("\n🔍 TEST 1: CREDIT RESPONSE REPOSITORY INCLUDED")
    print("-" * 50)

    query1 = """
    query CreditResponseRepositoryIncluded {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              CreditRepositoryIncluded {{
                CreditRepositorySourceType
                CreditRepositorySource
                Repository
                Source
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(query1)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 CREDIT RESPONSE REPOSITORY INCLUDED RESULTS:")
            print(f"   Total records: {len(records)}")

            all_bureaus = set()
            repository_details = []

            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        all_bureaus.add(bureau)

                    repository_included = credit_response.get('CreditRepositoryIncluded')
                    if repository_included:
                        for j, repo in enumerate(repository_included):
                            repo_source_type = repo.get('CreditRepositorySourceType')
                            repo_source = repo.get('CreditRepositorySource')
                            repository = repo.get('Repository')
                            source = repo.get('Source')

                            if any([repo_source_type, repo_source, repository, source]):
                                repository_details.append({
                                    "record_index": i,
                                    "repo_index": j,
                                    "credit_bureau": bureau,
                                    "repo_source_type": repo_source_type,
                                    "repo_source": repo_source,
                                    "repository": repository,
                                    "source": source
                                })

                                # Add any bureau info found
                                for field_value in [repo_source_type, repo_source, repository, source]:
                                    if field_value and isinstance(field_value, str):
                                        if any(bureau_name in field_value for bureau_name in ['TransUnion', 'Experian', 'Equifax', 'TU', 'EXP', 'EFX']):
                                            all_bureaus.add(field_value)

            print("\n📋 BUREAU ANALYSIS:")
            print(f"   All bureaus found: {list(all_bureaus)}")
            print(f"   Repository details found: {len(repository_details)}")

            if repository_details:
                print("\n📋 REPOSITORY DETAILS:")
                for detail in repository_details:
                    print(f"   Record {detail['record_index']}, Repo {detail['repo_index']}:")
                    print(f"     Credit Bureau: {detail['credit_bureau']}")
                    print(f"     Repo Source Type: {detail['repo_source_type']}")
                    print(f"     Repo Source: {detail['repo_source']}")
                    print(f"     Repository: {detail['repository']}")
                    print(f"     Source: {detail['source']}")
                    print("     ---")

                # Check for multi-bureau coverage
                if len(all_bureaus) > 1:
                    print("\n✅ MULTI-BUREAU ENTITY CONFIRMED!")
                    print(f"   Bureaus: {list(all_bureaus)}")
                else:
                    print("\n⚠️  SINGLE BUREAU ENTITY")
                    print(f"   Only {list(all_bureaus)[0] if all_bureaus else 'No'} data available")
            else:
                print("\n❌ NO REPOSITORY DATA FOUND")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Check if there are other credit response fields
    print("\n🔍 TEST 2: OTHER CREDIT RESPONSE FIELDS")
    print("-" * 50)

    query2 = """
    query OtherCreditResponseFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              # Check for any other fields that might contain bureau info
              CreditRequestData {{
                CreditRepositoryIncluded {{
                  CreditRepositorySourceType
                  CreditRepositorySource
                }}
              }}
              # Check for any other nested structures
              CreditFile {{
                CreditRepositorySourceType
                CreditRepositorySource
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(query2)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 OTHER CREDIT RESPONSE FIELDS RESULTS:")
            print(f"   Total records: {len(records)}")

            # Analyze what we found
            all_bureaus = set()
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        all_bureaus.add(bureau)

                    # Check CreditRequestData
                    credit_request_data = credit_response.get('CreditRequestData')
                    if credit_request_data:
                        for request_data in credit_request_data:
                            repo_included = request_data.get('CreditRepositoryIncluded')
                            if repo_included:
                                for repo in repo_included:
                                    source_type = repo.get('CreditRepositorySourceType')
                                    source = repo.get('CreditRepositorySource')
                                    if source_type:
                                        all_bureaus.add(source_type)
                                    if source:
                                        all_bureaus.add(source)

                    # Check CreditFile
                    credit_file = credit_response.get('CreditFile')
                    if credit_file:
                        for file in credit_file:
                            source_type = file.get('CreditRepositorySourceType')
                            source = file.get('CreditRepositorySource')
                            if source_type:
                                all_bureaus.add(source_type)
                            if source:
                                all_bureaus.add(source)

            print(f"   All bureaus found: {list(all_bureaus)}")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    print("\n🎯 CORRECT BUREAU FIELD QUERY COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    correct_bureau_field_query()
