#!/usr/bin/env python3
# Mock core_app.py for testing

def some_function():
    pass

        # FIXED: Simplified system prompt that forces tool usage
        system_prompt = f"""You are a customer service assistant.
{comprehensive_fields_text}

# CRITICAL: YOU MUST USE TOOLS FOR ALL CUSTOMER QUERIES

For ANY customer query containing:
- Email addresses (user@domain.com)
- Customer IDs (numbers like 1881899)

YOU MUST IMMEDIATELY call the tilores_search tool FIRST.

Available tools:
1. tilores_search - Find customers by email, name, or ID.

MANDATORY: Call tools first, then provide real data."""

        # Rest of function
        return system_prompt
