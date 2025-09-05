# Tilores GraphQL Schema Reference

**Generated:** December 2024
**Schema Version:** Complete Introspection
**Total Types:** 120 (87 credit-related)

## 📊 Schema Overview

- **Types:** 120 total
- **Queries:** 5 available
- **Mutations:** 4 available
- **Enums:** 2 types
- **Scalars:** 10 types
- **Credit Types:** 87 specialized credit-related types

## 🔍 Available Queries

### 1. `search` → SearchOutput!

Search for entities that match the search parameters.

- **Input:** `SearchInput!`

### 2. `entity` → EntityOutput!

Returns a single entity with the provided id.

- **Input:** `EntityInput!`

### 3. `entityByRecord` → EntityOutput!

Returns a single entity that contains the record with the provided id.

- **Input:** `EntityByRecordInput!`

### 4. `metrics` → Metrics!

Top-level entry point for tilores metrics.

### 5. `searchByText` → SearchByTextOutput!

Text-based search functionality.

- **Input:** `SearchByTextInput!`

## 🔄 Available Mutations

### 1. `submit` → SubmitOutput!

Adds new records and tries to match them with existing entities.

### 2. `submitWithPreview` → SubmitWithPreviewOutput!

Adds new records with preview of potential entity matches.

### 3. `disassemble` → DisassembleOutput!

Removes one or more edges or records.

### 4. `removeConnectionBan` → RemoveConnectionBanOutput!

Removes a connection ban between entities.

## 🏗️ Core Entity Structure

### Entity Fields

```graphql
type Entity {
  id: ID! # Unique identifier
  records: [Record!]! # All records in entity
  edges: [String!]! # Connection definitions
  duplicates: Duplicates! # Duplicate record IDs
  hits: Hits! # Rules satisfied per record
  score: Float! # Matching quality (0.0-1.0)
  consistency: Float! # Data consistency (0.0-1.0)
  hitScore: Float! # Search match quality (0.0-1.0)
  edgeInsights: EdgeInsights!
  recordInsights: RecordInsights!
}
```

## 📝 Record Structure (163 Fields)

### Core Customer Fields

- `STATUS: String` - Account status
- `FIRST_NAME: String` - Customer first name
- `LAST_NAME: String` - Customer last name
- `EMAIL: String` - Customer email
- `CLIENT_ID: String` - Unique client identifier
- `PRODUCT_NAME: String` - Product name
- `CURRENT_PRODUCT: String` - Current product
- `ENROLL_DATE: String` - Enrollment date

### Credit Data Field

- `CREDIT_RESPONSE: CreditResponse` - Complete credit report data

### Transaction Fields

- `TRANSACTION_AMOUNT: String`
- `PAYMENT_METHOD: String`
- `GATEWAY_RESPONSE: String`
- `LAST_APPROVED_TRANSACTION: String`

### Card Information Fields

- `CARD_FIRST_6_DIGIT: String`
- `CARD_LAST_4: String`
- `CARD_EXPIRED: Boolean`
- `BIN: String`

### Phone Call Fields

- `AGENT_USERNAME: String`
- `CALL_DURATION: String`
- `CALL_START_TIME: String`
- `CAMPAIGN_NAME: String`

### Support Ticket Fields (Zoho)

- `TICKETNUMBER: String`
- `SUBJECT: String`
- `ZOHO_STATUS: String`
- `CATEGORY: String`
- `SENTIMENT: String`

## 💳 Credit Response Structure

### CreditResponse Fields

```graphql
type CreditResponse {
  BORROWER: CreditResponseBorrower
  CREDIT_BUREAU: String
  CREDIT_FILE: CreditResponseCreditFile
  CREDIT_FROZEN_STATUS: CreditResponseCreditFrozenStatus
  CREDIT_INQUIRY: [CreditResponseCreditInquiry]
  CREDIT_LIABILITY: [CreditResponseCreditLiability]
  CREDIT_REPOSITORY_INCLUDED: CreditResponseCreditRepositoryIncluded
  CREDIT_REQUEST_DATA: CreditResponseCreditRequestData
  CREDIT_SCORE: [CreditResponseCreditScore]
  CREDIT_SUMMARY: CreditResponseCreditSummary
  CREDIT_SUMMARY_TUI: CreditResponseCreditSummaryTui
  CreditRatingCodeType: String
  CreditReportFirstIssuedDate: String
  CreditReportIdentifier: String
  CreditReportMergeTypeIndicator: String
  CreditResponseID: String
  MISMOVersionID: String
  Internal_Client_Key: String
  Client_key: String
  Report_ID: String
  Report_Type: String
  Vendor: String
}
```

### Credit Score Structure

```graphql
type CreditResponseCreditScore {
  BorrowerID: String
  CreditFileID: String
  CreditReportIdentifier: String
  CreditRepositorySourceType: String # Bureau (Experian, TransUnion, Equifax)
  CreditScoreID: String
  Factor: [CreditResponseCreditScoreFactor]
  ModelNameType: String
  NoScoreReasonCode: String
  NoScoreReasonType: String
  Value: String # Actual credit score
  # ... and 4 more fields
}
```

### Credit Liability Structure

```graphql
type CreditResponseCreditLiability {
  AccountClosedDate: String
  AccountIdentifier: String
  AccountOpenedDate: String
  AccountOwnershipType: String
  AccountPaidDate: String
  AccountType: String # Type of account
  CreditBalance: String # Current balance
  CreditLimitAmount: String # Credit limit
  CurrentRating: CreditResponseCreditLiabilityCurrentRating
  HighestAdverseRating: CreditResponseCreditLiabilityHighestAdverseRating
  LateCount: CreditResponseCreditLiabilityLateCount
  PaymentPattern: CreditResponseCreditLiabilityPaymentPattern
  # ... and 37 more fields
}
```

## 📊 RecordInsights (Advanced Querying)

### Available Operations

```graphql
type RecordInsights {
  records: [Record!]! # All records
  filter(condition: FilterCondition): RecordInsights!
  sort(criteria: SortCriteria): RecordInsights!
  group(field: String!): [RecordInsights!]!
  limit(count: Int!): RecordInsights!

  # Aggregation functions
  count: Int!
  countDistinct: Int!
  first: Record
  last: Record
  newest: Record
  oldest: Record

  # Statistical functions
  average: Float
  max: Float
  median: Float
  min: Float
  sum: Float
  standardDeviation: Float
  confidence: Float

  # Data extraction
  values: [Any]!
  valuesDistinct: [Any]!
  flatten: [Any]!
  flattenDistinct: [Any]!
  frequencyDistribution: [FrequencyDistributionEntry!]!
}
```

## 🎯 Optimized Query Examples

### 1. Basic Customer Data

```graphql
query GetCustomerBasics($id: ID!) {
  entity(input: { id: $id }) {
    entity {
      id
      records {
        id
        STATUS
        FIRST_NAME
        LAST_NAME
        EMAIL
        CLIENT_ID
        PRODUCT_NAME
        CURRENT_PRODUCT
        ENROLL_DATE
      }
    }
  }
}
```

### 2. Comprehensive Credit Analysis

```graphql
query GetComprehensiveCreditData($id: ID!) {
  entity(input: { id: $id }) {
    entity {
      id
      records {
        id
        # Basic customer data
        STATUS
        FIRST_NAME
        LAST_NAME
        EMAIL
        CLIENT_ID
        CURRENT_PRODUCT
        ENROLL_DATE

        # Complete credit response
        CREDIT_RESPONSE {
          CREDIT_BUREAU
          CreditReportFirstIssuedDate

          CREDIT_SCORE {
            Value
            ModelNameType
            CreditRepositorySourceType
            Factor {
              Code
              Text
              Factor_Type
            }
          }

          CREDIT_LIABILITY {
            AccountType
            CreditLimitAmount
            CreditBalance
            AccountOpenedDate
            AccountClosedDate
            CurrentRating {
              Code
              Type
            }
            HighestAdverseRating {
              Code
              Type
            }
            LateCount {
              Days30
              Days60
              Days90
            }
            PaymentPattern {
              Data
              StartDate
            }
          }

          CREDIT_INQUIRY {
            InquiryDate
            SubscriberName
            CreditBusinessType
          }

          CREDIT_FROZEN_STATUS {
            EquifaxIndicator
            ExperianIndicator
            TransUnionIndicator
          }
        }
      }
    }
  }
}
```

### 3. Multi-Data Analysis with RecordInsights

```graphql
query GetMultiDataAnalysis($id: ID!) {
  entity(input: { id: $id }) {
    entity {
      id

      # Customer data with insights
      recordInsights {
        filter(condition: { field: "STATUS", operator: "EXISTS" }) {
          first {
            STATUS
            FIRST_NAME
            LAST_NAME
            EMAIL
            CLIENT_ID
            CURRENT_PRODUCT
            ENROLL_DATE
          }
        }
      }

      # Credit data insights
      recordInsights {
        filter(condition: { field: "CREDIT_RESPONSE", operator: "EXISTS" }) {
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CREDIT_SCORE {
                Value
                CreditRepositorySourceType
              }
              CREDIT_LIABILITY {
                AccountType
                CreditLimitAmount
                CreditBalance
              }
            }
          }
        }
      }

      # Transaction data insights
      recordInsights {
        filter(condition: { field: "TRANSACTION_AMOUNT", operator: "EXISTS" }) {
          records {
            TRANSACTION_AMOUNT
            PAYMENT_METHOD
            GATEWAY_RESPONSE
            TRANSACTION_CREATED_DATE
          }
          count
          sum(field: "TRANSACTION_AMOUNT")
          average(field: "TRANSACTION_AMOUNT")
        }
      }

      # Support ticket insights
      recordInsights {
        filter(condition: { field: "TICKETNUMBER", operator: "EXISTS" }) {
          records {
            TICKETNUMBER
            SUBJECT
            ZOHO_STATUS
            CATEGORY
            SENTIMENT
            CREATEDTIME
          }
          count
          frequencyDistribution(field: "CATEGORY")
        }
      }
    }
  }
}
```

### 4. Temporal Credit Analysis

```graphql
query GetTemporalCreditAnalysis($id: ID!) {
  entity(input: { id: $id }) {
    entity {
      id

      # Get all credit reports ordered by date
      recordInsights {
        filter(condition: { field: "CREDIT_RESPONSE", operator: "EXISTS" }) {
          sort(
            criteria: {
              field: "CREDIT_RESPONSE.CreditReportFirstIssuedDate"
              direction: ASC
            }
          ) {
            records {
              CREDIT_RESPONSE {
                CREDIT_BUREAU
                CreditReportFirstIssuedDate
                CREDIT_SCORE {
                  Value
                  CreditRepositorySourceType
                }
                CREDIT_LIABILITY {
                  AccountType
                  CreditLimitAmount
                  CreditBalance
                  CurrentRating {
                    Code
                    Type
                  }
                }
              }
            }

            # Get first and most recent reports
            first {
              CREDIT_RESPONSE {
                CreditReportFirstIssuedDate
                CREDIT_SCORE {
                  Value
                  CreditRepositorySourceType
                }
              }
            }
            newest {
              CREDIT_RESPONSE {
                CreditReportFirstIssuedDate
                CREDIT_SCORE {
                  Value
                  CreditRepositorySourceType
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## 🔧 Advanced Filtering Examples

### Bureau-Specific Filtering

```graphql
# Filter for Experian reports only
recordInsights {
  filter(condition: {
    field: "CREDIT_RESPONSE.CREDIT_BUREAU",
    operator: "EQUALS",
    value: "Experian"
  }) {
    records {
      CREDIT_RESPONSE {
        CREDIT_SCORE { Value }
        CREDIT_LIABILITY { CreditLimitAmount CreditBalance }
      }
    }
  }
}
```

### Date Range Filtering

```graphql
# Filter for recent credit reports
recordInsights {
  filter(condition: {
    field: "CREDIT_RESPONSE.CreditReportFirstIssuedDate",
    operator: "GREATER_THAN",
    value: "2024-01-01"
  }) {
    records {
      CREDIT_RESPONSE {
        CreditReportFirstIssuedDate
        CREDIT_SCORE { Value CreditRepositorySourceType }
      }
    }
  }
}
```

## 📈 Key Insights for Implementation

### 1. **Credit Data Access Pattern**

- Credit data is nested under `records.CREDIT_RESPONSE`
- Each record can have one `CREDIT_RESPONSE` object
- Credit scores are arrays: `CREDIT_RESPONSE.CREDIT_SCORE[]`
- Credit liabilities are arrays: `CREDIT_RESPONSE.CREDIT_LIABILITY[]`

### 2. **Bureau Identification**

- Use `CREDIT_RESPONSE.CREDIT_BUREAU` for bureau name
- Use `CREDIT_SCORE.CreditRepositorySourceType` for bureau in scores
- Frozen status available per bureau in `CREDIT_FROZEN_STATUS`

### 3. **Temporal Analysis**

- Use `CreditReportFirstIssuedDate` for report dating
- Combine with RecordInsights `sort()` and `first()`/`newest()` for comparisons
- Group by bureau for bureau-specific temporal analysis

### 4. **Multi-Data Queries**

- Single query can fetch customer, credit, transaction, and support data
- Use RecordInsights `filter()` to separate data types
- Leverage aggregation functions for analytics

### 5. **Performance Optimization**

- Request only needed fields to reduce payload
- Use RecordInsights filtering instead of client-side filtering
- Leverage `limit()` for large datasets

---

**Note:** This schema reference is based on complete GraphQL introspection and represents the full available API surface. Use this as the authoritative source for all GraphQL query construction.
