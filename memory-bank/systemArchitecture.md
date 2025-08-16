# Tilores_X System Architecture

## Current Architecture (Phase VIII - Production Ready)

### Core Components

#### 1. **Core Engine** (`core_app.py`)
- **MultiProviderLLMEngine**: Central orchestrator for all LLM operations
- **QueryRouter**: Intelligent routing with context extraction
- **Field Discovery**: Dynamic Tilores schema introspection (310+ fields)
- **Provider Support**: OpenAI, Anthropic, Groq, Gemini, Mistral, OpenRouter
- **Caching**: Redis-backed with 24hr LLM responses, 1hr field cache
- **Tool Integration**: 4 Tilores tools with automatic binding

#### 2. **API Layer** (`main_enhanced.py`)
- **FastAPI Framework**: Full OpenAI API compatibility
- **Rate Limiting**: Per-endpoint limits with Redis/memory storage
- **Streaming Support**: Server-sent events for real-time responses
- **Monitoring Integration**: Request tracking and metrics
- **Endpoints**:
  - `/v1/chat/completions` - Main chat endpoint (100/min limit)
  - `/v1/models` - Model listing (500/min limit)
  - `/health` - Basic health check (1000/min limit)
  - `/health/detailed` - Comprehensive health with metrics
  - `/metrics` - Full system metrics and analytics

#### 3. **Redis Cache** (`redis_cache.py`)
- **Connection Management**: Singleton pattern with retry logic
- **Cache Types**:
  - Customer search results (1 hour TTL)
  - LLM responses (24 hour TTL)
  - Tilores fields (1 hour TTL)
  - Credit reports (30 minute TTL)
- **Fallback**: Graceful degradation when Redis unavailable

#### 4. **Monitoring System** (`monitoring.py`)
- **Performance Tracking**: Operation timers with metadata
- **Error Logging**: Detailed error tracking with context
- **Health Monitoring**: System health status calculation
- **Metrics Storage**: In-memory with optional Redis persistence
- **Analytics**: Provider usage, success rates, field coverage

#### 5. **Utilities**

##### Context Extraction (`utils/context_extraction.py`)
- **IDPatterns Class**:
  - Email extraction with RFC validation
  - Client ID detection (7-10 digits)
  - Salesforce ID parsing (003Ux format)
  - Phone normalization to E.164
- **Message Context**: Extract customer data from conversation history

##### Field Discovery (`field_discovery_system.py`)
- GraphQL introspection for Tilores schema
- Comprehensive field mapping (310+ fields)
- Type-specific field organization
- Vector database integration ready

##### Credit Analysis (`credit_analysis_system.py`)
- TransUnion integration
- Comprehensive credit report parsing
- Risk assessment calculations
- Payment history analysis

### Data Flow

```
User Request
    ↓
Rate Limiter → Pass/Reject
    ↓
Monitor.start_timer()
    ↓
Context Extraction → Extract IDs from query
    ↓
Query Router → Determine if Tilores needed
    ↓
[Branch: Tilores Tools]          [Branch: General LLM]
    ↓                                   ↓
Cache Check → Hit/Miss             Direct LLM Call
    ↓                                   ↓
Tilores API Call                   Response Generation
    ↓                                   ↓
Tool Execution                          ↓
    ↓                                   ↓
Response Generation ←──────────────────┘
    ↓
Monitor.end_timer()
    ↓
Cache Storage
    ↓
Response to User
```

### Configuration

#### Environment Variables
```bash
# Tilores Configuration
TILORES_API_URL=https://api.tilores.io/v1
TILORES_CLIENT_ID=your_client_id
TILORES_CLIENT_SECRET=your_secret
TILORES_TOKEN_URL=oauth_endpoint

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=...

# Infrastructure
REDIS_URL=redis://localhost:6379
LANGSMITH_API_KEY=ls_...

# Optional
RAILWAY_ENVIRONMENT=production
TILORES_TIMEOUT=30000
```

#### Rate Limits
- Chat Completions: 100 requests/minute
- Model Listing: 500 requests/minute
- Health Checks: 1000 requests/minute
- Metrics: 100 requests/minute
- Default: 200/minute, 3000/hour

### Performance Characteristics

#### Response Times
- Cache hit: <50ms
- Tilores search: 200-500ms
- LLM generation: 1-3s
- Field discovery: ~600ms

#### Resource Usage
- Memory: ~200MB baseline
- Redis: ~50MB for typical cache
- CPU: <5% idle, 20-30% active
- Network: ~10KB/request average

### Security Features

1. **Rate Limiting**: Prevents abuse and DoS
2. **Input Validation**: Pydantic models for all requests
3. **Error Handling**: No sensitive data in error responses
4. **Secret Management**: Environment variables only
5. **Cache Security**: Hashed keys, no PII in cache keys

### Monitoring & Observability

#### Metrics Tracked
- Request count by operation
- Response times (avg, min, max)
- Provider usage distribution
- Error rates and types
- Cache hit ratios
- Field coverage statistics
- Tilores connectivity status

#### Health Indicators
- **Healthy**: >95% success rate, Tilores connected
- **Degraded**: 80-95% success rate, recent errors
- **Unhealthy**: <80% success rate, Tilores disconnected

### Testing Infrastructure

#### Test Coverage
- Unit Tests: 103 tests across 3 modules
- Redis Cache: 100% coverage (34 tests)
- FastAPI Endpoints: 100% coverage (34 tests)
- Core App: 74% coverage (26 tests)

#### Test Fixtures (`tests/conftest.py`)
- Mock Redis clients
- Mock LLM providers
- Mock Tilores API
- Test data generators
- Environment mocking

### Deployment Considerations

#### Production Readiness
- ✅ Rate limiting configured
- ✅ Health checks implemented
- ✅ Metrics endpoint available
- ✅ Error handling comprehensive
- ✅ Logging structured
- ✅ Cache fallback working
- ✅ Provider failover logic

#### Scaling Options
1. **Horizontal**: Multiple FastAPI workers
2. **Redis Cluster**: For cache scaling
3. **Load Balancer**: Distribute requests
4. **CDN**: For static responses

### Recent Enhancements (Jan 2025)

1. **Phase VII**: Complete TDD testing infrastructure
2. **Code Quality**: Logic error fixes, linting configuration
3. **Advanced Features**:
   - Rate limiting integration
   - Context extraction utilities
   - Enhanced monitoring system
   - New health/metrics endpoints

### Future Roadmap

1. **Phase IX**: Production deployment
2. **Phase X**: Advanced analytics dashboard
3. **Phase XI**: Multi-tenant support
4. **Phase XII**: Real-time streaming enhancements
