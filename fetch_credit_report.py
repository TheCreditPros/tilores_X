#!/usr/bin/env python3
"""
Fetch Complete Credit Report for marcogjones@yahoo.com

Queries the Tilores GraphQL API for the complete credit report data
and saves the most recent TransUnion report to a file.
"""

import sys
import requests
import json
from direct_credit_api_fixed import MultiProviderCreditAPI

def main():
    # Initialize the API
    api = MultiProviderCreditAPI()

    # Use the known entity ID
    entity_id = '77698532-9a13-46ac-bfe9-1d630452161d'
    print(f'🔍 Using entity ID: {entity_id}')

    # Query basic fields that we know exist from schema introspection
    query = '''
    query GetCompleteCreditReport($id: ID!) {
      entity(input: { id: $id }) {
        entity {
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditRatingCodeType
              CreditReportFirstIssuedDate
              CreditReportIdentifier
              CreditReportMergeTypeIndicator
              CreditResponseID
              MISMOVersionID
              Internal_Client_Key
              Client_key
              Report_ID
              Report_Type
              Vendor
            }
          }
        }
      }
    }
    '''

    print('🔍 Fetching complete credit report data...')
    response = requests.post(
        api.tilores_api_url,
        headers={'Authorization': f'Bearer {api.get_tilores_token()}'},
        json={'query': query, 'variables': {'id': entity_id}},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        print('✅ Credit data retrieved successfully')

        # Extract the credit response
        records = data.get('data', {}).get('entity', {}).get('entity', {}).get('records', [])
        if records:
            credit_response = records[0].get('CREDIT_RESPONSE')
            if credit_response:
                print(f'📊 Raw credit response type: {type(credit_response)}')
                print(f'📊 Credit response length: {len(str(credit_response))}')

                # Save the complete raw credit report
                with open('marcogjones_complete_credit_report.json', 'w') as f:
                    json.dump(credit_response, f, indent=2)

                print('💾 Saved complete credit report to: marcogjones_complete_credit_report.json')

                # Check if this is a TransUnion report
                bureau = credit_response.get('CREDIT_BUREAU', 'Unknown')
                print(f'🏛️ Credit Bureau: {bureau}')

                # Show a comprehensive summary
                print('\n📋 Credit Report Summary:')
                if isinstance(credit_response, dict):
                    # Basic info
                    print(f'  • Bureau: {bureau}')
                    print(f'  • Report ID: {credit_response.get("CreditResponseID", "N/A")}')
                    print(f'  • Report Date: {credit_response.get("CreditReportFirstIssuedDate", "N/A")}')

                    # Borrower info
                    borrower = credit_response.get('BORROWER', {})
                    if borrower:
                        print(f'  • Borrower: {borrower.get("FirstName", "")} {borrower.get("LastName", "")}')

                    # Summary TUI (TransUnion-specific summary)
                    summary_tui = credit_response.get('CREDIT_SUMMARY_TUI', {})
                    if summary_tui:
                        print(f'  • Credit Score: {summary_tui.get("CreditScore", "N/A")}')
                        print(f'  • Total Accounts: {summary_tui.get("TotalAccounts", "N/A")}')
                        print(f'  • Open Accounts: {summary_tui.get("OpenAccounts", "N/A")}')
                        print(f'  • Delinquent Accounts: {summary_tui.get("DelinquentAccounts", "N/A")}')

                    # Arrays
                    liability = credit_response.get('CREDIT_LIABILITY', [])
                    inquiry = credit_response.get('CREDIT_INQUIRY', [])
                    scores = credit_response.get('CREDIT_SCORE', [])

                    print(f'  • Tradelines: {len(liability)} accounts')
                    print(f'  • Inquiries: {len(inquiry)} records')
                    print(f'  • Credit Scores: {len(scores)} scores')

                    # Check if this is TransUnion and save specifically
                    if bureau and 'transunion' in bureau.lower():
                        print('\n🎯 FOUND TRANSUNION REPORT!')
                        # Save specifically as TransUnion report
                        with open('marcogjones_transunion_credit_report.json', 'w') as f:
                            json.dump(credit_response, f, indent=2)
                        print('💾 Also saved as: marcogjones_transunion_credit_report.json')

                        # Show some detailed information
                        print('\n📊 TransUnion Report Details:')
                        if liability:
                            print(f'  📈 Sample Tradeline: Account {liability[0].get("AccountIdentifier", "N/A")} - Balance: ${liability[0].get("BalanceAmount", "N/A")}')
                        if inquiry:
                            print(f'  🔍 Recent Inquiry: {inquiry[0].get("EndUserName", "N/A")} on {inquiry[0].get("InquiryDate", "N/A")}')
                    else:
                        print(f'\n📝 This is a {bureau} report, not TransUnion. Looking for TransUnion report...')
            else:
                print('❌ No CREDIT_RESPONSE found in records')
        else:
            print('❌ No records found')
    else:
        print(f'❌ GraphQL query failed: {response.status_code}')
        print(f'❌ Error: {response.text}')

if __name__ == '__main__':
    main()
