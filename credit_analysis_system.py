"""
Advanced Credit Analysis System for Tilores Integration
Provides professional credit report generation and multi-bureau analysis
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp
from langchain.tools import tool


@dataclass
class CreditProfile:
    """Professional credit profile data structure."""

    client_id: str
    name: str
    credit_score: Optional[int] = None
    transunion_report: Optional[str] = None
    credit_utilization: Optional[float] = None
    payment_history: Optional[str] = None
    credit_age: Optional[str] = None
    recent_inquiries: Optional[int] = None
    derogatory_marks: Optional[int] = None
    credit_mix: Optional[str] = None
    recommendations: Optional[List[str]] = None


class AdvancedCreditAnalyzer:
    """Advanced credit analysis system with multi-bureau support."""

    def __init__(self):
        # Tilores API URLs - long URLs require noqa for line length
        self.api_url = (
            os.getenv("TILORES_API_URL") or "https://ly325mgfwk.execute-api.us-east-1.amazonaws.com"
        )  # noqa E501
        self.token_url = (
            os.getenv("TILORES_TOKEN_URL")
            or "https://saas-swidepnf-tilores.auth.us-east-1.amazoncognito.com/oauth2/token"
        )  # noqa E501
        self.client_id = os.getenv("TILORES_CLIENT_ID")
        self.client_secret = os.getenv("TILORES_CLIENT_SECRET")
        self.access_token = None

    async def get_access_token(self):
        """Get OAuth2 access token from Tilores."""
        if not all([self.token_url, self.client_id, self.client_secret]):
            raise Exception("Tilores credentials not configured")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.token_url,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},  # noqa E501
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                ) as response:
                    response.raise_for_status()
                    token_data = await response.json()
                    self.access_token = token_data.get("access_token")
                    return self.access_token
        except Exception as e:
            raise Exception(f"Failed to get Tilores token: {str(e)}")

    async def get_comprehensive_credit_data(self, client_identifier: str) -> Dict[str, Any]:  # noqa E501
        """Get comprehensive credit data from Tilores."""
        if not self.access_token:
            await self.get_access_token()

        # Enhanced GraphQL query for complete credit data access
        graphql_query = """
        query ComprehensiveCreditData($search_params: SearchInput!) {
          search(input: $search_params) {
            entities {
              id
              hits
              recordInsights {
                FIRST_NAME: valuesDistinct(field: "FIRST_NAME")
                LAST_NAME: valuesDistinct(field: "LAST_NAME")
                CLIENT_ID: valuesDistinct(field: "CLIENT_ID")
                EMAIL: valuesDistinct(field: "EMAIL")
                STARTING_CREDIT_SCORE: valuesDistinct(field: "STARTING_CREDIT_SCORE")  # noqa E501
                CURRENT_CREDIT_SCORE: valuesDistinct(field: "CURRENT_CREDIT_SCORE")  # noqa E501
                TRANSUNION_REPORT: valuesDistinct(field: "TRANSUNION_REPORT")
                EXPERIAN_REPORT: valuesDistinct(field: "EXPERIAN_REPORT")
                EQUIFAX_REPORT: valuesDistinct(field: "EQUIFAX_REPORT")
                CREDIT_UTILIZATION: valuesDistinct(field: "CREDIT_UTILIZATION")
                PAYMENT_HISTORY: valuesDistinct(field: "PAYMENT_HISTORY")
                CREDIT_AGE: valuesDistinct(field: "CREDIT_AGE")
                HARD_INQUIRIES: valuesDistinct(field: "HARD_INQUIRIES")
                DEROGATORY_MARKS: valuesDistinct(field: "DEROGATORY_MARKS")
                CREDIT_MIX: valuesDistinct(field: "CREDIT_MIX")
                DEBT_TO_INCOME: valuesDistinct(field: "DEBT_TO_INCOME")
                FICO_SCORE: valuesDistinct(field: "FICO_SCORE")
                VANTAGE_SCORE: valuesDistinct(field: "VANTAGE_SCORE")
              }
            }
          }
        }
        """

        # Determine search parameters
        search_params = {}
        if client_identifier.isdigit():
            search_params["CLIENT_ID"] = client_identifier
        elif "@" in client_identifier:
            search_params["EMAIL"] = client_identifier
        else:
            # Name search
            name_parts = client_identifier.split()
            if len(name_parts) >= 2:
                search_params["FIRST_NAME"] = name_parts[0]
                search_params["LAST_NAME"] = name_parts[1]
            else:
                search_params["FIRST_NAME"] = client_identifier

        payload = {"query": graphql_query, "variables": {"search_params": {"parameters": search_params}}}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"},
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            return {"error": f"Credit data retrieval failed: {str(e)}"}

    def analyze_credit_profile(self, credit_data: Dict[str, Any]) -> Optional[CreditProfile]:  # noqa E501
        """Analyze credit data and create professional credit profile."""
        search_data = credit_data.get("data", {}).get("search", {})
        entities = search_data.get("entities")
        if "error" in credit_data or not entities:
            return None

        entity = credit_data["data"]["search"]["entities"][0]
        insights = entity.get("recordInsights", {})

        # Extract core information
        first_name = insights.get("FIRST_NAME", ["Unknown"])[0]
        last_name = insights.get("LAST_NAME", ["Unknown"])[0]
        name = f"{first_name} {last_name}"
        client_id = insights.get("CLIENT_ID", ["Unknown"])[0]

        # Extract credit scores
        current_score = insights.get("CURRENT_CREDIT_SCORE", [None])[0]
        starting_score = insights.get("STARTING_CREDIT_SCORE", [None])[0]
        fico_score = insights.get("FICO_SCORE", [None])[0]

        # Use the most recent/relevant score
        credit_score = None
        if current_score and current_score != "N/A":
            credit_score = int(current_score) if str(current_score).isdigit() else None
        elif fico_score and fico_score != "N/A":
            credit_score = int(fico_score) if str(fico_score).isdigit() else None
        elif starting_score and starting_score != "N/A":
            credit_score = int(starting_score) if str(starting_score).isdigit() else None

        # Extract additional credit factors
        credit_util_raw = insights.get("CREDIT_UTILIZATION", [None])[0]
        credit_utilization = None
        if credit_util_raw and credit_util_raw != "N/A":
            try:
                util_str = str(credit_util_raw).replace("%", "")
                credit_utilization = float(util_str)
            except (ValueError, AttributeError):
                credit_utilization = None

        payment_history = insights.get("PAYMENT_HISTORY", ["Unknown"])[0]
        credit_age = insights.get("CREDIT_AGE", ["Unknown"])[0]
        hard_inquiries = insights.get("HARD_INQUIRIES", [0])[0]
        derogatory_marks = insights.get("DEROGATORY_MARKS", [0])[0]
        credit_mix = insights.get("CREDIT_MIX", ["Unknown"])[0]

        # Bureau reports
        transunion_report = insights.get("TRANSUNION_REPORT", ["N/A"])[0]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            credit_score, credit_utilization, payment_history, hard_inquiries, derogatory_marks
        )

        return CreditProfile(
            client_id=client_id,
            name=name,
            credit_score=credit_score,
            transunion_report=transunion_report,
            credit_utilization=credit_utilization,
            payment_history=payment_history,
            credit_age=credit_age,
            recent_inquiries=(int(hard_inquiries) if str(hard_inquiries).isdigit() else 0),
            derogatory_marks=(int(derogatory_marks) if str(derogatory_marks).isdigit() else 0),
            credit_mix=credit_mix,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        credit_score: Optional[int],
        credit_utilization: Optional[float],
        payment_history: str,
        hard_inquiries: int,
        derogatory_marks: int,
    ) -> List[str]:
        """Generate personalized credit improvement recommendations."""
        recommendations = []

        # Score-based recommendations
        if credit_score:
            if credit_score < 580:
                recommendations.append("🔴 CRITICAL: Focus on secured credit cards")  # noqa E501
                recommendations.append("💡 Consider credit counseling services")
            elif credit_score < 670:
                recommendations.append("🟡 FAIR: Reduce credit utilization below 30%")  # noqa E501
                recommendations.append("💡 Set up automatic payments")
            elif credit_score < 740:
                recommendations.append("🟢 GOOD: Optimize utilization <10%")
                recommendations.append("💡 Consider credit limit increases")
            else:
                recommendations.append("🌟 EXCELLENT: Maintain current habits")
                recommendations.append("💡 Consider premium credit products")

        # Utilization recommendations
        if credit_utilization:
            if credit_utilization > 30:
                recommendations.append(f"⚠️ High utilization at " f"{credit_utilization:.1f}% - pay down")
            elif credit_utilization > 10:
                recommendations.append(f"💡 Optimize utilization from " f"{credit_utilization:.1f}% to <10%")

        # Payment history recommendations
        if payment_history and "late" in payment_history.lower():
            recommendations.append("⏰ Set up automatic payments")

        # Inquiry recommendations
        if hard_inquiries > 3:
            recommendations.append("🔍 Limit new credit applications")

        # Derogatory marks recommendations
        if derogatory_marks > 0:
            recommendations.append("📋 Work on resolving derogatory marks")

        if not recommendations:
            recommendations.append("✅ Credit profile looks healthy")

        return recommendations

    def compare_credit_profiles(self, profiles: List[CreditProfile]) -> str:
        """Generate professional multi-client credit comparison."""
        if len(profiles) < 2:
            return "Need at least 2 credit profiles for comparison"

        comparison = ["=== MULTI-CLIENT CREDIT ANALYSIS ===\n"]

        # Overview table
        comparison.append("📊 CREDIT SCORE OVERVIEW:")
        for profile in profiles:
            score_status = "N/A"
            if profile.credit_score:
                if profile.credit_score >= 740:
                    score_status = f"🌟 {profile.credit_score} (EXCELLENT)"
                elif profile.credit_score >= 670:
                    score_status = f"🟢 {profile.credit_score} (GOOD)"
                elif profile.credit_score >= 580:
                    score_status = f"🟡 {profile.credit_score} (FAIR)"
                else:
                    score_status = f"🔴 {profile.credit_score} (POOR)"

            comparison.append(f"• {profile.name}: {score_status}")

        # Credit utilization comparison
        comparison.append("\n💳 CREDIT UTILIZATION:")
        for profile in profiles:
            if profile.credit_utilization is not None:
                if profile.credit_utilization <= 10:
                    utilization_status = "🟢 GOOD"
                elif profile.credit_utilization <= 30:
                    utilization_status = "🟡 HIGH"
                else:
                    utilization_status = "🔴 VERY HIGH"

                comparison.append(f"• {profile.name}: " f"{profile.credit_utilization:.1f}% " f"({utilization_status})")
            else:
                comparison.append(f"• {profile.name}: N/A")

        # Risk assessment
        comparison.append("\n⚠️ RISK ASSESSMENT:")
        for profile in profiles:
            risk_level = self._assess_risk_level(profile)
            comparison.append(f"• {profile.name}: {risk_level}")

        # Top recommendations for each client
        comparison.append("\n💡 TOP RECOMMENDATIONS:")
        for profile in profiles:
            if profile.recommendations:
                comparison.append(f"\n{profile.name}:")
                for rec in profile.recommendations[:3]:  # Top 3 only
                    comparison.append(f"  {rec}")

        return "\n".join(comparison)

    def _assess_risk_level(self, profile: CreditProfile) -> str:
        """Assess credit risk level for a profile."""
        if not profile.credit_score:
            return "🔍 INSUFFICIENT DATA"

        if profile.credit_score >= 740:
            return "🟢 LOW RISK"
        elif profile.credit_score >= 670:
            return "🟡 MODERATE RISK"
        elif profile.credit_score >= 580:
            return "🟠 HIGH RISK"
        else:
            return "🔴 VERY HIGH RISK"


# Global credit analyzer instance
credit_analyzer = AdvancedCreditAnalyzer()


@tool
async def get_customer_credit_report(client_identifier: str) -> str:
    """Get comprehensive credit report for a customer.

    Use this tool to access detailed credit information including:
    - Credit scores from multiple bureaus
    - Credit utilization analysis
    - Payment history assessment
    - Credit recommendations
    - Risk assessment
    """
    try:
        credit_data = await credit_analyzer.get_comprehensive_credit_data(client_identifier)

        if "error" in credit_data:
            return f"Error retrieving credit data: {credit_data['error']}"

        profile = credit_analyzer.analyze_credit_profile(credit_data)

        if not profile:
            return f"No credit data found for: {client_identifier}"

        # Format comprehensive credit report
        report = [f"=== CREDIT REPORT FOR {profile.name.upper()} ==="]
        report.append(f"Client ID: {profile.client_id}")
        report.append("")

        # Credit Score Section
        if profile.credit_score:
            if profile.credit_score >= 740:
                score_status = f"🌟 {profile.credit_score} (EXCELLENT)"
            elif profile.credit_score >= 670:
                score_status = f"🟢 {profile.credit_score} (GOOD)"
            elif profile.credit_score >= 580:
                score_status = f"🟡 {profile.credit_score} (FAIR)"
            else:
                score_status = f"🔴 {profile.credit_score} (POOR)"

            report.append(f"📊 CREDIT SCORE: {score_status}")
        else:
            report.append("📊 CREDIT SCORE: N/A")

        # Credit Metrics
        report.append("\n💳 CREDIT METRICS:")
        if profile.credit_utilization is not None:
            if profile.credit_utilization <= 10:
                utilization_status = "🟢"
            elif profile.credit_utilization <= 30:
                utilization_status = "🟡"
            else:
                utilization_status = "🔴"
            report.append(f"• Utilization: {profile.credit_utilization:.1f}% " f"{utilization_status}")
        else:
            report.append("• Utilization: N/A")

        if profile.payment_history != "Unknown":
            report.append(f"• Payment History: {profile.payment_history}")

        if profile.credit_age != "Unknown":
            report.append(f"• Credit Age: {profile.credit_age}")

        if profile.recent_inquiries is not None:
            if profile.recent_inquiries <= 2:
                inquiry_status = "🟢"
            elif profile.recent_inquiries <= 5:
                inquiry_status = "🟡"
            else:
                inquiry_status = "🔴"
            report.append(f"• Recent Inquiries: {profile.recent_inquiries} " f"{inquiry_status}")

        if profile.derogatory_marks is not None:
            derrog_status = "🟢" if profile.derogatory_marks == 0 else "🔴"
            report.append(f"• Derogatory Marks: {profile.derogatory_marks} " f"{derrog_status}")

        # Bureau Reports
        if profile.transunion_report and profile.transunion_report != "N/A":
            report.append("\n📋 BUREAU REPORTS:")
            report.append("• TransUnion: Available")

        # Risk Assessment
        risk_level = credit_analyzer._assess_risk_level(profile)
        report.append(f"\n⚠️ RISK ASSESSMENT: {risk_level}")

        # Recommendations
        if profile.recommendations:
            report.append("\n💡 RECOMMENDATIONS:")
            for rec in profile.recommendations:
                report.append(f"• {rec}")

        return "\n".join(report)

    except Exception as e:
        return f"Error generating credit report: {str(e)}"


@tool
async def compare_customer_credit_profiles(client_identifiers: str) -> str:
    """Compare credit profiles across multiple customers.

    Input: Comma-separated list of client identifiers
    Example: "1234567, 7654321" or "john@email.com, jane@email.com"

    Provides professional multi-client credit analysis and comparison.
    """
    try:
        # Parse client identifiers
        identifiers = [id.strip() for id in client_identifiers.split(",")]

        if len(identifiers) < 2:
            return "Need at least 2 client identifiers for comparison"

        # Get credit profiles for all clients
        profiles = []
        for identifier in identifiers:
            credit_data = await credit_analyzer.get_comprehensive_credit_data(identifier)

            if "error" not in credit_data:
                profile = credit_analyzer.analyze_credit_profile(credit_data)
                if profile:
                    profiles.append(profile)

        if len(profiles) < 2:
            return "Could not retrieve sufficient credit data for comparison"

        # Generate comparison report
        comparison_report = credit_analyzer.compare_credit_profiles(profiles)

        return comparison_report

    except Exception as e:
        return f"Error comparing credit profiles: {str(e)}"
