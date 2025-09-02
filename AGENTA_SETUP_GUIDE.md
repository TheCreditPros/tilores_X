# Agenta.ai Integration Setup Guide

## Overview

This guide explains how to set up and use the Agenta.ai SDK integration for dynamic prompt management in the Tilores_X platform.

## Prerequisites

1. **Agenta.ai Account**: Sign up at [https://cloud.agenta.ai](https://cloud.agenta.ai)
2. **API Key**: Generate an API key from your Agenta.ai dashboard
3. **Python Environment**: Ensure you have Python 3.8+ installed

## Installation

The Agenta SDK will be automatically installed when you run the test script:

```bash
python test_agenta_integration.py
```

Or install manually:

```bash
pip install -U agenta
```

## Environment Configuration

Add these variables to your `.env` file:

```bash
# Agenta.ai Configuration
AGENTA_API_KEY=your_agenta_api_key_here
AGENTA_HOST=https://cloud.agenta.ai
AGENTA_APP_SLUG=tilores-x
```

## Features

### 1. Dynamic Prompt Management

The system automatically selects appropriate prompts based on query type:

- **Status Queries**: Concise account status responses
- **Credit Analysis**: Comprehensive credit report analysis
- **Transaction Analysis**: Payment and billing insights
- **Multi-Data Analysis**: Cross-data source intelligence

### 2. A/B Testing Support

Use the `prompt_id` and `prompt_version` parameters in API requests:

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    { "role": "user", "content": "Analyze credit for customer@example.com" }
  ],
  "prompt_id": "credit-analysis-v2",
  "prompt_version": "1.1"
}
```

### 3. Observability Integration

The system automatically logs:

- Query types and performance metrics
- Response times and success rates
- Prompt effectiveness data

## Query Type Detection

The system intelligently routes queries:

| Query Type  | Keywords                                   | Example                                            |
| ----------- | ------------------------------------------ | -------------------------------------------------- |
| Status      | "account status", "active", "canceled"     | "What is the account status for user@example.com?" |
| Credit      | "credit", "score", "bureau", "utilization" | "Analyze credit report for customer"               |
| Transaction | "payment", "billing", "transaction"        | "Show payment history"                             |
| Multi-Data  | "comprehensive", "complete", "overview"    | "Full customer analysis"                           |

## Testing

Run the comprehensive test suite:

```bash
python test_agenta_integration.py
```

This will:

1. Install the Agenta SDK
2. Test SDK import and initialization
3. Start the enhanced API server
4. Test status query functionality (previously failing)
5. Test Agenta.ai prompt integration
6. Provide detailed results

## API Endpoints

### Main Endpoint

- **URL**: `POST /v1/chat/completions`
- **Compatibility**: OpenAI-compatible
- **Enhanced Fields**:
  - `prompt_id`: Specific prompt variant to use
  - `prompt_version`: Version of the prompt

### Health Check

- **URL**: `GET /health`
- **Response**: Server status and timestamp

## Fallback Behavior

The system gracefully handles Agenta.ai unavailability:

1. **Primary**: Agenta.ai SDK for dynamic prompts
2. **Fallback**: Local JSON prompt store
3. **Ultimate Fallback**: Built-in default prompts

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure Agenta SDK is installed

   ```bash
   pip install -U agenta
   ```

2. **Authentication Error**: Check your API key

   ```bash
   echo $AGENTA_API_KEY
   ```

3. **Connection Error**: Verify network connectivity to Agenta.ai

### Debug Mode

Enable debug logging by checking server output for:

- `✅ Agenta SDK imported successfully`
- `✅ Agenta SDK initialized successfully`
- `📝 Using prompt: [variant] (source: agenta)`

## Benefits

1. **Dynamic Prompts**: Real-time prompt optimization
2. **A/B Testing**: Compare prompt performance
3. **Observability**: Track prompt effectiveness
4. **Fallback Safety**: Always functional, even offline
5. **Performance**: Cached responses for speed

## Next Steps

1. Set up your Agenta.ai account and API key
2. Run the test suite to verify functionality
3. Configure custom prompts in Agenta.ai dashboard
4. Monitor performance through Agenta.ai observability

For support, check the server logs or contact the development team.
