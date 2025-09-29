import json
import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple

from openai import AzureOpenAI

# AutoHealer functionality used indirectly through captured failures file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-3.5-turbo")


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
            api_key=OPENAI_API_KEY, api_version="2024-05-01-preview", azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI client: {e}")
        return None


client = get_openai_client()


class LocatorFailure:
    """Represents a locator failure extracted from test results."""

    def __init__(
        self,
        test_name: str,
        file_path: str,
        line_number: int,
        failing_locator: str,
        error_message: str,
        element_description: str = "",
    ):
        self.test_name = test_name
        self.file_path = file_path
        self.line_number = line_number
        self.failing_locator = failing_locator
        self.error_message = error_message
        self.element_description = element_description
        self.suggested_locator: Optional[str] = None


def parse_locator_failures_from_test_results(test_data: dict) -> List[LocatorFailure]:
    """
    Parse test failure logs to extract failing locators and their locations.

    Returns:
        List of LocatorFailure objects containing failing locator info
    """
    failures: List[LocatorFailure] = []

    # Handle pytest-json-report format
    if "tests" in test_data:
        failed_tests = [test for test in test_data["tests"] if test.get("outcome") == "failed"]
    else:
        return failures

    for test in failed_tests:
        test_name = test.get("nodeid", "unknown_test")
        failure_log = test.get("longrepr", "") or str(test.get("call", {}).get("longrepr", ""))

        # Extract locator failures from the error message
        locator_failures = extract_locator_info_from_error(test_name, failure_log)
        failures.extend(locator_failures)

    return failures


def extract_locator_info_from_error(test_name: str, error_log: str) -> List[LocatorFailure]:
    """
    Extract locator information from test error logs.

    Patterns to look for:
    - Playwright locator errors with file/line info
    - Element not found errors
    - Timeout waiting for locator errors
    """
    failures: List[LocatorFailure] = []

    # Common patterns for locator failures
    locator_patterns = [
        # Playwright timeout errors: "Locator.click: Timeout 30000ms exceeded."
        r'Locator\.(click|fill|hover|wait_for).*?Timeout.*?exceeded.*?locator\("([^"]+)"\)',
        # Element not found errors with locators
        r'Element.*?not found.*?locator[:\s]+"([^"]+)"',
        r'could not find element.*?locator[:\s]+"([^"]+)"',
        # Playwright strict mode violations
        r'strict mode violation.*?locator\("([^"]+)"\)',
        # General locator method calls in stack traces
        r'page\.locator\("([^"]+)"\)',
        r'\.locator\("([^"]+)"\)',
    ]

    # File path and line number patterns from stack traces
    file_line_patterns = [
        r"([A-Za-z]:[^:]+\.py):(\d+):.*",  # Windows paths
        r"(/[^:]+\.py):(\d+):.*",  # Unix paths
        r'File "([^"]+\.py)", line (\d+)',  # Python traceback format
    ]

    for pattern in locator_patterns:
        matches = re.finditer(pattern, error_log, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            locator = match.group(-1)  # Last group is usually the locator

            # Find file path and line number near this match
            file_path, line_num = find_file_line_in_context(error_log, match.start())

            if file_path and line_num:
                # Extract element description if available
                description = extract_element_description(error_log, locator)

                failure = LocatorFailure(
                    test_name=test_name,
                    file_path=file_path,
                    line_number=line_num,
                    failing_locator=locator,
                    error_message=error_log[:500],  # First 500 chars
                    element_description=description,
                )
                failures.append(failure)

    return failures


def find_file_line_in_context(text: str, position: int) -> Tuple[Optional[str], Optional[int]]:
    """Find file path and line number near a specific position in error text."""

    # Look in a window around the position
    start = max(0, position - 500)
    end = min(len(text), position + 500)
    context = text[start:end]

    file_line_patterns = [
        r"([A-Za-z]:[^:\s]+\.py):(\d+)",  # Windows paths
        r"(/[^:\s]+\.py):(\d+)",  # Unix paths
        r'File "([^"]+\.py)", line (\d+)',  # Python traceback format
    ]

    for pattern in file_line_patterns:
        match = re.search(pattern, context)
        if match:
            file_path = match.group(1).strip('"')
            line_num = int(match.group(2))

            # Filter for test files only
            if any(test_dir in file_path for test_dir in ["test_", "tests/", "SRC/tests"]):
                return file_path, line_num

    return None, None


def extract_element_description(error_log: str, locator: str) -> str:
    """Extract element description from error context."""

    # Look for common description patterns near the locator
    description_patterns = [
        rf"# ([^\\n]+).*?{re.escape(locator)}",  # Comments above locator
        rf"{re.escape(locator)}.*?# ([^\\n]+)",  # Comments after locator
        rf'get.*?element.*?"([^"]+)".*?{re.escape(locator)}',  # get_element calls
        rf'{re.escape(locator)}.*?element.*?"([^"]+)"',
    ]

    for pattern in description_patterns:
        match = re.search(pattern, error_log, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return "element"


def get_relative_path(file_path: str) -> str:
    """Convert absolute path to relative path for git operations."""
    if not os.path.isabs(file_path):
        return file_path

    path_parts = file_path.replace("\\", "/").split("/")
    known_dirs = ["SRC", "Utilities", "TestDataCommon"]
    for i, part in enumerate(path_parts):
        if part in known_dirs:
            return "/".join(path_parts[i:])

    return file_path  # Return original if no known directory found


def create_locator_fix_patch(failure: LocatorFailure, new_locator: str) -> str:
    """
    Create a targeted patch that replaces the old locator with the new one
    at the specific file location.
    """
    try:
        # Convert absolute path to relative path for git patch
        relative_path = get_relative_path(failure.file_path)
        print(f"🔧 Using relative path for patch: {relative_path}")

        # Read the target file - use relative path for reading if absolute path doesn't work
        file_to_read = failure.file_path if os.path.exists(failure.file_path) else relative_path
        with open(file_to_read, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if failure.line_number > len(lines):
            print(f"❌ Line number {failure.line_number} exceeds file length")
            return ""

        # First try the specific line number
        line_index = failure.line_number - 1  # Convert to 0-based index
        original_line = lines[line_index]
        modified_line = original_line.replace(f'"{failure.failing_locator}"', f'"{new_locator}"')

        # If double quotes didn't work, try single quotes
        if modified_line == original_line:
            modified_line = original_line.replace(f"'{failure.failing_locator}'", f"'{new_locator}'")

        # If locator not found on specific line, search the entire file
        if modified_line == original_line:
            print(f"⚠️  Locator '{failure.failing_locator}' not found on line {failure.line_number}")
            print("🔍 Searching entire file for the locator...")

            # Search for the locator in the entire file using the refined logic
            found_line_index = None
            for i, line in enumerate(lines):
                # Use same logic as auto_healer.py for consistency
                if failure.failing_locator in line and "=" in line:
                    equals_pos = line.find("=")
                    locator_pos = line.find(failure.failing_locator)

                    # Ensure = comes before the locator and it's in quotes
                    if equals_pos < locator_pos and (
                        f'"{failure.failing_locator}"' in line or f"'{failure.failing_locator}'" in line
                    ):
                        # Additional validation: look for locator-like variable names
                        left_side = line[:equals_pos].strip()
                        if any(
                            pattern in left_side.lower()
                            for pattern in ["loc", "_input", "_button", "_field", "_element", "_selector"]
                        ) and not left_side.startswith(("self.", "page.", "(", "[")):

                            found_line_index = i
                            original_line = line
                            modified_line = line.replace(f'"{failure.failing_locator}"', f'"{new_locator}"')
                            if modified_line == original_line:
                                modified_line = line.replace(f"'{failure.failing_locator}'", f"'{new_locator}'")

                            if modified_line != original_line:
                                print(f"✅ Found locator on line {i + 1}: {line.strip()}")
                                failure.line_number = i + 1  # Update the line number
                                break

            if found_line_index is None:
                print(f"❌ Could not find locator '{failure.failing_locator}' anywhere in the file")
                return ""

        # Create unified diff patch using relative path
        patch = f"""--- a/{relative_path}
+++ b/{relative_path}
@@ -{failure.line_number},1 +{failure.line_number},1 @@
-{original_line.rstrip()}
+{modified_line.rstrip()}
"""

        return patch

    except Exception as e:
        print(f"❌ Error creating patch: {str(e)}")
        return ""


def apply_locator_fix_directly(failure: LocatorFailure) -> bool:
    """
    Apply the locator fix directly to the file.
    This approach works with peter-evans/create-pull-request GitHub Action.
    """
    if not failure.suggested_locator:
        print(f"❌ No suggested locator available for {failure.test_name}")
        return False

    try:
        # Get the file path to modify
        relative_path = get_relative_path(failure.file_path)
        file_to_edit = failure.file_path if os.path.exists(failure.file_path) else relative_path

        print(f"🔧 Applying locator fix to: {file_to_edit}")
        print(f"   Old locator: {failure.failing_locator}")
        print(f"   New locator: {failure.suggested_locator}")

        # Read the file
        with open(file_to_edit, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if failure.line_number > len(lines):
            print(f"❌ Line number {failure.line_number} exceeds file length")
            return False

        # Show current file content around the target line for debugging
        print(f"📋 Current file content around line {failure.line_number}:")
        start_line = max(0, failure.line_number - 3)
        end_line = min(len(lines), failure.line_number + 2)

        for i in range(start_line, end_line):
            marker = ">>> " if i + 1 == failure.line_number else "    "
            print(f"{marker}{i+1:3}: {lines[i].rstrip()}")

        # Try to find and replace the locator
        modified = False
        line_index = failure.line_number - 1  # Convert to 0-based index
        original_line = lines[line_index]

        # Try replacing with double quotes first
        if f'"{failure.failing_locator}"' in original_line:
            lines[line_index] = original_line.replace(f'"{failure.failing_locator}"', f'"{failure.suggested_locator}"')
            modified = True
        # Try single quotes
        elif f"'{failure.failing_locator}'" in original_line:
            lines[line_index] = original_line.replace(f"'{failure.failing_locator}'", f"'{failure.suggested_locator}'")
            modified = True
        else:
            # Search the entire file if not found on specific line
            print(f"⚠️ Locator not found on line {failure.line_number}, searching entire file...")
            for i, line in enumerate(lines):
                if failure.failing_locator in line and "=" in line:
                    equals_pos = line.find("=")
                    locator_pos = line.find(failure.failing_locator)

                    # Ensure = comes before the locator and it's in quotes
                    if equals_pos < locator_pos and (
                        f'"{failure.failing_locator}"' in line or f"'{failure.failing_locator}'" in line
                    ):
                        # Additional validation: look for locator-like variable names
                        left_side = line[:equals_pos].strip()
                        if any(
                            pattern in left_side.lower()
                            for pattern in ["loc", "_input", "_button", "_field", "_element", "_selector"]
                        ) and not left_side.startswith(("self.", "page.", "(", "[")):

                            if f'"{failure.failing_locator}"' in line:
                                lines[i] = line.replace(
                                    f'"{failure.failing_locator}"', f'"{failure.suggested_locator}"'
                                )
                            else:
                                lines[i] = line.replace(
                                    f"'{failure.failing_locator}'", f"'{failure.suggested_locator}'"
                                )

                            print(f"✅ Found and replaced locator on line {i + 1}")
                            failure.line_number = i + 1  # Update line number for logging
                            modified = True
                            break

        if not modified:
            print(f"❌ Could not find locator '{failure.failing_locator}' in file")
            return False

        # Write the modified content back to file
        with open(file_to_edit, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Successfully applied locator fix to {file_to_edit}")
        return True

    except Exception as e:
        print(f"❌ Error applying locator fix: {str(e)}")
        return False


# Note: Manual review PR functionality removed as we now focus on targeted locator fixes


def process_failures():
    """Process captured locator failures and create targeted PR fixes."""

    # Check for captured failures file (created by auto_healer.py during test execution)
    captured_failures_file = "reports/captured_locator_failures.json"

    if not os.path.exists(captured_failures_file):
        print(f"❌ No captured locator failures found at: {captured_failures_file}")
        print("ℹ️  This file is created by auto_healer.py when running in GitHub Actions")
        return

    print(f"📖 Reading captured locator failures from: {captured_failures_file}")

    try:
        with open(captured_failures_file) as f:
            captured_failures = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {captured_failures_file}: {e}")
        return
    except Exception as e:
        print(f"❌ Error reading {captured_failures_file}: {e}")
        return

    if not captured_failures:
        print("✅ No captured locator failures found. Nothing to heal.")
        return

    print(f"🎯 Found {len(captured_failures)} captured locator failures to process")
    healed_count = 0

    for captured_failure in captured_failures:
        try:
            # Convert captured failure to LocatorFailure object
            failure = LocatorFailure(
                test_name=f"captured_from_{os.path.basename(captured_failure.get('test_file', 'unknown'))}",
                file_path=captured_failure.get("test_file", ""),
                line_number=captured_failure.get("line_number", 0),
                failing_locator=captured_failure.get("failing_locator", ""),
                error_message=captured_failure.get("error_message", ""),
                element_description=captured_failure.get("element_description", "element"),
            )

            # Use the already-captured AI suggestion
            failure.suggested_locator = captured_failure.get("suggested_locator")

            print(f"\n🔧 Processing captured locator failure:")
            print(f"   📁 File: {failure.file_path}:{failure.line_number}")
            print(f"   🎯 Failed Locator: {failure.failing_locator}")
            print(f"   💡 AI Suggested: {failure.suggested_locator}")
            print(f"   📝 Element: {failure.element_description}")

            if failure.suggested_locator:
                # Apply locator fix directly (PR will be created by GitHub Action)
                success = apply_locator_fix_directly(failure)

                if success:
                    healed_count += 1
                    print(f"✅ Locator fix applied: {failure.file_path}")
                else:
                    print(f"❌ Failed to apply fix for {failure.file_path}")
            else:
                print(f"⚠️ No AI suggestion available - skipping")

        except Exception as e:
            print(f"❌ Error processing captured failure: {str(e)}")
            import traceback

            print(f"Detailed error: {traceback.format_exc()}")
            continue

    print(
        f"\n🎉 AutoHeal Summary: Created {healed_count} locator fix PR(s) out of {len(captured_failures)} captured failures"
    )

    # Keep the captured failures file as artifact for debugging - DO NOT delete
    print(f"📁 Captured failures file preserved for artifact upload: {captured_failures_file}")


if __name__ == "__main__":
    print("🚀 Starting AutoHeal Agent...")
    process_failures()
