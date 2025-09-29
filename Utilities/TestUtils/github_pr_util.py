"""
GitHub PR Utility for AutoHealer
Creates pull requests for locator fixes when running in GitHub Actions pipeline.
"""

import json
import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple

import requests

from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class GitHubPRUtil:
    """Utility class for creating GitHub PRs with locator fixes."""

    def __init__(self):
        """Initialize GitHub PR utility with environment configuration."""
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repository = os.getenv("GITHUB_REPOSITORY")
        self.github_actor = os.getenv("GITHUB_ACTOR", "autohealer-bot")
        self.github_workflow = os.getenv("GITHUB_WORKFLOW", "test-execution")
        self.github_run_id = os.getenv("GITHUB_RUN_ID")
        self.github_run_number = os.getenv("GITHUB_RUN_NUMBER")
        self.github_sha = os.getenv("GITHUB_SHA")
        
        # Check if running in GitHub Actions
        self.is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
        
        # API base URL
        self.api_base_url = "https://api.github.com"
        
        # Headers for GitHub API
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AutoHealer-Bot/1.0"
        }
        
        # Track locator fixes for batching
        self.locator_fixes: List[Dict] = []
        
    def is_running_in_github_actions(self) -> bool:
        """Check if the current execution is running in GitHub Actions."""
        return self.is_github_actions
    
    def is_configured(self) -> bool:
        """Check if GitHub PR utility is properly configured."""
        if not self.is_github_actions:
            return False
            
        missing_vars = []
        if not self.github_token:
            missing_vars.append("GITHUB_TOKEN")
        if not self.github_repository:
            missing_vars.append("GITHUB_REPOSITORY")
            
        if missing_vars:
            logger.warning(f"GitHub PR utility not configured. Missing environment variables: {', '.join(missing_vars)}")
            return False
            
        return True
    
    def add_locator_fix(self, original_locator: str, suggested_locator: str, 
                       file_path: str, description: str, error_message: str,
                       test_function: str = None, line_number: int = None) -> None:
        """
        Add a locator fix to the batch for PR creation.
        
        Args:
            original_locator: The original failing locator
            suggested_locator: The AI-suggested replacement locator
            file_path: Path to the test file containing the locator
            description: Description of the element
            error_message: The error that occurred
            test_function: Name of the test function (if available)
            line_number: Line number where the locator is used (if available)
        """
        if not self.is_configured():
            return
            
        fix_data = {
            "original_locator": original_locator,
            "suggested_locator": suggested_locator,
            "file_path": file_path,
            "description": description,
            "error_message": error_message,
            "test_function": test_function,
            "line_number": line_number,
            "timestamp": self._get_timestamp()
        }
        
        self.locator_fixes.append(fix_data)
        logger.info(f"Added locator fix to batch: {original_locator} -> {suggested_locator} in {file_path}")
    
    def create_pr_for_fixes(self) -> Optional[str]:
        """
        Create a GitHub PR with all collected locator fixes.
        
        Returns:
            PR URL if successful, None otherwise
        """
        if not self.is_configured():
            logger.warning("Cannot create PR: GitHub PR utility not properly configured")
            return None
            
        if not self.locator_fixes:
            logger.info("No locator fixes to create PR for")
            return None
            
        try:
            # Create a new branch for the fixes
            branch_name = self._create_fix_branch()
            if not branch_name:
                return None
                
            # Apply fixes to files
            files_modified = self._apply_fixes_to_files()
            if not files_modified:
                logger.warning("No files were modified with locator fixes")
                return None
                
            # Commit changes
            commit_sha = self._commit_changes(branch_name, files_modified)
            if not commit_sha:
                return None
                
            # Create pull request
            pr_url = self._create_pull_request(branch_name, files_modified)
            
            if pr_url:
                logger.info(f"Successfully created PR for locator fixes: {pr_url}")
                # Clear the fixes after successful PR creation
                self.locator_fixes.clear()
            
            return pr_url
            
        except Exception as e:
            logger.error(f"Failed to create PR for locator fixes: {str(e)}")
            return None
    
    def _create_fix_branch(self) -> Optional[str]:
        """Create a new branch for locator fixes."""
        try:
            branch_name = f"autohealer/locator-fixes-{self.github_run_number}-{self._get_timestamp()}"
            
            # Get the default branch SHA
            repo_info = self._make_github_request("GET", f"/repos/{self.github_repository}")
            default_branch = repo_info["default_branch"]
            
            # Get the SHA of the default branch
            branch_info = self._make_github_request("GET", f"/repos/{self.github_repository}/git/refs/heads/{default_branch}")
            base_sha = branch_info["object"]["sha"]
            
            # Create new branch
            create_branch_data = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha
            }
            
            self._make_github_request("POST", f"/repos/{self.github_repository}/git/refs", create_branch_data)
            logger.info(f"Created branch: {branch_name}")
            
            return branch_name
            
        except Exception as e:
            logger.error(f"Failed to create branch: {str(e)}")
            return None
    
    def _apply_fixes_to_files(self) -> Dict[str, str]:
        """
        Apply locator fixes to files and return modified file contents.
        
        Returns:
            Dictionary mapping file paths to their new contents
        """
        files_modified = {}
        
        # Group fixes by file path
        fixes_by_file = {}
        for fix in self.locator_fixes:
            file_path = fix["file_path"]
            if file_path not in fixes_by_file:
                fixes_by_file[file_path] = []
            fixes_by_file[file_path].append(fix)
        
        # Apply fixes to each file
        for file_path, fixes in fixes_by_file.items():
            try:
                # Get current file content from GitHub
                file_content = self._get_file_content(file_path)
                if file_content is None:
                    continue
                    
                modified_content = self._apply_fixes_to_content(file_content, fixes)
                if modified_content != file_content:
                    files_modified[file_path] = modified_content
                    logger.info(f"Applied fixes to {file_path}")
                    
            except Exception as e:
                logger.error(f"Failed to apply fixes to {file_path}: {str(e)}")
                continue
                
        return files_modified
    
    def _apply_fixes_to_content(self, content: str, fixes: List[Dict]) -> str:
        """Apply locator fixes to file content."""
        modified_content = content
        
        for fix in fixes:
            original_locator = fix["original_locator"]
            suggested_locator = fix["suggested_locator"]
            
            # Escape special regex characters
            escaped_original = re.escape(original_locator)
            
            # Try to find and replace the locator in various common patterns
            patterns = [
                f'"{escaped_original}"',  # Double quotes
                f"'{escaped_original}'",  # Single quotes
                f'locator\\("{escaped_original}"\\)',  # page.locator() method
                f'locator\\(\'{escaped_original}\'\\)',  # page.locator() with single quotes
            ]
            
            replaced = False
            for pattern in patterns:
                if re.search(pattern, modified_content):
                    # Replace with the suggested locator maintaining the same quote style
                    if pattern.startswith('"'):
                        replacement = f'"{suggested_locator}"'
                    elif pattern.startswith("'"):
                        replacement = f"'{suggested_locator}'"
                    elif 'locator("' in pattern:
                        replacement = f'locator("{suggested_locator}")'
                    elif "locator('" in pattern:
                        replacement = f"locator('{suggested_locator}')"
                    else:
                        replacement = suggested_locator
                    
                    modified_content = re.sub(pattern, replacement, modified_content, count=1)
                    replaced = True
                    logger.debug(f"Replaced locator using pattern: {pattern}")
                    break
            
            if not replaced:
                logger.warning(f"Could not find pattern to replace locator: {original_locator}")
        
        return modified_content
    
    def _get_file_content(self, file_path: str) -> Optional[str]:
        """Get file content from GitHub repository."""
        try:
            response = self._make_github_request("GET", f"/repos/{self.github_repository}/contents/{file_path}")
            
            if response.get("type") == "file":
                import base64
                content = base64.b64decode(response["content"]).decode("utf-8")
                return content
            else:
                logger.error(f"Path {file_path} is not a file")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get content for {file_path}: {str(e)}")
            return None
    
    def _commit_changes(self, branch_name: str, files_modified: Dict[str, str]) -> Optional[str]:
        """Commit the modified files to the branch."""
        try:
            # Get the latest commit SHA of the branch
            branch_ref = self._make_github_request("GET", f"/repos/{self.github_repository}/git/refs/heads/{branch_name}")
            latest_commit_sha = branch_ref["object"]["sha"]
            
            # Get the tree SHA of the latest commit
            commit_info = self._make_github_request("GET", f"/repos/{self.github_repository}/git/commits/{latest_commit_sha}")
            base_tree_sha = commit_info["tree"]["sha"]
            
            # Create blobs for modified files
            tree_items = []
            for file_path, content in files_modified.items():
                blob_data = {"content": content, "encoding": "utf-8"}
                blob_response = self._make_github_request("POST", f"/repos/{self.github_repository}/git/blobs", blob_data)
                
                tree_items.append({
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_response["sha"]
                })
            
            # Create new tree
            tree_data = {"base_tree": base_tree_sha, "tree": tree_items}
            tree_response = self._make_github_request("POST", f"/repos/{self.github_repository}/git/trees", tree_data)
            new_tree_sha = tree_response["sha"]
            
            # Create commit
            commit_message = self._generate_commit_message()
            commit_data = {
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [latest_commit_sha]
            }
            commit_response = self._make_github_request("POST", f"/repos/{self.github_repository}/git/commits", commit_data)
            new_commit_sha = commit_response["sha"]
            
            # Update branch reference
            update_ref_data = {"sha": new_commit_sha}
            self._make_github_request("PATCH", f"/repos/{self.github_repository}/git/refs/heads/{branch_name}", update_ref_data)
            
            logger.info(f"Committed changes to branch {branch_name}: {new_commit_sha}")
            return new_commit_sha
            
        except Exception as e:
            logger.error(f"Failed to commit changes: {str(e)}")
            return None
    
    def _create_pull_request(self, branch_name: str, files_modified: Dict[str, str]) -> Optional[str]:
        """Create a pull request for the locator fixes."""
        try:
            # Get repository info to determine default branch
            repo_info = self._make_github_request("GET", f"/repos/{self.github_repository}")
            default_branch = repo_info["default_branch"]
            
            # Generate PR title and body
            pr_title = self._generate_pr_title()
            pr_body = self._generate_pr_body(files_modified)
            
            # Create pull request
            pr_data = {
                "title": pr_title,
                "body": pr_body,
                "head": branch_name,
                "base": default_branch,
                "draft": False
            }
            
            pr_response = self._make_github_request("POST", f"/repos/{self.github_repository}/pulls", pr_data)
            pr_url = pr_response["html_url"]
            
            logger.info(f"Created pull request: {pr_url}")
            return pr_url
            
        except Exception as e:
            logger.error(f"Failed to create pull request: {str(e)}")
            return None
    
    def _generate_commit_message(self) -> str:
        """Generate commit message for locator fixes."""
        fix_count = len(self.locator_fixes)
        files_count = len(set(fix["file_path"] for fix in self.locator_fixes))
        
        return f"🔧 AutoHealer: Fix {fix_count} failing locator{'s' if fix_count > 1 else ''} in {files_count} file{'s' if files_count > 1 else ''}"
    
    def _generate_pr_title(self) -> str:
        """Generate PR title for locator fixes."""
        fix_count = len(self.locator_fixes)
        return f"🔧 AutoHealer: Fix {fix_count} failing locator{'s' if fix_count > 1 else ''}"
    
    def _generate_pr_body(self, files_modified: Dict[str, str]) -> str:
        """Generate PR body with details of locator fixes."""
        body_parts = [
            "## 🤖 AutoHealer Locator Fixes",
            "",
            f"This PR was automatically created by AutoHealer during test execution in workflow run #{self.github_run_number}.",
            "",
            "### 📋 Summary of Changes",
            f"- **Fixed locators:** {len(self.locator_fixes)}",
            f"- **Modified files:** {len(files_modified)}",
            f"- **Workflow run:** [#{self.github_run_number}](https://github.com/{self.github_repository}/actions/runs/{self.github_run_id})",
            "",
            "### 🔍 Locator Fixes Details",
            ""
        ]
        
        # Group fixes by file for better organization
        fixes_by_file = {}
        for fix in self.locator_fixes:
            file_path = fix["file_path"]
            if file_path not in fixes_by_file:
                fixes_by_file[file_path] = []
            fixes_by_file[file_path].append(fix)
        
        for file_path, fixes in fixes_by_file.items():
            body_parts.append(f"#### 📄 `{file_path}`")
            body_parts.append("")
            
            for i, fix in enumerate(fixes, 1):
                body_parts.extend([
                    f"**Fix #{i}:** {fix['description']}",
                    f"- **Original locator:** `{fix['original_locator']}`",
                    f"- **Suggested locator:** `{fix['suggested_locator']}`",
                    f"- **Error:** {fix['error_message'][:100]}{'...' if len(fix['error_message']) > 100 else ''}",
                ])
                
                if fix.get('test_function'):
                    body_parts.append(f"- **Test function:** `{fix['test_function']}`")
                if fix.get('line_number'):
                    body_parts.append(f"- **Line number:** {fix['line_number']}")
                    
                body_parts.append("")
        
        body_parts.extend([
            "### ⚠️ Review Required",
            "",
            "Please review these changes carefully before merging:",
            "1. **Verify** that the new locators correctly identify the intended elements",
            "2. **Test** the changes in your local environment",
            "3. **Run** the affected tests to ensure they pass",
            "4. **Consider** if these changes might affect other tests",
            "",
            "### 🚀 How to Test",
            "1. Check out this branch locally",
            "2. Run the affected tests",
            "3. Verify that the elements are correctly identified",
            "",
            f"---",
            f"*Generated by AutoHealer Bot - Workflow: {self.github_workflow}*"
        ])
        
        return "\n".join(body_parts)
    
    def _make_github_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make a request to GitHub API."""
        url = f"{self.api_base_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=self.headers)
        elif method == "POST":
            response = requests.post(url, headers=self.headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=self.headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if not response.ok:
            error_msg = f"GitHub API request failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return response.json()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        import datetime
        return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    def find_locator_in_test_files(self, locator: str, description: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Find the test file, function, and line number where a locator is used.
        
        Args:
            locator: The locator to search for
            description: Element description to help with searching
            
        Returns:
            Tuple of (file_path, test_function, line_number) or (None, None, None) if not found
        """
        try:
            # Use git grep to search for the locator in test files
            escaped_locator = locator.replace('"', '\\"').replace("'", "\\'")
            
            # Try different search patterns
            search_patterns = [
                f'"{escaped_locator}"',
                f"'{escaped_locator.replace(chr(34), chr(39))}'",
                escaped_locator
            ]
            
            for pattern in search_patterns:
                try:
                    # Search for the pattern in Python test files
                    result = subprocess.run(
                        ["git", "grep", "-n", "--", pattern, "*.py"],
                        capture_output=True,
                        text=True,
                        cwd=os.getcwd()
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if ':' in line:
                                parts = line.split(':', 2)
                                if len(parts) >= 2:
                                    file_path = parts[0]
                                    line_number = int(parts[1])
                                    
                                    # Try to find the test function
                                    test_function = self._find_test_function(file_path, line_number)
                                    
                                    return file_path, test_function, line_number
                                    
                except subprocess.SubprocessError:
                    continue
            
            logger.warning(f"Could not find locator '{locator}' in test files")
            return None, None, None
            
        except Exception as e:
            logger.error(f"Error searching for locator in test files: {str(e)}")
            return None, None, None

    def _find_test_function(self, file_path: str, line_number: int) -> Optional[str]:
        """Find the test function name that contains the given line number."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Search backwards from the line to find the function definition
            current_function = None
            for i in range(line_number - 1, -1, -1):
                line = lines[i].strip()
                if line.startswith('def ') and ('test_' in line or 'Test' in line):
                    # Extract function name
                    func_name = line.split('def ')[1].split('(')[0].strip()
                    current_function = func_name
                    break
            
            return current_function
            
        except Exception as e:
            logger.error(f"Error finding test function in {file_path}: {str(e)}")
            return None
