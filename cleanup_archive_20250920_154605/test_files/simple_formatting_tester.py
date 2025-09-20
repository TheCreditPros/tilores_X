#!/usr/bin/env python3
"""
Simple formatting tester using requests to test API responses
and manual browser verification instructions
"""

import requests
import json
import time
from pathlib import Path

class FormattingTester:
    def __init__(self):
        self.api_base = "http://localhost:8080"
        self.openwebui_url = "http://localhost:3000"
        self.test_results = []

    def test_api_response(self, test_name: str, query: str, expected_elements: list):
        """Test API response formatting"""
        print(f"\n🧪 Testing API: {test_name}")
        print(f"   Query: {query}")

        try:
            # Make API request
            response = requests.post(
                f"{self.api_base}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query}],
                    "stream": False
                },
                timeout=30
            )

            if response.status_code != 200:
                print(f"   ❌ API Error: {response.status_code}")
                return {"test_name": test_name, "error": f"API Error: {response.status_code}"}

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Analyze formatting
            formatting_results = self.analyze_formatting(content, expected_elements)

            # Store results
            result = {
                "test_name": test_name,
                "query": query,
                "response": content,
                "formatting_results": formatting_results,
                "response_length": len(content),
                "timestamp": time.time()
            }

            self.test_results.append(result)

            # Print analysis
            print(f"   Response length: {len(content)} chars")
            for element, details in formatting_results.items():
                status = "✅" if details["found"] else "❌"
                print(f"   {status} {element}: {details['count']} found")

            # Print sample of response
            print(f"   Sample: {content[:200]}...")

            return result

        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            return {"test_name": test_name, "error": str(e)}

    def analyze_formatting(self, content: str, expected_elements: list):
        """Analyze formatting elements in response"""
        results = {}

        for element in expected_elements:
            if element == "bold_headers":
                # Count **Header:** patterns
                import re
                bold_headers = re.findall(r'\*\*([^*]+):\*\*', content)
                results[element] = {
                    "found": len(bold_headers) > 0,
                    "count": len(bold_headers),
                    "examples": bold_headers[:3]
                }

            elif element == "bullet_points":
                # Count bullet points
                bullet_count = content.count("- ") + content.count("• ")
                results[element] = {
                    "found": bullet_count > 3,
                    "count": bullet_count,
                    "examples": []
                }

            elif element == "line_breaks":
                # Count newlines
                newline_count = content.count("\n")
                results[element] = {
                    "found": newline_count > 10,
                    "count": newline_count,
                    "examples": []
                }

            elif element == "sections":
                # Check for common sections
                sections = []
                section_keywords = ["Credit Scores", "Account Overview", "Payment History", "Key Insights"]
                for keyword in section_keywords:
                    if keyword in content:
                        sections.append(keyword)

                results[element] = {
                    "found": len(sections) >= 2,
                    "count": len(sections),
                    "examples": sections
                }

        return results

    def generate_browser_test_instructions(self):
        """Generate instructions for manual browser testing"""
        print("\n🌐 BROWSER TEST INSTRUCTIONS")
        print("=" * 50)
        print(f"1. Open browser to: {self.openwebui_url}")
        print("2. Configure API connection:")
        print("   - Settings > Connections")
        print("   - API Base URL: http://host.docker.internal:8080/v1")
        print("   - API Key: test-key")
        print("3. Test these queries and check formatting:")

        test_queries = [
            "who is e.j.price1986@gmail.com",
            "what is their experian credit score",
            "/client my email is e.j.price1986@gmail.com, how is my credit",
            "/cs what is the status of e.j.price1986@gmail.com"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"   {i}. {query}")

        print("\n📊 LOOK FOR:")
        print("   ✅ Bold headers (**Credit Scores:**)")
        print("   ✅ Bullet points with spacing")
        print("   ✅ Line breaks between sections")
        print("   ✅ Clean visual separation")
        print("   ✅ No cramped text")

        print(f"\n📸 Take screenshots and compare with API responses")

    def run_comprehensive_test(self):
        """Run comprehensive formatting tests"""
        print("🚀 COMPREHENSIVE FORMATTING TEST")
        print("=" * 50)

        # Test cases
        test_cases = [
            {
                "name": "Basic Customer Query",
                "query": "who is e.j.price1986@gmail.com",
                "expected": ["bold_headers", "bullet_points", "line_breaks", "sections"]
            },
            {
                "name": "Credit Score Query",
                "query": "what is their experian credit score",
                "expected": ["bold_headers", "bullet_points", "line_breaks", "sections"]
            },
            {
                "name": "Client Agent Query",
                "query": "/client my email is e.j.price1986@gmail.com, how is my credit",
                "expected": ["bold_headers", "bullet_points", "line_breaks", "sections"]
            },
            {
                "name": "CS Agent Query",
                "query": "/cs what is the status of e.j.price1986@gmail.com",
                "expected": ["bold_headers", "bullet_points", "line_breaks"]
            }
        ]

        # Test API responses
        for test_case in test_cases:
            self.test_api_response(
                test_case["name"],
                test_case["query"],
                test_case["expected"]
            )

        # Generate report
        self.generate_report()

        # Generate browser test instructions
        self.generate_browser_test_instructions()

    def generate_report(self):
        """Generate test report"""
        print("\n📊 API FORMATTING TEST REPORT")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = 0

        for result in self.test_results:
            if "error" not in result:
                formatting_results = result["formatting_results"]
                passed_elements = sum(1 for v in formatting_results.values() if v["found"])
                total_elements = len(formatting_results)

                if passed_elements == total_elements:
                    passed_tests += 1

                print(f"\n🧪 {result['test_name']}")
                print(f"   Success: {passed_elements}/{total_elements} elements")

                for element, details in formatting_results.items():
                    status = "✅" if details["found"] else "❌"
                    print(f"     {status} {element}: {details['count']} found")
                    if details["examples"]:
                        print(f"       Examples: {details['examples']}")
            else:
                print(f"\n❌ {result['test_name']}: {result['error']}")

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 API RESULTS:")
        print(f"   Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")

        # Save results
        with open("api_formatting_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        print(f"   Detailed results: api_formatting_results.json")

        return success_rate

if __name__ == "__main__":
    tester = FormattingTester()
    tester.run_comprehensive_test()
