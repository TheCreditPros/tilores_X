# Tilores GraphQL Schema Tools - Usage Guide

**Status:** 100% Complete and Validated
**Last Updated:** December 2024

## 🛠️ Available Tools Overview

Our comprehensive GraphQL schema mapping toolset provides everything needed to work with the Tilores API effectively:

| Tool                                  | Purpose                         | Usage                            |
| ------------------------------------- | ------------------------------- | -------------------------------- |
| `schema_explorer.py`                  | Complete schema introspection   | `python3 schema_explorer.py`     |
| `schema_analyzer.py`                  | Structure analysis & samples    | `python3 schema_analyzer.py`     |
| `schema_final_review.py`              | Validation & completeness check | `python3 schema_final_review.py` |
| `schema_utils.py`                     | Query templates & utilities     | Import and use functions         |
| `TILORES_GRAPHQL_SCHEMA_REFERENCE.md` | Human-readable documentation    | Reference guide                  |
| `SCHEMA_NESTED_OBJECTS_MAP.md`        | Nested relationships map        | Relationship reference           |

## 🔧 Tool Usage Instructions

### 1. Schema Explorer (`schema_explorer.py`)

**Purpose:** Complete GraphQL introspection and schema generation

**Usage:**

```bash
python3 schema_explorer.py
```

**What it does:**

- Connects to Tilores GraphQL API using OAuth
- Runs comprehensive introspection query
- Processes all 132 schema elements
- Generates `tilores_graphql_schema.json` (raw schema data)
- Validates all type references and relationships

**When to use:**

- When schema changes are suspected
- To regenerate the complete schema map
- For initial setup or validation

### 2. Schema Analyzer (`schema_analyzer.py`)

**Purpose:** Analyze schema structure and generate documentation

**Usage:**

```bash
python3 schema_analyzer.py
```

**What it does:**

- Loads and analyzes the complete schema
- Shows Entity, Record, CreditResponse structures
- Lists all available queries and mutations
- Identifies credit-related types (87 found)
- Generates sample GraphQL queries

**Output includes:**

- Complete field listings for core types
- Available operations breakdown
- Sample query examples
- Credit data structure analysis

### 3. Schema Final Review (`schema_final_review.py`)

**Purpose:** Comprehensive validation and completeness checking

**Usage:**

```bash
python3 schema_final_review.py
```

**What it validates:**

- All 130 type references (0 missing ✅)
- Nested object relationships
- Credit response completeness (10 major types)
- RecordInsights operations (23 operations)
- Query and mutation availability
- Complete schema integrity

**Validation Results:**

- 🎉 **100% SCHEMA COMPLETENESS VALIDATED**
- Zero missing type references
- All expected operations present

### 4. Schema Utils (`schema_utils.py`)

**Purpose:** Practical utilities and query templates

**Import and use:**

```python
from schema_utils import *

# Get standard templates
basic_query = get_basic_customer_query()
credit_query = get_comprehensive_credit_query()
multi_data_query = get_multi_data_query()
temporal_query = get_temporal_credit_query()

# Bureau-specific queries
experian_query = get_experian_only_query()
transunion_query = get_transunion_only_query()
equifax_query = get_equifax_only_query()

# Custom query builder
utils = TiloresSchemaUtils()
custom_query = utils.build_custom_query(
    include_basic=True,
    include_credit=True,
    include_transactions=True
)
```

**Available Functions:**

- `get_basic_customer_query()` - Core customer data
- `get_comprehensive_credit_query()` - Full credit analysis
- `get_multi_data_query()` - All data types combined
- `get_temporal_credit_query()` - Historical comparisons
- `get_experian_only_query()` - Experian-specific data
- `get_transunion_only_query()` - TransUnion-specific data
- `get_equifax_only_query()` - Equifax-specific data
- `build_custom_query()` - Custom query builder

## 📚 Documentation Files

### TILORES_GRAPHQL_SCHEMA_REFERENCE.md

**Complete human-readable documentation including:**

- All 5 available queries with descriptions
- All 4 available mutations with descriptions
- Complete Entity, Record, CreditResponse structures
- RecordInsights operations (23 total)
- Optimized query examples
- Advanced filtering patterns
- Performance optimization tips

### SCHEMA_NESTED_OBJECTS_MAP.md

**Detailed nested relationships map including:**

- Complete entity relationship hierarchy
- All nested object structures
- Field counts for each type
- Validation results summary
- Schema statistics table

## 🎯 Common Usage Patterns

### 1. Getting Started

```bash
# First time setup - generate complete schema
python3 schema_explorer.py

# Analyze the schema structure
python3 schema_analyzer.py

# Validate completeness
python3 schema_final_review.py
```

### 2. Using Query Templates

```python
from schema_utils import get_comprehensive_credit_query

# Get the template
query = get_comprehensive_credit_query()

# Use in your API calls
variables = {"id": "dc93a2cd-de0a-444f-ad47-3003ba998cd3"}
# Execute query with your GraphQL client
```

### 3. Building Custom Queries

```python
from schema_utils import TiloresSchemaUtils

utils = TiloresSchemaUtils()

# Build a custom query for specific needs
custom_query = utils.build_custom_query(
    include_basic=True,          # Customer data
    include_credit=True,         # Credit information
    include_transactions=False,  # Skip transactions
    include_tickets=True,        # Include support tickets
    credit_fields=["CREDIT_BUREAU", "CreditReportFirstIssuedDate"]
)
```

### 4. Bureau-Specific Analysis

```python
from schema_utils import get_experian_only_query

# Get Experian-only data
experian_query = get_experian_only_query()

# Or build date-filtered query
utils = TiloresSchemaUtils()
recent_reports = utils.get_date_range_query("2024-01-01")
```

### 5. Field Discovery

```python
from schema_utils import TiloresSchemaUtils

utils = TiloresSchemaUtils()

# List available fields
record_fields = utils.list_record_fields()        # 163 fields
credit_fields = utils.list_credit_fields()        # 22 fields
score_fields = utils.get_credit_score_fields()    # 14 fields
liability_fields = utils.get_credit_liability_fields()  # 54 fields
```

## 🔍 Key Schema Insights for Usage

### Entity Structure

```
Entity
├── records: [Record!]!           # All customer data
└── recordInsights: RecordInsights! # Powerful filtering/aggregation
```

### Credit Data Access Pattern

```
Record
└── CREDIT_RESPONSE: CreditResponse
    ├── CREDIT_SCORE: [CreditResponseCreditScore]     # Array of scores
    ├── CREDIT_LIABILITY: [CreditResponseCreditLiability] # Array of accounts
    └── CREDIT_INQUIRY: [CreditResponseCreditInquiry]     # Array of inquiries
```

### RecordInsights Power

```
RecordInsights
├── filter(condition: FilterCondition)  # Advanced filtering
├── sort(criteria: SortCriteria)        # Multi-field sorting
├── group(field: String!)               # Data grouping
├── first(), newest(), oldest()         # Temporal access
└── count, sum, average, etc.           # Aggregation functions
```

## ⚡ Performance Tips

1. **Use Specific Fields:** Only request fields you need
2. **Leverage RecordInsights:** Use server-side filtering instead of client-side
3. **Bureau-Specific Queries:** Filter by bureau when analyzing specific credit reports
4. **Temporal Queries:** Use `sort()` with date fields for historical analysis
5. **Aggregation:** Use RecordInsights aggregation functions for analytics

## 🎉 Validation Status

**✅ 100% SCHEMA COMPLETENESS VALIDATED**

- 132 total schema elements mapped
- 130 type references found, 0 missing
- All entities and nested objects documented
- All expected queries and mutations present
- Complete credit data structure mapped
- Full RecordInsights functionality available

## 🚀 Next Steps

1. **Use the tools** to explore and understand the schema
2. **Reference the documentation** for specific field information
3. **Leverage query templates** for common operations
4. **Build custom queries** for specific use cases
5. **Validate completeness** when schema changes are suspected

The schema tools provide everything needed to work effectively with the Tilores GraphQL API, from initial exploration to production query construction.
