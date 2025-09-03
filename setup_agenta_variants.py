#!/usr / bin / env python3
"""
Setup Agenta.ai Prompt Variants

Creates prompt variants in Agenta.ai UI using our template prompts.
"""

import json
import os
from typing import Dict, List

class AgentaVariantSetup:
    def __init__(self):
        """Initialize variant setup"""
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.app_slug = "tilores - x"

        print("🎯 Agenta.ai Variant Setup Guide")
        print("=" * 50)

    def load_template_prompts(self) -> Dict:
        """Load template prompts"""
        try:
            with open("agenta_template_prompts.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ agenta_template_prompts.json not found")
            return {}

    def generate_variant_configs(self) -> List[Dict]:
        """Generate variant configurations for Agenta.ai UI"""
        template_prompts = self.load_template_prompts()

        if not template_prompts:
            return []

        variants = []

        for prompt_id, config in template_prompts.items():
            variant = {
                "name": config.get("name", prompt_id),
                "description": config.get("description", ""),
                "parameters": {
                    "system_prompt": config.get("system_prompt", ""),
                    "temperature": config.get("temperature", 0.7),
                    "max_tokens": config.get("max_tokens", 1500),
                    "model": "gpt - 4o - mini"
                },
                "use_case": config.get("use_case", ""),
                "variant_slug": config.get("variant_slug", prompt_id),
                "created_at": config.get("created_at", "2025 - 01 - 27T10:00:00Z")
            }
            variants.append(variant)

        return variants

    def create_setup_instructions(self) -> str:
        """Create step - by - step setup instructions"""
        variants = self.generate_variant_configs()

        instructions = """
# 🚀 Agenta.ai UI Configuration Guide

## Step 1: Access Your Agenta.ai Dashboard
1. Go to https://cloud.agenta.ai
2. Log in with your account
3. Navigate to your 'tilores - x' application

## Step 2: Configure Webhooks
In Settings > Webhooks, add these URLs:

```
Evaluation Complete: https://tilores - x.up.railway.app / webhooks / evaluation - complete
Deployment Status: https://tilores - x.up.railway.app / webhooks / deployment - status
Performance Alert: https://tilores - x.up.railway.app / webhooks / performance - alert
```

## Step 3: Create Prompt Variants
Create these 6 variants in the Playground:

"""

        for i, variant in enumerate(variants, 1):
            instructions += """
### Variant {i}: {variant['name']}
- **Name**: `{variant['name']}`
- **Description**: {variant['description']}
- **Model**: {variant['parameters']['model']}
- **Temperature**: {variant['parameters']['temperature']}
- **Max Tokens**: {variant['parameters']['max_tokens']}
- **System Prompt**:
```
{variant['parameters']['system_prompt'][:200]}...
```
- **Use Case**: {variant['use_case']}

"""

        instructions += """
## Step 4: Run Test Evaluations
1. Go to Evaluations section
2. Select a test set (you have 6 available)
3. Choose variants to test
4. Run evaluation
5. Review results and webhook notifications

## Step 5: Set Up A / B Testing
1. Go to Experiments section
2. Create new experiment
3. Select variants to compare
4. Set traffic split (e.g., 50 / 50)
5. Define success metrics
6. Launch experiment

## Step 6: Monitor Performance
1. Check webhook logs in your production API
2. Monitor response times and token usage
3. Set up alerts for performance thresholds
4. Review evaluation results regularly

## 🎯 Success Criteria
- [ ] All 6 variants created
- [ ] Webhooks configured and tested
- [ ] At least one evaluation completed
- [ ] A / B test experiment running
- [ ] Performance monitoring active

"""

        return instructions

    def save_variant_details(self):
        """Save detailed variant configurations"""
        variants = self.generate_variant_configs()

        # Save full variant configs
        with open("agenta_variant_configs.json", "w") as f:
            json.dump(variants, f, indent=2)

        print(f"✅ Saved {len(variants)} variant configurations to agenta_variant_configs.json")

        # Save setup instructions
        instructions = self.create_setup_instructions()
        with open("AGENTA_UI_SETUP_GUIDE.md", "w") as f:
            f.write(instructions)

        print("✅ Saved setup guide to AGENTA_UI_SETUP_GUIDE.md")

        return variants

    def display_quick_setup(self):
        """Display quick setup summary"""
        variants = self.generate_variant_configs()

        print("\n🎯 QUICK SETUP SUMMARY")
        print("=" * 30)
        print(f"📊 Variants to Create: {len(variants)}")
        print("🔗 Webhooks to Configure: 3")
        print("🧪 Test Sets Available: 6")
        print("📋 Total Test Cases: 25")

        print("\n📝 VARIANT OVERVIEW:")
        for i, variant in enumerate(variants, 1):
            name = variant['name']
            temp = variant['parameters']['temperature']
            tokens = variant['parameters']['max_tokens']
            print(f"  {i}. {name} (temp: {temp}, tokens: {tokens})")

        print("\n🔗 WEBHOOK URLS:")
        webhooks = [
            "evaluation - complete",
            "deployment - status",
            "performance - alert"
        ]

        for webhook in webhooks:
            print(f"  • https://tilores - x.up.railway.app / webhooks/{webhook}")

        print("\n🚀 NEXT ACTION:")
        print("  1. Open https://cloud.agenta.ai")
        print("  2. Go to your 'tilores - x' app")
        print("  3. Follow the setup guide in AGENTA_UI_SETUP_GUIDE.md")

def main():
    """Main function"""
    setup = AgentaVariantSetup()

    # Save detailed configurations
    variants = setup.save_variant_details()

    # Display quick setup
    setup.display_quick_setup()

    return len(variants) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
