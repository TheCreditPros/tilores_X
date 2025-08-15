# Architecture Documentation

## Purpose

This directory contains architectural documentation for the Tilores_X project. It serves as a central repository for design decisions, system architecture, component relationships, and technical specifications.

## Contents

The architecture documentation includes:

1. **System Overview**: High-level description of the Tilores_X system
2. **Component Architecture**: Detailed documentation of individual components
3. **Data Flow Diagrams**: Visual representations of data flow through the system
4. **API Specifications**: Detailed API documentation
5. **Integration Points**: Documentation of integration with external systems
6. **Security Architecture**: Security considerations and implementations
7. **Performance Considerations**: Performance optimizations and considerations

## Organization

Architecture documentation is organized as follows:

- **README.md**: This overview document
- **system-overview.md**: High-level system architecture
- **components/**: Directory containing component-specific documentation
- **diagrams/**: Directory containing architectural diagrams
- **api/**: Directory containing API specifications
- **integrations/**: Directory containing integration documentation
- **security/**: Directory containing security architecture documentation
- **performance/**: Directory containing performance considerations

## Audience

This documentation is intended for:

- Developers working on the Tilores_X project
- System architects designing integrations
- Technical leads evaluating the system
- Operations teams deploying and maintaining the system

## Maintenance

Architecture documentation should be:

- Updated whenever significant architectural changes are made
- Reviewed quarterly for accuracy and completeness
- Version-controlled alongside code changes
- Referenced in relevant decision documents

## Current Architecture

Tilores_X follows a streamlined architecture with 8 core files:

### Core Application Files

1. **`core_app.py`** - Core application logic implementing the Tilores API functionality
   - Contains main business logic for customer data retrieval
   - Integrates with Tilores API endpoints
   - Handles data processing and transformation

2. **`main_enhanced.py`** - Enhanced main application entry point
   - FastAPI application setup and configuration
   - LangServe integration for `/chat/invoke` endpoint
   - Route definitions and middleware configuration

3. **`redis_cache.py`** - Redis caching implementation for performance optimization
   - Caches frequent API responses
   - Reduces latency for repeated queries
   - Configurable TTL and cache strategies

### Configuration Files

4. **`.env.template`** - Environment variable template for configuration
   - API keys and secrets configuration
   - Database connection strings
   - Feature flags and runtime settings

5. **`requirements.txt`** - Project dependencies
   - Python package specifications
   - Version pinning for stability
   - Development and production dependencies

6. **`.gitignore`** - Git ignore configuration
   - Excludes sensitive files and build artifacts
   - Python-specific ignore patterns

### Documentation & Testing

7. **`README.md`** - Project documentation (see [main README](../README.md) for user guide)
   - Quick start guide and usage examples
   - API endpoint documentation
   - Integration instructions

8. **`test_setup.py`** - Test configuration and setup
   - Test environment configuration
   - Test data fixtures and utilities
   - Validation and testing procedures

### Supported Models & Providers

| Provider | Models | Status | Use Case |
|----------|--------|--------|----------|
| OpenAI | gpt-4o-mini, gpt-3.5-turbo | ✅ Working | General purpose, fast responses |
| Groq | llama-3.3-70b-versatile, deepseek-r1-distill-llama-70b | ✅ Working | High performance, cost-effective |
| Anthropic | claude-3-haiku, claude-3-sonnet | ✅ Working | Advanced reasoning, complex queries |
| Google | gemini-pro, gemini-flash | ✅ Working | Multimodal capabilities |

### System Design Principles

The system is designed for:

- **Railway Deployment**: Optimized for cloud deployment with minimal configuration
- **AnythingLLM Integration**: Native compatibility with `/chat/invoke` endpoint
- **Simplified Maintenance**: Reduced complexity for easier updates and debugging
- **Optimal Performance**: Minimal overhead with strategic caching

### API Examples & Usage

#### Health Check
```bash
curl https://tilores-unified-api-production.up.railway.app/health
```

#### Customer Search via AnythingLLM
Natural language queries supported:
- "Find customer with client ID 1648647"
- "Get credit report for Dawn Bruton"
- "What is customer 1881899's email address?"

#### Direct API Integration
```bash
curl -X POST https://tilores-unified-api-production.up.railway.app/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "input": "Find customer with client ID 1648647",
      "model": "gpt-4o-mini"
    }
  }'
```

### Development & Operations

#### Testing Procedures
```bash
# Simple test suite
python test_simplified_runner.py

# Pre-commit validation
./scripts/test/pre_commit_validation.sh
```

#### Deployment Process
```bash
# Validate and deploy
./deploy-simple.sh
```

#### Environment Configuration
1. Copy `.env.template` to `.env.local`
2. Configure API keys for:
   - Tilores API access
   - LLM provider credentials (OpenAI, Groq, Anthropic, Google)
   - LangSmith tracing (optional)
   - Redis cache connection
3. Set environment-specific variables

## Future Documentation

As the project evolves, additional architecture documentation will be added to this directory, including:

- Detailed component specifications
- Sequence diagrams for key operations
- Deployment architecture
- Scaling considerations
- Disaster recovery planning

## Template

When adding new architecture documentation, use the following template:

```markdown
# [Component/Feature] Architecture

## Overview

Brief description of the component or feature and its role in the system.

## Design Goals

- Goal 1
- Goal 2
- Goal 3

## Implementation Details

Detailed description of the implementation, including:

- Key classes/functions
- Algorithms
- Data structures
- External dependencies

## Interfaces

Description of interfaces exposed by this component:

- Public methods/functions
- API endpoints
- Events/callbacks

## Dependencies

- Internal dependencies
- External dependencies
- Configuration requirements

## Performance Considerations

- Expected performance characteristics
- Optimization strategies
- Potential bottlenecks

## Security Considerations

- Security measures implemented
- Potential vulnerabilities
- Mitigation strategies

## Future Enhancements

- Planned improvements
- Potential extensions
- Technical debt to address
