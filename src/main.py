#!/usr/bin/env python3
"""
Main entry point for Jira Issue Creation GitHub Action.

This script handles environment variables, validates inputs, and orchestrates
the issue creation process with comprehensive error handling and logging.
"""

import sys
import logging
from typing import Dict, Any

from .validators import InputValidator
from .jira_client import JiraClient
from .utils import (
    setup_logging, 
    EnvironmentHelper, 
    GitHubIntegration,
    mask_sensitive_data
)
from .exceptions import (
    JiraActionError,
    ValidationError,
    JiraConnectionError,
    JiraOperationError
)


def validate_and_prepare_config() -> Dict[str, Any]:
    """
    Validate all inputs and prepare configuration dictionary.
    
    Returns:
        Dict[str, Any]: Validated configuration
        
    Raises:
        ValidationError: If any input validation fails
    """
    logger = logging.getLogger(__name__)
    logger.info("Validating input parameters...")
    
    try:
        # Get all raw inputs
        raw_inputs = EnvironmentHelper.get_all_inputs()
        
        # Initialize validator
        validator = InputValidator()
        
        # Validate all inputs
        config = {
            'jira_server': validator.validate_url(raw_inputs['jira_server']),
            'jira_username': validator.validate_username(raw_inputs['jira_username']),
            'jira_api_token': validator.validate_token(raw_inputs['jira_api_token']),
            'project_key': validator.validate_project_key(raw_inputs['project_key']),
            'issue_type': validator.validate_issue_type(raw_inputs['issue_type']),
            'issue_summary': validator.validate_summary(raw_inputs['issue_summary']),
            'issue_description': validator.validate_description(raw_inputs['issue_description']),
            'issue_priority': validator.validate_priority(raw_inputs['issue_priority']),
            'parent_issue_key': validator.validate_parent_issue_key(raw_inputs['parent_issue_key']),
            'assignee': raw_inputs['assignee'] if raw_inputs['assignee'] else None,
            'labels': validator.validate_labels(raw_inputs['issue_labels']),
            'attachment_paths': validator.validate_attachment_paths(raw_inputs['attachment_paths'])
        }
        
        # Validate assignee if provided
        if config['assignee']:
            config['assignee'] = validator.validate_username(config['assignee'])
        
        # Additional validation for sub-tasks
        if config['issue_type'].lower() == 'sub-task' and not config['parent_issue_key']:
            raise ValidationError("Parent issue key is required for Sub-task type")
        
        # Log configuration (with sensitive data masked)
        log_config = config.copy()
        log_config['jira_api_token'] = mask_sensitive_data(log_config['jira_api_token'])
        logger.info(f"Configuration validated successfully")
        logger.debug(f"Validated configuration: {log_config}")
        
        return config
        
    except ValueError as e:
        raise ValidationError(f"Environment variable error: {str(e)}")


def create_jira_issue(config: Dict[str, Any]) -> str:
    """
    Create Jira issue using validated configuration.
    
    Args:
        config: Validated configuration dictionary
        
    Returns:
        str: Created issue key
        
    Raises:
        JiraConnectionError: If connection to Jira fails
        JiraOperationError: If issue creation fails
    """
    logger = logging.getLogger(__name__)
    logger.info("Initializing Jira client...")
    
    # Create Jira client
    client = JiraClient(
        server=config['jira_server'],
        username=config['jira_username'],
        api_token=config['jira_api_token']
    )
    
    # Create issue
    logger.info("Creating Jira issue...")
    issue_key = client.create_issue(config)
    
    return issue_key


def main() -> None:
    """Main execution function."""
    # Setup logging
    log_level = EnvironmentHelper.get_optional_env('INPUT_LOG_LEVEL', 'INFO')
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("=== Jira Issue Creation Action Started ===")
    
    try:
        # Validate inputs and prepare configuration
        config = validate_and_prepare_config()
        
        # Log action summary
        logger.info(f"Creating {config['issue_type']} in project {config['project_key']}")
        logger.info(f"Summary: {config['issue_summary'][:50]}{'...' if len(config['issue_summary']) > 50 else ''}")
        
        # Create Jira issue
        issue_key = create_jira_issue(config)
        
        # Update GitHub Actions outputs
        GitHubIntegration.set_output('issue_key', issue_key)
        GitHubIntegration.set_output('issue_url', f"{config['jira_server']}/browse/{issue_key}")
        
        # Update GitHub step summary
        GitHubIntegration.update_step_summary(config['jira_server'], issue_key)
        
        logger.info(f"=== Action completed successfully! Issue created: {issue_key} ===")
        
    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        logger.error("Please check your input parameters and try again.")
        sys.exit(1)
        
    except JiraConnectionError as e:
        logger.error(f"Failed to connect to Jira: {e}")
        logger.error("Please check your Jira server URL, username, and API token.")
        sys.exit(1)
        
    except JiraOperationError as e:
        logger.error(f"Failed to create Jira issue: {e}")
        logger.error("Please check your project permissions and input parameters.")
        sys.exit(1)
        
    except JiraActionError as e:
        logger.error(f"Action failed: {e}")
        if e.details:
            logger.error(f"Details: {e.details}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        logger.error("Please report this issue to the action maintainers.")
        logger.debug("Exception details:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()