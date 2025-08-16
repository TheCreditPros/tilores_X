#!/usr/bin/env python3
"""
Real customer test data gathered from Tilores
Generated automatically - do not edit manually
"""

REAL_TEST_CUSTOMERS = [
    {
        "email": "blessedwina@aol.com",
        "raw_response": "I encountered an error: langchain_core.language_models.chat_models.BaseChatModel.generate_prompt() got multiple values for keyword argument 'callbacks'. Please try again.",
        "status": "success",
        "name": "Unknown Customer",
        "has_credit_report": false
    },
    {
        "email": "lelisguardado@sbcglobal.net",
        "raw_response": "I encountered an error: langchain_core.language_models.chat_models.BaseChatModel.generate_prompt() got multiple values for keyword argument 'callbacks'. Please try again.",
        "status": "success",
        "name": "Unknown Customer",
        "has_credit_report": false
    },
    {
        "email": "migdaliareyes53@gmail.com",
        "raw_response": "I encountered an error: langchain_core.language_models.chat_models.BaseChatModel.generate_prompt() got multiple values for keyword argument 'callbacks'. Please try again.",
        "status": "success",
        "name": "Unknown Customer",
        "has_credit_report": false
    }
]

def get_real_customers():
    """Get the real customer test data"""
    return REAL_TEST_CUSTOMERS
