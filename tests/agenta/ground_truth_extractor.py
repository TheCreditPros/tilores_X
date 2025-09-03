#!/usr / bin / env python3
"""
Ground Truth Extractor for Agenta Testing Framework

Extracts comprehensive test cases and expected outputs from the master data file
to serve as authoritative ground truth for Agenta.ai prompt variant testing.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class GroundTruthExtractor:
    """Extract ground truth data from master data file for Agenta testing"""

    def __init__(self, master_data_file: str = None):
        """Initialize the ground truth extractor"""
        self.master_data_file = master_data_file or self._find_master_data_file()
        self.master_data = None
        self.ground_truth = {}

        if self.master_data_file and os.path.exists(self.master_data_file):
            self._load_master_data()
            self._extract_ground_truth()
        else:
            raise FileNotFoundError(f"Master data file not found: {self.master_data_file}")

    def _find_master_data_file(self) -> str:
        """Find the most recent master data file"""
        # Look for master data files in the current directory
        patterns = [
            "MASTER_COMPLETE_DATA_WITH_FULL_PHONE_*.json",
            "MASTER_COMPLETE_DATA_*.json"
        ]

        master_files = []
        for pattern in patterns:
            import glob
            files = glob.glob(pattern)
            master_files.extend(files)

        if master_files:
            # Return the most recent file
            return max(master_files, key=os.path.getmtime)

        return "MASTER_COMPLETE_DATA_WITH_FULL_PHONE_20250902_155645.json"

    def _load_master_data(self):
        """Load the master data file"""
        try:
            with open(self.master_data_file, 'r', encoding='utf - 8') as f:
                self.master_data = json.load(f)
            print(f"✅ Loaded master data from: {self.master_data_file}")
        except Exception as e:
            raise Exception(f"Failed to load master data: {e}")

    def _extract_ground_truth(self):
        """Extract ground truth fields from master data"""
        if not self.master_data:
            return

        # Extract metadata
        metadata = self.master_data.get('metadata', {})

        # Extract customer identity
        customer_identity = self.master_data.get('customer_identity', {})

        # Extract credit profile
        credit_profile = self.master_data.get('complete_credit_profile', {})

        # Extract transaction profile
        transaction_profile = self.master_data.get('complete_transaction_profile', {})

        # Extract phone profile
        phone_profile = self.master_data.get('complete_phone_profile', {})

        # Extract card profile
        card_profile = self.master_data.get('complete_card_profile', {})

        # Extract ticket profile
        ticket_profile = self.master_data.get('complete_ticket_profile', {})

        # Build comprehensive ground truth
        self.ground_truth = {
            # Customer Identity Fields (Exact Match - Weight 3.0)
            "customer_email": customer_identity.get('email'),
            "customer_name": f"{customer_identity.get('first_name', '')} {customer_identity.get('last_name', '')}".strip(),
            "first_name": customer_identity.get('first_name'),
            "last_name": customer_identity.get('last_name'),
            "client_id": customer_identity.get('client_id'),
            "entity_id": metadata.get('entity_id'),

            # Credit Analysis Fields (Mixed Weights)
            "total_credit_reports": credit_profile.get('total_credit_reports', 0),
            "has_credit_data": credit_profile.get('total_credit_reports', 0) > 0,
            "credit_bureau": self._extract_latest_credit_bureau(credit_profile),
            "latest_credit_score": self._extract_latest_credit_score(credit_profile),
            "credit_score_range": self._extract_credit_score_range(credit_profile),
            "credit_report_date_range": self._extract_credit_date_range(credit_profile),

            # Transaction Analysis Fields (Mixed Weights)
            "total_transactions": transaction_profile.get('total_transaction_records', 0),
            "has_transaction_data": transaction_profile.get('total_transaction_records', 0) > 0,
            "total_transaction_amount": self._extract_total_transaction_amount(transaction_profile),
            "average_transaction_amount": self._extract_average_transaction_amount(transaction_profile),
            "transaction_methods": self._extract_transaction_methods(transaction_profile),

            # Phone & Contact Fields (Boolean - Weight 2.0)
            "has_phone_data": len(phone_profile.get('contact_records', [])) > 0 or len(phone_profile.get('phone_number_records', [])) > 0,
            "contact_records_count": len(phone_profile.get('contact_records', [])),
            "phone_number_records_count": len(phone_profile.get('phone_number_records', [])),
            "zoho_integration_records_count": len(phone_profile.get('zoho_integration_records', [])),

            # Card & Ticket Fields (Boolean - Weight 2.0)
            "has_card_data": card_profile.get('has_cards', False),
            "total_cards": card_profile.get('total_cards', 0),
            "has_ticket_data": ticket_profile.get('has_tickets', False),
            "total_tickets": len(ticket_profile.get('tickets', [])),

            # Derived Risk Assessment Fields (Categorical - Weight 2.0)
            "risk_level": self._assess_risk_level(credit_profile),
            "account_status": self._determine_account_status(),
            "data_completeness": metadata.get('completeness_score', 0.0),

            # Data Availability Flags (Boolean - Weight 2.0)
            "customer_found": True,  # Since we have complete data
            "data_available": True,
            "multiple_data_sources": len(metadata.get('data_sources_included', [])) > 1,
        }

        print(f"✅ Extracted {len(self.ground_truth)} ground truth fields")

    def _extract_latest_credit_bureau(self, credit_profile: Dict) -> Optional[str]:
        """Extract the latest credit bureau from credit reports"""
        credit_reports = credit_profile.get('credit_reports', [])
        if credit_reports:
            latest_report = credit_reports[-1]  # Assuming reports are chronologically ordered
            return latest_report.get('CREDIT_RESPONSE', {}).get('CREDIT_BUREAU')
        return None

    def _extract_latest_credit_score(self, credit_profile: Dict) -> Optional[int]:
        """Extract the latest credit score"""
        credit_reports = credit_profile.get('credit_reports', [])
        if credit_reports:
            latest_report = credit_reports[-1]
            credit_response = latest_report.get('CREDIT_RESPONSE', {})
            credit_score_data = credit_response.get('CREDIT_SCORE')

            if isinstance(credit_score_data, list) and credit_score_data:
                score_value = credit_score_data[0].get('Value')
                try:
                    return int(score_value) if score_value else None
                except (ValueError, TypeError):
                    return None
            elif isinstance(credit_score_data, dict):
                score_value = credit_score_data.get('Value')
                try:
                    return int(score_value) if score_value else None
                except (ValueError, TypeError):
                    return None
        return None

    def _extract_credit_score_range(self, credit_profile: Dict) -> Optional[str]:
        """Extract credit score range from all reports"""
        scores = []
        credit_reports = credit_profile.get('credit_reports', [])

        for report in credit_reports:
            credit_response = report.get('CREDIT_RESPONSE', {})
            credit_score_data = credit_response.get('CREDIT_SCORE')

            if isinstance(credit_score_data, list):
                for score_entry in credit_score_data:
                    score_value = score_entry.get('Value')
                    try:
                        if score_value:
                            scores.append(int(score_value))
                    except (ValueError, TypeError):
                        continue
            elif isinstance(credit_score_data, dict):
                score_value = credit_score_data.get('Value')
                try:
                    if score_value:
                        scores.append(int(score_value))
                except (ValueError, TypeError):
                    continue

        if scores:
            return f"{min(scores)}-{max(scores)}"
        return None

    def _extract_credit_date_range(self, credit_profile: Dict) -> Optional[str]:
        """Extract date range from credit reports"""
        dates = []
        credit_reports = credit_profile.get('credit_reports', [])

        for report in credit_reports:
            credit_response = report.get('CREDIT_RESPONSE', {})
            date = credit_response.get('CreditReportFirstIssuedDate')
            if date:
                dates.append(date)

        if dates:
            dates.sort()
            return f"{dates[0]} to {dates[-1]}"
        return None

    def _extract_total_transaction_amount(self, transaction_profile: Dict) -> Optional[float]:
        """Extract total transaction amount"""
        financial_summary = transaction_profile.get('financial_summary', {})
        total_amount = financial_summary.get('total_amount')
        try:
            return float(total_amount) if total_amount is not None else None
        except (ValueError, TypeError):
            return None

    def _extract_average_transaction_amount(self, transaction_profile: Dict) -> Optional[float]:
        """Extract average transaction amount"""
        financial_summary = transaction_profile.get('financial_summary', {})
        avg_amount = financial_summary.get('average_amount')
        try:
            return float(avg_amount) if avg_amount is not None else None
        except (ValueError, TypeError):
            return None

    def _extract_transaction_methods(self, transaction_profile: Dict) -> List[str]:
        """Extract unique transaction methods"""
        methods = set()
        transactions = transaction_profile.get('all_transactions', [])

        for transaction in transactions:
            method = transaction.get('PAYMENT_METHOD')
            if method:
                methods.add(method)

        return list(methods)

    def _assess_risk_level(self, credit_profile: Dict) -> str:
        """Assess risk level based on credit score"""
        latest_score = self._extract_latest_credit_score(credit_profile)

        if latest_score is None:
            return "unknown"
        elif latest_score >= 750:
            return "low"
        elif latest_score >= 650:
            return "medium"
        else:
            return "high"

    def _determine_account_status(self) -> str:
        """Determine account status based on available data"""
        # Since we have comprehensive data, assume active status
        return "active"

    def get_ground_truth(self) -> Dict[str, Any]:
        """Get the extracted ground truth data"""
        return self.ground_truth.copy()

    def get_customer_context(self) -> Dict[str, Any]:
        """Get customer context for test case generation"""
        return {
            "customer_email": self.ground_truth.get("customer_email"),
            "customer_name": self.ground_truth.get("customer_name"),
            "client_id": self.ground_truth.get("client_id"),
            "entity_id": self.ground_truth.get("entity_id"),
        }

    def save_ground_truth(self, output_file: str = None) -> str:
        """Save ground truth to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tests / agenta / ground_truth_{timestamp}.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        output_data = {
            "metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "source_file": self.master_data_file,
                "total_fields": len(self.ground_truth)
            },
            "ground_truth": self.ground_truth,
            "customer_context": self.get_customer_context()
        }

        with open(output_file, 'w', encoding='utf - 8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Ground truth saved to: {output_file}")
        return output_file

    def print_summary(self):
        """Print a summary of extracted ground truth"""
        print("\n📊 GROUND TRUTH EXTRACTION SUMMARY")
        print("=" * 50)

        print(f"📁 Source File: {self.master_data_file}")
        print(f"📊 Total Fields: {len(self.ground_truth)}")

        print("\n👤 CUSTOMER IDENTITY:")
        print(f"  Email: {self.ground_truth.get('customer_email')}")
        print(f"  Name: {self.ground_truth.get('customer_name')}")
        print(f"  Client ID: {self.ground_truth.get('client_id')}")

        print("\n💳 CREDIT ANALYSIS:")
        print(f"  Total Reports: {self.ground_truth.get('total_credit_reports')}")
        print(f"  Latest Score: {self.ground_truth.get('latest_credit_score')}")
        print(f"  Score Range: {self.ground_truth.get('credit_score_range')}")
        print(f"  Risk Level: {self.ground_truth.get('risk_level')}")

        print("\n💰 TRANSACTION ANALYSIS:")
        print(f"  Total Transactions: {self.ground_truth.get('total_transactions')}")
        total_amount = self.ground_truth.get('total_transaction_amount', 0)
        avg_amount = self.ground_truth.get('average_transaction_amount', 0)
        print(f"  Total Amount: ${total_amount:.2f}" if total_amount else "  Total Amount: N / A")
        print(f"  Average Amount: ${avg_amount:.2f}" if avg_amount else "  Average Amount: N / A")

        print("\n📞 CONTACT & SUPPORT:")
        print(f"  Has Phone Data: {self.ground_truth.get('has_phone_data')}")
        print(f"  Contact Records: {self.ground_truth.get('contact_records_count')}")
        print(f"  Has Ticket Data: {self.ground_truth.get('has_ticket_data')}")

        print("\n🎯 DATA AVAILABILITY:")
        print(f"  Customer Found: {self.ground_truth.get('customer_found')}")
        print(f"  Data Available: {self.ground_truth.get('data_available')}")
        print(f"  Completeness Score: {self.ground_truth.get('data_completeness')}")


def main():
    """Main execution for testing"""
    print("🚀 GROUND TRUTH EXTRACTOR")
    print("=" * 40)

    try:
        # Initialize extractor
        extractor = GroundTruthExtractor()

        # Print summary
        extractor.print_summary()

        # Save ground truth
        output_file = extractor.save_ground_truth()

        print("\n✅ Ground truth extraction complete!")
        print(f"📁 Output file: {output_file}")

        return output_file

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
