"""
Jira API client with enhanced error handling and security.

This module provides a secure wrapper for Jira API operations with comprehensive
error handling, retry logic, and security validations.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from jira import JIRA, JIRAError

try:
    from exceptions import JiraConnectionError, JiraOperationError, AttachmentError
except ImportError:
    from src.exceptions import JiraConnectionError, JiraOperationError, AttachmentError


class JiraClient:
    """Secure wrapper for Jira API operations."""
    
    def __init__(self, server: str, username: str, api_token: str):
        """
        Initialize Jira client with authentication.
        
        Args:
            server: Jira server URL
            username: Jira username
            api_token: Jira API token
            
        Raises:
            JiraConnectionError: If connection to Jira fails
        """
        self.server = server
        self.username = username
        self.logger = logging.getLogger(__name__)
        
        try:
            self.jira = JIRA(
                server=server,
                basic_auth=(username, api_token),
                timeout=30,
                max_retries=3,
                options={
                    'verify': True,  # Verify SSL certificates
                    'headers': {
                        'User-Agent': 'GitHub-Action-Jira-Issue/2.0.0'
                    }
                }
            )
            
            # Test connection by getting server info
            server_info = self.jira.server_info()
            self.logger.info(f"Successfully connected to Jira server: {server_info.get('serverTitle', 'Unknown')}")
            
        except JIRAError as e:
            self._handle_connection_error(e)
        except Exception as e:
            raise JiraConnectionError(f"Unexpected error connecting to Jira: {str(e)}")
    
    def create_issue(self, config: Dict[str, Any]) -> str:
        """
        Create a Jira issue with the provided configuration.
        
        Args:
            config: Dictionary containing issue configuration
            
        Returns:
            str: The created issue key
            
        Raises:
            JiraOperationError: If issue creation fails
        """
        try:
            self.logger.info(f"Creating {config['issue_type']} in project {config['project_key']}")
            
            # Validate assignee if provided
            assignee_valid = False
            if config.get('assignee'):
                assignee_valid = self._validate_assignee(config['assignee'])
            
            # Validate parent issue for sub-tasks
            if config.get('parent_issue_key') and config['issue_type'].lower() == 'sub-task':
                self._validate_parent_issue(config['parent_issue_key'])
            
            # Prepare issue data
            issue_data = self._prepare_issue_data(config, assignee_valid)
            
            # Create the issue
            self.logger.debug(f"Creating issue with data: {self._sanitize_for_log(issue_data)}")
            issue = self.jira.create_issue(fields=issue_data)
            
            self.logger.info(f"Successfully created issue: {issue.key}")
            
            # Add attachments if provided
            if config.get('attachment_paths'):
                self._add_attachments(issue, config['attachment_paths'])
            
            return issue.key
            
        except JIRAError as e:
            self._handle_operation_error(e, "create issue")
        except Exception as e:
            raise JiraOperationError(f"Unexpected error creating issue: {str(e)}")
    
    def _validate_assignee(self, assignee: str) -> bool:
        """
        Validate that assignee exists in Jira.
        
        Args:
            assignee: Username to validate
            
        Returns:
            bool: True if assignee is valid, False otherwise
        """
        try:
            user = self.jira.user(assignee)
            self.logger.info(f"Assignee '{assignee}' is valid (Display name: {user.displayName})")
            return True
        except JIRAError as e:
            if e.status_code == 404:
                self.logger.warning(f"Assignee '{assignee}' not found in Jira, issue will be unassigned")
            else:
                self.logger.warning(f"Cannot validate assignee '{assignee}': {str(e)}")
            return False
        except Exception as e:
            self.logger.warning(f"Error validating assignee '{assignee}': {str(e)}")
            return False
    
    def _validate_parent_issue(self, parent_key: str) -> None:
        """
        Validate that parent issue exists for sub-task creation.
        
        Args:
            parent_key: Parent issue key to validate
            
        Raises:
            JiraOperationError: If parent issue doesn't exist or is invalid
        """
        try:
            parent_issue = self.jira.issue(parent_key)
            self.logger.info(f"Parent issue '{parent_key}' is valid: {parent_issue.fields.summary}")
        except JIRAError as e:
            if e.status_code == 404:
                raise JiraOperationError(f"Parent issue '{parent_key}' not found")
            else:
                raise JiraOperationError(f"Cannot access parent issue '{parent_key}': {str(e)}")
        except Exception as e:
            raise JiraOperationError(f"Error validating parent issue '{parent_key}': {str(e)}")
    
    def _prepare_issue_data(self, config: Dict[str, Any], assignee_valid: bool) -> Dict[str, Any]:
        """
        Prepare issue data structure for Jira API.
        
        Args:
            config: Issue configuration
            assignee_valid: Whether the assignee is valid
            
        Returns:
            Dict[str, Any]: Formatted issue data for Jira API
        """
        issue_data = {
            'project': {'key': config['project_key']},
            'issuetype': {'name': config['issue_type']},
            'summary': config['issue_summary'],
            'description': config['issue_description'],
            'priority': {'name': config['issue_priority']},
        }
        
        # Add labels if provided
        if config.get('labels'):
            issue_data['labels'] = config['labels']
        
        # Add parent for sub-tasks
        if config.get('parent_issue_key') and config['issue_type'].lower() == 'sub-task':
            issue_data['parent'] = {'key': config['parent_issue_key']}
            self.logger.info(f"Setting parent issue: {config['parent_issue_key']}")
        
        # Add assignee if valid
        if config.get('assignee') and assignee_valid:
            issue_data['assignee'] = {'name': config['assignee']}
            self.logger.info(f"Assigning issue to: {config['assignee']}")
        
        return issue_data
    
    def _add_attachments(self, issue: Any, attachment_paths: List[str]) -> None:
        """
        Add attachments to the created issue.
        
        Args:
            issue: The Jira issue object
            attachment_paths: List of file paths to attach
            
        Raises:
            AttachmentError: If attachment operation fails
        """
        self.logger.info(f"Adding {len(attachment_paths)} attachment(s) to issue {issue.key}")
        
        successful_attachments = 0
        failed_attachments = []
        
        for path in attachment_paths:
            try:
                if not os.path.exists(path):
                    self.logger.warning(f"Attachment file not found: {path}")
                    failed_attachments.append(f"{path} (file not found)")
                    continue
                
                if not os.access(path, os.R_OK):
                    self.logger.warning(f"Attachment file not readable: {path}")
                    failed_attachments.append(f"{path} (not readable)")
                    continue
                
                # Get file size for logging
                file_size = os.path.getsize(path)
                self.logger.debug(f"Attaching file: {path} ({file_size} bytes)")
                
                with open(path, 'rb') as f:
                    attachment = self.jira.add_attachment(issue=issue, attachment=f)
                    self.logger.info(f"Successfully attached: {attachment.filename}")
                    successful_attachments += 1
                
            except JIRAError as e:
                error_msg = f"Failed to attach {path}: {str(e)}"
                self.logger.error(error_msg)
                failed_attachments.append(f"{path} (Jira error: {str(e)})")
            except Exception as e:
                error_msg = f"Failed to attach {path}: {str(e)}"
                self.logger.error(error_msg)
                failed_attachments.append(f"{path} (error: {str(e)})")
        
        # Log summary
        if successful_attachments > 0:
            self.logger.info(f"Successfully attached {successful_attachments} file(s)")
        
        if failed_attachments:
            self.logger.warning(f"Failed to attach {len(failed_attachments)} file(s): {', '.join(failed_attachments)}")
            # Don't fail the entire operation for attachment errors, just log them
    
    def _sanitize_for_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize sensitive data for logging.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Dict[str, Any]: Sanitized data safe for logging
        """
        sanitized = data.copy()
        
        # Truncate long descriptions for logging
        if 'description' in sanitized and len(sanitized['description']) > 100:
            sanitized['description'] = sanitized['description'][:100] + "..."
        
        return sanitized
    
    def _handle_connection_error(self, error: JIRAError) -> None:
        """
        Handle Jira connection errors with specific messages.
        
        Args:
            error: The JIRAError that occurred
            
        Raises:
            JiraConnectionError: With appropriate error message
        """
        status_code = getattr(error, 'status_code', None)
        
        error_messages = {
            401: "Authentication failed. Please check your username and API token.",
            403: "Access forbidden. Your account may not have permission to access this Jira instance.",
            404: "Jira server not found. Please verify the server URL.",
            429: "Rate limit exceeded. Please try again later.",
            500: "Jira server internal error. Please try again later or contact your administrator.",
            502: "Bad gateway. There may be network connectivity issues.",
            503: "Jira service unavailable. The server may be under maintenance.",
            504: "Gateway timeout. The request took too long to complete."
        }
        
        if status_code in error_messages:
            message = error_messages[status_code]
            details = f"HTTP {status_code}: {getattr(error, 'text', 'No additional details')}"
        else:
            message = f"Connection to Jira failed"
            details = f"HTTP {status_code}: {str(error)}"
        
        self.logger.error(f"Jira connection error: {message} ({details})")
        raise JiraConnectionError(message, details)
    
    def _handle_operation_error(self, error: JIRAError, operation: str) -> None:
        """
        Handle Jira operation errors.
        
        Args:
            error: The JIRAError that occurred
            operation: Description of the operation that failed
            
        Raises:
            JiraOperationError: With appropriate error message
        """
        status_code = getattr(error, 'status_code', None)
        
        error_messages = {
            400: f"Bad request for {operation}. Please check your input parameters.",
            401: f"Authentication failed during {operation}.",
            403: f"Permission denied for {operation}. Contact your Jira administrator.",
            404: f"Resource not found for {operation}. Check project key, issue type, or parent issue.",
            409: f"Conflict occurred during {operation}. The resource may already exist.",
            422: f"Invalid input for {operation}. Check required fields and field types.",
            429: f"Rate limit exceeded during {operation}. Please try again later."
        }
        
        if status_code in error_messages:
            message = error_messages[status_code]
            details = f"HTTP {status_code}: {getattr(error, 'text', 'No additional details')}"
        else:
            message = f"Operation '{operation}' failed"
            details = f"HTTP {status_code}: {str(error)}"
        
        self.logger.error(f"Jira operation error: {message} ({details})")
        raise JiraOperationError(message, details)