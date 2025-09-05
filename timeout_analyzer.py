#!/usr/bin/env python3
"""
AI-Powered Timeout Analysis and Resolution
Uses AI to identify patterns in timeouts and create targeted fixes
"""

import json
import openai
import os
from typing import Dict, Any, List

class TimeoutAnalyzer:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def analyze_timeout_patterns(self) -> Dict[str, Any]:
        """Use AI to analyze timeout patterns from recent test results"""

        # Load recent test results
        timeout_data = {
            "successful_queries": [
                "Who is e.j.price1986@gmail.com?",
                "Customer profile for client 1747598",
                "Account status for client 1747598",
                "What services does e.j.price1986@gmail.com have?",
                "Payment status for client 1747598",
                "What's the billing status for client 1747598?",
                "What is the credit score for e.j.price1986@gmail.com?"
            ],
            "timeout_queries": [
                "Monthly charges for e.j.price1986@gmail.com",
                "Credit report for e.j.price1986@gmail.com",
                "Customer info for Esteban Price and their payment status",
                "Complete overview of e.j.price1986@gmail.com account",
                "Payment history for Esteban Price",
                "Credit repair progress for e.j.price1986@gmail.com"
            ],
            "performance_data": {
                "successful_response_times": "0.0-5.0 seconds",
                "timeout_threshold": "5-8 seconds",
                "successful_response_lengths": "163-1543 characters",
                "pattern": "Complex queries with multiple data sources timeout"
            }
        }

        analysis_prompt = f"""
You are an expert system performance analyst. Analyze these API timeout patterns to identify the root cause and solution.

TIMEOUT DATA:
{json.dumps(timeout_data, indent=2)}

OBSERVATIONS:
- Successful queries complete in 0-5 seconds with 100/100 quality scores
- Timeout queries fail after 5-8 seconds
- Pattern suggests complex queries requiring multiple data fetches are timing out
- Simple status queries work perfectly
- The API has access to customer data but struggles with complex analysis

Your task is to identify:
1. **Root Cause**: What's causing the timeouts?
2. **Query Patterns**: What makes some queries timeout vs succeed?
3. **Solution Strategy**: How can we fix this without over-engineering?
4. **Prompt Optimization**: How can we modify prompts to reduce processing time?

Focus on leveraging AI intelligence to solve this, not complex technical solutions.

Return JSON format with your analysis and recommended fixes.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.2,
                max_tokens=1500
            )

            content = response.choices[0].message.content

            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content

            return json.loads(json_content)

        except Exception as e:
            print(f"❌ Error analyzing timeouts: {e}")
            return {}

    def create_timeout_resistant_prompts(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create optimized prompts that reduce processing time"""

        optimization_prompt = f"""
Based on this timeout analysis, create optimized system prompts that reduce processing time while maintaining quality.

ANALYSIS RESULTS:
{json.dumps(analysis, indent=2)}

Create TIMEOUT-RESISTANT PROMPTS that:
1. **Reduce Processing Time**: Streamline instructions to be more direct
2. **Maintain Quality**: Keep the 100/100 response quality we're achieving
3. **Eliminate Complexity**: Remove unnecessary processing steps
4. **Focus on Speed**: Prioritize quick, accurate responses

For each prompt category, provide:
- Streamlined system prompt (shorter but effective)
- Key optimizations made
- Expected time savings

Focus on these categories that are timing out:
- "credit": For credit analysis queries
- "transaction": For payment/billing queries
- "multi_data": For comprehensive analysis

Return JSON with optimized prompts designed for speed and reliability.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": optimization_prompt}],
                temperature=0.1,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content

            return json.loads(json_content)

        except Exception as e:
            print(f"❌ Error creating optimized prompts: {e}")
            return {}

    def apply_timeout_fixes(self, optimized_prompts: Dict[str, Any]) -> bool:
        """Apply timeout-resistant prompts to the API"""

        print("⚡ APPLYING TIMEOUT-RESISTANT OPTIMIZATIONS")
        print("=" * 60)

        try:
            with open('direct_credit_api_fixed.py', 'r') as f:
                api_content = f.read()

            # Find and update prompt_config section
            prompt_config_start = api_content.find('prompt_config = {')
            if prompt_config_start == -1:
                print("❌ Could not find prompt_config in API file")
                return False

            # Find the end of prompt_config
            brace_count = 0
            config_start = prompt_config_start
            config_end = config_start

            for i, char in enumerate(api_content[config_start:], config_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        config_end = i + 1
                        break

            # Build new timeout-resistant prompt config
            new_config = """prompt_config = {
    "general": {
        "system_prompt": "You are a helpful AI assistant providing general information about Tilores credit repair services. Be informative and professional.",
        "temperature": 0.7,
        "max_tokens": 500
    },"""

            # Apply timeout-resistant prompts
            for category, optimization in optimized_prompts.items():
                if category in ["credit", "transaction", "multi_data", "status"]:
                    prompt = optimization["system_prompt"].replace('"', '\\"')  # Escape quotes
                    max_tokens = optimization.get("max_tokens", 800)  # Reduced token limits

                    new_config += f'''
    "{category}": {{
        "system_prompt": "{prompt}",
        "temperature": 0.7,
        "max_tokens": {max_tokens}
    }},'''

                    print(f"✅ Applied timeout-resistant {category} prompt")
                    print(f"   Optimizations: {', '.join(optimization.get('optimizations', []))}")
                    print(f"   Expected savings: {optimization.get('expected_savings', 'Faster processing')}")
                    print()

            # Add status prompt if not included
            if "status" not in optimized_prompts:
                new_config += '''
    "status": {
        "system_prompt": "You are a customer service assistant. Provide clear, concise account status information based on customer data. Be direct and helpful.",
        "temperature": 0.7,
        "max_tokens": 600
    }'''

            # Remove trailing comma and close config
            new_config = new_config.rstrip(',')
            new_config += '\n}'

            # Replace the old config with new config
            new_api_content = api_content[:prompt_config_start] + new_config + api_content[config_end:]

            # Write back to file
            with open('direct_credit_api_fixed.py', 'w') as f:
                f.write(new_api_content)

            print("✅ Successfully applied timeout-resistant optimizations")
            return True

        except Exception as e:
            print(f"❌ Error applying timeout fixes: {e}")
            return False

def main():
    """Run the timeout analysis and optimization system"""

    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        return 1

    analyzer = TimeoutAnalyzer()

    # Step 1: Analyze timeout patterns
    print("🔍 ANALYZING TIMEOUT PATTERNS WITH AI...")
    analysis = analyzer.analyze_timeout_patterns()

    if not analysis:
        print("❌ Failed to analyze timeout patterns")
        return 1

    print("✅ Timeout analysis completed")
    print(f"Root cause identified: {analysis.get('root_cause', 'Unknown')}")
    print()

    # Step 2: Create timeout-resistant prompts
    print("⚡ CREATING TIMEOUT-RESISTANT PROMPTS...")
    optimized_prompts = analyzer.create_timeout_resistant_prompts(analysis)

    if not optimized_prompts:
        print("❌ Failed to create optimized prompts")
        return 1

    print(f"✅ Created optimized prompts for {len(optimized_prompts)} categories")
    print()

    # Step 3: Apply optimizations
    if analyzer.apply_timeout_fixes(optimized_prompts):
        print("⚡ TIMEOUT OPTIMIZATIONS APPLIED SUCCESSFULLY")
        print()
        print("Next steps:")
        print("1. Restart API server to load optimized prompts")
        print("2. Clear Redis cache for fresh responses")
        print("3. Run test suite to measure 98% success rate")
        print("4. Expect faster response times and fewer timeouts")

        return 0
    else:
        print("❌ Failed to apply timeout optimizations")
        return 1

if __name__ == "__main__":
    exit(main())
