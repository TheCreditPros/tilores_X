#!/usr / bin / env python3
"""
Live Data Ground Truth Builder
Extracts complete real data from Tilores for test customer to create definitive ground truth dataset
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

@dataclass
class GroundTruthRecord:
    """Single ground truth test record with inputs and expected outputs"""
    id: str
    description: str
    inputs: Dict[str, Any]
    expected: Dict[str, Any]
    metadata: Dict[str, Any]

class LiveDataGroundTruthBuilder:
    """Builds ground truth dataset from live Tilores data"""
    
    def __init__(self):
        self.tilores_api = None
        self.test_customer_email = "e.j.price1986@gmail.com"
        self.test_customer_id = "7859095"
        self.ground_truth_records = []
        
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
    
    def extract_complete_customer_data(self) -> Optional[Dict[str, Any]]:
        """Extract complete customer data from Tilores"""
        
        print(f"🔍 Extracting complete data for {self.test_customer_email}...")
        
        # Start with basic query, then expand with multiple queries
        basic_query = """
        query BasicCustomerData {{
          search(input: {{ parameters: {{ EMAIL: "{self.test_customer_email}" }} }}) {{
            entities {{
              id
              records {{
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
                STATUS
                ACTIVE
                PHONE_NUMBER
                ENROLL_DATE
                CREATED_DATE
                TRANSACTION_AMOUNT
                PAYMENT_METHOD
                CREDIT_RESPONSE {{
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                }}
                CALL_ID
                CALL_DURATION
                TICKETNUMBER
                CARD_LAST_4
                CARD_TYPE
              }}
              recordInsights {{
                totalRecords: count
                creditScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                creditBureaus: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_BUREAU")
              }}
            }}
          }}
        }}
        """
        
        try:
            result = self.tilores_api.gql(basic_query)
            
            if result and 'data' in result and result['data']['search']['entities']:
                entity_data = result['data']['search']['entities'][0]  # First entity
                print(f"✅ Extracted complete data: {len(entity_data['records'])} records")
                return entity_data
            else:
                print(f"❌ No data found for {self.test_customer_email}")
                return None
                
        except Exception as e:
            print(f"❌ Data extraction failed: {e}")
            return None
    
    def build_ground_truth_test_cases(self, customer_data: Dict[str, Any]) -> List[GroundTruthRecord]:
        """Build comprehensive ground truth test cases from customer data"""
        
        print("🏗️  Building ground truth test cases...")
        
        records = customer_data.get('records', [])
        insights = customer_data.get('recordInsights', {})
        
        if not records:
            print("❌ No records found in customer data")
            return []
        
        # Extract key data points from records
        primary_record = records[0]  # Use first record as primary
        
        # Extract credit data
        credit_data = primary_record.get('CREDIT_RESPONSE', {})
        credit_scores = insights.get('creditScores', [])
        credit_bureaus = insights.get('creditBureaus', [])
        
        # Extract transaction data
        transaction_amount = primary_record.get('TRANSACTION_AMOUNT')
        last_transaction = primary_record.get('LAST_APPROVED_TRANSACTION')
        payment_method = primary_record.get('PAYMENT_METHOD')
        
        # Extract identity data
        first_name = primary_record.get('FIRST_NAME')
        last_name = primary_record.get('LAST_NAME')
        email = primary_record.get('EMAIL')
        phone = primary_record.get('PHONE_NUMBER')
        client_id = primary_record.get('CLIENT_ID')
        
        # Extract status data
        status = primary_record.get('STATUS')
        active = primary_record.get('ACTIVE')
        enrollment_date = primary_record.get('ENROLL_DATE')
        
        # Extract counts
        total_records = insights.get('totalRecords', 0)
        credit_reports = insights.get('creditReports', 0)
        phone_records = insights.get('phoneRecords', 0)
        transaction_records = insights.get('transactionRecords', 0)
        
        test_cases = []
        
        # Test Case 1: Basic Customer Profile
        test_cases.append(GroundTruthRecord(
            id="profile_basic",
            description="Basic customer profile lookup",
            inputs={
                "customer_id": email,
                "context": "basic profile"
            },
            expected={
                "customer_found": True,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "client_id": client_id,
                "status": status,
                "active": active,
                "total_records": total_records
            },
            metadata={
                "test_type": "identity_verification",
                "data_sources": ["identity", "system"],
                "complexity": "low"
            }
        ))
        
        # Test Case 2: Account Status Check
        test_cases.append(GroundTruthRecord(
            id="status_check",
            description="Account status and activity check",
            inputs={
                "customer_id": email,
                "context": "account status"
            },
            expected={
                "account_status": status,
                "is_active": active,
                "enrollment_date": enrollment_date,
                "has_recent_activity": bool(last_transaction),
                "total_records": total_records
            },
            metadata={
                "test_type": "status_verification",
                "data_sources": ["system", "transaction"],
                "complexity": "low"
            }
        ))
        
        # Test Case 3: Credit Analysis
        if credit_data and credit_scores:
            latest_score = max(credit_scores) if credit_scores else None
            
            test_cases.append(GroundTruthRecord(
                id="credit_analysis",
                description="Credit report analysis",
                inputs={
                    "customer_id": email,
                    "context": "credit analysis"
                },
                expected={
                    "has_credit_data": True,
                    "credit_scores": credit_scores,
                    "latest_score": latest_score,
                    "credit_bureaus": credit_bureaus,
                    "credit_reports_count": credit_reports,
                    "credit_bureau": credit_data.get('CREDIT_BUREAU'),
                    "report_date": credit_data.get('CreditReportFirstIssuedDate')
                },
                metadata={
                    "test_type": "credit_analysis",
                    "data_sources": ["credit"],
                    "complexity": "high"
                }
            ))
        
        # Test Case 4: Transaction History
        if transaction_amount or last_transaction:
            test_cases.append(GroundTruthRecord(
                id="transaction_history",
                description="Payment and transaction history",
                inputs={
                    "customer_id": email,
                    "context": "payment history"
                },
                expected={
                    "has_transactions": bool(transaction_amount or last_transaction),
                    "transaction_amount": transaction_amount,
                    "last_transaction": last_transaction,
                    "payment_method": payment_method,
                    "transaction_records_count": transaction_records
                },
                metadata={
                    "test_type": "transaction_analysis",
                    "data_sources": ["transaction"],
                    "complexity": "medium"
                }
            ))
        
        # Test Case 5: Comprehensive Analysis
        test_cases.append(GroundTruthRecord(
            id="comprehensive_analysis",
            description="Complete multi - data source analysis",
            inputs={
                "customer_id": email,
                "context": "comprehensive analysis"
            },
            expected={
                "customer_profile": {
                    "name": f"{first_name} {last_name}",
                    "email": email,
                    "client_id": client_id,
                    "status": status
                },
                "data_availability": {
                    "credit_reports": credit_reports > 0,
                    "phone_records": phone_records > 0,
                    "transaction_records": transaction_records > 0,
                    "total_records": total_records
                },
                "risk_indicators": {
                    "has_credit_data": bool(credit_data),
                    "account_active": active,
                    "recent_activity": bool(last_transaction)
                }
            },
            metadata={
                "test_type": "comprehensive_analysis",
                "data_sources": ["identity", "credit", "transaction", "phone", "system"],
                "complexity": "high"
            }
        ))
        
        # Test Case 6: Risk Assessment
        risk_level = "low"  # Default
        if not active:
            risk_level = "high"
        elif not credit_data:
            risk_level = "medium"
        
        test_cases.append(GroundTruthRecord(
            id="risk_assessment",
            description="Customer risk assessment",
            inputs={
                "customer_id": email,
                "context": "risk assessment"
            },
            expected={
                "risk_level": risk_level,
                "risk_factors": {
                    "account_inactive": not active,
                    "no_credit_data": not bool(credit_data),
                    "no_recent_transactions": not bool(last_transaction)
                },
                "recommendation": "monitor" if risk_level == "low" else "review"
            },
            metadata={
                "test_type": "risk_assessment",
                "data_sources": ["credit", "transaction", "system"],
                "complexity": "high"
            }
        ))
        
        print(f"✅ Built {len(test_cases)} ground truth test cases")
        return test_cases
    
    def save_ground_truth_dataset(self, test_cases: List[GroundTruthRecord], filename: str = None) -> str:
        """Save ground truth dataset to JSONL file"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ground_truth_dataset_{timestamp}.jsonl"
        
        print(f"💾 Saving ground truth dataset to {filename}...")
        
        with open(filename, 'w') as f:
            for test_case in test_cases:
                # Convert to dict and write as JSONL
                record_dict = asdict(test_case)
                f.write(json.dumps(record_dict, default=str) + '\n')
        
        print(f"✅ Saved {len(test_cases)} test cases to {filename}")
        return filename
    
    def generate_evaluation_config(self, dataset_filename: str) -> str:
        """Generate evaluation configuration file"""
        
        config_filename = dataset_filename.replace('.jsonl', '_eval_config.json')
        
        config = {
            "dataset_file": dataset_filename,
            "test_customer": {
                "email": self.test_customer_email,
                "id": self.test_customer_id,
                "description": "Primary test customer with complete multi - data source records"
            },
            "field_weights": {
                "customer_found": 3.0,
                "first_name": 2.0,
                "last_name": 2.0,
                "email": 3.0,
                "client_id": 2.0,
                "status": 2.0,
                "active": 2.0,
                "has_credit_data": 3.0,
                "credit_scores": 2.0,
                "latest_score": 2.0,
                "risk_level": 3.0,
                "recommendation": 2.0,
                "total_records": 1.0
            },
            "evaluation_criteria": {
                "exact_match_fields": ["email", "client_id", "status", "active"],
                "numeric_tolerance_fields": ["total_records", "credit_reports_count"],
                "list_comparison_fields": ["credit_scores", "credit_bureaus"],
                "llm_judge_fields": ["recommendation", "risk_factors"]
            },
            "scoring_thresholds": {
                "pass_threshold": 0.80,
                "excellent_threshold": 0.95,
                "numeric_tolerance_percent": 0.02,
                "string_similarity_threshold": 0.85
            }
        }
        
        with open(config_filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Generated evaluation config: {config_filename}")
        return config_filename
    
    def generate_summary_report(self, test_cases: List[GroundTruthRecord]) -> str:
        """Generate summary report of the ground truth dataset"""
        
        report = []
        report.append("🎯 GROUND TRUTH DATASET SUMMARY")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Test Customer: {self.test_customer_email}")
        report.append(f"Total Test Cases: {len(test_cases)}")
        report.append("")
        
        # Group by test type
        by_type = {}
        by_complexity = {}
        by_data_sources = {}
        
        for test_case in test_cases:
            test_type = test_case.metadata.get('test_type', 'unknown')
            complexity = test_case.metadata.get('complexity', 'unknown')
            data_sources = test_case.metadata.get('data_sources', [])
            
            by_type[test_type] = by_type.get(test_type, 0) + 1
            by_complexity[complexity] = by_complexity.get(complexity, 0) + 1
            
            for source in data_sources:
                by_data_sources[source] = by_data_sources.get(source, 0) + 1
        
        report.append("📊 TEST CASE BREAKDOWN")
        report.append("-" * 30)
        report.append("By Test Type:")
        for test_type, count in sorted(by_type.items()):
            report.append(f"  • {test_type}: {count} cases")
        
        report.append("\nBy Complexity:")
        for complexity, count in sorted(by_complexity.items()):
            report.append(f"  • {complexity}: {count} cases")
        
        report.append("\nBy Data Sources:")
        for source, count in sorted(by_data_sources.items()):
            report.append(f"  • {source}: {count} cases")
        
        report.append("")
        report.append("📋 DETAILED TEST CASES")
        report.append("-" * 30)
        
        for i, test_case in enumerate(test_cases, 1):
            report.append(f"{i}. {test_case.id}")
            report.append(f"   Description: {test_case.description}")
            report.append(f"   Type: {test_case.metadata.get('test_type')}")
            report.append(f"   Complexity: {test_case.metadata.get('complexity')}")
            report.append(f"   Data Sources: {', '.join(test_case.metadata.get('data_sources', []))}")
            report.append(f"   Expected Fields: {len(test_case.expected)}")
            report.append("")
        
        return "\n".join(report)

def main():
    """Main execution function"""
    print("🚀 LIVE DATA GROUND TRUTH BUILDER")
    print("=" * 60)
    
    builder = LiveDataGroundTruthBuilder()
    
    # Initialize Tilores API
    if not builder.initialize_tilores():
        return
    
    # Extract complete customer data
    customer_data = builder.extract_complete_customer_data()
    if not customer_data:
        return
    
    # Build ground truth test cases
    test_cases = builder.build_ground_truth_test_cases(customer_data)
    if not test_cases:
        return
    
    # Save dataset
    dataset_file = builder.save_ground_truth_dataset(test_cases)
    
    # Generate evaluation config
    config_file = builder.generate_evaluation_config(dataset_file)
    
    # Generate summary report
    summary = builder.generate_summary_report(test_cases)
    
    # Save summary report
    summary_file = dataset_file.replace('.jsonl', '_summary.txt')
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print("\n" + summary)
    
    print("\n🎯 GROUND TRUTH DATASET COMPLETE!")
    print(f"📄 Dataset: {dataset_file}")
    print(f"⚙️  Config: {config_file}")
    print(f"📊 Summary: {summary_file}")
    print("\n✅ Ready for Agenta evaluation testing!")

if __name__ == "__main__":
    main()
