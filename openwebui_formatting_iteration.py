#!/usr/bin/env python3
"""
OpenWebUI Formatting Iteration System
Tests different formatting approaches and provides immediate feedback
"""

import requests
import json
import time
from pathlib import Path

class FormattingIterator:
    def __init__(self):
        self.api_base = "http://localhost:8080"
        self.test_query = "/client my email is e.j.price1986@gmail.com, how is my credit"
        self.iteration_count = 0
        self.results_history = []

    def test_current_formatting(self):
        """Test current formatting approach"""
        self.iteration_count += 1
        print(f"\n🔄 ITERATION #{self.iteration_count}")
        print("=" * 50)

        try:
            response = requests.post(
                f"{self.api_base}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": self.test_query}],
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Analyze formatting
                analysis = self.analyze_response(content)

                # Save iteration result
                result = {
                    "iteration": self.iteration_count,
                    "timestamp": time.time(),
                    "response": content,
                    "analysis": analysis
                }

                self.results_history.append(result)

                # Display results
                self.display_analysis(analysis, content)

                # Save for manual inspection
                filename = f"iteration_{self.iteration_count}_response.txt"
                with open(filename, "w") as f:
                    f.write(content)

                print(f"💾 Response saved to: {filename}")

                return analysis

            else:
                print(f"❌ API Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def analyze_response(self, content):
        """Analyze response formatting quality"""
        import re

        analysis = {
            "length": len(content),
            "line_breaks": content.count("\n"),
            "bold_headers": len(re.findall(r'\*\*([^*]+):\*\*', content)),
            "bullet_points": content.count("- "),
            "sections": len(re.findall(r'\*\*([^*]*(?:Credit|Account|Payment|Key|Next)[^*]*):\*\*', content)),
            "double_spaces": content.count("  \n"),
            "empty_lines": content.count("\n\n"),
            "formatting_score": 0
        }

        # Calculate formatting score (0-100)
        score = 0

        # Length check (good responses are substantial)
        if analysis["length"] > 1500:
            score += 20
        elif analysis["length"] > 800:
            score += 10

        # Bold headers (should have multiple sections)
        if analysis["bold_headers"] >= 4:
            score += 25
        elif analysis["bold_headers"] >= 2:
            score += 15

        # Bullet points (should have good separation)
        if analysis["bullet_points"] >= 20:
            score += 25
        elif analysis["bullet_points"] >= 10:
            score += 15

        # Line breaks (proper spacing)
        if analysis["line_breaks"] >= 50:
            score += 15
        elif analysis["line_breaks"] >= 30:
            score += 10

        # Sections (structured content)
        if analysis["sections"] >= 3:
            score += 15
        elif analysis["sections"] >= 2:
            score += 10

        analysis["formatting_score"] = score
        return analysis

    def display_analysis(self, analysis, content):
        """Display formatting analysis"""
        print(f"📊 FORMATTING ANALYSIS:")
        print(f"   Length: {analysis['length']} chars")
        print(f"   Line breaks: {analysis['line_breaks']}")
        print(f"   Bold headers: {analysis['bold_headers']}")
        print(f"   Bullet points: {analysis['bullet_points']}")
        print(f"   Sections: {analysis['sections']}")
        print(f"   Double spaces: {analysis['double_spaces']}")
        print(f"   Empty lines: {analysis['empty_lines']}")
        print(f"   📈 Formatting Score: {analysis['formatting_score']}/100")

        # Show sample
        print(f"\n📝 SAMPLE (first 300 chars):")
        print("-" * 40)
        print(content[:300] + "...")
        print("-" * 40)

        # Quality assessment
        if analysis['formatting_score'] >= 80:
            print("✅ EXCELLENT formatting quality!")
        elif analysis['formatting_score'] >= 60:
            print("⚠️ GOOD formatting, room for improvement")
        else:
            print("❌ POOR formatting, needs work")

    def suggest_improvements(self, analysis):
        """Suggest specific formatting improvements"""
        suggestions = []

        if analysis['bold_headers'] < 4:
            suggestions.append("Add more section headers (**Header:**)")

        if analysis['bullet_points'] < 15:
            suggestions.append("Increase bullet point separation")

        if analysis['double_spaces'] < 10:
            suggestions.append("Add more two-space line breaks (  \\n)")

        if analysis['empty_lines'] < 5:
            suggestions.append("Add more paragraph breaks (\\n\\n)")

        if analysis['sections'] < 3:
            suggestions.append("Create more distinct sections")

        return suggestions

    def generate_openwebui_test_instructions(self):
        """Generate step-by-step OpenWebUI testing instructions"""
        print(f"\n🌐 OPENWEBUI MANUAL TEST INSTRUCTIONS")
        print("=" * 50)
        print("1. Open browser: http://localhost:3000")
        print("2. If not configured, set up API connection:")
        print("   - Click Settings (gear icon)")
        print("   - Go to Connections")
        print("   - Add OpenAI API:")
        print("     • API Base URL: http://host.docker.internal:8080/v1")
        print("     • API Key: test-key")
        print("   - Save and verify models appear")
        print("3. Start new chat")
        print("4. Send test query:")
        print(f"   {self.test_query}")
        print("5. Compare OpenWebUI rendering with saved response")
        print("6. Check for:")
        print("   ✅ Bold headers render as bold text")
        print("   ✅ Bullet points have proper spacing")
        print("   ✅ Line breaks create visual separation")
        print("   ✅ No cramped or run-together text")
        print("   ✅ Clean section organization")

        if self.iteration_count > 0:
            latest = self.results_history[-1]
            print(f"\n📊 Expected Quality Metrics:")
            print(f"   - Response length: ~{latest['analysis']['length']} chars")
            print(f"   - Bold headers: {latest['analysis']['bold_headers']}")
            print(f"   - Bullet points: {latest['analysis']['bullet_points']}")
            print(f"   - Formatting score: {latest['analysis']['formatting_score']}/100")

    def run_iteration_cycle(self):
        """Run complete iteration cycle"""
        print("🚀 OPENWEBUI FORMATTING ITERATION SYSTEM")
        print("=" * 50)

        # Test current formatting
        analysis = self.test_current_formatting()

        if analysis:
            # Generate suggestions
            suggestions = self.suggest_improvements(analysis)

            if suggestions:
                print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")

            # Generate OpenWebUI test instructions
            self.generate_openwebui_test_instructions()

            # Save iteration history
            with open("formatting_iteration_history.json", "w") as f:
                json.dump(self.results_history, f, indent=2)

            print(f"\n💾 Iteration history saved to: formatting_iteration_history.json")

            return analysis['formatting_score']

        return 0

def main():
    """Main iteration runner"""
    iterator = FormattingIterator()
    score = iterator.run_iteration_cycle()

    print(f"\n🎯 NEXT STEPS:")
    if score >= 80:
        print("1. Test in OpenWebUI browser interface")
        print("2. Compare rendering with saved response")
        print("3. If rendering looks good, deploy to production")
        print("4. If rendering has issues, iterate on formatting approach")
    else:
        print("1. Improve formatting based on suggestions")
        print("2. Re-run this script to test improvements")
        print("3. Iterate until formatting score >= 80")
        print("4. Then test in OpenWebUI browser")

if __name__ == "__main__":
    main()
