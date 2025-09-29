import json
import os
import subprocess

import openai
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
BASE_BRANCH = os.getenv("GITHUB_REF_NAME", "main")
BRANCH_PREFIX = "autoheal/"

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def ai_autoheal_failure(test_name, failure_log, dom_snapshot=""):
    prompt = f"""
    Test case: {test_name}
    Failure log: {failure_log}
    DOM snapshot (truncated): {dom_snapshot}

    Suggest a corrected locator or test update (minimal change).
    Provide explanation, confidence score, and a patch (unified diff).
    Return JSON with: issue_type, confidence, explanation, patch
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
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
        result = subprocess.run(["git", "apply", "--check", patch_file], capture_output=True, text=True)
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
            else:
                print(f"⚠️ Skipping {test_name} (low confidence: {healing.get('confidence', 0):.2f})")

        except Exception as e:
            print(f"❌ Error processing {test_name}: {e}")
            continue

    print(f"\n🎉 AutoHeal Summary: Created {healed_count} PR(s) out of {len(failed_tests)} failed tests")


if __name__ == "__main__":
    print("🚀 Starting AutoHeal Agent...")
    process_failures()
