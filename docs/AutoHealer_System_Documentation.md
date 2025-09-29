# AutoHealer System Flow - Technical Documentation

## **System Overview**
AI-powered locator healing system that captures test failures, generates smart fixes, and creates GitHub PRs for review.

---

## **📋 Core Components**

### **1. `auto_healer.py` - Runtime Failure Detection**

#### **Primary Functions:**
- **`getElement(locator, description)`** - Main entry point for element location with healing
- **`_capture_locator_failure(locator, description, error_message)`** - Captures failures in GitHub Actions mode
- **`_attempt_ai_healing(original_locator, description, error_message)`** - Local healing attempts
- **`_get_ai_suggestion_for_capture(locator, description, error_message)`** - Gets AI suggestions for captured failures

#### **Failure Detection Functions:**
- **`_find_locator_source(locator)`** - Locates where the failing locator is defined in code
- **`_find_locator_definition_file(locator)`** - Searches codebase for locator declarations
- **`_is_locator_definition_line(line, locator)`** - Validates if a line contains the target locator
- **`_create_failure_record(locator, description, error_message, ai_suggestion, test_file, test_line)`** - Creates structured failure data

#### **Data Persistence Functions:**
- **`_save_captured_failure(failure_record)`** - Saves failure to JSON file
- **`_save_failure_with_retry(failures_file, failure_record)`** - Handles concurrent write operations
- **`_is_duplicate_failure(failure_record, existing_failures)`** - Prevents duplicate entries

---

### **2. `autoheal_agent.py` - Post-Test PR Creation**

#### **Main Processing Functions:**
- **`process_failures()`** - Main orchestrator that processes all captured failures
- **`apply_locator_fix_directly(failure)`** - Applies locator changes directly to files

#### **AI Integration Functions:**
- **`get_openai_client()`** - Initializes Azure OpenAI client with validation

#### **Code Modification Functions:**
- **`get_relative_path(file_path)`** - Converts absolute paths for file operations

#### **Legacy Processing Functions (Optional):**
- **`parse_locator_failures_from_test_results(test_data)`** - Parses pytest JSON reports
- **`extract_locator_info_from_error(test_name, error_log)`** - Extracts locator info from stack traces
- **`find_file_line_in_context(text, position)`** - Locates file/line from error context

---

### **3. `MasterPipeline_autoHeal.yml` - CI/CD Integration**

#### **Key Pipeline Steps:**
1. **Test Execution** - Runs with `GITHUB_ACTIONS=true` to enable capture mode
2. **Auto-healing Trigger** - `if: env.TEST_FAILED == '1'` activates healing
3. **Agent Execution** - `python Utilities/TestUtils/autoheal_agent.py` applies fixes directly
4. **PR Creation** - `peter-evans/create-pull-request@v6` handles Git operations and PR creation
5. **Artifact Upload** - Preserves `captured_locator_failures.json` and DOM snapshots

---

## **🔄 Detailed Flow**

### **Phase 1: Test Execution (GitHub Actions)**

```python
# auto_healer.py
AutoHealer.__init__(page)  # Sets capture_mode = True in GitHub Actions

getElement(locator, description):
  ├── page.locator(locator)  # Try original locator
  ├── if failure → _capture_locator_failure()
  │   ├── _find_locator_source()  # Find where locator is defined
  │   ├── _get_ai_suggestion_for_capture()  # Get AI alternative
  │   ├── _create_failure_record()  # Structure the data
  │   └── _save_captured_failure()  # Save to JSON
  └── return None  # Let test fail naturally
```

### **Phase 2: Post-Test Healing (CI Pipeline)**

```python
# autoheal_agent.py
process_failures():
  ├── Load captured_locator_failures.json
  ├── For each failure:
  │   ├── Create LocatorFailure object
  │   └── apply_locator_fix_directly():
  │       ├── Read target file
  │       ├── Find and replace locator
  │       └── Write modified file back
  └── Summary report

# GitHub Action (peter-evans/create-pull-request)
create-pull-request@v6:
  ├── Detect file changes
  ├── Create branch: autoheal/locator-fixes-{run_id}
  ├── Commit changes
  ├── Push branch
  └── Open PR with labels and description
```

### **Phase 3: File Modification Logic**

```python
apply_locator_fix_directly(failure):
  ├── get_relative_path()  # Convert to project-relative path
  ├── Read target file lines
  ├── Show current content around target line for debugging
  ├── Try specific line replacement (double/single quotes)
  ├── If not found → search entire file with validation:
  │   ├── Check for locator assignment patterns
  │   ├── Validate variable naming conventions
  │   └── Ensure proper quote handling
  ├── Apply replacement: "old_locator" → "new_locator"
  └── Write modified content back to file
```

---

## **🎯 Key Integration Points**

### **Environment Detection**
```python
# auto_healer.py line 59
self.capture_mode = os.getenv("GITHUB_ACTIONS") == "true"
```

### **Failure Data Structure**
```json
{
  "timestamp": "2025-09-29 19:44:19",
  "test_file": "SRC/pages/login_page.py", 
  "line_number": 15,
  "failing_locator": "#old-login-btn",
  "suggested_locator": "[data-testid='login-button']",
  "element_description": "login button",
  "error_message": "Element not found: #old-login-btn"
}
```

### **PR Creation Template**
- **Title**: `🔧 Fix locator in {test_name}`
- **Labels**: `autoheal`, `locator-fix`, `ai-suggested`, `needs-testing`
- **Branch**: `autoheal/locator-fix_{test_name}_{random_hex}`

---

## **🚀 Usage Guide**

### **Local Development Mode**
When running tests locally (not in GitHub Actions):
- AutoHealer attempts real-time healing during test execution
- Uses `_attempt_ai_healing()` to fix locators on the fly
- Provides immediate feedback to developers

### **CI/CD Mode (GitHub Actions)**
When `GITHUB_ACTIONS=true`:
- AutoHealer captures failures without interrupting tests
- Saves all failure data to `reports/captured_locator_failures.json`
- Post-test agent processes failures and creates PRs

### **Configuration Requirements**

#### **Environment Variables:**
```bash
# Required for AI functionality
OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Required for GitHub integration
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=owner/repo-name
```

#### **Dependencies:**
```bash
pip install openai playwright PyGithub
```

---

## **🔧 Technical Implementation Details**

### **Locator Detection Algorithm**
The system identifies locator definitions using sophisticated pattern matching:

```python
def apply_locator_fix_directly(failure):
    # Multi-step locator detection and replacement:
    # 1. Try exact line match with proper quote handling
    # 2. Full file search with assignment pattern validation
    # 3. Variable naming convention checks (loc, _button, _field, etc.)
    # 4. Prevents false matches in method calls or comments
    
    # Enhanced quote handling for both single and double quotes
    if f'"{failure.failing_locator}"' in line:
        lines[i] = line.replace(f'"{failure.failing_locator}"', f'"{failure.suggested_locator}"')
    else:
        lines[i] = line.replace(f"'{failure.failing_locator}'", f"'{failure.suggested_locator}'")
```

### **AI Prompt Engineering**
Uses carefully crafted prompts that prioritize:
1. **Test IDs and Data Attributes** - `[data-testid='submit-btn']`
2. **Semantic HTML attributes** - `[aria-label='Submit form']`
3. **ID and Name attributes** - `#submit-button`
4. **Class-based selectors** - `.submit-btn.primary`

### **Error Handling & Resilience**
- **File write operations** handled with proper encoding and error reporting  
- **Line number validation** ensures target line exists before modification
- **Multi-quote support** handles both single and double quote scenarios
- **Fallback search** performs full-file scan when specific line fails
- **Duplicate detection** prevents redundant fixes for same failure
- **Graceful failure** provides detailed error messages and debugging info

---

## **📊 Benefits & Metrics**

### **Key Benefits**
- **Zero test interruption** - Failures captured, not fixed during execution
- **Human oversight** - All AI suggestions require PR review
- **Precise targeting** - Fixes exact locator at specific line
- **Zero false positives** - Only creates PRs for actual locator failures

### **Success Metrics**
- **Reduced maintenance time** - Automated locator fix suggestions
- **Improved test stability** - AI-powered locator recommendations
- **Better team collaboration** - Clear PR descriptions with context
- **Audit trail** - Complete history of all locator changes

---

## **🔍 Troubleshooting**

### **Common Issues & Solutions**

#### **No captured failures generated:**
- Verify `GITHUB_ACTIONS=true` environment variable
- Check that tests are actually failing with locator issues
- Ensure `reports/` directory is writable

#### **PR creation fails:**
- Validate GitHub token permissions (needs `contents: write`)
- Check `peter-evans/create-pull-request@v6` action configuration
- Verify repository settings allow PR creation

#### **File modification fails:**
- Check file permissions and encoding (UTF-8 expected)
- Verify target file exists and is accessible
- Ensure locator patterns match expected variable naming conventions
- Review debug output showing file content around target line

---

## **🔄 Maintenance & Updates**

### **Regular Maintenance Tasks**
1. **Monitor AI suggestion quality** - Review merged PRs for accuracy
2. **Update locator patterns** - Add new patterns to detection algorithms
3. **Refine prompts** - Improve AI suggestions based on usage patterns
4. **Clean up old branches** - Remove merged autoheal branches periodically

### **System Updates**
- **OpenAI model updates** - Test with new model versions
- **Playwright changes** - Adapt to new locator methods  
- **GitHub Actions updates** - Keep `peter-evans/create-pull-request` action current
- **Code formatting** - Maintain consistent style and readability standards

### **Implementation Notes**
- **Simplified Architecture** - Direct file modification approach eliminates Git patch complexity
- **Enhanced Debugging** - Detailed logging shows file content and replacement operations
- **Improved Reliability** - Robust quote handling and fallback search mechanisms
- **Clean Code** - Consistent formatting and proper error handling throughout

This system ensures **intelligent automation** for test maintenance while maintaining **complete human control** over all changes through the PR review process.
