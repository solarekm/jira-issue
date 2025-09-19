"""
Utility functions for the Jira Action.

This module provides helper functions for common operations
like environment variable handling and GitHub integration.
"""

import os
import logging
from typing import Optional, List, Dict


class GitHubIntegration:
    """Helper class for GitHub Actions integration."""

    @staticmethod
    def update_step_summary(jira_server: str, issue_key: str) -> None:
        """
        Update GitHub step summary with issue link.

        Args:
            jira_server: Jira server URL
            issue_key: Created issue key
        """
        summary_path = os.getenv("GITHUB_STEP_SUMMARY")
        if not summary_path:
            logging.warning("GITHUB_STEP_SUMMARY environment variable not found")
            return

        try:
            issue_url = f"{jira_server}/browse/{issue_key}"
            summary_line = f"✅ **Jira Issue Created:** [{issue_key}]({issue_url})\\n\\n"

            # Append to existing summary
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(summary_line)

            logging.info(f"Updated GitHub step summary with issue link: {issue_url}")

        except Exception as e:
            logging.warning(f"Failed to update GitHub step summary: {str(e)}")

    @staticmethod
    def set_output(name: str, value: str) -> None:
        """
        Set GitHub Actions output.

        Args:
            name: Output name
            value: Output value
        """
        output_file = os.getenv("GITHUB_OUTPUT")
        if not output_file:
            logging.warning("GITHUB_OUTPUT environment variable not found")
            return

        try:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"{name}={value}\\n")
            logging.debug(f"Set GitHub output: {name}={value}")
        except Exception as e:
            logging.warning(f"Failed to set GitHub output: {str(e)}")


class EnvironmentHelper:
    """Helper class for environment variable operations."""

    @staticmethod
    def get_required_env(name: str) -> str:
        """
        Get required environment variable.

        Args:
            name: Environment variable name

        Returns:
            str: Environment variable value

        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Required environment variable {name} is not set")
        return value

    @staticmethod
    def get_optional_env(name: str, default: str = "") -> str:
        """
        Get optional environment variable.

        Args:
            name: Environment variable name
            default: Default value if not set

        Returns:
            str: Environment variable value or default
        """
        return os.getenv(name, default)

    @staticmethod
    def parse_comma_separated(value: Optional[str]) -> List[str]:
        """
        Parse comma-separated string into list.

        Args:
            value: Comma-separated string

        Returns:
            List[str]: List of trimmed values
        """
        if not value or not value.strip():
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def get_all_inputs() -> Dict[str, str]:
        """
        Get all GitHub Actions inputs from environment variables.

        Returns:
            Dict[str, str]: Dictionary of all input values
        """
        return {
            "jira_server": EnvironmentHelper.get_required_env("INPUT_JIRA_SERVER"),
            "jira_username": EnvironmentHelper.get_required_env("INPUT_JIRA_USERNAME"),
            "jira_api_token": EnvironmentHelper.get_required_env("INPUT_JIRA_API_TOKEN"),
            "project_key": EnvironmentHelper.get_required_env("INPUT_PROJECT_KEY"),
            "issue_type": EnvironmentHelper.get_required_env("INPUT_ISSUE_TYPE"),
            "issue_summary": EnvironmentHelper.get_required_env("INPUT_ISSUE_SUMMARY"),
            "issue_description": EnvironmentHelper.get_required_env("INPUT_ISSUE_DESCRIPTION"),
            "issue_priority": EnvironmentHelper.get_required_env("INPUT_ISSUE_PRIORITY"),
            "parent_issue_key": EnvironmentHelper.get_optional_env("INPUT_PARENT_ISSUE_KEY"),
            "assignee": EnvironmentHelper.get_optional_env("INPUT_ASSIGNEE"),
            "issue_labels": EnvironmentHelper.get_optional_env("INPUT_ISSUE_LABELS"),
            "attachment_paths": EnvironmentHelper.get_optional_env("INPUT_ATTACHMENT_PATHS"),
        }


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the action.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure logging format
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging.

    Args:
        data: Data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to leave visible at the end

    Returns:
        str: Masked data
    """
    if not data or len(data) <= visible_chars:
        return mask_char * 8  # Standard mask length

    visible_part = data[-visible_chars:]
    masked_part = mask_char * (len(data) - visible_chars)
    return masked_part + visible_part
