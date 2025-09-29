import json
import os
import subprocess

from openai import AzureOpenAI
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-3.5-turbo")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
BASE_BRANCH = os.getenv("GITHUB_REF_NAME", "main")
BRANCH_PREFIX = "autoheal/"

# Initialize Azure OpenAI client with validation
def get_openai_client():
    """Initialize and return Azure OpenAI client with proper validation."""
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return None
    if not AZURE_OPENAI_ENDPOINT:
        print("❌ AZURE_OPENAI_ENDPOINT not found in environment variables")
        return None
        
    try:
        return AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version="2024-05-01-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI client: {e}")
        return None

client = get_openai_client()


def ai_autoheal_failure(test_name, failure_log, dom_snapshot=""):
    prompt = f"""
    Test case: {test_name}
    Failure log: {failure_log}
    DOM snapshot (truncated): {dom_snapshot}

    Suggest a corrected locator or test update (minimal change).
    Provide explanation, confidence score, and a patch (unified diff).
    Return JSON with: issue_type, confidence, explanation, patch
    """
    # Check if client is available
    if not client:
        print("❌ Azure OpenAI client not available")
        return {
            "issue_type": "client_error",
            "confidence": 0.0,
            "explanation": "Azure OpenAI client not properly initialized",
            "patch": "",
        }
    
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are a QA automation repair assistant. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        content = response.choices[0].message.content
        # Try to parse JSON, handle cases where response might not be pure JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Extract JSON if it's embedded in markdown or other text
            import re

            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback response if no valid JSON found
                return {
                    "issue_type": "parsing_error",
                    "confidence": 0.0,
                    "explanation": f"Could not parse AI response: {content}",
                    "patch": "",
                }
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {str(e)}")
        return {"issue_type": "api_error", "confidence": 0.0, "explanation": f"API error: {str(e)}", "patch": ""}


def apply_patch_and_pr(test_name, patch, explanation, confidence):
    """Apply patch and create PR with error handling."""
    if not patch or not patch.strip():
        print(f"❌ Empty patch for {test_name}, skipping PR creation")
        return None

    try:
        # Validate required environment variables
        if not GITHUB_TOKEN:
            print("❌ GITHUB_TOKEN not found in environment")
            return None
        if not REPO_NAME:
            print("❌ GITHUB_REPOSITORY not found in environment")
            return None

        branch_name = f"{BRANCH_PREFIX}{test_name.replace('/', '_').replace('::', '_')}_{os.urandom(4).hex()}"
        patch_file = "autoheal.patch"

        # Write and apply patch
        with open(patch_file, "w") as f:
            f.write(patch)

        # Apply patch with error handling
        result = subprocess.run(["git", "apply", "--check", patch_file], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"❌ Patch validation failed for {test_name}: {result.stderr}")
            return None

        subprocess.run(["git", "apply", patch_file], check=True)
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"🔧 AutoHeal: Fix for {test_name}\n\nConfidence: {confidence}\n{explanation}"],
            check=True,
        )
        subprocess.run(["git", "push", "origin", branch_name], check=True)

        # Create PR
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(REPO_NAME)

        pr_body = f"""## 🤖 AutoHeal Fix

**Test Case:** `{test_name}`
**Confidence:** {confidence:.2f}

### 📝 Explanation
{explanation}

### 🔧 Changes Applied
```diff
{patch}
```

---
*This PR was automatically created by AutoHeal based on test failure analysis.*
"""

        pr = repo.create_pull(
            title=f"🔧 AutoHeal: Fix for {test_name}",
            body=pr_body,
            head=branch_name,
            base=BASE_BRANCH,
        )

        # Add labels
        try:
            pr.add_to_labels("autoheal", "automated-fix", "needs-review")
        except Exception as e:
            print(f"⚠️ Could not add labels to PR: {e}")

        print(f"✅ AutoHeal PR created for {test_name}: {pr.html_url}")
        return pr.html_url

    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed for {test_name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Failed to create PR for {test_name}: {e}")
        return None
    finally:
        # Cleanup
        if os.path.exists("autoheal.patch"):
            os.remove("autoheal.patch")


def create_manual_review_pr(test_name, failure_log, patch_content):
    """Create a PR for manual review when AI is not available."""
    try:
        # Validate required environment variables
        if not GITHUB_TOKEN or not REPO_NAME:
            print("❌ GitHub configuration not available for manual PR creation")
            return None
            
        branch_name = f"{BRANCH_PREFIX}manual-review_{test_name.replace('/', '_').replace('::', '_')}_{os.urandom(4).hex()}"
        
        # Create manual review file
        review_file = f"MANUAL_REVIEW_{test_name.replace('/', '_').replace('::', '_')}.md"
        with open(review_file, "w") as f:
            f.write(patch_content)
            
        # Git operations
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        subprocess.run(["git", "add", review_file], check=True)
        subprocess.run(["git", "commit", "-m", f"📋 Manual Review: {test_name}\n\nTest failure requires manual investigation"], check=True)
        subprocess.run(["git", "push", "origin", branch_name], check=True)

        # Create PR
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(REPO_NAME)
        
        pr_body = f"""## 📋 Manual Review Required

**Test Case:** `{test_name}`
**Status:** Failed - AI AutoHeal not available

### 🔍 Failure Details
```
{failure_log[:1500]}
```

### 🛠️ Action Required
1. **Investigate** the test failure manually
2. **Check** if locators need updating
3. **Verify** test logic and data
4. **Apply** necessary fixes
5. **Close** this PR after resolution

### 📝 Notes
- AutoHeal AI was not available during execution
- This PR is for tracking and manual investigation
- The failure may be due to locator changes, test data issues, or application changes

---
*This PR was created automatically for manual investigation of test failures.*
"""
        
        pr = repo.create_pull(
            title=f"📋 Manual Review: {test_name}",
            body=pr_body,
            head=branch_name,
            base=BASE_BRANCH,
        )
        
        # Add labels
        try:
            pr.add_to_labels("manual-review", "test-failure", "needs-investigation")
        except Exception as e:
            print(f"⚠️ Could not add labels to manual review PR: {e}")
            
        # Clean up review file
        if os.path.exists(review_file):
            os.remove(review_file)
            
        return pr.html_url
        
    except Exception as e:
        print(f"❌ Failed to create manual review PR for {test_name}: {e}")
        return None


def process_failures():
    """Process test failures and create AutoHeal PRs."""

    # Check for test results file (pytest-json-report format)
    test_files = ["test-results.json", "failures.json", ".pytest_cache/failures.json"]
    test_file = None

    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break

    if not test_file:
        print("❌ No test results file found. Checked:", ", ".join(test_files))
        return

    print(f"📖 Reading test results from: {test_file}")

    try:
        with open(test_file) as f:
            test_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {test_file}: {e}")
        return
    except Exception as e:
        print(f"❌ Error reading {test_file}: {e}")
        return

    # Handle different JSON formats
    failed_tests = []

    # pytest-json-report format
    if "tests" in test_data:
        failed_tests = [test for test in test_data["tests"] if test.get("outcome") == "failed"]
    # Custom failures.json format
    elif "tests" in test_data:
        failed_tests = test_data.get("tests", [])
    else:
        print("❌ Unrecognized test results format")
        return

    if not failed_tests:
        print("✅ No failed tests found. Nothing to heal.")
        return

    print(f"🔍 Found {len(failed_tests)} failed tests to analyze")
    healed_count = 0

    for failure in failed_tests:
        try:
            # Extract test information
            test_name = failure.get("nodeid") or failure.get("name", "unknown_test")
            failure_log = failure.get("longrepr") or failure.get("call", {}).get("longrepr", "No failure details")

            print(f"\n🔧 Processing: {test_name}")

            # Get DOM snapshot if available (from auto_healer reports)
            dom_snapshot = ""
            if os.path.exists("reports"):
                # Look for DOM snapshots related to this test
                import glob

                snapshots = glob.glob(f"reports/dom_snapshot_*_{test_name.replace('::', '_')}*.html")
                if snapshots:
                    try:
                        with open(snapshots[0], "r", encoding="utf-8") as f:
                            dom_snapshot = f.read()[:2000]  # Truncate for API
                    except Exception:
                        pass

            # Get AI healing suggestion
            healing = ai_autoheal_failure(test_name, failure_log, dom_snapshot)

            if healing.get("confidence", 0) >= 0.7:
                print(f"✅ High confidence fix found (confidence: {healing['confidence']:.2f})")
                pr_url = apply_patch_and_pr(test_name, healing["patch"], healing["explanation"], healing["confidence"])
                if pr_url:
                    healed_count += 1
            elif healing.get("issue_type") in ["client_error", "api_error"]:
                print(f"⚠️ API issue detected - creating manual review PR for {test_name}")
                # Create a PR with failure information for manual review
                manual_patch = f"""# Manual Review Required for Test: {test_name}

## Test Failure Details:
{failure_log[:1000]}...

## Notes:
- AutoHeal AI was not available
- Manual investigation required
- Check locators and test logic
"""
                manual_pr_url = create_manual_review_pr(test_name, failure_log, manual_patch)
                if manual_pr_url:
                    print(f"📋 Manual review PR created: {manual_pr_url}")
            else:
                print(f"⚠️ Skipping {test_name} (low confidence: {healing.get('confidence', 0):.2f})")

        except Exception as e:
            print(f"❌ Error processing {test_name}: {e}")
            continue

    print(f"\n🎉 AutoHeal Summary: Created {healed_count} PR(s) out of {len(failed_tests)} failed tests")


if __name__ == "__main__":
    print("🚀 Starting AutoHeal Agent...")
    process_failures()
