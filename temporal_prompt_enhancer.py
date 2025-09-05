#!/usr/bin/env python3
"""
Temporal Prompt Enhancement System
Specifically improves prompts for multi-turn conversations and temporal analysis
"""

import json
import openai
import os
from typing import Dict, Any

class TemporalPromptEnhancer:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def analyze_temporal_failures(self) -> Dict[str, Any]:
        """Analyze the specific failures in temporal conversations"""

        # Load the multi-threaded test results
        try:
            with open('multi_threaded_results_20250904_193753.json', 'r') as f:
                results = json.load(f)
        except FileNotFoundError:
            print("❌ Multi-threaded results file not found")
            return {}

        failure_patterns = {
            "context_maintenance": {
                "score": results["average_scores"]["context_maintenance"],
                "issues": [
                    "Context degrades across conversation turns",
                    "Assistant asks for information already provided",
                    "Fails to maintain customer identity across turns"
                ]
            },
            "temporal_analysis": {
                "score": results["average_scores"]["temporal_analysis"],
                "issues": [
                    "Cannot compare first vs latest data",
                    "Struggles with time-based analysis",
                    "Confusion with future enrollment dates",
                    "No historical data comparison capabilities"
                ]
            },
            "conversation_flow": {
                "score": results["average_scores"]["conversation_flow"],
                "issues": [
                    "Responses don't build on previous turns",
                    "Lacks continuity in multi-turn scenarios",
                    "Generic responses instead of contextual ones"
                ]
            }
        }

        return failure_patterns

    def generate_enhanced_prompts(self, failure_patterns: Dict[str, Any]) -> Dict[str, str]:
        """Generate enhanced prompts specifically for temporal and conversational scenarios"""

        enhancement_prompt = f"""
You are an expert AI prompt engineer specializing in conversational AI and temporal data analysis.

CURRENT MULTI-TURN CONVERSATION PERFORMANCE:
- Context Maintenance: {failure_patterns['context_maintenance']['score']:.1f}/100
- Temporal Analysis: {failure_patterns['temporal_analysis']['score']:.1f}/100
- Conversation Flow: {failure_patterns['conversation_flow']['score']:.1f}/100

SPECIFIC ISSUES TO ADDRESS:
{json.dumps(failure_patterns, indent=2)}

Create ENHANCED SYSTEM PROMPTS that specifically address these multi-turn conversation challenges:

1. **CONTEXT MAINTENANCE**: Prompts should instruct the AI to:
   - Remember customer details from previous turns
   - Reference earlier conversation context
   - Maintain customer identity throughout the conversation
   - Build upon previous responses rather than starting fresh

2. **TEMPORAL ANALYSIS**: Prompts should guide the AI to:
   - Handle requests for historical comparisons gracefully
   - Explain when temporal data isn't available
   - Provide meaningful analysis even with limited historical data
   - Address future date issues (enrollment dates in future)
   - Suggest alternative approaches when direct comparisons aren't possible

3. **CONVERSATION FLOW**: Prompts should ensure:
   - Each response builds on the previous conversation
   - Responses feel connected and contextual
   - Natural progression through multi-turn scenarios
   - Proactive suggestions when data limitations exist

Create enhanced prompts for these categories:
- "credit": For credit analysis with temporal awareness
- "transaction": For payment history with timeline analysis
- "multi_data": For comprehensive analysis across conversation turns
- "status": For account status with conversational context

Return JSON format with improved prompts that specifically address multi-turn conversations and temporal analysis limitations.

Example format:
{{
  "credit": {{
    "system_prompt": "You are a conversational credit analysis assistant with strong context awareness...",
    "key_improvements": ["Better context maintenance", "Temporal analysis guidance"],
    "expected_impact": "Should improve multi-turn credit conversations"
  }}
}}
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": enhancement_prompt}],
                temperature=0.2,
                max_tokens=2500
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
            print(f"❌ Error generating enhanced prompts: {e}")
            return {}

    def apply_temporal_enhancements(self, enhanced_prompts: Dict[str, Any]) -> bool:
        """Apply the temporally-enhanced prompts to the API"""

        print("🕒 APPLYING TEMPORAL PROMPT ENHANCEMENTS")
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

            # Build new temporally-enhanced prompt config
            new_config = """prompt_config = {
    "general": {
        "system_prompt": "You are a helpful AI assistant providing general information about Tilores credit repair services. Be informative and professional.",
        "temperature": 0.7,
        "max_tokens": 500
    },"""

            # Apply enhanced prompts
            for category, enhancement in enhanced_prompts.items():
                if category in ["credit", "transaction", "status", "multi_data"]:
                    prompt = enhancement["system_prompt"].replace('"', '\\"')  # Escape quotes
                    new_config += f'''
    "{category}": {{
        "system_prompt": "{prompt}",
        "temperature": 0.7,
        "max_tokens": {"1500" if category == "multi_data" else "1000"}
    }},'''

                    print(f"✅ Enhanced {category} prompt for temporal conversations")
                    print(f"   Key improvements: {', '.join(enhancement.get('key_improvements', []))}")
                    print(f"   Expected impact: {enhancement.get('expected_impact', 'Improved performance')}")
                    print()

            # Remove trailing comma and close config
            new_config = new_config.rstrip(',')
            new_config += '\n}'

            # Replace the old config with new config
            new_api_content = api_content[:prompt_config_start] + new_config + api_content[config_end:]

            # Write back to file
            with open('direct_credit_api_fixed.py', 'w') as f:
                f.write(new_api_content)

            print("✅ Successfully applied temporal prompt enhancements")
            return True

        except Exception as e:
            print(f"❌ Error applying enhancements: {e}")
            return False

def main():
    """Run the temporal prompt enhancement system"""

    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        return 1

    enhancer = TemporalPromptEnhancer()

    # Step 1: Analyze temporal conversation failures
    print("📊 ANALYZING TEMPORAL CONVERSATION FAILURES...")
    failure_patterns = enhancer.analyze_temporal_failures()

    if not failure_patterns:
        print("❌ Could not analyze failures")
        return 1

    print(f"Identified issues in {len(failure_patterns)} areas")
    print()

    # Step 2: Generate enhanced prompts
    print("🧠 GENERATING TEMPORAL-ENHANCED PROMPTS...")
    enhanced_prompts = enhancer.generate_enhanced_prompts(failure_patterns)

    if not enhanced_prompts:
        print("❌ Failed to generate enhanced prompts")
        return 1

    print(f"Generated enhanced prompts for {len(enhanced_prompts)} categories")
    print()

    # Step 3: Apply enhancements
    if enhancer.apply_temporal_enhancements(enhanced_prompts):
        print("🕒 TEMPORAL ENHANCEMENTS APPLIED SUCCESSFULLY")
        print()
        print("Next steps:")
        print("1. Restart the API server to load new prompts")
        print("2. Clear Redis cache to avoid cached responses")
        print("3. Re-run multi-threaded conversation tests")
        print("4. Expect improved context maintenance and temporal handling")

        return 0
    else:
        print("❌ Failed to apply temporal enhancements")
        return 1

if __name__ == "__main__":
    exit(main())
