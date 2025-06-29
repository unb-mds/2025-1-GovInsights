# 🛠️ Script Usage Guide

## 🎯 **Quick Reference**

### **✅ Validation Scripts** (`scripts/validation/`)

#### **🔍 Structure Validation**
```bash
python scripts/validation/validate_integration_tests.py
```
**Purpose:** Validates syntax, imports, and basic structure of all test files
**Output:** Console report + validation results
**When to use:** Before making changes, after updates

#### **📊 Coverage Analysis**  
```bash
python scripts/validation/analyze_test_coverage.py
```
**Purpose:** Analyzes code coverage across all modules
**Output:** Detailed coverage report + recommendations
**When to use:** To check test completeness

#### **⚡ Quick Analysis**
```bash
python scripts/validation/quick_test_analysis.py
```
**Purpose:** Fast overview of test structure and status
**Output:** JSON report + quick metrics
**When to use:** For rapid health checks

#### **🚀 Full Test Execution**
```bash
python scripts/validation/run_final_integration_tests.py
```
**Purpose:** Executes all integration tests with detailed reporting
**Output:** Complete execution report + results
**When to use:** For comprehensive validation

---

## 🏗️ **Infrastructure Scripts** (`scripts/infrastructure/`)

#### **🔧 Health Check**
```bash
python scripts/infrastructure/test_integration_health.py
```
**Purpose:** Verifies test environment health
**When to use:** Before running tests, troubleshooting

#### **📦 Import Validation**
```bash
python scripts/infrastructure/test_imports_integration.py
```
**Purpose:** Validates all imports and dependencies
**When to use:** After dependency changes

#### **🏠 Basic Infrastructure**
```bash
python scripts/infrastructure/test_basic_infrastructure.py
```
**Purpose:** Tests basic project infrastructure
**When to use:** Project setup validation

---

## 🛠️ **Fix Scripts** (`scripts/fixes/`) - Reference Only

> **Note:** These scripts were used historically to fix issues. They are kept for reference and understanding of what was corrected.

#### **🔤 Encoding Fix**
```bash
# Historical - already applied
python scripts/fixes/fix_encoding.py
```
**Purpose:** Fixed UTF-8 encoding issues in test files
**Status:** ✅ Applied

#### **🔗 End-to-End Test Fix**
```bash
# Historical - already applied  
python scripts/fixes/fix_end_to_end_tests.py
```
**Purpose:** Corrected end-to-end test structure and mocks
**Status:** ✅ Applied

#### **🔍 Method Existence Fix**
```bash
# Historical - already applied
python scripts/fixes/fix_buscar_indicadores.py
```
**Purpose:** Fixed missing method references
**Status:** ✅ Applied

---

## 📋 **Script Details**

### **🔍 validate_integration_tests.py**

**What it does:**
- Checks Python syntax in all test files
- Validates import statements
- Counts test methods and classes
- Identifies structural issues

**Output:**
```
✅ File validation results
📊 Statistics summary  
⚠️ Issues found (if any)
📝 Recommendations
```

**Return codes:**
- `0` - All tests valid
- `1` - Issues found

### **📊 analyze_test_coverage.py**

**What it does:**
- Runs coverage analysis on all modules
- Generates detailed coverage report
- Identifies untested code areas
- Provides improvement recommendations

**Output:**
```
📈 Coverage percentage by module
📋 Detailed line-by-line analysis
🎯 Areas needing attention
💡 Improvement suggestions
```

**Requirements:**
- `coverage` package installed
- Test files must be runnable

### **⚡ quick_test_analysis.py**

**What it does:**
- Fast structure analysis
- Basic metrics collection  
- JSON report generation
- Health status overview

**Output:**
```json
{
  "total_files": 8,
  "valid_files": 8,
  "test_methods": 95,
  "coverage": "94%",
  "status": "excellent"
}
```

### **🚀 run_final_integration_tests.py**

**What it does:**
- Executes all integration tests
- Collects execution results
- Generates comprehensive report
- Provides success/failure analysis

**Output:**
```
🧪 Test execution results
📊 Pass/fail statistics
⏱️ Execution times
📝 Detailed error reports (if any)
```

---

## 🎯 **Common Usage Patterns**

### **🔍 Daily Development**
```bash
# Quick health check
python scripts/validation/quick_test_analysis.py

# If issues found, validate structure
python scripts/validation/validate_integration_tests.py
```

### **📊 Before Release**
```bash
# Full coverage analysis
python scripts/validation/analyze_test_coverage.py

# Complete test execution
python scripts/validation/run_final_integration_tests.py
```

### **🐛 Troubleshooting**
```bash
# Check environment
python scripts/infrastructure/test_integration_health.py

# Validate imports
python scripts/infrastructure/test_imports_integration.py

# Basic infrastructure
python scripts/infrastructure/test_basic_infrastructure.py
```

### **📈 Coverage Improvement**
```bash
# Analyze current coverage
python scripts/validation/analyze_test_coverage.py

# Check structure after changes
python scripts/validation/validate_integration_tests.py

# Verify improvements
python scripts/validation/run_final_integration_tests.py
```

---

## ⚙️ **Script Requirements**

### **🐍 Python Environment**
```bash
# Ensure Python 3.7+ is available
python --version

# Install requirements
pip install -r requirements.txt
```

### **📦 Required Packages**
- `coverage` - For coverage analysis
- `pytest` - For test execution  
- `json` - For structured output
- Standard library modules

### **📁 Working Directory**
All scripts should be run from the project root:
```bash
cd /path/to/2025-1-GovInsights/
python test_analysis/scripts/validation/script_name.py
```

---

## 🚨 **Troubleshooting**

### **❌ Common Issues**

#### **ImportError: No module named 'src'**
```bash
# Solution: Run from project root
cd /path/to/2025-1-GovInsights/
python test_analysis/scripts/validation/script_name.py
```

#### **Coverage not found**
```bash
# Solution: Install coverage
pip install coverage
```

#### **Tests fail to run**
```bash
# Solution: Check environment
python test_analysis/scripts/infrastructure/test_integration_health.py
```

#### **Permission denied**
```bash
# Solution: Check file permissions
chmod +x test_analysis/scripts/validation/*.py
```

---

## 📊 **Output Formats**

### **Console Output**
- Real-time progress indicators
- Color-coded results (when supported)
- Summary statistics
- Immediate feedback

### **JSON Reports**
- Structured data in `data/json_reports/`
- Machine-readable results
- Perfect for automation
- Consistent format

### **Text Reports**
- Human-readable in `data/coverage/`
- Detailed explanations
- Copy-paste friendly
- Archive-suitable

---

*Use these scripts efficiently to maintain excellent test quality! 🎯*
