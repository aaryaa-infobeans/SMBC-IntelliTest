#!/usr/bin/env python3
"""
Script to prepare email HTML body by replacing placeholders with actual values from GitHub Actions.
"""
import os
import sys
from pathlib import Path


def calculate_percentages(total, passed, failed, skipped):
    """Calculate percentage values for test results."""
    if total == 0:
        return "0", "0", "0", "0"
    
    passed_percent = round((passed / total) * 100, 1)
    failed_percent = round((failed / total) * 100, 1)
    skipped_percent = round((skipped / total) * 100, 1)
    
    return str(passed_percent), str(failed_percent), str(skipped_percent), str(passed_percent)


def replace_placeholders(template_path, output_path, replacements):
    """Replace placeholders in the template with actual values."""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for placeholder, value in replacements.items():
        content = content.replace(f"{{{{{placeholder}}}}}", str(value))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Email body prepared and saved to {output_path}")


def safe_int(value, default=0):
    """Safely convert a value to int, handling empty strings and None."""
    if not value or value.strip() == '':
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def main():
    # Get values from environment variables
    github_actor = os.environ.get('GITHUB_ACTOR', 'Unknown')
    test_result = os.environ.get('TEST_RESULT', 'Unknown')
    github_ref = os.environ.get('GITHUB_REF', 'Unknown')
    total_tests = safe_int(os.environ.get('TOTAL_TESTS', '0'))
    passed_tests = safe_int(os.environ.get('PASSED_TESTS', '0'))
    failed_tests = safe_int(os.environ.get('FAILED_TESTS', '0'))
    skipped_tests = safe_int(os.environ.get('SKIPPED_TESTS', '0'))
    github_repository = os.environ.get('GITHUB_REPOSITORY', 'Unknown')
    github_workflow = os.environ.get('GITHUB_WORKFLOW', 'Unknown')
    github_run_number = os.environ.get('GITHUB_RUN_NUMBER', 'Unknown')
    github_run_id = os.environ.get('GITHUB_RUN_ID', 'Unknown')
    github_server_url = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
    
    # Calculate percentages
    passed_percent, failed_percent, skipped_percent, success_rate = calculate_percentages(
        total_tests, passed_tests, failed_tests, skipped_tests
    )
    
    # Prepare replacements dictionary
    replacements = {
        'GITHUB_ACTOR': github_actor,
        'TEST_RESULT': test_result,
        'GITHUB_REF': github_ref,
        'TOTAL_TESTS': total_tests,
        'PASSED_TESTS': passed_tests,
        'FAILED_TESTS': failed_tests,
        'SKIPPED_TESTS': skipped_tests,
        'PASSED_PERCENT': passed_percent,
        'FAILED_PERCENT': failed_percent,
        'SKIPPED_PERCENT': skipped_percent,
        'SUCCESS_RATE': success_rate,
        'GITHUB_REPOSITORY': github_repository,
        'GITHUB_WORKFLOW': github_workflow,
        'GITHUB_RUN_NUMBER': github_run_number,
        'GITHUB_RUN_ID': github_run_id,
        'GITHUB_SERVER_URL': github_server_url
    }
    
    # Get template and output paths
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / 'templates' / 'email-template.html'
    output_path = Path.cwd() / 'email-body.html'
    
    # Check if template exists
    if not template_path.exists():
        print(f"Error: Template file not found at {template_path}")
        sys.exit(1)
    
    # Replace placeholders and save
    replace_placeholders(template_path, output_path, replacements)
    
    # Also output the path for GitHub Actions
    print(f"::set-output name=email_body_path::{output_path}")


if __name__ == "__main__":
    main()
