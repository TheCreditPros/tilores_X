#!/usr/bin/env python3
"""
Playwright automation for testing OpenWebUI formatting locally
Automates browser interactions to test different prompt structures
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright
from pathlib import Path

class OpenWebUITester:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_url = "http://host.docker.internal:8080/v1"
        self.test_results = []

    async def setup_browser(self):
        """Initialize browser and page"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)  # Set to True for headless
        self.page = await self.browser.new_page()

        # Set viewport for consistent screenshots
        await self.page.set_viewport_size({"width": 1200, "height": 800})

    async def setup_openwebui(self):
        """Setup OpenWebUI with our API connection"""
        print("🔧 Setting up OpenWebUI...")

        # Navigate to OpenWebUI
        await self.page.goto(self.base_url)
        await self.page.wait_for_load_state('networkidle')

        # Check if we need to create account or if already logged in
        try:
            # Look for sign up form
            await self.page.wait_for_selector('input[type="email"]', timeout=3000)
            print("   Creating admin account...")

            # Fill signup form
            await self.page.fill('input[type="email"]', 'admin@test.com')
            await self.page.fill('input[type="password"]', 'password123')
            await self.page.fill('input[placeholder*="Name"]', 'Admin User')

            # Submit form
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state('networkidle')

        except:
            print("   Already logged in or different UI")

        # Configure API connection
        await self.configure_api_connection()

    async def configure_api_connection(self):
        """Configure OpenWebUI to use our local API"""
        print("   Configuring API connection...")

        try:
            # Try to find settings/admin panel
            # Look for settings icon or menu
            settings_selectors = [
                '[data-testid="settings"]',
                'button[aria-label*="Settings"]',
                'a[href*="settings"]',
                '.settings',
                '[title*="Settings"]'
            ]

            for selector in settings_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    break
                except:
                    continue

            # Look for connections or API settings
            connection_selectors = [
                'text="Connections"',
                'text="API"',
                'text="Models"',
                '[href*="connections"]',
                '[href*="models"]'
            ]

            for selector in connection_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    break
                except:
                    continue

            # Add API configuration
            await self.page.fill('input[placeholder*="API"]', self.api_url)
            await self.page.fill('input[placeholder*="key"]', 'test-key')

            # Save configuration
            save_selectors = ['button:has-text("Save")', 'button:has-text("Add")', 'button[type="submit"]']
            for selector in save_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    break
                except:
                    continue

        except Exception as e:
            print(f"   API configuration may need manual setup: {e}")

    async def test_formatting_iteration(self, test_name: str, query: str, expected_elements: list):
        """Test a specific query and check for formatting elements"""
        print(f"\n🧪 Testing: {test_name}")

        try:
            # Navigate to chat interface
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')

            # Find chat input
            chat_selectors = [
                'textarea[placeholder*="message"]',
                'input[placeholder*="message"]',
                'textarea',
                '.chat-input textarea',
                '[data-testid="chat-input"]'
            ]

            chat_input = None
            for selector in chat_selectors:
                try:
                    chat_input = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if not chat_input:
                raise Exception("Could not find chat input")

            # Send query
            await chat_input.fill(query)
            await self.page.keyboard.press('Enter')

            # Wait for response
            await self.page.wait_for_timeout(5000)  # Wait for API response

            # Wait for response to appear
            response_selectors = [
                '.message:last-child',
                '.chat-message:last-child',
                '[data-testid="message"]:last-child',
                '.response:last-child'
            ]

            response_element = None
            for selector in response_selectors:
                try:
                    response_element = await self.page.wait_for_selector(selector, timeout=10000)
                    break
                except:
                    continue

            if not response_element:
                raise Exception("Could not find response element")

            # Get response text and HTML
            response_text = await response_element.inner_text()
            response_html = await response_element.inner_html()

            # Check for expected formatting elements
            formatting_results = {}
            for element in expected_elements:
                if element == "bold_headers":
                    # Check for bold text in HTML
                    formatting_results[element] = "<strong>" in response_html or "**" in response_text
                elif element == "bullet_points":
                    # Check for bullet points
                    formatting_results[element] = ("•" in response_text or
                                                 "<li>" in response_html or
                                                 response_text.count("- ") > 2)
                elif element == "line_breaks":
                    # Check for proper line spacing
                    formatting_results[element] = response_text.count("\n") > 5
                elif element == "sections":
                    # Check for section separation
                    formatting_results[element] = ("Credit Scores" in response_text and
                                                 "Account Overview" in response_text)

            # Take screenshot
            screenshot_path = f"screenshots/{test_name.replace(' ', '_')}.png"
            Path("screenshots").mkdir(exist_ok=True)
            await self.page.screenshot(path=screenshot_path)

            # Store results
            result = {
                "test_name": test_name,
                "query": query,
                "response_text": response_text[:500] + "..." if len(response_text) > 500 else response_text,
                "response_html": response_html[:500] + "..." if len(response_html) > 500 else response_html,
                "formatting_results": formatting_results,
                "screenshot": screenshot_path,
                "timestamp": time.time()
            }

            self.test_results.append(result)

            # Print results
            print(f"   Response length: {len(response_text)} chars")
            for element, found in formatting_results.items():
                status = "✅" if found else "❌"
                print(f"   {status} {element}: {found}")

            return result

        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            return {"test_name": test_name, "error": str(e)}

    async def run_formatting_tests(self):
        """Run comprehensive formatting tests"""
        print("🚀 STARTING OPENWEBUI FORMATTING TESTS")
        print("=" * 50)

        await self.setup_browser()
        await self.setup_openwebui()

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

        # Run tests
        for test_case in test_cases:
            await self.test_formatting_iteration(
                test_case["name"],
                test_case["query"],
                test_case["expected"]
            )

            # Wait between tests
            await self.page.wait_for_timeout(2000)

        # Generate report
        await self.generate_report()

        await self.browser.close()
        await self.playwright.stop()

    async def generate_report(self):
        """Generate test report"""
        print("\n📊 FORMATTING TEST REPORT")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = 0

        for result in self.test_results:
            if "error" not in result:
                formatting_results = result["formatting_results"]
                passed_elements = sum(1 for v in formatting_results.values() if v)
                total_elements = len(formatting_results)

                if passed_elements == total_elements:
                    passed_tests += 1

                print(f"\n🧪 {result['test_name']}")
                print(f"   Query: {result['query']}")
                print(f"   Formatting: {passed_elements}/{total_elements} elements")

                for element, found in formatting_results.items():
                    status = "✅" if found else "❌"
                    print(f"     {status} {element}")

                print(f"   Screenshot: {result['screenshot']}")
            else:
                print(f"\n❌ {result['test_name']}: {result['error']}")

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")

        # Save detailed results
        with open("formatting_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        print(f"   Detailed results: formatting_test_results.json")

        return success_rate

async def main():
    """Main test runner"""
    tester = OpenWebUITester()
    await tester.run_formatting_tests()

if __name__ == "__main__":
    asyncio.run(main())
