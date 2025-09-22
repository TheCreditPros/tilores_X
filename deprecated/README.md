# Deprecated Files - No Longer Used

These files are from previous development phases and are no longer part of the current LLM-driven orchestration architecture. They are kept for historical reference but should not be used in production.

## Categories of Deprecated Files:

### Agenta Integration Files

- `agenta_*` - Old Agenta.ai platform integration (replaced by direct LLM orchestration)
- `routing_aware_*` - Old routing-based architecture (replaced by LLM intelligence)

### OpenWebUI Integration Files

- `openwebui_*` - OpenWebUI deployment scripts (not current deployment target)
- `configure_openwebui_*` - OpenWebUI configuration (superseded)

### Analysis & Investigation Files

- `*investigation*.py` - Old debugging and analysis scripts
- `*analysis*.py` - Data analysis tools from earlier phases
- `phase*_*.py` - Incremental development phases

### Autonomous AI Files

- `autonomous_*` - Old autonomous AI platform experiments
- `enhanced_*` - Enhanced versions replaced by current architecture

### Deployment & Setup Files

- `deploy_to_agenta.py` - Old Agenta deployment
- `setup_agenta_*` - Agenta environment setup
- `railway_*` - Railway-specific deployment scripts

### Current Architecture (LLM-Driven Orchestration)

The current system uses:

- **LLM Intelligence**: System selects optimal GraphQL templates, LLM analyzes data
- **Cross-Table Synthesis**: Single queries combine transactions, accounts, credit data
- **Auto-Restart Daemon**: Zero manual server restarts during development
- **Agent-Specific Formatting**: Zoho CS vs Client Chat maintained

See main README.md for current architecture details.
