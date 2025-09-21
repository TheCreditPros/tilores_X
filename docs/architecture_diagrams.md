# Tilores_X Architecture Diagrams

## Current Architecture: LLM-Driven Orchestration (September 2025)

### Core System Flow

```mermaid
graph TB
    A[User Query] --> B{Mandatory Slash Command?}
    B -->|No| C[Reject with helpful error]
    B -->|Yes| D[Parse /agent category query]

    D --> E[LLM-Driven Orchestration System]
    E --> F[Category Detection<br/>billing/credit/status]
    F --> G[System Template Selection]
    G --> H[GraphQL Execution<br/>Real Tilores Data]
    H --> I[Data Extraction<br/>Customer Records]
    I --> J[LLM Intelligence Analysis]
    J --> K[Agent-Specific Formatting]
    K --> L[Response to User]

    G --> M{billing_payment}
    G --> N{credit_scores}
    G --> O{account_status}
    G --> P{billing_credit_combined}

    M --> H
    N --> H
    O --> H
    P --> H
```

### Auto-Restart Development Daemon

```mermaid
graph TB
    A[Developer Edits Code] --> B[File Change Detection]
    B --> C{File Type Check}
    C -->|Python File| D{Cooldown Check<br/>2-second window}
    C -->|Other| E[Ignore]
    D -->|Within cooldown| F[Ignore - Too soon]
    D -->|Cooldown passed| G[Graceful Server Shutdown]
    G --> H[Server Process Cleanup]
    H --> I[Server Auto-Restart]
    I --> J[Health Verification]
    J --> K[Ready for Testing]

    L[Watchdog Library] --> B
    M[Polling Fallback<br/>macOS compatibility] --> B
```

### Multi-Threaded Query Processing

```mermaid
graph TB
    A[Concurrent User Queries] --> B{Slash Command Detection}
    B --> C1[/cs billing Query #1]
    B --> C2[/cs status Query #2]
    B --> C3[/client billing Query #3]

    C1 --> D1[LLM Orchestration #1<br/>billing_payment template]
    C2 --> D2[LLM Orchestration #2<br/>account_status template]
    C3 --> D3[LLM Orchestration #3<br/>billing_payment template]

    D1 --> E1[GraphQL Query #1<br/>Transaction Data]
    D2 --> E2[GraphQL Query #2<br/>Account Data]
    D3 --> E3[GraphQL Query #3<br/>Transaction Data]

    E1 --> F1[LLM Analysis #1<br/>Zoho CS Formatting]
    E2 --> F2[LLM Analysis #2<br/>Zoho CS Formatting]
    E3 --> F3[LLM Analysis #3<br/>Client Chat Formatting]

    F1 --> G1[Response #1<br/>2.3s total]
    F2 --> G2[Response #2<br/>2.0s total]
    F3 --> G3[Response #3<br/>2.4s total]

    G1 --> H[All Responses<br/>Delivered Concurrently]
    G2 --> H
    G3 --> H
```

### Agent Intelligence Architecture

```mermaid
graph TB
    A[User Query] --> B{Agent Type}
    B -->|zoho_cs_agent| C[Zoho CS Agent<br/>Professional Formatting]
    B -->|client_chat_agent| D[Client Chat Agent<br/>Educational Formatting]

    C --> E[Common Data Access<br/>billing_payment<br/>credit_scores<br/>account_status<br/>billing_credit_combined]
    D --> E

    E --> F[GraphQL Orchestration<br/>Real Tilores Data]
    F --> G[LLM Intelligence<br/>Cross-table synthesis<br/>Pattern analysis<br/>Data insights]

    G --> H{Zoho CS Formatting}
    G --> I{Client Chat Formatting}

    H --> J[Bullet points<br/>Third-person language<br/>Professional tone]
    I --> K[Friendly tone<br/>Emojis<br/>Educational structure<br/>Supportive guidance]

    J --> L[Final Response]
    K --> L
```

### Development Workflow Improvement

```mermaid
graph TB
    subgraph "BEFORE (Manual Process)"
        A1[Edit Code<br/>5 seconds] --> B1[Kill Server<br/>pkill -f uvicorn<br/>10 seconds]
        B1 --> C1[Restart Server<br/>python -m uvicorn...<br/>15 seconds]
        C1 --> D1[Test Changes<br/>varies]
        D1 --> E1[Total: 30-60+ seconds]
    end

    subgraph "AFTER (Automated Process)"
        A2[Edit Code<br/>5 seconds] --> B2[Daemon Detects<br/>Instantly<br/><1 second]
        B2 --> C2[Auto-Restart<br/>3 seconds]
        C2 --> D2[Test Changes<br/>Immediately<br/>varies]
        D2 --> E2[Total: 8-10 seconds]
    end

    F[75% Time Reduction] --> E2
    G[Zero Context Switching] --> E2
    H[Instant Feedback] --> E2
```

### System Health Monitoring

```mermaid
graph TB
    A[System Components] --> B[FastAPI Server<br/>Port 8080]
    A --> C[LLM Orchestration<br/>direct_credit_api_fixed.py]
    A --> D[LangChain Integration<br/>core_app.py]
    A --> E[Auto-Restart Daemon<br/>Background Process]
    A --> F[Redis Cache<br/>Optional]

    B --> G[Health Checks<br/>/health endpoint]
    C --> H[GraphQL Validation<br/>Tilores API]
    D --> I[Provider Connectivity<br/>OpenAI/Groq/etc]
    E --> J[File Monitoring<br/>Python changes]
    F --> K[Cache Performance<br/>Hit rates]

    G --> L[Monitoring Dashboard]
    H --> L
    I --> L
    J --> L
    K --> L

    L --> M[Real-time Alerts]
    L --> N[Performance Metrics]
    L --> O[Error Tracking]
```

### Data Flow Architecture

```mermaid
graph TB
    subgraph "User Layer"
        A1[Web Interface] --> B1[REST API Calls]
        A2[CLI Tools] --> B1
        A3[Testing Scripts] --> B1
    end

    subgraph "API Layer"
        B1 --> C1[FastAPI Router<br/>main_enhanced.py]
        C1 --> D1{Request Type}
        D1 -->|Chat Completion| E1[LLM Orchestration<br/>direct_credit_api_fixed.py]
        D1 -->|Health Check| F1[Health Monitor]
        D1 -->|Models List| G1[Model Discovery]
    end

    subgraph "Orchestration Layer"
        E1 --> H1{Slash Command?}
        H1 -->|Yes| I1[Parse Command<br/>/agent category]
        H1 -->|No| J1[General LLM<br/>core_app.py]

        I1 --> K1[Category Detection<br/>billing/credit/status]
        K1 --> L1[Template Selection<br/>billing_payment, etc.]
        L1 --> M1[GraphQL Execution<br/>Tilores API]
        M1 --> N1[Data Extraction<br/>Customer Records]
        N1 --> O1[LLM Analysis<br/>Agent-Specific Prompts]
        O1 --> P1[Formatted Response]
    end

    subgraph "Infrastructure Layer"
        Q1[Redis Cache<br/>24h LLM, 1h data]
        R1[Auto-Restart Daemon<br/>File monitoring]
        S1[Tilores GraphQL API<br/>Customer data]
        T1[LLM Providers<br/>OpenAI, Groq, etc.]

        M1 --> S1
        O1 --> T1
        E1 --> Q1
        R1 --> C1
    end

    P1 --> U1[Response to User]
    J1 --> U1
    F1 --> U1
    G1 --> U1
```
