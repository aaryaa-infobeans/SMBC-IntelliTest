"""
AutoHealer Configuration
Centralized configuration for AutoHealer GitHub PR integration.
"""

import os
from typing import Dict, Any


class AutoHealerConfig:
    """Configuration class for AutoHealer settings."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        # PR Creation Settings
        self.enable_pr_creation = os.getenv("AUTOHEALER_ENABLE_PR", "true").lower() == "true"
        self.pr_draft_mode = os.getenv("AUTOHEALER_PR_DRAFT", "false").lower() == "true"
        self.max_fixes_per_pr = int(os.getenv("AUTOHEALER_MAX_FIXES_PER_PR", "10"))
        
        # GitHub Settings
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repository = os.getenv("GITHUB_REPOSITORY")
        self.github_base_branch = os.getenv("AUTOHEALER_BASE_BRANCH", "main")
        
        # AutoHealer Behavior Settings
        self.max_healing_attempts = int(os.getenv("AUTOHEALER_MAX_ATTEMPTS", "3"))
        self.enable_fallback_suggestions = os.getenv("AUTOHEALER_ENABLE_FALLBACK", "true").lower() == "true"
        self.save_dom_snapshots = os.getenv("AUTOHEALER_SAVE_DOM", "true").lower() == "true"
        
        # Locator Search Settings
        self.search_timeout = int(os.getenv("AUTOHEALER_SEARCH_TIMEOUT", "30"))
        self.include_test_patterns = os.getenv("AUTOHEALER_TEST_PATTERNS", "test_*.py,*_test.py").split(",")
        self.exclude_patterns = os.getenv("AUTOHEALER_EXCLUDE_PATTERNS", "__pycache__,*.pyc").split(",")
        
        # Logging Settings
        self.log_level = os.getenv("AUTOHEALER_LOG_LEVEL", "INFO")
        self.log_pr_details = os.getenv("AUTOHEALER_LOG_PR_DETAILS", "true").lower() == "true"
        
    def is_enabled(self) -> bool:
        """Check if AutoHealer PR creation is enabled."""
        return (
            self.enable_pr_creation and 
            os.getenv("GITHUB_ACTIONS") == "true" and
            self.github_token is not None and
            self.github_repository is not None
        )
    
    def get_branch_name(self, run_number: str = None) -> str:
        """Generate branch name for AutoHealer fixes."""
        if run_number is None:
            run_number = os.getenv("GITHUB_RUN_NUMBER", "manual")
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"autohealer/locator-fixes-{run_number}-{timestamp}"
    
    def get_pr_labels(self) -> list:
        """Get labels to apply to the PR."""
        default_labels = ["autohealer", "locator-fix", "automated-pr"]
        custom_labels = os.getenv("AUTOHEALER_PR_LABELS", "").split(",")
        custom_labels = [label.strip() for label in custom_labels if label.strip()]
        
        return default_labels + custom_labels
    
    def get_pr_reviewers(self) -> list:
        """Get reviewers to assign to the PR."""
        reviewers = os.getenv("AUTOHEALER_PR_REVIEWERS", "").split(",")
        return [reviewer.strip() for reviewer in reviewers if reviewer.strip()]
    
    def get_pr_assignees(self) -> list:
        """Get assignees for the PR."""
        assignees = os.getenv("AUTOHEALER_PR_ASSIGNEES", "").split(",")
        return [assignee.strip() for assignee in assignees if assignee.strip()]
    
    def should_create_pr(self, fixes_count: int) -> bool:
        """Determine if a PR should be created based on the number of fixes."""
        if not self.is_enabled():
            return False
            
        if fixes_count == 0:
            return False
            
        if fixes_count > self.max_fixes_per_pr:
            # Log warning but still create PR
            import logging
            logging.warning(f"High number of fixes ({fixes_count}) exceeds recommended maximum ({self.max_fixes_per_pr})")
            
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging."""
        return {
            "enable_pr_creation": self.enable_pr_creation,
            "pr_draft_mode": self.pr_draft_mode,
            "max_fixes_per_pr": self.max_fixes_per_pr,
            "github_repository": self.github_repository,
            "github_base_branch": self.github_base_branch,
            "max_healing_attempts": self.max_healing_attempts,
            "enable_fallback_suggestions": self.enable_fallback_suggestions,
            "save_dom_snapshots": self.save_dom_snapshots,
            "search_timeout": self.search_timeout,
            "include_test_patterns": self.include_test_patterns,
            "exclude_patterns": self.exclude_patterns,
            "log_level": self.log_level,
            "log_pr_details": self.log_pr_details,
            "is_enabled": self.is_enabled()
        }


# Global configuration instance
_config = None


def get_config() -> AutoHealerConfig:
    """Get the global AutoHealer configuration instance."""
    global _config
    if _config is None:
        _config = AutoHealerConfig()
    return _config


def print_config():
    """Print current AutoHealer configuration for debugging."""
    config = get_config()
    import json
    print("AutoHealer Configuration:")
    print(json.dumps(config.to_dict(), indent=2))


# Environment variable documentation
ENVIRONMENT_VARIABLES = {
    "AUTOHEALER_ENABLE_PR": "Enable/disable PR creation (true/false, default: true)",
    "AUTOHEALER_PR_DRAFT": "Create PR as draft (true/false, default: false)",
    "AUTOHEALER_MAX_FIXES_PER_PR": "Maximum number of fixes per PR (int, default: 10)",
    "AUTOHEALER_BASE_BRANCH": "Base branch for PRs (string, default: main)",
    "AUTOHEALER_MAX_ATTEMPTS": "Maximum healing attempts per locator (int, default: 3)",
    "AUTOHEALER_ENABLE_FALLBACK": "Enable fallback suggestions (true/false, default: true)",
    "AUTOHEALER_SAVE_DOM": "Save DOM snapshots (true/false, default: true)",
    "AUTOHEALER_SEARCH_TIMEOUT": "Timeout for locator search in seconds (int, default: 30)",
    "AUTOHEALER_TEST_PATTERNS": "Test file patterns (comma-separated, default: test_*.py,*_test.py)",
    "AUTOHEALER_EXCLUDE_PATTERNS": "Exclude patterns (comma-separated, default: __pycache__,*.pyc)",
    "AUTOHEALER_LOG_LEVEL": "Log level (DEBUG/INFO/WARNING/ERROR, default: INFO)",
    "AUTOHEALER_LOG_PR_DETAILS": "Log PR creation details (true/false, default: true)",
    "AUTOHEALER_PR_LABELS": "Additional PR labels (comma-separated)",
    "AUTOHEALER_PR_REVIEWERS": "PR reviewers (comma-separated GitHub usernames)",
    "AUTOHEALER_PR_ASSIGNEES": "PR assignees (comma-separated GitHub usernames)",
    "GITHUB_TOKEN": "GitHub personal access token (required for PR creation)",
    "GITHUB_REPOSITORY": "GitHub repository in format owner/repo (set by GitHub Actions)",
    "GITHUB_ACTIONS": "Set to 'true' by GitHub Actions (used for detection)"
}
