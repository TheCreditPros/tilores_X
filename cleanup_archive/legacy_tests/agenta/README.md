# 🎯 Agenta Testing Framework

A comprehensive testing framework for Agenta.ai prompt variants that leverages your complete master data as authoritative ground truth for field-level accuracy scoring and automated prompt optimization.

## 🚀 **Quick Start**

### **1. Environment Setup**

```bash
# Required: Agenta.ai API key
export AGENTA_API_KEY="your-agenta-api-key"

# Required: Variant endpoints (configure in Agenta.ai dashboard)
export APP_URL_BASELINE="https://cloud.agenta.ai/api/org/app/invoke?variant=baseline&environment=dev"
export APP_URL_CHALLENGER="https://cloud.agenta.ai/api/org/app/invoke?variant=challenger&environment=dev"

# Optional: LLM judge for free-text evaluation
export OPENAI_API_KEY="your-openai-key"
export JUDGE_MODEL="gpt-4o-mini"
```

### **2. Run Quick Test**

```bash
cd tests/agenta
python agenta_test_runner.py --quick 5
```

### **3. Run Complete Pipeline**

```python
from agenta_test_runner import AgentaTestRunner

# Initialize and validate environment
runner = AgentaTestRunner()
validation = runner.validate_environment()

if validation["valid"]:
    # Run complete testing pipeline
    results = runner.run_complete_pipeline()
    print(f"Success: {results['success']}")
    print(f"Files generated: {len(results['files_generated'])}")
else:
    print("Fix environment issues first")
```

## 📊 **Framework Components**

### **Core Components**

1. **Ground Truth Extractor** (`ground_truth_extractor.py`)

   - Extracts test cases from your master data file
   - Creates comprehensive expected outputs
   - Handles all data types (credit, transactions, phone, cards, tickets)

2. **Evaluation Framework** (`agenta_evaluation_framework.py`)

   - Multi-variant testing execution
   - Field-level accuracy scoring with configurable weights
   - LLM judge integration for free-text fields
   - Performance metrics tracking

3. **Test Case Generator** (`test_case_generator.py`)

   - Creates JSONL test cases from ground truth
   - Covers all query types and scenarios
   - Includes edge cases and error conditions

4. **Results Analyzer** (`results_analyzer.py`)

   - Comprehensive results analysis
   - Promotion rule evaluation
   - Markdown report generation
   - Performance recommendations

5. **Test Runner** (`agenta_test_runner.py`)
   - Orchestrates complete pipeline
   - Environment validation
   - Automated execution and reporting

## 🎯 **Test Cases Generated**

Based on your master data (`MASTER_COMPLETE_DATA_WITH_FULL_PHONE_20250902_155645.json`):

### **Customer Data (Ground Truth)**

- **Email:** e.j.price1986@gmail.com
- **Name:** Esteban Price
- **Client ID:** 1747598
- **Entity ID:** dc93a2cd-de0a-444f-ad47-3003ba998cd3

### **Test Categories**

**Account Status Tests (3 tests)**

- Email-based lookup
- Client ID lookup
- Concise status query

**Credit Analysis Tests (4 tests)**

- Comprehensive credit analysis
- Credit score inquiry
- Risk assessment
- Credit history timeline

**Transaction Analysis Tests (3 tests)**

- Comprehensive transaction analysis
- Payment patterns
- Transaction summary

**Phone Analysis Tests (2 tests)**

- Phone call data analysis
- Contact history

**Multi-Data Analysis Tests (3 tests)**

- Comprehensive customer analysis
- 360-degree customer view
- Data availability check

**Edge Cases Tests (4 tests)**

- Nonexistent customer
- Empty query
- Malformed email
- Very long query

**Total: ~19 comprehensive test cases**

## 📈 **Scoring System**

### **Field Weights**

**Exact Match Fields (Weight 3.0):**

- `customer_name`, `customer_email`, `client_id`
- `total_credit_reports`, `total_transactions`

**Numeric Tolerance Fields (Weight 2.0):**

- `latest_credit_score` (±5 points or ±2%)
- `total_transaction_amount`, `average_transaction_amount` (±2%)

**Boolean Fields (Weight 2.0):**

- `has_credit_data`, `has_transaction_data`, `has_phone_data`
- `customer_found`, `data_available`

**Categorical Fields (Weight 2.0):**

- `risk_level` (low/medium/high)
- `credit_bureau`, `account_status`

**Free Text Fields (Weight 1.0):**

- `explanation`, `risk_assessment`
- Uses LLM judge + similarity scoring

### **Tolerance Settings**

- **Numeric Percent:** ±2% relative tolerance
- **Numeric Absolute:** ±5 points absolute tolerance
- **Similarity Threshold:** 85% for LLM judge bypass

## 🏆 **Promotion Rules**

A challenger variant is promoted if it meets **ALL** criteria:

1. **Score Improvement:** ≥3% improvement over baseline
2. **Latency Acceptable:** ≤10% latency increase
3. **Sufficient Tests:** ≥5 test cases executed
4. **Success Rate:** ≥90% successful evaluations

## 📁 **Output Files**

Each test run generates:

- `ground_truth.json` - Extracted ground truth data
- `test_cases.jsonl` - Generated test cases
- `evaluation_results.json` - Raw evaluation results
- `analysis_results.json` - Detailed analysis
- `evaluation_report.md` - Human-readable report
- `pipeline_summary.json` - Execution summary

## 🔧 **Configuration**

### **Custom Configuration**

```json
{
  "field_weights": {
    "customer_name": 3.0,
    "latest_credit_score": 2.0,
    "explanation": 1.0
  },
  "promotion_rules": {
    "min_score_improvement": 0.05,
    "max_latency_increase": 0.15
  }
}
```

### **Environment Variables**

```bash
# Required
AGENTA_API_KEY="your-key"
APP_URL_BASELINE="baseline-endpoint"
APP_URL_CHALLENGER="challenger-endpoint"

# Optional
OPENAI_API_KEY="judge-key"
JUDGE_MODEL="gpt-4o-mini"
JUDGE_BASE_URL="https://api.openai.com/v1"
```

## 📊 **Usage Examples**

### **Basic Pipeline**

```python
from agenta_test_runner import AgentaTestRunner

runner = AgentaTestRunner()
results = runner.run_complete_pipeline()
```

### **Quick Test**

```python
# Test with only 5 test cases
results = runner.run_quick_test(test_case_limit=5)
```

### **Custom Configuration**

```python
config = {
    "test_case_limit": 10,
    "field_weights": {"customer_name": 5.0},
    "promotion_rules": {"min_score_improvement": 0.05}
}

runner = AgentaTestRunner(config)
results = runner.run_complete_pipeline()
```

### **Individual Components**

```python
# Extract ground truth only
from ground_truth_extractor import GroundTruthExtractor
extractor = GroundTruthExtractor()
ground_truth = extractor.get_ground_truth()

# Generate test cases only
from test_case_generator import TestCaseGenerator
generator = TestCaseGenerator()
test_cases = generator.generate_all_test_cases()

# Run evaluation only
from agenta_evaluation_framework import AgentaEvaluationFramework
framework = AgentaEvaluationFramework()
results = framework.evaluate_test_suite(test_cases)
```

## 📈 **Expected Results**

### **Quality Metrics**

- **Field Accuracy:** >95% for exact match fields
- **Numeric Tolerance:** >90% within tolerance ranges
- **LLM Judge Score:** >0.85 for explanation fields
- **Overall Score:** >0.90 for production promotion

### **Performance Metrics**

- **Response Time:** <5s p90 latency
- **Token Efficiency:** <2000 tokens average
- **Cost:** <$0.01 per evaluation
- **Reliability:** >99% successful evaluations

## 🎯 **Integration with Existing System**

This framework integrates seamlessly with your existing infrastructure:

- ✅ **Enhanced Agenta Manager** (`agenta_sdk_manager_enhanced.py`)
- ✅ **Template Prompts** (`agenta_template_prompts.json`)
- ✅ **Production API** (`direct_credit_api_fixed.py`)
- ✅ **Testing Infrastructure** (`tests/` directory)
- ✅ **Master Data** (`MASTER_COMPLETE_DATA_WITH_FULL_PHONE_*.json`)

## 🚀 **CLI Interface**

```bash
# Validate environment
python agenta_test_runner.py --validate

# Quick test with 5 cases
python agenta_test_runner.py --quick 5

# Custom configuration
python agenta_test_runner.py --config custom_config.json --limit 10

# Custom output directory
python agenta_test_runner.py --output-dir /path/to/results
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"Master data file not found"**

   ```bash
   # Ensure master data file exists
   ls MASTER_COMPLETE_DATA_WITH_FULL_PHONE_*.json
   ```

2. **"No variant endpoints configured"**

   ```bash
   # Set environment variables
   export APP_URL_BASELINE="your-baseline-url"
   export APP_URL_CHALLENGER="your-challenger-url"
   ```

3. **"LLM judge failed"**
   ```bash
   # Set OpenAI API key (optional - will use similarity fallback)
   export OPENAI_API_KEY="your-openai-key"
   ```

### **Validation**

```python
# Check environment before running
runner = AgentaTestRunner()
validation = runner.validate_environment()

if not validation["valid"]:
    for error in validation["errors"]:
        print(f"❌ {error}")
```

## 📚 **Advanced Usage**

### **Custom Field Weights**

Adjust field importance based on your priorities:

```python
config = {
    "field_weights": {
        # Critical business fields
        "customer_name": 5.0,
        "latest_credit_score": 4.0,

        # Important data fields
        "has_credit_data": 3.0,
        "total_transactions": 3.0,

        # Nice-to-have fields
        "explanation": 1.0
    }
}
```

### **Custom Promotion Rules**

Set stricter or more lenient promotion criteria:

```python
config = {
    "promotion_rules": {
        "min_score_improvement": 0.05,  # 5% improvement required
        "max_latency_increase": 0.05,   # Max 5% latency increase
        "min_test_cases": 10,           # Minimum 10 test cases
        "min_success_rate": 0.95        # 95% success rate required
    }
}
```

### **Batch Testing**

Test multiple configurations:

```python
configs = [
    {"field_weights": {"customer_name": 3.0}},
    {"field_weights": {"customer_name": 5.0}},
    {"promotion_rules": {"min_score_improvement": 0.05}}
]

for i, config in enumerate(configs):
    runner = AgentaTestRunner(config)
    results = runner.run_complete_pipeline()
    print(f"Config {i+1}: {'✅' if results['success'] else '❌'}")
```

## 🎉 **Benefits**

### **Immediate Value**

- ✅ **Data-Driven Decisions:** Objective prompt comparison with real data
- ✅ **Automated Testing:** No manual evaluation required
- ✅ **Comprehensive Coverage:** Tests all query types and edge cases
- ✅ **Production Ready:** Built on your existing infrastructure

### **Long-Term Value**

- 🚀 **Continuous Optimization:** Automated prompt improvement pipeline
- 📊 **Performance Insights:** Detailed analytics and recommendations
- 🛡️ **Regression Prevention:** Automated quality gates
- 📈 **Scalable Testing:** Easily add new test cases and scenarios

This framework transforms your Agenta.ai integration into a comprehensive testing and optimization platform, providing immediate value for prompt variant evaluation and establishing a foundation for continuous improvement.


